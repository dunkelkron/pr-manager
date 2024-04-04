import os
from github import Github
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_NAME = os.environ.get('REPO_NAME')
MENTION_USER = os.environ.get('MENTION_USER')

def handle_pull_request(pull_request):
    for file in pull_request.get_files():
        # Check file status
        if file.status == 'added':
            # New file, accept pull request
            pull_request.create_issue_comment("New file added. Pull request accepted.")
            pull_request.merge()
            return
        elif file.status == 'modified':
            # Modified file, check original author
            commits = file.get_commits()
            original_author = commits[0].author.login if commits else None
            if original_author == pull_request.user.login:
                # Original author, accept pull request
                pull_request.create_issue_comment("File edited by original author. Pull request accepted.")
                pull_request.merge()
                return
            else:
                # Not original author, request more info
                pull_request.create_issue_comment("File edited by different user. More info needed.")
                return
        elif file.status == 'removed':
            # Deleted file, put on hold and mention user
            pull_request.create_issue_comment(f"File deleted. Pull request put on hold. @{MENTION_USER} please review.")
            return

def main():
    # Authenticate with GitHub using the bot token
    github = Github(GITHUB_TOKEN)

    # Get the repository
    repo = github.get_repo(REPO_NAME)

    # Listen for pull request events
    for pr in repo.get_pulls(state='open'):
        # Check if the pull request is newly opened
        if pr.created_at == pr.updated_at:
            # Newly opened pull request, handle it
            handle_pull_request(pr)

if __name__ == "__main__":
    main()
