#!/usr/bin/env python3
"""
Simple test script to verify the PR Description Bot functionality.
This script tests imports and basic function definitions.
"""

import os
import sys

# Add the bot directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "bot"))


def test_imports():
    """Test if all required modules can be imported."""
    try:
        from github import Github

        print("✅ PyGithub imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PyGithub: {e}")
        return False

    try:
        import openai

        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import OpenAI: {e}")
        return False

    try:
        from main import generate_description, get_pr_details, update_pr_description

        print("✅ Bot functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import bot functions: {e}")
        return False


def test_function_definitions():
    """Test if all required functions are defined."""
    from main import generate_description, get_pr_details, update_pr_description

    functions = [
        ("get_pr_details", get_pr_details),
        ("generate_description", generate_description),
        ("update_pr_description", update_pr_description),
    ]

    for name, func in functions:
        if callable(func):
            print(f"✅ {name} is callable")
        else:
            print(f"❌ {name} is not callable")
            return False

    return True


def main():
    """Run all tests."""
    print("🧪 Testing PR Description Bot...\n")

    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install dependencies:")
        print("pip install -r bot/requirements.txt")
        sys.exit(1)

    print()

    # Test function definitions
    if not test_function_definitions():
        print("\n❌ Function definition tests failed.")
        sys.exit(1)

    print("\n🎉 All tests passed! The bot is ready to use.")
    print("\nNext steps:")
    print("1. Set up GitHub repository secrets")
    print("2. Push code to trigger GitHub Actions")
    print("3. Create a PR to test the bot")


if __name__ == "__main__":
    main()
