"""
Tests for Simulation API - app/api/simulation.py

Tests the pure functions and helpers in the simulation API module:
- optimize_interview_prompt()
- INTERVIEW_PROMPT_PREFIX constant
"""
import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

from app.api.simulation import optimize_interview_prompt, INTERVIEW_PROMPT_PREFIX


class TestOptimizeInterviewPrompt:
    """Tests for optimize_interview_prompt() function."""

    def test_returns_empty_string_when_input_empty(self):
        """Empty prompt returns empty string."""
        result = optimize_interview_prompt("")
        assert result == ""

    def test_returns_none_when_input_none(self):
        """None prompt returns None."""
        result = optimize_interview_prompt(None)
        assert result is None

    def test_adds_prefix_to_normal_prompt(self):
        """Normal prompt gets the interview prefix added."""
        prompt = "What do you think about this topic?"
        result = optimize_interview_prompt(prompt)
        assert result.startswith(INTERVIEW_PROMPT_PREFIX)
        assert "What do you think about this topic?" in result

    def test_does_not_duplicate_prefix(self):
        """Prompt already with prefix is not modified."""
        prompt = INTERVIEW_PROMPT_PREFIX + "Original question"
        result = optimize_interview_prompt(prompt)
        # Should be unchanged (no duplicate prefix)
        assert result == prompt
        # Count occurrences should be exactly 1
        assert result.count(INTERVIEW_PROMPT_PREFIX) == 1

    def test_prefix_constant_is_correct(self):
        """INTERVIEW_PROMPT_PREFIX has expected value for avoiding tool calls."""
        # The prefix should instruct agent to respond without tools
        assert "不调用任何工具" in INTERVIEW_PROMPT_PREFIX
        assert "直接用文本回复" in INTERVIEW_PROMPT_PREFIX

    def test_preserves_prompt_content_after_prefix(self):
        """The full original prompt content is preserved after prefix."""
        original = "What is your opinion on climate change?"
        result = optimize_interview_prompt(original)
        assert original in result

    def test_works_with_chinese_prompt(self):
        """Handles Chinese language prompts correctly."""
        prompt = "你觉得这个政策怎么样？"
        result = optimize_interview_prompt(prompt)
        assert result.startswith(INTERVIEW_PROMPT_PREFIX)
        assert "你觉得这个政策怎么样？" in result

    def test_works_with_long_prompt(self):
        """Handles long prompts without truncation."""
        long_prompt = "分析以下情况：" + "x" * 500
        result = optimize_interview_prompt(long_prompt)
        assert long_prompt in result
        assert len(result) > len(long_prompt)

    def test_works_with_special_characters(self):
        """Handles prompts with special characters."""
        prompt = 'User said: "What\'s up?" \n New lines work!'
        result = optimize_interview_prompt(prompt)
        assert prompt in result

    def test_whitespace_handling(self):
        """Preserves whitespace in prompt."""
        prompt = "Line1\nLine2\r\nLine3"
        result = optimize_interview_prompt(prompt)
        assert "Line1\nLine2" in result

    def test_concatenation_format(self):
        """Prefix and prompt are concatenated correctly."""
        prompt = "Test question"
        result = optimize_interview_prompt(prompt)
        # Should be prefix directly followed by the prompt (no extra separator)
        expected = INTERVIEW_PROMPT_PREFIX + prompt
        assert result == expected


class TestInterviewPromptPrefix:
    """Tests for the INTERVIEW_PROMPT_PREFIX constant itself."""

    def test_prefix_is_string(self):
        """INTERVIEW_PROMPT_PREFIX is a string."""
        assert isinstance(INTERVIEW_PROMPT_PREFIX, str)

    def test_prefix_is_not_empty(self):
        """INTERVIEW_PROMPT_PREFIX is not empty."""
        assert len(INTERVIEW_PROMPT_PREFIX) > 0

    def test_prefix_contains_instruction_to_not_use_tools(self):
        """Prefix contains instruction to avoid tool calls."""
        assert "不调用任何工具" in INTERVIEW_PROMPT_PREFIX

    def test_prefix_contains_instruction_to_use_text(self):
        """Prefix contains instruction to respond with text only."""
        assert "直接用文本回复" in INTERVIEW_PROMPT_PREFIX

    def test_prefix_mentions_persona(self):
        """Prefix references agent's persona and memories."""
        assert "人设" in INTERVIEW_PROMPT_PREFIX or "记忆" in INTERVIEW_PROMPT_PREFIX
