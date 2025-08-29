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

        # Try to get the repository's PR template
        pr_template = ""
        try:
            template_content = repo.get_contents(".github/pull_request_template.md")
            pr_template = template_content.decoded_content.decode("utf-8")
            print("✅ Found PR template in repository")
        except Exception as template_error:
            print(f"⚠️  No PR template found: {template_error}")
            # open local template
            with open("pull_request_template.md", "r") as file:
                pr_template = file.read()
            print("✅ Found PR template in local file")

        # Get PR Diff with file filtering
        diff = list(pr.get_files())  # Convert PaginatedList to regular list
        diff_text = ""
        total_changes = 0
        ignored_files = []

        # Configuration: Adjust these values to control file filtering
        # File size limits (in bytes) - can be overridden via environment variables
        MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "100")) * 1024  # Default: 100KB
        MAX_PATCH_SIZE = (
            int(os.getenv("MAX_PATCH_SIZE", "50")) * 1024
        )  # Default: 50KB patch content
        MAX_TOTAL_CHANGES = (
            int(os.getenv("MAX_TOTAL_CHANGES", "200")) * 1024
        )  # Default: 200KB total

        # File types to always ignore (usually large binary files)
        IGNORED_EXTENSIONS = {
            ".bin",
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".jar",
            ".war",
            ".ear",
            ".zip",
            ".tar",
            ".gz",
            ".rar",
            ".7z",
            ".iso",
            ".img",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".tiff",
            ".svg",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".db",
            ".sqlite",
            ".mdb",
            ".accdb",
            ".log",
            ".tmp",
            ".cache",
            ".lock",
        }

        for file in diff:
            file_size = file.changes or 0
            patch_size = len(file.patch or "") if file.patch else 0

            # Skip files with ignored extensions
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext in IGNORED_EXTENSIONS:
                ignored_files.append(f"{file.filename} (ignored extension: {file_ext})")
                continue

            # Skip very large files or patches
            if file_size > MAX_FILE_SIZE or patch_size > MAX_PATCH_SIZE:
                ignored_files.append(
                    f"{file.filename} (size: {file_size}, patch: {patch_size} bytes)"
                )
                continue

            # Check if adding this file would exceed total limit
            if total_changes + patch_size > MAX_TOTAL_CHANGES:
                ignored_files.append(f"{file.filename} (would exceed total limit)")
                continue

            # Add file info and patch
            diff_text += f"File: {file.filename}\n"
            diff_text += f"Status: {file.status}\n"
            diff_text += f"Changes: +{file.additions} -{file.deletions}\n"
            if file.patch:
                diff_text += f"Patch:\n{file.patch}\n"
            diff_text += "\n"

            total_changes += patch_size

        # Add summary of ignored files
        if ignored_files:
            diff_text += f"\n--- IGNORED LARGE FILES ---\n"
            diff_text += f"Total ignored: {len(ignored_files)}\n"
            diff_text += f"Files ignored due to size limits:\n"
            for ignored in ignored_files[:10]:  # Limit to first 10 ignored files
                diff_text += f"- {ignored}\n"
            if len(ignored_files) > 10:
                diff_text += f"... and {len(ignored_files) - 10} more files\n"

        print(f"Total changes included: {total_changes} bytes")
        print(f"Files ignored: {len(ignored_files)}")
        print(f"Files processed: {len(diff) - len(ignored_files)}")

        # Add summary at the beginning of diff_text
        summary = f"--- PR ANALYSIS SUMMARY ---\n"
        summary += f"Total files in PR: {len(diff)}\n"
        summary += f"Files included: {len(diff) - len(ignored_files)}\n"
        summary += f"Files ignored: {len(ignored_files)}\n"
        summary += f"Total changes: {total_changes} bytes\n\n"
        diff_text = summary + diff_text

        # Get Commit Messages
        commits = pr.get_commits()
        commit_messages = "\n".join([commit.commit.message for commit in commits])

        return pr, pr.title, diff_text, commit_messages, pr_template
    except Exception as e:
        print(f"Error fetching PR details: {e}")
        sys.exit(1)


def generate_description(api_key, title, diff, commits, template):
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

    **Repository PR Template:**
    {template}

    **Instructions:**
    Use the repository's PR template above to generate the description.
    Fill in the template sections based on the changes in the PR.
    If the template has checkboxes, check the appropriate ones based on the changes.
    Keep the same structure and formatting as the template.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are TechLead, you are a senior software engineer and you are a great PR "
                    "description writer Follow the structure of the PR template. "
                    "You are given a PR title, commit messages, a PR template and file diffs. "
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

    pr_instance, pr_title, pr_diff, pr_commits, pr_template = get_pr_details(
        GITHUB_TOKEN, GITHUB_REPOSITORY, PR_NUMBER
    )
    generated_text = generate_description(
        OPENAI_API_KEY, pr_title, pr_diff, pr_commits, pr_template
    )
    update_pr_description(pr_instance, generated_text)
