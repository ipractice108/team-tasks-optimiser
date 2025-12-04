import os
import logging
from datetime import datetime, timedelta
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from database import Database
from analyzer import AIAnalyzer

logger = logging.getLogger(__name__)


class BotHandlers:
    """Telegram bot handlers"""

    def __init__(self, db: Database, analyzer: AIAnalyzer):
        self.db = db
        self.analyzer = analyzer
        self.admin_id = int(os.getenv('ADMIN_USER_ID', 0))
        self.monitored_chats = set()  # Store chat IDs to monitor

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        await update.message.reply_text(
            f"Привет, {user.first_name}!\n\n"
            "Я - AI бот для анализа рабочих чатов.\n\n"
            "Добавьте меня в свой рабочий чат, и я буду:\n"
            "📊 Собирать сообщения из всех топиков\n"
            "🤖 Анализировать процессы и коммуникацию\n"
            "💡 Предлагать оптимизации\n"
            "📨 Отправлять отчёты вам в личку 2 раза в неделю\n\n"
            "Команды:\n"
            "/start - это сообщение\n"
            "/analyze - запустить анализ вручную\n"
            "/status - статус мониторинга\n"
            "/help - помощь"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📖 ПОМОЩЬ

**Как использовать:**

1. Добавьте меня в рабочий чат как администратора
2. Я автоматически начну собирать сообщения
3. Два раза в неделю буду отправлять вам анализ

**Команды:**

/start - Приветствие и описание
/analyze - Запустить анализ вручную (только для админа)
/status - Проверить статус мониторинга
/help - Показать эту справку

**Функции:**

✅ Мониторинг сообщений во всех топиках
✅ AI-анализ процессов и коммуникации
✅ Выявление узких мест
✅ Рекомендации по оптимизации
✅ Автоматические отчёты 2 раза в неделю

**Конфиденциальность:**

🔒 Все сообщения хранятся локально
🔒 Анализ происходит через защищённый API
🔒 Отчёты отправляются только вам
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        # Get message count
        messages = self.db.get_messages(chat_id, days_back=7)
        topics = self.db.get_topics(chat_id, days_back=7)

        status_text = f"""
📊 **СТАТУС МОНИТОРИНГА**

Чат ID: `{chat_id}`
За последние 7 дней:
• Собрано сообщений: {len(messages)}
• Обнаружено топиков: {len(topics)}

Топики: {', '.join(topics) if topics else 'Нет топиков'}

Следующий автоматический анализ: по расписанию
        """
        await update.message.reply_text(status_text, parse_mode='Markdown')

    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command - manual analysis trigger"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        # Check if user is admin
        if user_id != self.admin_id:
            await update.message.reply_text(
                "⛔ Только администратор может запускать анализ вручную."
            )
            return

        await update.message.reply_text(
            "🔄 Запускаю анализ... Это может занять некоторое время."
        )

        try:
            # Perform analysis
            await self.perform_analysis(user_id, chat_id, context)
        except Exception as e:
            logger.error(f"Error in manual analysis: {e}")
            await update.message.reply_text(
                f"❌ Ошибка при анализе: {str(e)}"
            )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        message = update.message
        if not message or not message.text:
            return

        chat = update.effective_chat
        user = update.effective_user

        # Save message to database
        try:
            thread_id = None
            topic_name = None

            # Check if message is in a topic
            if hasattr(message, 'message_thread_id') and message.message_thread_id:
                thread_id = message.message_thread_id

            # Try to get topic name from the chat
            if hasattr(message, 'reply_to_message') and message.reply_to_message:
                if hasattr(message.reply_to_message, 'forum_topic_created'):
                    topic_name = message.reply_to_message.forum_topic_created.name

            # If we still don't have topic name, use thread_id
            if thread_id and not topic_name:
                topic_name = f"Topic {thread_id}"

            self.db.save_message(
                message_id=message.message_id,
                telegram_id=user.id,
                chat_id=chat.id,
                text=message.text,
                thread_id=thread_id,
                topic_name=topic_name,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )

            logger.info(f"Saved message from {user.first_name} in chat {chat.id}")

        except Exception as e:
            logger.error(f"Error saving message: {e}")

    async def perform_analysis(self, user_id: int, chat_id: int,
                              context: ContextTypes.DEFAULT_TYPE):
        """Perform analysis and send report to user"""
        try:
            # Get messages
            days_back = int(os.getenv('ANALYSIS_DAYS_BACK', 7))
            min_messages = int(os.getenv('MIN_MESSAGES_FOR_ANALYSIS', 10))

            messages = self.db.get_messages(chat_id, days_back=days_back)
            topics = self.db.get_topics(chat_id, days_back=days_back)

            if len(messages) < min_messages:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"⚠️ Недостаточно сообщений для анализа.\n"
                         f"Собрано: {len(messages)}, требуется минимум: {min_messages}"
                )
                return

            # Perform analysis
            logger.info(f"Analyzing {len(messages)} messages for user {user_id}")

            analysis = self.analyzer.analyze_messages(messages, topics)

            # Save report
            period_end = datetime.utcnow()
            period_start = period_end - timedelta(days=days_back)

            self.db.save_report(
                telegram_id=user_id,
                chat_id=chat_id,
                report_text=analysis,
                messages_analyzed=len(messages),
                period_start=period_start,
                period_end=period_end
            )

            # Send report to user
            header = f"""
📊 **ОТЧЁТ ПО АНАЛИЗУ ЧАТА**

Период: {period_start.strftime('%d.%m.%Y')} - {period_end.strftime('%d.%m.%Y')}
Сообщений проанализировано: {len(messages)}
Топиков: {len(topics)}

{'—'*30}
            """

            # Split long messages if needed (Telegram limit is 4096 chars)
            full_message = header + "\n" + analysis

            if len(full_message) <= 4096:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=full_message,
                    parse_mode='Markdown'
                )
            else:
                # Send in parts
                await context.bot.send_message(
                    chat_id=user_id,
                    text=header,
                    parse_mode='Markdown'
                )

                # Split analysis into chunks
                chunks = [analysis[i:i+4000] for i in range(0, len(analysis), 4000)]
                for chunk in chunks:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=chunk
                    )

            logger.info(f"Analysis report sent to user {user_id}")

        except Exception as e:
            logger.error(f"Error in perform_analysis: {e}")
            await context.bot.send_message(
                chat_id=user_id,
                text=f"❌ Ошибка при анализе: {str(e)}"
            )

    async def post_init(self, application: Application):
        """Post initialization - set bot commands"""
        commands = [
            BotCommand("start", "Начать работу с ботом"),
            BotCommand("analyze", "Запустить анализ вручную"),
            BotCommand("status", "Статус мониторинга"),
            BotCommand("help", "Помощь"),
        ]
        await application.bot.set_my_commands(commands)


def setup_handlers(application: Application, db: Database, analyzer: AIAnalyzer):
    """Setup bot handlers"""
    handlers = BotHandlers(db, analyzer)

    # Register commands
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("status", handlers.status_command))
    application.add_handler(CommandHandler("analyze", handlers.analyze_command))

    # Register message handler (for all text messages in groups)
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handlers.handle_message
        )
    )

    # Set post init
    application.post_init = handlers.post_init

    return handlers
