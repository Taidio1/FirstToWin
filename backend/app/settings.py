from __future__ import annotations

import os

import dotenv

dotenv.load_dotenv()


class VariableNotFoundError(Exception):
    def __init__(self, variable_name: str):
        super().__init__(f"Environment variable '{variable_name}' not found.")


def parse_bool(name: str) -> bool:
    if (env_value := os.getenv(name)) is None:
        raise VariableNotFoundError(name)

    return env_value.lower() in ("true", "1", "t")


def parse_int(name: str) -> int:
    if (env_value := os.getenv(name)) is None:
        raise VariableNotFoundError(name)

    return int(env_value)


def parse_str(name: str) -> str:
    if (env_value := os.getenv(name)) is None:
        raise VariableNotFoundError(name)

    return env_value


def parse_optional_bool(name: str, default: bool = False) -> bool:
    if (env_value := os.getenv(name)) is None:
        return default

    return env_value.lower() in ("true", "1", "t", "yes", "y")


def parse_optional_str(name: str) -> str | None:
    value = os.getenv(name)
    return value if value else None


# Server settings
SERVER_HOST = parse_str("SERVER_HOST")
SERVER_PORT = parse_int("SERVER_PORT")

# Database settings
DB_URL = parse_str("DB_URL")


# Development settings
DEBUG = parse_bool("DEBUG")

# Supabase Auth settings
SUPABASE_URL = parse_optional_str("SUPABASE_URL")
SUPABASE_ANON_KEY = parse_optional_str("SUPABASE_ANON_KEY")
SUPABASE_AUTH_ENABLED = parse_optional_bool("SUPABASE_AUTH_ENABLED", default=True)
