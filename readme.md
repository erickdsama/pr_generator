# PR Description Bot: From Python Script to CI/CD Deployment

This document outlines the process for creating, containerizing, and automating a Python bot designed to analyze project changes and generate descriptive pull request (PR) descriptions. The automation is handled by GitHub Actions, and the bot is packaged with Docker for portability and deployment.

---

## 1. Project Goal & Overview

The primary goal is to automate the creation of meaningful PR descriptions. This bot will:
1.  **Analyze Changes**: Inspect the diffs and commit messages within a pull request.
2.  **Generate Description**: Use a service like OpenAI to generate a summary of the changes.
3.  **Update the PR**: Automatically populate the PR's description field with the generated content.
4.  **Automate**: Trigger this process automatically whenever a new PR is opened or updated.
5.  **Containerize**: Package the bot into a Docker image for consistent execution.
6.  **CI/CD**: Create a continuous integration and deployment pipeline to build and publish the Docker image to a registry like Docker Hub.

---

## 2. Project Structure

A clean and logical project structure is essential. Here is a recommended layout:

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

---

## 3. Part I: The Python Bot

This script is the core of the operation. It interacts with the GitHub API to fetch PR data and then uses an AI service to generate a description.

### `bot/requirements.txt`

List the necessary Python libraries.

```
PyGithub
openai
python-dotenv
```

### `bot/main.py`

This script contains the logic for fetching PR details, generating the description, and updating the PR.

```python
import os
import sys
from github import Github
import openai

def get_pr_details(repo_token, repo_name, pr_number):
    """Fetches the title, diff, and commit messages for a given PR."""
    try:
        g = Github(repo_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)

        # Get PR Diff
        diff = pr.get_files()
        diff_text = ""
        for file in diff:
            diff_text += f"File: {file.filename}\nPatch:\n{file.patch}\n\n"

        # Get Commit Messages
        commits = pr.get_commits()
        commit_messages = "\n".join([commit.commit.message for commit in commits])

        return pr, pr.title, diff_text, commit_messages
    except Exception as e:
        print(f"Error fetching PR details: {e}")
        sys.exit(1)

def generate_description(api_key, title, diff, commits):
    """Generates a PR description using OpenAI."""
    openai.api_key = api_key
    prompt = f"""
    Based on the following pull request details, generate a concise and clear PR description.
    The description should include a summary of changes and the motivation behind them.

    **PR Title:** {title}

    **Commit Messages:**
    {commits}

    **File Diffs:**
    {diff}

    **Generated PR Description:**
    """
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating description with OpenAI: {e}")
        sys.exit(1)

def update_pr_description(pr, new_description):
    """Updates the PR description on GitHub."""
    try:
        pr.edit(body=new_description)
        print("Successfully updated PR description.")
    except Exception as e:
        print(f"Error updating PR description: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # These will be provided by the GitHub Actions environment
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
    PR_NUMBER = int(os.getenv("PR_NUMBER"))
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if not all([GITHUB_TOKEN, GITHUB_REPOSITORY, PR_NUMBER, OPENAI_API_KEY]):
        print("One or more environment variables are missing.")
        sys.exit(1)

    pr_instance, pr_title, pr_diff, pr_commits = get_pr_details(
        GITHUB_TOKEN, GITHUB_REPOSITORY, PR_NUMBER
    )

    generated_text = generate_description(
        OPENAI_API_KEY, pr_title, pr_diff, pr_commits
    )

    update_pr_description(pr_instance, generated_text)
```

---

## 4. Part II: GitHub Actions for PR Automation

This workflow runs the Python script whenever a PR is created or updated.

### `.github/workflows/pr_description_generator.yml`

```yaml
name: Generate PR Description

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r bot/requirements.txt

      - name: Run PR Description Bot
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: python bot/main.py
```
**Note**: You must add `OPENAI_API_KEY` as a repository secret in your GitHub settings (`Settings > Secrets and variables > Actions`). `GITHUB_TOKEN` is automatically available.

---

## 5. Part III: Dockerizing the Bot

Containerizing the application ensures it runs in a consistent environment, which is crucial for CI/CD.

### `Dockerfile`

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY bot/ .

# Define the command to run the application
# This can be used for manual runs or other orchestrators
ENTRYPOINT ["python", "main.py"]
```

---

## 6. Part IV: CI/CD Pipeline for Docker

This workflow automates building the Docker image and pushing it to Docker Hub whenever changes are merged into the `main` branch.

### `.github/workflows/docker_publish.yml`

```yaml
name: CI - Build and Push Docker Image

on:
  push:
    branches:
      - main

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/pr-description-bot:latest,${{ secrets.DOCKERHUB_USERNAME }}/pr-description-bot:${{ github.sha }}
```
**Note**: You must add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` (an access token, not your password) as repository secrets.
