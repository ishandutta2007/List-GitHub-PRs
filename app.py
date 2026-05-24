from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fetch_github_PRs import get_PRs, save_to_file, DEFAULT_REPOS
from typing import List, Optional
import os

app = FastAPI()

# Mount static files
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.get("/api/PRs")
async def fetch_PRs(
    repos: Optional[List[str]] = Query(None),
    append: bool = Query(False)
):
    # Determine repo list
    repo_list = []
    if repos:
        for r in repos:
            if '/' in r:
                owner, repo = r.split('/', 1)
                repo_list.append((owner.strip(), repo.strip()))
    
    # Fallback to defaults if no valid repos provided
    using_defaults = False
    if not repo_list:
        repo_list = DEFAULT_REPOS
        using_defaults = True

    # Clear file first if NOT in append mode
    if not append:
        open("PRs.txt", "w").close()

    results = []
    for owner, repo in repo_list:
        try:
            usernames = get_PRs(owner, repo)
            if usernames:
                save_to_file(usernames, append=True)
                results.append({
                    "repo": f"{owner}/{repo}",
                    "usernames": usernames,
                    "count": len(usernames),
                    "status": "success"
                })
            else:
                results.append({
                    "repo": f"{owner}/{repo}",
                    "usernames": [],
                    "count": 0,
                    "status": "no_prs"
                })
        except Exception as e:
            results.append({
                "repo": f"{owner}/{repo}",
                "usernames": [],
                "count": 0,
                "status": "error",
                "error": str(e)
            })

    return {"results": results, "using_defaults": using_defaults}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
