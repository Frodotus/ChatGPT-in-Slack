import re

from app.config import Config


def redact_string(input_string: str) -> str:
    """
    Redact sensitive information from a string (inspired by @quangnhut123)

    Args:
        - input_string (str): the string to redact

    Returns:
        - str: the redacted string
    """
    output_string = input_string
    if Config.REDACTION_ENABLED:
        output_string = re.sub(Config.REDACT_EMAIL_PATTERN, "[EMAIL]", output_string)
        output_string = re.sub(
            Config.REDACT_CREDIT_CARD_PATTERN, "[CREDIT CARD]", output_string
        )
        output_string = re.sub(Config.REDACT_PHONE_PATTERN, "[PHONE]", output_string)
        output_string = re.sub(Config.REDACT_SSN_PATTERN, "[SSN]", output_string)
        output_string = re.sub(
            Config.REDACT_USER_DEFINED_PATTERN, "[REDACTED]", output_string
        )

    return output_string
