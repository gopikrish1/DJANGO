"""
Comprehensive End-to-End API Test Script
Tests all requirements outlined in the workflow.
"""
import requests
import tempfile
import os

BASE_URL = 'http://127.0.0.1:8000'
print("Starting Comprehensive API Tests...\n" + "="*40)

# =======================================================
# 1. AUTHENTICATION
# =======================================================
print("TEST 1: Authentication")
login_resp = requests.post(f"{BASE_URL}/api/auth/login/", json={
    "username": "admin",
    "password": "1213"
})
assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
data = login_resp.json()
assert "access" in data and "refresh" in data, "Tokens missing in response"
token = data["access"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Login successful. Access token received.\n")


# =======================================================
# 2. UNAUTHENTICATED ACCESS
# =======================================================
print("TEST 2: Unauthenticated Protection")
unauth_resp = requests.get(f"{BASE_URL}/api/documents/")
assert unauth_resp.status_code == 401, "API should block unauthenticated access!"
print("✅ Unauthenticated access successfully blocked (401).\n")


# =======================================================
# 3. DOCUMENTS CRUD
# =======================================================
print("TEST 3: Documents Endpoints")

# a. List Documents (Initially empty)
docs_resp = requests.get(f"{BASE_URL}/api/documents/", headers=headers)
assert docs_resp.status_code == 200
print(f"✅ GET /documents/ -> {docs_resp.status_code}")

# b. Upload Document
with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
    tmp.write(b"Hello this is a test document.")
    tmp_path = tmp.name

try:
    with open(tmp_path, 'rb') as f:
        files = {'file': f}
        data = {'title': 'Test Automation Document'}
        upload_resp = requests.post(
            f"{BASE_URL}/api/documents/",
            headers=headers,
            data=data,
            files=files
        )
    assert upload_resp.status_code == 201, f"Upload failed: {upload_resp.text}"
    doc_id = upload_resp.json()["id"]
    print(f"✅ POST /documents/ -> Uploaded doc ID {doc_id}")
finally:
    os.remove(tmp_path)

# c. Retrieve Document
retrieve_resp = requests.get(f"{BASE_URL}/api/documents/{doc_id}/", headers=headers)
assert retrieve_resp.status_code == 200
assert retrieve_resp.json()["title"] == 'Test Automation Document'
print(f"✅ GET /documents/{doc_id}/ -> Retrieved correctly")

# d. Delete Document
delete_resp = requests.delete(f"{BASE_URL}/api/documents/{doc_id}/", headers=headers)
assert delete_resp.status_code == 204
print(f"✅ DELETE /documents/{doc_id}/ -> Deleted correctly")

# e. Verify Deletion
verify_del_resp = requests.get(f"{BASE_URL}/api/documents/{doc_id}/", headers=headers)
assert verify_del_resp.status_code == 404
print(f"✅ Verified document {doc_id} no longer exists (404).\n")


# =======================================================
# 4. QUERIES SYSTEM
# =======================================================
print("TEST 4: Queries Endpoints")

# a. Submit a Query
query_resp = requests.post(
    f"{BASE_URL}/api/query/",
    headers=headers,
    json={"query_text": "Automated system test query"}
)
assert query_resp.status_code == 201
query_id = query_resp.json()["id"]
print(f"✅ POST /query/ -> Created query ID {query_id}")

# b. List Queries History
history_resp = requests.get(f"{BASE_URL}/api/queries/", headers=headers)
assert history_resp.status_code == 200
results = history_resp.json().get("results", [])
assert len(results) > 0, "Query list should not be empty"
found = any(q["id"] == query_id for q in results)
assert found, "Recently submitted query not found in history"
print(f"✅ GET /queries/ -> History successfully retrieved")

print("\n" + "="*40 + "\n🎉 ALL TESTS PASSED SUCCESSFULLY! The entire API is verified.")
