# 🚀 Быстрый старт

## За 5 минут до запуска

### 1. Установите Python 3.9+

```bash
python3 --version
```

### 2. Клонируйте репозиторий

```bash
git clone <repository-url>
cd team-tasks-optimiser
```

### 3. Создайте бота в Telegram

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Сохраните **Bot Token** (выглядит как `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 4. Получите Claude API ключ

1. Зарегистрируйтесь на [console.anthropic.com](https://console.anthropic.com/)
2. Создайте API ключ
3. Сохраните его (выглядит как `sk-ant-api03-xxx...`)

### 5. Узнайте свой Telegram ID

1. Напишите боту [@userinfobot](https://t.me/userinfobot)
2. Он пришлёт ваш ID (например, `123456789`)

### 6. Настройте конфигурацию

```bash
cp .env.example .env
nano .env  # или любой другой редактор
```

Заполните три обязательных поля:

```env
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
ANTHROPIC_API_KEY=ваш_ключ_от_Anthropic
ADMIN_USER_ID=ваш_telegram_id
```

### 7. Запустите бота

**Вариант A: Скрипт (рекомендуется для начала)**

```bash
./run.sh
```

**Вариант B: Вручную**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Вариант C: Docker**

```bash
docker-compose up -d
```

### 8. Добавьте бота в чат

1. Откройте ваш рабочий чат
2. Добавьте бота через "Add Members"
3. **Важно:** Сделайте бота администратором

### 9. Проверьте работу

Напишите боту в личку:

```
/start
```

В рабочем чате:

```
/status
```

## ✅ Готово!

Теперь бот:
- Собирает все сообщения из чата
- Будет отправлять вам анализ 2 раза в неделю
- Доступен для ручного анализа через `/analyze`

## 🔧 Настройка расписания

По умолчанию анализ отправляется:
- Понедельник в 10:00
- Четверг в 10:00

Чтобы изменить, отредактируйте `.env`:

```env
# Например, вторник и пятница в 15:00
ANALYSIS_SCHEDULE_DAY_1=1  # Вторник (0=Пн, 1=Вт, ..., 6=Вс)
ANALYSIS_SCHEDULE_TIME_1=15:00
ANALYSIS_SCHEDULE_DAY_2=4  # Пятница
ANALYSIS_SCHEDULE_TIME_2=15:00
```

## 🐛 Что-то не работает?

### Бот не видит сообщения

→ Сделайте бота **администратором** чата

### Не приходят отчёты

→ Убедитесь, что написали боту `/start` в личке

### Ошибка API

→ Проверьте правильность ключей в `.env`

### Проверить логи

```bash
tail -f bot.log
```

## 📖 Полная документация

См. [README.md](README.md)
