import pytest
from fastapi.testclient import TestClient
from app.main import app  # Adjust this to your FastAPI app location

client = TestClient(app)
# Sample questions for testing
test_inputs = [
    {
        "input": {"query": "What is the definition of negligence?", "source": "statutes"},
        "expected_substring": "negligence",  # loose matching
    }
]

@pytest.mark.parametrize("test_case", test_inputs)
def test_rag_ask_endpoint(test_case):
    response = client.post("/ask", json=test_case["input"])
    assert response.status_code == 200
    assert "answer" in response.json()
    assert test_case["expected_substring"].lower() in response.json()["answer"].lower()
