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
    "anthropic/claude-sonnet-4.6",
    "anthropic/claude-3.7-sonnet",
    "anthropic/claude-3.5-sonnet",
    "google/gemini-3.1-pro-preview",
    "google/gemini-2.5-pro",
    "google/gemini-2.5-flash",
    "deepseek/deepseek-v3.2",
    "deepseek/deepseek-chat-v3-0324",
    "minimax/minimax-m2.7",
    "z-ai/glm-5.1",
    "moonshotai/kimi-k2.5",
    "x-ai/grok-4.1-fast",
    "qwen/qwen3.6-plus",
    "qwen/qwen-2.5-72b-instruct",
    "meta-llama/llama-4-maverick",
    "mistralai/mistral-large",
]


def get_user_data_dir() -> Path:
    data_home = Path.home() / ".local" / "share"
    user_data_dir = data_home / APP_SLUG
    user_data_dir.mkdir(parents=True, exist_ok=True)
    return user_data_dir


def get_settings_path() -> Path:
    return get_user_data_dir() / SETTINGS_FILE_NAME
