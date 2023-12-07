import requests
import os
import base64
# Replace these variables with your own values
github_username = "srajthakur"
github_repo = "testgit"
access_token = "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"
branch_name = 'master'
new_branch = 'restoremaster8'

# Step 1: Get Access Token
headers = {"Authorization": f"token {access_token}"}

# Step 2: Fetch ZIP of Master Branch
#master_sha_url = f"https://api.github.com/repos/{github_username}/git/refs/{github_repo}"
branch_sha_url = f"https://api.github.com/repos/{github_username}/{github_repo}/git/refs/heads/{branch_name}"
zip_url = f"https://api.github.com/repos/{github_username}/{github_repo}/zipball/master"

response = requests.get(branch_sha_url, headers=headers)
# response.raise_for_status()


# Extract the SHA of the branch
branch_sha = response.json().get("object", {}).get("sha")



if response.status_code == 200:
    print("Access token is valid.")
else:
    print(f"Access token is invalid. Status code: {response.status_code}")
    print("Response:", response.json())
response = requests.get(zip_url, headers=headers)
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


import zipfile



with zipfile.ZipFile('master.zip', 'r') as zip_ref:
    zip_ref.extractall()

# Step 4: Upload ZIP to New Branch
upload_url = f"https://api.github.com/repos/{github_username}/{github_repo}/git/blobs"
contents = []
source_folder = 'unzipped/' + os.listdir('unzipped')[0]
for root, dirs, files in os.walk(source_folder):
    for file in files:
        file_path = os.path.relpath(os.path.join(root, file), source_folder)
        contents.append(file_path)

# Step 2: Create Blobs
blob_shas = {}
for file_path in contents:
    with open(os.path.join(source_folder, file_path), 'rb') as f:
        content = f.read()
        encoded_content = base64.b64encode(content).decode('utf-8')

    blob_url = f"https://api.github.com/repos/{github_username}/{github_repo}/git/blobs"
    blob_data = {
        "content": encoded_content,
        "encoding": "base64"
    }

    response = requests.post(blob_url, headers={"Authorization": f"token {access_token}"}, json=blob_data)
    response.raise_for_status()
    blob_shas[file_path] = response.json()["sha"]

# Step 3: Create Trees
tree = []
for file_path, blob_sha in blob_shas.items():
    tree_entry = {
        "path": file_path,
        "mode": "100644",  # File mode
        "type": "blob",
        "sha": blob_sha
    }
    tree.append(tree_entry)

tree_data = {
    "base_tree": None,  # Use None for the initial commit
    "tree": tree
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










#change done