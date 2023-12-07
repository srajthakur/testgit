import requests

# Replace these variables with your own values
github_username = "srajthakur"
github_repo = "testgit"
access_token = "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"

# Step 1: Get Access Token
headers = {"Authorization": f"token {access_token}"}

# Step 2: Fetch ZIP of Master Branch
zip_url = f"https://api.github.com/repos/{github_username}/{github_repo}/zipball/master"
response = requests.get(zip_url, headers=headers)
with open("master.zip", "wb") as f:
    f.write(response.content)

# Step 3: Create Branch
branch_url = f"https://api.github.com/repos/{github_username}/{github_repo}/git/refs"
branch_data = {
    "ref": "refs/heads/restoremaster",
    "sha": "main"  # Use the SHA of the master branch
}
response = requests.post(branch_url, headers=headers, json=branch_data)
# Print the response content for debugging
print(response.content)
print("dsfaaaaaaaaaaaaaaaaaaaaaaaa")

# Check if the response was successful
response.raise_for_status()

# Extract the SHA of the new branch
restoremaster_sha = response.json().get("object", {}).get("sha")

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
    "base_tree": restoremaster_sha,
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
    "message": "Upload ZIP to restoremaster branch",
    "parents": [restoremaster_sha],
    "tree": tree_sha
}

commit_url = f"https://api.github.com/repos/{github_username}/{github_repo}/git/commits"
response = requests.post(commit_url, headers=headers, json=commit_data)
commit_sha = response.json()["sha"]

update_ref_url = f"https://api.github.com/repos/{github_username}/{github_repo}/git/refs/heads/restoremaster"
update_ref_data = {
    "sha": commit_sha
}

response = requests.patch(update_ref_url, headers=headers, json=update_ref_data)

# Step 5: Compare Master and Restore Master
compare_url = f"https://api.github.com/repos/{github_username}/{github_repo}/compare/master...restoremaster"
response = requests.get(compare_url, headers=headers)
comparison_data = response.json()

print("Comparison URL:", comparison_data["html_url"])
