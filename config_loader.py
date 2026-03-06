"""
Configuration loader for Gabija.

Loads configuration from either:
1. config.toml file (if it exists)
2. Environment variables
3. Combination of both (env vars override config.toml)

Usage:
    from config_loader import load_config
    
    config = load_config()
    claude_key = config.claude.api_key
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

# Use tomllib for Python 3.11+, otherwise fall back to tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError(
            "tomli is required for Python < 3.11. Install with: pip install tomli"
        )


@dataclass
class GoogleWorkspaceConfig:
    """Google Workspace API configuration."""
    service_account_file: Optional[str] = None
    delegated_user_email: Optional[str] = None
    scopes: list[str] = field(default_factory=lambda: [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/tasks"
    ])


@dataclass
class ClaudeConfig:
    """Claude API configuration."""
    api_key: Optional[str] = None
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096


@dataclass
class GitHubConfig:
    """GitHub API configuration."""
    token: Optional[str] = None
    organization: Optional[str] = None
    project_number: Optional[int] = None


@dataclass
class TrelloConfig:
    """Trello API configuration."""
    api_key: Optional[str] = None
    token: Optional[str] = None
    board_id: Optional[str] = None


@dataclass
class GeneralConfig:
    """General application configuration."""
    timezone: str = "America/Chicago"
    log_level: str = "INFO"


@dataclass
class Config:
    """Main configuration container."""
    google_workspace: GoogleWorkspaceConfig
    claude: ClaudeConfig
    github: GitHubConfig
    trello: TrelloConfig
    general: GeneralConfig


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration from file and/or environment variables.
    
    Args:
        config_path: Path to config.toml. Defaults to ./config.toml
        
    Returns:
        Config object with all settings
        
    Raises:
        FileNotFoundError: If no config.toml and required env vars are missing
        ValueError: If configuration is invalid
    """
    if config_path is None:
        config_path = Path(__file__).parent / "config.toml"
    
    # Try to load from TOML file
    config_data: Dict[str, Any] = {}
    if config_path.exists():
        with open(config_path, "rb") as f:
            config_data = tomllib.load(f)
    
    # Load or override with environment variables
    google_data = config_data.get("google_workspace", {})
    google_config = GoogleWorkspaceConfig(
        service_account_file=os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", 
                                        google_data.get("service_account_file")),
        delegated_user_email=os.getenv("GOOGLE_DELEGATED_USER_EMAIL",
                                        google_data.get("delegated_user_email")),
        scopes=google_data.get("scopes", [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/tasks"
        ])
    )
    
    claude_data = config_data.get("claude", {})
    claude_config = ClaudeConfig(
        api_key=os.getenv("CLAUDE_API_KEY", claude_data.get("api_key")),
        model=os.getenv("CLAUDE_MODEL", claude_data.get("model", "claude-3-5-sonnet-20241022")),
        max_tokens=int(os.getenv("CLAUDE_MAX_TOKENS", claude_data.get("max_tokens", 4096)))
    )
    
    github_data = config_data.get("github", {})
    github_config = GitHubConfig(
        token=os.getenv("GITHUB_TOKEN", github_data.get("token")),
        organization=os.getenv("GITHUB_ORG", github_data.get("organization")),
        project_number=int(os.getenv("GITHUB_PROJECT_NUMBER", 
                                      github_data.get("project_number", 0) or 0)) or None
    )
    
    trello_data = config_data.get("trello", {})
    trello_config = TrelloConfig(
        api_key=os.getenv("TRELLO_API_KEY", trello_data.get("api_key")),
        token=os.getenv("TRELLO_TOKEN", trello_data.get("token")),
        board_id=os.getenv("TRELLO_BOARD_ID", trello_data.get("board_id"))
    )
    
    general_data = config_data.get("general", {})
    general_config = GeneralConfig(
        timezone=os.getenv("TIMEZONE", general_data.get("timezone", "America/Chicago")),
        log_level=os.getenv("LOG_LEVEL", general_data.get("log_level", "INFO"))
    )
    
    return Config(
        google_workspace=google_config,
        claude=claude_config,
        github=github_config,
        trello=trello_config,
        general=general_config
    )


def validate_config(config: Config, require_all: bool = False) -> list[str]:
    """
    Validate configuration and return list of missing required fields.
    
    Args:
        config: Configuration to validate
        require_all: If True, all services must be configured
        
    Returns:
        List of missing configuration items (empty if valid)
    """
    missing = []
    
    # Only validate what's actually needed - services can be optional
    if require_all:
        if not config.claude.api_key:
            missing.append("Claude API key")
        if not config.github.token:
            missing.append("GitHub token")
        if not config.google_workspace.service_account_file:
            missing.append("Google Workspace service account file")
        if not config.trello.api_key or not config.trello.token:
            missing.append("Trello API credentials")
    
    return missing


if __name__ == "__main__":
    """Quick test of configuration loading."""
    try:
        config = load_config()
        missing = validate_config(config, require_all=True)
        
        if missing:
            print("⚠️  Missing configuration items:")
            for item in missing:
                print(f"   - {item}")
            print("\nCreate config.toml or set environment variables.")
            print("See config.example.toml or .env.example for reference.")
        else:
            print("✓ Configuration loaded successfully")
            print(f"  Claude model: {config.claude.model}")
            print(f"  Timezone: {config.general.timezone}")
            print(f"  Log level: {config.general.log_level}")
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
