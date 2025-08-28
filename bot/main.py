import os
import sys

import openai
from github import Github


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
            engine="text-davinci-003", prompt=prompt, max_tokens=300, temperature=0.7
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

    generated_text = generate_description(OPENAI_API_KEY, pr_title, pr_diff, pr_commits)

    update_pr_description(pr_instance, generated_text)
