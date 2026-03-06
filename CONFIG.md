# Configuration Setup

This project uses a secure configuration system that keeps sensitive credentials out of version control.


## Required Credentials

**Using TOML file:**
   ```bash
   cp config.example.toml config.toml
   # Edit config.toml with your actual credentials
   ```

### Claude API
- Get your API key from: https://console.anthropic.com/
- Set as `CLAUDE_API_KEY` or in `config.json`

### GitHub
- Create a Personal Access Token: Settings → Developer Settings → Personal Access Tokens
- Required scopes: `repo`, `project`, `read:org`
- Set as `GITHUB_TOKEN` or in `config.json`

### Google Workspace
- Create a service account in Google Cloud Console
- Enable Calendar and Tasks APIs
- Download the service account JSON file
- Set path as `GOOGLE_SERVICE_ACCOUNT_FILE`
- Set delegated user email as `GOOGLE_DELEGATED_USER_EMAIL`

### Trello
- Get API key: https://trello.com/app-key
- Generate token using the link on that page
- Set as `TRELLO_API_KEY` and `TRELLO_TOKEN`

## Usage in Code

```python
from config_loader import load_config

config = load_config()

# Access credentials
claude_key = config.claude.api_key
github_token = config.github.token
```