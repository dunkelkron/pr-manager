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

def get_original_author(file_path, repo):
    try:
        # Retrieve commit history for the file
        commits = repo.get_commits(path=file_path)
        alpha = [commit.commit.author.name for commit in commits]
        if not alpha:
            print(f"No commits found for file '{file_path}'.")
            return None
        else:
            original_author = alpha[-1]
            return original_author
    except Exception as e:
        print(f"Error retrieving commit history: {e}")
        print("Authors:", alpha)
        return None


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
    if len(files_added) > 0:
        handle_added_files(pull_request, files_added)
    if len(files_modified) > 0:
        handle_modified_files(pull_request, files_modified)
    if len(files_removed) > 0:
        handle_removed_files(pull_request, files_removed)
    
    # Update the state of the pull request after processing
    pull_request.edit(state='closed')

def handle_added_files(pull_request, files_added):
    print("Handling added files...")
    if len(files_added) > 1:
        print("Multiple files added. Please add files one at a time and create separate pull requests.")
        pull_request.create_issue_comment("Multiple files added. Please add files one at a time and create separate pull requests.")
        pull_request.edit(state='closed')
    else:
        # Handle single added file
        for filename in files_added:
            print(f"Added file '{filename}' detected.")
            # Accept the pull request as it's a new file addition
            print("New file(s) added. Pull request accepted.")
            pull_request.create_issue_comment("New file(s) added. Pull request accepted.")
            pull_request.merge()



def handle_modified_files(pull_request, files_modified):
    print("Handling modified files...")
    print(f"Number of modified files: {len(files_modified)}")
    if len(files_modified) != 1:
        print("Invalid number of modified files. Expected only one file to be modified.")
        pull_request.create_issue_comment("Invalid number of modified files. Please modify only one file at a time. This pull request is being closed.")
        pull_request.edit(state='closed')
    else:
        modified_file = files_modified[0]
        print(f"Modified file '{modified_file}' detected.")
        original_author = get_original_author(modified_file, pull_request.base.repo)
        modifier = pull_request.user.login
        print(f"Original author: {original_author}")
        print(f"Modifier (user who opened pull request): {modifier}")
        if modifier == original_author:
            print(f"Modifier '{modifier}' is the original author. Pull request accepted.")
            pull_request.create_issue_comment(f"Modifier '{modifier}' is the original author. Pull request accepted.")
            pull_request.merge()
        else:
            print(f"Modifier '{modifier}' is not the original author '{original_author}'. Closing pull request.")
            pull_request.create_issue_comment(f"Modifier '{modifier}' is not the original author '{original_author}'. Closing pull request.")
            pull_request.edit(state='closed')


def handle_removed_files(pull_request, files_removed):
    print("Handling removed files...")
    print("File(s) deleted. Pull request closed.")
    # Close the pull request
    pull_request.edit(state='closed')
    # Create a new issue to inform the user about the deletion
    deletion_message = f"File(s) deleted in pull request #{pull_request.number}. Please review."
    base_repo = pull_request.base.repo
    base_repo.create_issue(title="File Deletion", body=deletion_message, assignee=MENTION_USER)

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
