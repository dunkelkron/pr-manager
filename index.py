import os
from github import Github
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Get environment variables
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_NAME = os.environ.get('REPO_NAME')
MENTION_USER = os.environ.get('MENTION_USER')

def handle_pull_request(pull_request):
    print("Handling pull request...")
    files_added = []
    files_modified = []
    files_removed = []
    
    # Check all files in the pull request
    for file in pull_request.get_files():
        print(f"Processing file: {file.filename}")
        # Check file status
        if file.status == 'added':
            files_added.append(file.filename)
        elif file.status == 'modified':
            files_modified.append(file.filename)
        elif file.status == 'removed':
            files_removed.append(file.filename)

    # Handle different scenarios
    if len(files_added) > 1:
        print("Multiple files added. Please add files one at a time and create separate pull requests.")
        pull_request.create_issue_comment("Multiple files added. Please add files one at a time and create separate pull requests.")
        pull_request.edit(state='closed')
    elif len(files_modified) > 1:
        print("Multiple files modified. Please modify files one at a time and create separate pull requests.")
        pull_request.create_issue_comment("Multiple files modified. Please modify files one at a time and create separate pull requests.")
        pull_request.edit(state='closed')
    elif len(files_removed) > 0:
        print("File(s) deleted. Pull request closed.")
        # Close the pull request
        pull_request.edit(state='closed')
        # Create a new issue to inform the user about the deletion
        deletion_message = f"File(s) deleted in pull request #{pull_request.number}. Please review."
        base_repo = pull_request.base.repo
        base_repo.create_issue(title="File Deletion", body=deletion_message, assignee=MENTION_USER)
    else:
        # Proceed with normal handling
        original_author = pull_request.user.login
        for filename in files_added + files_modified:
            print(f"Modified or added file '{filename}' detected. Edited by {original_author}.")
            try:
                # Check if the file was modified by the original author
                if filename in files_added or (filename in files_modified and original_author == pull_request.head.user.login):
                    print("Original author modifying. Pull request accepted.")
                    pull_request.create_issue_comment("Original author modifying. Pull request accepted.")
                    pull_request.merge()
                else:
                    print("Not original author modifying. Closing pull request.")
                    pull_request.create_issue_comment("Not original author modifying. Closing pull request.")
                    pull_request.edit(state='closed')
                    break
            except Exception as e:
                print(f"Error handling pull request: {e}")

def check_for_pull_requests():
    print("Checking for new pull requests...")
    # Authenticate with GitHub using the bot token
    github = Github(GITHUB_TOKEN)

    # Get the repository
    repo = github.get_repo(REPO_NAME)

    # Check for new pull requests
    for pr in repo.get_pulls(state='open'):
        # Newly opened pull request, handle it
        handle_pull_request(pr)

def main():
    print("Bot script is running...")
    while True:
        # Check for new pull requests
        check_for_pull_requests()
        
        # Wait for 60 seconds before checking again
        time.sleep(60)

if __name__ == "__main__":
    main()
