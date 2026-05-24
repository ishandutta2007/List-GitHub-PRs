import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Default list of (owner, repo) pairs
DEFAULT_REPOS = [
    ('ishandutta2007', 'Top-AI-repos')
]
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")



import requests

def get_PRs(owner, repo, token=None):
    # Use global ADMIN_TOKEN if token is not provided
    if token is None:
        token = ADMIN_TOKEN

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    
    # 'state=all' gets open, closed, and merged PRs
    # 'per_page=100' is the maximum allowed by GitHub
    params = {"state": "all", "per_page": 100, "page": 1}
    headers = {"Accept": "application/vnd.github+json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"

    all_usernames = []

    while True:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise Exception(f"GitHub API error: {response.status_code} {response.text}")

        pulls = response.json()
        if not pulls:
            break
            
        # Extract usernames from the pull request objects
        page_usernames = [pr['user']['login'] for pr in pulls]
        all_usernames.extend(page_usernames)
        
        print(f"Fetched page {params['page']}...")
        params["page"] += 1
        
    return all_usernames


def save_to_file(usernames, filename="PRs.txt", append=False):
    """Saves a list of usernames to a file, one per line."""
    if not usernames:
        return False
    
    mode = "a" if append else "w"
    with open(filename, mode) as f:
        for username in usernames:
            f.write(username + "\n")
    return True

if __name__ == "__main__":
    import sys
    append_flag = "--append" in sys.argv

    # Clear file first if NOT in append mode
    if not append_flag:
        open("PRs.txt", "w").close()

    total_found = 0
    for owner, repo in DEFAULT_REPOS:
        print(f"Fetching PRs for {owner}/{repo}...")
        usernames = get_PRs(owner, repo)
        print(f"Total PRs found: {len(usernames)}")
        if usernames:
            save_to_file(usernames, append=True)
            print(f"  Added {len(usernames)} usernames.")
            total_found += len(usernames)
        else:
            print(f"  No PRs found for {owner}/{repo}.")
            
    print(f"\nTotal usernames saved to PRs.txt: {total_found}")
