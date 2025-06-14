"""
LLM Integration Module

This module provides AI-powered analysis capabilities using DeepSeek API
for enhanced stock analysis, news interpretation, and growth catalyst identification.
"""

from .deepseek_analyzer import DeepSeekAnalyzer
from .llm_scorer import LLMScorer

__all__ = ["DeepSeekAnalyzer", "LLMScorer"]
