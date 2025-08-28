import asyncio
import os
import sys

from github import Github
from openai import OpenAI

template_md_pr = """
# Description


## Type of change

- [ ] Bug fix (change which fixes an issue)
- [ ] New feature (change which adds functionality)
- [ ] Breaking change (would cause existing functionality to not work as expected)

# How Has This Been Tested?

Please describe the tests that you ran to verify your changes. Provide screenshots or logs.

- [ ] Test A
- [ ] Test B

## Checklist

- [ ] I have updated documentation if needed
- [ ] My code follows the style guidelines
- [ ] I have added necessary code tests

"""


def get_pr_details(repo_token, repo_name, pr_number):
    """Fetches the title, diff, and commit messages for a given PR."""
    try:
        g = Github(login_or_token=repo_token)
        print("g", g)
        print("repo_name", repo_name)
        repo = g.get_repo(repo_name)
        print("repo", repo)
        pr = repo.get_pull(pr_number)
        print("pr", pr)
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
    client = OpenAI(
        # This is the default and can be omitted
        api_key=api_key,
    )
    prompt = f"""
    Based on the following pull request details, generate a concise and clear PR description.
    The description should include a summary of changes and the motivation behind them.

    **PR Title:** {title}

    **Commit Messages:**
    {commits}

    **File Diffs:**
    {diff}

    **Generated PR Description:**
    ALWAYS USE THIS TEMPLATE TO GENERATE THE PR DESCRIPTION:
    {template_md_pr}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are TechLead, you are a senior software engineer and you are a great PR"
                    "description writer. You are given a PR title, commit messages, and file diffs. "
                    "You are to generate a PR description that is concise and clear. alwatys use markdown format.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
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
