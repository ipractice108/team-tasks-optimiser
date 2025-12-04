from .ai_analyzer import AIAnalyzer

# Optional import - only if anthropic is installed
try:
    from .claude_analyzer import ClaudeAnalyzer
    __all__ = ['AIAnalyzer', 'ClaudeAnalyzer']
except ImportError:
    __all__ = ['AIAnalyzer']
