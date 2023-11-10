import os
from typing import Any, Optional

from dotenv import load_dotenv


class Config:
    # Explicit type annotations for each configuration parameter
    SYSTEM_TEXT: str
    SLACK_APP_TOKEN: str
    SLACK_BOT_TOKEN: str
    OPENAI_API_KEY: str
    OPENAI_TIMEOUT_SECONDS: int
    OPENAI_MODEL: str
    OPENAI_TEMPERATURE: float
    OPENAI_API_TYPE: Optional[str]
    OPENAI_API_BASE: str
    OPENAI_API_VERSION: Optional[str]
    OPENAI_DEPLOYMENT_ID: Optional[str]
    OPENAI_FUNCTION_CALL_MODULE_NAME: Optional[str]
    SLACK_APP_LOG_LEVEL: str
    TRANSLATE_MARKDOWN: bool
    REDACTION_ENABLED: bool
    USE_SLACK_LANGUAGE: bool
    REDACT_EMAIL_PATTERN: str
    REDACT_PHONE_PATTERN: str
    REDACT_CREDIT_CARD_PATTERN: str
    REDACT_SSN_PATTERN: str
    REDACT_USER_DEFINED_PATTERN: str

    _instance = None
    __initialized = False

    DEFAULT_CONFIG = {
        "SYSTEM_TEXT": (
            "You are a bot in a slack chat room. You might receive messages from multiple people. "
            "Format bold text *like this*, italic text _like this_ and strikethrough text ~like this~. "
            "Slack user IDs match the regex `<@U.*?>`. Your Slack user ID is <@{bot_user_id}>. "
            "Each message has the author's Slack user ID prepended, like the regex `^<@U.*?>: ` followed by the message text."
        ),
        "OPENAI_TIMEOUT_SECONDS": 30,
        "OPENAI_MODEL": "gpt-3.5-turbo",
        "OPENAI_TEMPERATURE": 1,
        "OPENAI_API_TYPE": None,
        "OPENAI_API_BASE": "https://api.openai.com/v1",
        "OPENAI_API_VERSION": None,
        "OPENAI_DEPLOYMENT_ID": None,
        "OPENAI_FUNCTION_CALL_MODULE_NAME": None,
        "SLACK_APP_LOG_LEVEL": "DEBUG",
        "TRANSLATE_MARKDOWN": False,
        "REDACTION_ENABLED": False,
        "USE_SLACK_LANGUAGE": False,
        "REDACT_EMAIL_PATTERN": r"\b[A-Za-z0-9.*%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "REDACT_PHONE_PATTERN": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "REDACT_CREDIT_CARD_PATTERN": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
        "REDACT_SSN_PATTERN": r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b",
        "REDACT_USER_DEFINED_PATTERN": r"(?!)",
    }

    @staticmethod
    def fetch_env(key: str, default_value: Any) -> Any:
        raw_value = os.environ.get(key)
        if raw_value is None:
            return default_value

        if isinstance(default_value, bool):
            return raw_value.lower() == "true"

        try:
            # Explicit type conversion based on the type of the default value
            return type(default_value)(raw_value)
        except ValueError:
            raise ValueError(
                f"Invalid format for environment variable {key}: {raw_value}"
            )

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            load_dotenv()
            for k, v in cls.DEFAULT_CONFIG.items():
                try:
                    setattr(cls, k, cls.fetch_env(k, v))
                except ValueError as e:
                    # Handle the case where an environment variable is set but cannot be converted to the required type
                    print(f"Error loading configuration for {k}: {e}")
                    # Optionally, raise an exception or handle it as per your application's needs
            cls.__initialized = True

        return cls._instance

    def __init__(self):
        pass

    @classmethod
    def reload_configuration(cls):
        for k, v in cls.DEFAULT_CONFIG.items():
            try:
                setattr(cls, k, cls.fetch_env(k, v))
            except ValueError as e:
                print(f"Error reloading configuration for {k}: {e}")
