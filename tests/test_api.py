"""
Integration and endpoint tests for EcoOrbit FastAPI application.
Run tests using: pytest
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_persona_defaults_success():
    """Verify that valid persona defaults are returned with correct fields."""
    response = client.get("/api/persona/urban_commuter")
    assert response.status_code == 200
    data = response.json()
    assert "car_distance" in data
    assert "diet_type" in data
    assert data["diet_type"] == "diet_vegetarian"


def test_get_persona_defaults_not_found():
    """Verify that requesting an invalid persona returns a 404 error."""
    response = client.get("/api/persona/unknown_persona_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Persona 'unknown_persona_id' not found."


def test_calculate_footprint_success():
    """Verify calculator endpoint successfully computes emissions."""
    payload = {
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
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "transport" in data
    assert "home" in data
    assert "food" in data
    assert "consumption" in data
    assert "total" in data
    assert data["total"] > 0


def test_calculate_footprint_invalid_data():
    """Verify calculator validation returns 422 for bad input types/negative values."""
    # Negative distance is invalid due to Pydantic constraints
    payload = {
        "car_distance": -200.0,
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
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 422


@patch("main.generate_coach_response")
def test_get_coach_advice_mocked(mock_coach):
    """Verify the AI coach endpoint routes requests and returns generated advice."""
    mock_coach.return_value = {
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
