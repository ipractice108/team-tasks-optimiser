# Railway Deployment Guide

## Critical: Environment Variables Setup

Railway does NOT automatically read the .env file. You MUST manually configure all environment variables in Railway's dashboard.

### Required Environment Variables

Go to your Railway project → Variables tab and add:

```
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
AI_PROVIDER=groq
AI_API_KEY=your_groq_api_key_here
AI_MODEL=llama-3.3-70b-versatile
ADMIN_USER_ID=your_telegram_user_id
DATABASE_URL=sqlite:///./data/chat_analyzer.db
ANALYSIS_SCHEDULE_DAY_1=0
ANALYSIS_SCHEDULE_TIME_1=10:00
ANALYSIS_SCHEDULE_DAY_2=3
ANALYSIS_SCHEDULE_TIME_2=10:00
ANALYSIS_DAYS_BACK=7
MIN_MESSAGES_FOR_ANALYSIS=10
```

**⚠️ IMPORTANT: Use your actual values from the .env file, not these placeholders!**

## How to Add Environment Variables in Railway

1. Open your Railway project
2. Click on your service
3. Click on the "Variables" tab
4. Click "New Variable"
5. Add each variable one by one from the list above
6. After adding all variables, Railway will automatically redeploy

## Checking Logs

To check if your bot is running correctly:

1. Go to your Railway project
2. Click on your service
3. Click on "Deployments" tab
4. Click on the latest deployment
5. View the logs

### Expected Log Output

You should see:
```
============================================================
Starting Telegram Chat Analyzer Bot
============================================================
Initializing database...
Database initialized
Admin user set: 8216523502
Initializing AI analyzer...
Using AI provider: groq
AI analyzer initialized
Setting up bot handlers...
Bot handlers configured
Setting up analysis scheduler...
Scheduler started
============================================================
Bot is running! Press Ctrl+C to stop.
============================================================
Bot initialized successfully
Bot username: @your_bot_name
Bot ID: 8382984885
```

### Common Errors in Logs

**Error: Missing environment variables**
```
Missing required environment variables: TELEGRAM_BOT_TOKEN, ADMIN_USER_ID
```
→ Solution: Add missing variables in Railway Variables tab

**Error: Invalid AI_PROVIDER**
```
Invalid AI_PROVIDER: None
```
→ Solution: Add AI_PROVIDER=groq in Railway Variables

**Error: AI_API_KEY is required**
```
AI_API_KEY is required for provider: groq
```
→ Solution: Add your Groq API key in Railway Variables

## Testing the Bot

After deployment with proper environment variables:

1. Open Telegram
2. Find your bot
3. Send `/start` - should get welcome message
4. Send `/status` - should show monitoring status
5. In your work chat (where bot is admin), send `/analyze` - should start analysis

## Troubleshooting

### Bot doesn't respond to commands

**Check 1: Environment Variables**
- Verify ALL environment variables are set in Railway (not just .env file)
- Railway doesn't read .env files automatically

**Check 2: Bot Permissions**
- Bot must be ADMINISTRATOR in the work chat
- Privacy Mode must be DISABLED (via @BotFather)

**Check 3: Railway Logs**
- Check for any error messages in deployment logs
- Look for "Bot is running!" message

**Check 4: Test in Private Chat First**
- Send `/start` to bot in private message
- If it doesn't respond in private chat, it's a deployment issue
- If it responds in private but not in group, it's a permissions issue

### Bot crashes on startup

Check Railway logs for specific error messages and compare with "Expected Log Output" above.

## Redeploying After Changes

After any code changes:

1. Commit and push to GitHub:
```bash
git add .
git commit -m "Your commit message"
git push
```

2. Railway will automatically detect the push and redeploy

## Manual Redeploy

If you need to manually trigger a redeploy:

1. Go to Railway project
2. Click on service
3. Click "⋮" (three dots) menu
4. Select "Redeploy"

## Database Persistence

The bot uses SQLite database stored in `/app/data/chat_analyzer.db`.

⚠️ **Important**: Railway's ephemeral filesystem means the database will be lost on redeploys unless you:
1. Use a persistent volume (Railway Pro plan)
2. Or switch to PostgreSQL (add Railway PostgreSQL service)

For testing, SQLite is fine. For production, consider PostgreSQL.

## Checking Bot Status in Telegram

1. Send `/start` to bot - tests basic connectivity
2. Send `/status` - shows how many messages collected
3. Send `/analyze` - manually triggers analysis (admin only)

If `/start` works but `/analyze` doesn't:
- Check you're the admin (ADMIN_USER_ID matches your Telegram ID)
- Check there are enough messages (MIN_MESSAGES_FOR_ANALYSIS=10)
- Check Railway logs for errors during analysis
