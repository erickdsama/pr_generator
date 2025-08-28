# PR Description Bot

An automated Python bot that analyzes pull request changes and generates descriptive PR descriptions using OpenAI's API. The bot is containerized with Docker and automated through GitHub Actions.

## Features

- 🤖 **Automated PR Analysis**: Analyzes diffs and commit messages automatically
- ✨ **AI-Powered Descriptions**: Uses OpenAI to generate meaningful PR descriptions
- 🔄 **Real-time Updates**: Triggers on PR creation and updates
- 🐳 **Dockerized**: Consistent execution environment
- 🚀 **CI/CD Pipeline**: Automated Docker image building and publishing

## Project Structure

```
pr-description-bot/
├── .github/
│   └── workflows/
│       ├── pr_description_generator.yml  # Action to generate PR descriptions
│       └── docker_publish.yml            # Action to build and publish Docker image
├── bot/
│   ├── __init__.py
│   ├── main.py                         # Main script logic
│   └── requirements.txt                # Python dependencies
├── Dockerfile
└── README.md
```

## Prerequisites

- Python 3.10+
- GitHub repository with Actions enabled
- OpenAI API key
- Docker Hub account (for containerization)

## Setup Instructions

### 1. Repository Secrets

Add the following secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

- `OPENAI_API_KEY`: Your OpenAI API key
- `DOCKERHUB_TOKEN`: Your Docker Hub access token (not password)

### 2. Local Development

#### Option A: Using Docker (Recommended)
1. Run the pre-built Docker image:
```bash
docker run --rm \
  -e GITHUB_TOKEN="your_github_token" \
  -e OPENAI_API_KEY="your_openai_api_key" \
  -e GITHUB_REPOSITORY="owner/repo-name" \
  -e PR_NUMBER="123" \
  erickdsama/pr-description-bot:latest
```

#### Option B: Local Python Setup
1. Clone the repository:
```bash
git clone <your-repo-url>
cd pr-description-bot
```

2. Install dependencies:
```bash
cd bot
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export GITHUB_TOKEN="your_github_token"
export OPENAI_API_KEY="your_openai_api_key"
export GITHUB_REPOSITORY="owner/repo-name"
export PR_NUMBER="123"
```

4. Run the bot:
```bash
python main.py
```

### 3. Docker Usage

1. Build the image:
```bash
docker build -t pr-description-bot .
```

2. Run the container:
```bash
docker run --rm \
  -e GITHUB_TOKEN="your_token" \
  -e OPENAI_API_KEY="your_key" \
  -e GITHUB_REPOSITORY="owner/repo" \
  -e PR_NUMBER="123" \
  erickdsama/pr-description-bot:latest
```

## How It Works

### 1. PR Analysis
When a pull request is opened or updated, the GitHub Action:
- Fetches the PR details using the GitHub API
- Extracts file diffs and commit messages
- Prepares the data for AI analysis

### 2. Description Generation
The bot uses OpenAI's API to:
- Analyze the changes and commit messages
- Generate a concise, meaningful description
- Include motivation and summary of changes

### 3. PR Update
The generated description is automatically:
- Posted to the PR description field
- Available for review and modification

## GitHub Actions Workflows

### PR Description Generator
- **Trigger**: PR opened or synchronized
- **Action**: Runs the bot to generate descriptions
- **Output**: Updates PR description automatically

### Docker Publish
- **Trigger**: Push to main branch
- **Action**: Builds and publishes Docker image
- **Output**: Latest and SHA-tagged images on Docker Hub

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GITHUB_TOKEN` | GitHub API token | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `GITHUB_REPOSITORY` | Repository name (owner/repo) | Yes | - |
| `PR_NUMBER` | Pull request number | Yes | - |
| `MAX_FILE_SIZE` | Maximum file size in KB | No | 100 |
| `MAX_PATCH_SIZE` | Maximum patch content in KB | No | 50 |
| `MAX_TOTAL_CHANGES` | Maximum total changes in KB | No | 200 |

### OpenAI Configuration

The bot uses the following OpenAI parameters:
- **Engine**: `gpt-5-mini`
- **Max Tokens**: 300
- **Temperature**: 0.7

### File Filtering Configuration

The bot automatically filters out large files to optimize API usage and context:

- **MAX_FILE_SIZE**: Maximum file size in KB (default: 100KB)
- **MAX_PATCH_SIZE**: Maximum patch content in KB (default: 50KB)
- **MAX_TOTAL_CHANGES**: Maximum total changes in KB (default: 200KB)

**Automatically Ignored File Types:**
- Binary files: `.exe`, `.dll`, `.so`, `.jar`, `.zip`, `.tar`
- Media files: `.png`, `.jpg`, `.mp3`, `.mp4`, `.pdf`
- Database files: `.db`, `.sqlite`, `.log`
- Temporary files: `.tmp`, `.cache`, `.lock`

You can override these limits by setting environment variables in your GitHub Actions workflow.

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**: Ensure all required secrets are set in GitHub
2. **OpenAI API Errors**: Check your API key and billing status
3. **GitHub Token Permissions**: Ensure the token has repo access
4. **Docker Build Failures**: Verify Dockerfile syntax and dependencies

### Debug Mode

To run with verbose logging, modify the main script to include debug prints or use Python's logging module.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues and questions:
- Check the troubleshooting section
- Review GitHub Actions logs
- Open an issue in the repository

---

**Note**: This bot requires appropriate API access and may incur costs based on OpenAI usage. Monitor your API usage and set appropriate limits.
