import os
from typing import List, Dict
from datetime import datetime
import anthropic
from database.models import Message


class ClaudeAnalyzer:
    """AI Analyzer using Claude API"""

    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv('ANTHROPIC_API_KEY')

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def analyze_messages(self, messages: List[Message], topics: List[str] = None) -> str:
        """
        Analyze messages and generate insights and optimization recommendations

        Args:
            messages: List of Message objects
            topics: List of topic names found in the chat

        Returns:
            Analysis report text
        """
        if not messages:
            return "Недостаточно сообщений для анализа."

        # Prepare messages for analysis
        messages_text = self._format_messages(messages, topics)

        # Create analysis prompt
        prompt = self._create_analysis_prompt(messages_text, topics, len(messages))

        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            return f"Ошибка при анализе: {str(e)}"

    def _format_messages(self, messages: List[Message], topics: List[str] = None) -> str:
        """Format messages for analysis"""
        formatted = []

        # Group by topic if topics exist
        if topics:
            for topic in topics:
                topic_messages = [m for m in messages if m.topic_name == topic]
                if topic_messages:
                    formatted.append(f"\n{'='*60}")
                    formatted.append(f"ТОПИК: {topic}")
                    formatted.append(f"{'='*60}\n")

                    for msg in topic_messages:
                        user_name = msg.user.first_name or msg.user.username or "Пользователь"
                        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M")
                        formatted.append(f"[{timestamp}] {user_name}: {msg.text}")

            # Messages without topic
            no_topic_messages = [m for m in messages if not m.topic_name]
            if no_topic_messages:
                formatted.append(f"\n{'='*60}")
                formatted.append("ОБЩИЕ СООБЩЕНИЯ (без топика)")
                formatted.append(f"{'='*60}\n")

                for msg in no_topic_messages:
                    user_name = msg.user.first_name or msg.user.username or "Пользователь"
                    timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M")
                    formatted.append(f"[{timestamp}] {user_name}: {msg.text}")
        else:
            # No topics - just list all messages
            for msg in messages:
                user_name = msg.user.first_name or msg.user.username or "Пользователь"
                timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M")
                formatted.append(f"[{timestamp}] {user_name}: {msg.text}")

        return "\n".join(formatted)

    def _create_analysis_prompt(self, messages_text: str, topics: List[str],
                               message_count: int) -> str:
        """Create analysis prompt for Claude"""

        topics_info = ""
        if topics:
            topics_info = f"\n\nОбнаруженные топики в чате: {', '.join(topics)}"

        prompt = f"""Ты - AI-аналитик, специализирующийся на оптимизации рабочих процессов команд.

Проанализируй следующие {message_count} сообщений из рабочего чата команды.{topics_info}

СООБЩЕНИЯ ДЛЯ АНАЛИЗА:
{messages_text}

Твоя задача - провести глубокий анализ и предоставить конкретные, действенные рекомендации по улучшению процессов.

Структура анализа:

1. ОБЩАЯ КАРТИНА
   - Краткий обзор активности команды
   - Основные обсуждаемые темы
   - Общий тон и настроение команды

2. АНАЛИЗ ПО НАПРАВЛЕНИЯМ{topics_info and ' (если есть топики, проанализируй каждый отдельно)' or ''}
   - Что обсуждается в каждом направлении
   - Какие решения принимаются
   - Какие проблемы возникают

3. ВЫЯВЛЕННЫЕ ПРОБЛЕМЫ
   - Узкие места в процессах
   - Повторяющиеся вопросы (признак недостаточной документации)
   - Задержки в коммуникации
   - Дублирование работы
   - Неэффективные процессы

4. КОНКРЕТНЫЕ РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ
   Для каждой рекомендации укажи:
   - ЧТО нужно изменить
   - ЗАЧЕМ это нужно (какую проблему решает)
   - КАК это внедрить (конкретные шаги)
   - ПРИОРИТЕТ (высокий/средний/низкий)

5. ЧТО НЕ СТОИТ ДЕЛАТЬ
   - Практики, которые следует прекратить
   - Неэффективные подходы, которые были замечены
   - Что отнимает время без пользы

6. ПОЗИТИВНЫЕ МОМЕНТЫ
   - Что команда делает хорошо
   - Какие практики стоит сохранить и развивать

Пиши на русском языке, конкретно и по делу. Избегай общих фраз - давай именно действенные рекомендации, основанные на реальных данных из чата.
"""

        return prompt

    def generate_summary_report(self, full_analysis: str, topics: List[str] = None) -> str:
        """Generate a shorter summary version of the analysis"""
        try:
            prompt = f"""Создай краткую выжимку (не более 500 слов) из следующего подробного анализа рабочего чата:

{full_analysis}

Выжимка должна содержать:
1. Главные проблемы (топ-3)
2. Самые важные рекомендации (топ-3)
3. Что прекратить делать (топ-2)

Пиши кратко, конкретно, по пунктам."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            return full_analysis  # Return full analysis if summary fails
