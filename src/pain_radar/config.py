"""Configuration management using pydantic-settings."""

from __future__ import annotations

import json
from typing import List, Union

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="PAIN_RADAR_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Subreddits to mine
    subreddits: List[str] = Field(
        default_factory=lambda: [
            "IndieHackers",
            "SideProject",
            "MicroSaaS",
            "SaaS",
            "Startups",
            "Entrepreneur",
            "SmallBusiness",
        ],
        description="List of subreddits to track for pain signals",
    )

    @field_validator("subreddits", mode="before")
    @classmethod
    def parse_subreddits(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse subreddits from JSON string or list."""
        if isinstance(v, str):
            # Remove any newlines and extra whitespace for multiline JSON
            v = v.replace("\n", "").replace("  ", "")
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                # Try comma-separated
                return [s.strip() for s in v.split(",") if s.strip()]
        return v

    # Reddit fetching parameters
    listing: str = Field(
        default="hot",
        description="Reddit listing type: hot, new, top, rising",
    )
    posts_per_subreddit: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Number of posts to fetch per subreddit",
    )
    top_comments: int = Field(
        default=20,
        ge=0,
        le=100,
        description="Number of top comments to fetch per post",
    )

    # Concurrency control
    max_concurrency: int = Field(
        default=8,
        ge=1,
        le=50,
        description="Maximum concurrent requests",
    )

    # Storage
    db_path: str = Field(
        default="pain_radar.sqlite3",
        description="Path to SQLite database file",
    )

    # OpenAI configuration
    openai_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("OPENAI_API_KEY", "PAIN_RADAR_OPENAI_API_KEY"),
        description="OpenAI API key (accepts OPENAI_API_KEY or PAIN_RADAR_OPENAI_API_KEY)",
    )
    openai_model: str = Field(
        default="gpt-4o",
        description="OpenAI model to use for pain signal analysis",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR",
    )
    log_json: bool = Field(
        default=False,
        description="Output logs as JSON (for production)",
    )

    # User agent for scraping
    user_agent: str = Field(
        default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        description="User agent string for HTTP requests",
    )


def get_settings() -> Settings:
    """Load and return application settings."""
    return Settings()

settings = get_settings()
