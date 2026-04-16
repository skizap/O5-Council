from __future__ import annotations

from pathlib import Path

APP_NAME = "O5 Council"
APP_SLUG = "o5-council"
APP_TITLE = "O5 Council"
APP_VERSION = "0.1.0"
SETTINGS_FILE_NAME = "settings.json"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_REFERER = "https://github.com/skizap/O5-Council"
OPENROUTER_TITLE = "O5 Council"
DEFAULT_REQUEST_TIMEOUT_SECONDS = 120.0
DEFAULT_MAX_ROUNDS = 3
DEFAULT_CONSENSUS_TARGET = 3
DEFAULT_TASK_MODE = "Strategic plan"
DEFAULT_ROLE_SET = [
    "Chair Strategist",
    "Systems Analyst",
    "Skeptical Auditor",
    "Operations Planner",
    "Diplomatic Mediator",
]
DEFAULT_MODELS = [
    "openai/gpt-4.1-mini",
    "anthropic/claude-3.7-sonnet",
    "google/gemini-2.5-flash",
    "meta-llama/llama-4-maverick",
    "qwen/qwen-2.5-72b-instruct",
]
COMMON_OPENROUTER_MODELS = [
    "openai/gpt-4.1-mini",
    "openai/gpt-4.1",
    "anthropic/claude-3.7-sonnet",
    "anthropic/claude-3.5-sonnet",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "meta-llama/llama-4-maverick",
    "deepseek/deepseek-chat-v3-0324",
    "qwen/qwen-2.5-72b-instruct",
    "mistralai/mistral-large",
]


def get_user_data_dir() -> Path:
    data_home = Path.home() / ".local" / "share"
    user_data_dir = data_home / APP_SLUG
    user_data_dir.mkdir(parents=True, exist_ok=True)
    return user_data_dir


def get_settings_path() -> Path:
    return get_user_data_dir() / SETTINGS_FILE_NAME
