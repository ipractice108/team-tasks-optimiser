#!/usr/bin/env python3
"""
Configuration checker for Telegram Chat Analyzer Bot
Checks if all required settings are configured correctly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_status(check_name, status, message=""):
    """Print colored status message"""
    if status:
        print(f"✅ {check_name}")
        if message:
            print(f"   → {message}")
    else:
        print(f"❌ {check_name}")
        if message:
            print(f"   → {message}")

def check_env_var(var_name, required=True):
    """Check if environment variable exists and is not empty"""
    value = os.getenv(var_name)
    if not value:
        if required:
            print_status(f"{var_name}", False, "Не установлен или пуст")
            return False
        else:
            print_status(f"{var_name}", True, "Не установлен (опционально)")
            return True

    # Mask sensitive values
    if "KEY" in var_name or "TOKEN" in var_name:
        display_value = value[:10] + "..." if len(value) > 10 else "***"
    else:
        display_value = value

    print_status(f"{var_name}", True, f"= {display_value}")
    return True

def check_telegram_token():
    """Validate Telegram bot token format"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        return False

    # Basic format check: should contain ':'
    if ':' not in token:
        print_status("Формат TELEGRAM_BOT_TOKEN", False,
                    "Неверный формат токена (должен содержать ':')")
        return False

    print_status("Формат TELEGRAM_BOT_TOKEN", True, "Корректный")
    return True

def check_ai_provider():
    """Validate AI provider configuration"""
    provider = os.getenv('AI_PROVIDER', 'groq').lower()

    valid_providers = ['groq', 'gemini', 'ollama', 'claude']
    if provider not in valid_providers:
        print_status("AI_PROVIDER", False,
                    f"Неверный провайдер '{provider}'. Доступны: {', '.join(valid_providers)}")
        return False

    print_status("AI_PROVIDER", True, f"= {provider}")

    # Check API key for providers that need it
    if provider != 'ollama':
        api_key = os.getenv('AI_API_KEY')
        if not api_key:
            print_status("AI_API_KEY", False,
                        f"API ключ обязателен для провайдера '{provider}'")
            return False

        # Validate key format
        key_preview = api_key[:15] + "..." if len(api_key) > 15 else "***"

        if provider == 'claude' and not api_key.startswith('sk-ant-'):
            print_status("AI_API_KEY", False,
                        f"Ключ Claude должен начинаться с 'sk-ant-'")
            return False
        elif provider == 'groq' and not api_key.startswith('gsk_'):
            print_status("AI_API_KEY", False,
                        f"Ключ Groq должен начинаться с 'gsk_'")
            return False

        print_status("AI_API_KEY", True, f"= {key_preview}")
    else:
        print_status("AI_API_KEY", True, "Не требуется для Ollama")

    # Check model
    model = os.getenv('AI_MODEL', '')
    if model:
        print_status("AI_MODEL", True, f"= {model}")
    else:
        defaults = {
            'groq': 'llama-3.3-70b-versatile',
            'gemini': 'gemini-pro',
            'ollama': 'llama3.1',
            'claude': 'claude-3-5-sonnet-20241022'
        }
        print_status("AI_MODEL", True, f"По умолчанию: {defaults.get(provider, 'н/д')}")

    return True

def check_user_id():
    """Validate admin user ID"""
    user_id = os.getenv('ADMIN_USER_ID')
    if not user_id:
        return False

    try:
        uid = int(user_id)
        if uid <= 0:
            print_status("Формат ADMIN_USER_ID", False,
                        "ID должен быть положительным числом")
            return False
        print_status("Формат ADMIN_USER_ID", True, f"ID = {uid}")
        return True
    except ValueError:
        print_status("Формат ADMIN_USER_ID", False,
                    "ID должен быть числом")
        return False

def check_schedule():
    """Check schedule configuration"""
    try:
        day1 = int(os.getenv('ANALYSIS_SCHEDULE_DAY_1', 0))
        time1 = os.getenv('ANALYSIS_SCHEDULE_TIME_1', '10:00')
        day2 = int(os.getenv('ANALYSIS_SCHEDULE_DAY_2', 3))
        time2 = os.getenv('ANALYSIS_SCHEDULE_TIME_2', '10:00')

        days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

        if not (0 <= day1 <= 6):
            print_status("Расписание", False, f"День 1 должен быть от 0 до 6, получен: {day1}")
            return False

        if not (0 <= day2 <= 6):
            print_status("Расписание", False, f"День 2 должен быть от 0 до 6, получен: {day2}")
            return False

        # Validate time format
        for t in [time1, time2]:
            parts = t.split(':')
            if len(parts) != 2:
                print_status("Расписание", False, f"Неверный формат времени: {t}")
                return False
            hour, minute = map(int, parts)
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                print_status("Расписание", False, f"Неверное время: {t}")
                return False

        print_status("Расписание", True,
                    f"{days[day1]} в {time1}, {days[day2]} в {time2}")
        return True
    except Exception as e:
        print_status("Расписание", False, str(e))
        return False

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print_status("Python версия", True,
                    f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_status("Python версия", False,
                    f"{version.major}.{version.minor}.{version.micro} (требуется 3.9+)")
        return False

def main():
    """Main check function"""
    print("=" * 60)
    print("🔍 ПРОВЕРКА КОНФИГУРАЦИИ БОТА")
    print("=" * 60)
    print()

    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("   → Скопируйте .env.example в .env и заполните его:")
        print("   → cp .env.example .env")
        return False

    print("✅ Файл .env найден")
    print()

    # Check Python version
    print("📋 Проверка окружения:")
    python_ok = check_python_version()
    print()

    # Check required variables
    print("📋 Проверка обязательных переменных:")
    token_ok = check_env_var('TELEGRAM_BOT_TOKEN')
    user_id_ok = check_env_var('ADMIN_USER_ID')
    print()

    # Validate formats
    print("📋 Проверка форматов:")
    token_format_ok = check_telegram_token() if token_ok else False
    user_format_ok = check_user_id() if user_id_ok else False
    print()

    # Check AI provider
    print("📋 Проверка AI провайдера:")
    ai_provider_ok = check_ai_provider()
    print()

    # Check optional variables
    print("📋 Проверка опциональных переменных:")
    check_env_var('DATABASE_URL', required=False)
    schedule_ok = check_schedule()
    check_env_var('ANALYSIS_DAYS_BACK', required=False)
    check_env_var('MIN_MESSAGES_FOR_ANALYSIS', required=False)
    print()

    # Summary
    print("=" * 60)
    all_ok = all([
        python_ok,
        token_ok, user_id_ok,
        token_format_ok, user_format_ok,
        ai_provider_ok,
        schedule_ok
    ])

    if all_ok:
        print("✅ ВСЁ ГОТОВО! Можно запускать бота:")
        print()
        print("   python main.py")
        print()
        print("   или")
        print()
        print("   ./run.sh")
        print("=" * 60)
        return True
    else:
        print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ")
        print()
        print("Пожалуйста, исправьте ошибки в файле .env")
        print("=" * 60)
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
