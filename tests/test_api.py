"""
Integration and endpoint tests for EcoOrbit FastAPI application.
Run tests using: pytest
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# --- Helper payload for a valid footprint calculation ---
VALID_FOOTPRINT_PAYLOAD = {
    "car_distance": 200.0,
    "car_fuel": "car_petrol",
    "transit_distance": 300.0,
    "flight_hours": 0.0,
    "electricity_kwh": 100.0,
    "gas_kwh": 50.0,
    "waste_kg": 10.0,
    "diet_type": "diet_vegan",
    "clothing_items": 1,
    "electronics_items": 0,
    "recycling_pct": 50.0,
}

MOCK_COACH_RESPONSE = {
    "intro": "Greeting and analysis of user's highest emissions category.",
    "highest_category": "Food",
    "tips": [
        {
            "title": "Reduce food waste",
            "description": "Plan your weekly meals.",
            "estimated_reduction": "-18 kg CO2e/month",
        }
    ],
    "conclusion": "Good luck!",
}


# --- Persona Endpoint Tests ---


def test_get_persona_defaults_urban_commuter():
    """Verify urban_commuter persona defaults contain expected fields."""
    response = client.get("/api/persona/urban_commuter")
    assert response.status_code == 200
    data = response.json()
    assert "car_distance" in data
    assert "diet_type" in data
    assert data["diet_type"] == "diet_vegetarian"


def test_get_persona_defaults_suburban_homeowner():
    """Verify suburban_homeowner persona defaults are returned correctly."""
    response = client.get("/api/persona/suburban_homeowner")
    assert response.status_code == 200
    data = response.json()
    assert "car_distance" in data
    assert "electricity_kwh" in data
    assert data["diet_type"] == "diet_medium_meat"


def test_get_persona_defaults_global_jetsetter():
    """Verify global_jetsetter persona defaults are returned correctly."""
    response = client.get("/api/persona/global_jetsetter")
    assert response.status_code == 200
    data = response.json()
    assert "flight_hours" in data
    assert data["flight_hours"] > 0


def test_get_persona_defaults_not_found():
    """Verify that requesting an invalid persona returns a 404 error."""
    response = client.get("/api/persona/unknown_persona_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Persona 'unknown_persona_id' not found."


# --- Calculate Endpoint Tests ---


def test_calculate_footprint_success():
    """Verify calculator endpoint successfully computes emissions."""
    response = client.post("/api/calculate", json=VALID_FOOTPRINT_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert "transport" in data
    assert "home" in data
    assert "food" in data
    assert "consumption" in data
    assert "total" in data
    assert data["total"] > 0


def test_calculate_footprint_all_zero():
    """Verify calculator handles a minimal (zero-value) payload."""
    payload = {**VALID_FOOTPRINT_PAYLOAD, "car_distance": 0.0, "flight_hours": 0.0}
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 200
    assert response.json()["transport"] >= 0


def test_calculate_footprint_invalid_negative_distance():
    """Verify calculator validation returns 422 for negative car distance."""
    payload = {**VALID_FOOTPRINT_PAYLOAD, "car_distance": -200.0}
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 422


def test_calculate_footprint_invalid_fuel_type():
    """Verify calculator validation returns 422 for an unknown fuel type string."""
    payload = {**VALID_FOOTPRINT_PAYLOAD, "car_fuel": "car_rocket"}
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 422


def test_calculate_footprint_invalid_diet_type():
    """Verify calculator validation returns 422 for an unknown diet type string."""
    payload = {**VALID_FOOTPRINT_PAYLOAD, "diet_type": "diet_carnivore"}
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 422


def test_calculate_footprint_recycling_out_of_range():
    """Verify calculator validation returns 422 when recycling_pct > 100."""
    payload = {**VALID_FOOTPRINT_PAYLOAD, "recycling_pct": 150.0}
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 422


# --- Coach Endpoint Tests ---


@patch("main.generate_coach_response")
def test_get_coach_advice_mocked(mock_coach):
    """Verify the AI coach endpoint routes requests and returns generated advice."""
    mock_coach.return_value = MOCK_COACH_RESPONSE

    payload = {
        "persona": "urban_commuter",
        "emissions": {
            "transport": 50.0,
            "home": 60.0,
            "food": 45.0,
            "consumption": 20.0,
            "total": 175.0,
        },
        "chat_history": [
            {"role": "user", "content": "Hi EcoCoach!"},
            {"role": "assistant", "content": "Hello! How can I help you?"},
        ],
    }

    response = client.post("/api/coach", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "intro" in data
    assert "highest_category" in data
    assert "tips" in data
    assert len(data["tips"]) == 1
    assert data["tips"][0]["title"] == "Reduce food waste"
    assert data["conclusion"] == "Good luck!"
    mock_coach.assert_called_once()


@patch("main.generate_coach_response")
def test_get_coach_advice_empty_history(mock_coach):
    """Verify coach endpoint works correctly with no prior chat history."""
    mock_coach.return_value = MOCK_COACH_RESPONSE

    payload = {
        "persona": "suburban_homeowner",
        "emissions": {
            "transport": 300.0,
            "home": 150.0,
            "food": 50.0,
            "consumption": 30.0,
            "total": 530.0,
        },
        "chat_history": [],
    }

    response = client.post("/api/coach", json=payload)
    assert response.status_code == 200
    assert "intro" in response.json()


# --- Security Header Tests ---


def test_response_security_headers():
    """Verify that all 7 secure HTTP response headers are set on API endpoints."""
    response = client.get("/api/persona/urban_commuter")
    assert response.status_code == 200
    headers = response.headers
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "max-age=63072000" in headers.get("Strict-Transport-Security", "")
    assert "camera=()" in headers.get("Permissions-Policy", "")
    assert "default-src 'self'" in headers.get("Content-Security-Policy", "")


def test_csp_header_no_unsafe_inline():
    """Verify CSP header does not contain unsafe-inline (XSS vulnerability)."""
    response = client.get("/api/persona/urban_commuter")
    csp = response.headers.get("Content-Security-Policy", "")
    assert "unsafe-inline" not in csp
    assert "unsafe-eval" not in csp
