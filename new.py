import requests

# Replace these variables with your own values
github_username = "srajthakur"
github_repo = "testgit"
access_token = "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"
branch_name = 'master'
new_branch = 'restoremaster4'
# Step 1: Get Access Token
headers = {"Authorization": f"token {access_token}"}

# Step 2: Fetch ZIP of Master Branch
#master_sha_url = f"https://api.github.com/repos/{github_username}/git/refs/{github_repo}"
branch_sha_url = f"https://api.github.com/repos/{github_username}/{github_repo}/git/refs/heads/{branch_name}"
zip_url = f"https://api.github.com/repos/{github_username}/{github_repo}/zipball/master"
response = requests.get(zip_url, headers=headers)
response = requests.get(branch_sha_url, headers=headers)
response.raise_for_status()


# Extract the SHA of the branch
branch_sha = response.json().get("object", {}).get("sha")



if response.status_code == 200:
    print("Access token is valid.")
else:
    print(f"Access token is invalid. Status code: {response.status_code}")
    print("Response:", response.json())
with open("master.zip", "wb") as f:
    f.write(response.content)

# Step 3: Create Branch
branch_url = f"https://api.github.com/repos/{github_username}/{github_repo}/git/refs"
branch_data = {
    "ref": f"refs/heads/{new_branch}",
    "sha": branch_sha  # Use the SHA of the master branch
}
response = requests.post(branch_url, headers=headers, json=branch_data)
# Print the response content for debugging


# Check if the response was successful
response.raise_for_status()

# Extract the SHA of the new branch
new_branch_sha = response.json().get("object", {}).get("sha")

# Step 4: Upload ZIP to New Branch
upload_url = f"https://api.github.com/repos/{github_username}/{github_repo}/git/blobs"
with open("master.zip", "rb") as f:
    zip_content = f.read()

blob_data = {
    "content": zip_content,
    "encoding": "base64"
}
response = requests.post(upload_url, headers=headers, json=blob_data)
blob_sha = response.json()["sha"]

tree_data = {
    "base_tree": new_branch_sha,
    "tree": [
        {
            "path": "master.zip",
            "mode": "100644",
            "type": "blob",
            "sha": blob_sha
        }
    ]
}

tree_url = f"https://api.github.com/repos/{github_username}/{github_repo}/git/trees"
response = requests.post(tree_url, headers=headers, json=tree_data)
tree_sha = response.json()["sha"]

commit_data = {
    "message": "Upload ZIP to new_branch ",
    "parents": [new_branch_sha],
    "tree": tree_sha
}

commit_url = f"https://api.github.com/repos/{github_username}/{github_repo}/git/commits"
response = requests.post(commit_url, headers=headers, json=commit_data)
commit_sha = response.json()["sha"]

update_ref_url = f"https://api.github.com/repos/{github_username}/{github_repo}/git/refs/heads/{new_branch}"
update_ref_data = {
    "sha": commit_sha
}

response = requests.patch(update_ref_url, headers=headers, json=update_ref_data)

# Step 5: Compare Master and Restore Master
compare_url = f"https://api.github.com/repos/{github_username}/{github_repo}/compare/master...{new_branch}"
response = requests.get(compare_url, headers=headers)
comparison_data = response.json()
response.raise_for_status()

# Check if there are differences
are_differences = response.json()["status"] != "identical"

print(f"Are there differences between {branch_name} and restoremaster? {are_differences}")
