import pytest
from fastapi.testclient import TestClient

from app.main import app  # Make sure this points to your FastAPI app

client = TestClient(app)

# === Sample test cases ===
test_inputs = [
    {
        "input": {
            "query": "What is the definition of negligence?",
            "source": "statutes",
        },
        "expected_substrings": ["duty", "care"],
    },
    {
        "input": {
            "query": "What does INS v. Cardoza-Fonseca decide?",
            "source": "precedents",
        },
        "expected_substrings": ["asylum", "persecution", "reasonable possibility"],
    },
    {
        "input": {
            "query": "Who qualifies for asylum under U.S. immigration law?",
            "source": "both",
        },
        "expected_substrings": ["well-founded fear", "asylum", "refugee"],
    },
    {
        "input": {
            "query": "What rights does an immigrant have during removal proceedings?",
            "source": "statutes",
        },
        "expected_substrings": ["notice", "representation", "hearing", "deportation"],
    },
    {
        "input": {
            "query": "What was held in Matter of Acosta?",
            "source": "precedents",
        },
        "expected_substrings": [
            "immutable characteristic",
            "particular social group",
            "Acosta",
        ],
    },
    {
        "input": {
            "query": "What is the immigration policy on moon colonists?",
            "source": "both",
        },
        "expected_substrings": [
            "Not found",
            "no information",
            "irrelevant",
        ],  # for hallucination
    },
]


# === Parametrized test ===
@pytest.mark.parametrize("test_case", test_inputs)
def test_rag_ask_endpoint(test_case):
    response = client.post("/api/ask", json=test_case["input"])
    assert response.status_code == 200, f"Failed with: {response.text}"

    json_resp = response.json()
    assert "answer" in json_resp, "No 'answer' key in response"

    answer_lower = json_resp["answer"].lower()
    substrings = test_case.get("expected_substrings") or [
        test_case["expected_substring"]
    ]

    match_found = any(sub.lower() in answer_lower for sub in substrings)
    assert (
        match_found
    ), f"None of the expected keywords {substrings} were found in answer:\n{json_resp['answer']}"
