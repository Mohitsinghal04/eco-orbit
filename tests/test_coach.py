"""
Unit tests for the rules-based sustainability fallback engine in EcoOrbit.
Run tests using: pytest
"""

from unittest.mock import MagicMock, patch

from coach import generate_coach_response, get_rule_based_advice


def test_fallback_advice_transport_highest():
    """Verify fallback advice when transport emissions are the highest."""
    emissions = {
        "transport": 500.0,
        "home": 200.0,
        "food": 60.0,
        "consumption": 50.0,
        "total": 810.0,
    }
    advice = get_rule_based_advice("urban_commuter", emissions)

    assert "intro" in advice
    assert "highest_category" in advice
    assert "tips" in advice
    assert "conclusion" in advice

    assert advice["highest_category"] == "Transport"
    assert len(advice["tips"]) == 3
    assert advice["tips"][0]["title"] == "Carpool or use EV options"
    assert "-45 kg CO2e/month" in advice["tips"][0]["estimated_reduction"]


def test_fallback_advice_home_highest():
    """Verify fallback advice when home emissions are the highest."""
    emissions = {
        "transport": 100.0,
        "home": 400.0,
        "food": 60.0,
        "consumption": 50.0,
        "total": 610.0,
    }
    advice = get_rule_based_advice("suburban_homeowner", emissions)

    assert advice["highest_category"] == "Home Energy"
    assert len(advice["tips"]) == 3
    assert advice["tips"][0]["title"] == "Smart Thermostat Adjustments"
    assert "-35 kg CO2e/month" in advice["tips"][0]["estimated_reduction"]


def test_fallback_advice_food_highest():
    """Verify fallback advice when food emissions are the highest."""
    emissions = {
        "transport": 50.0,
        "home": 100.0,
        "food": 216.0,
        "consumption": 50.0,
        "total": 416.0,
    }
    advice = get_rule_based_advice("urban_commuter", emissions)

    assert advice["highest_category"] == "Food"
    assert len(advice["tips"]) == 3
    assert advice["tips"][0]["title"] == "Meatless Days"
    assert "-50 kg CO2e/month" in advice["tips"][0]["estimated_reduction"]


def test_fallback_advice_consumption_highest():
    """Verify fallback advice when consumption emissions are the highest."""
    emissions = {
        "transport": 50.0,
        "home": 100.0,
        "food": 60.0,
        "consumption": 300.0,
        "total": 510.0,
    }
    advice = get_rule_based_advice("global_jetsetter", emissions)

    assert advice["highest_category"] == "Shopping/Consumption"
    assert len(advice["tips"]) == 3
    assert advice["tips"][0]["title"] == "Thrift & Secondhand"
    assert "-10 kg CO2e/item avoided" in advice["tips"][0]["estimated_reduction"]


def test_generate_coach_response_fallback_no_key():
    """Verify generate_coach_response falls back to rules-based when Gemini is disabled."""
    with patch("coach.has_gemini", False):
        emissions = {
            "transport": 50.0,
            "home": 60.0,
            "food": 200.0,
            "consumption": 30.0,
            "total": 340.0,
        }
        res = generate_coach_response("urban_commuter", emissions, [])
        assert res["highest_category"] == "Food"
        assert "EcoCoach" in res["intro"]


def test_generate_coach_response_gemini_success():
    """Verify generate_coach_response parses successful Gemini JSON response."""
    with patch("google.generativeai.GenerativeModel.generate_content") as mock_generate:
        mock_response = MagicMock()
        mock_response.text = (
            '{"intro": "Hello test", "highest_category": "Transport", '
            '"tips": [{"title": "Ride bike", "description": "Bike more", '
            '"estimated_reduction": "-10 kg"}], "conclusion": "Bye test"}'
        )
        mock_generate.return_value = mock_response

        with patch("coach.has_gemini", True):
            emissions = {
                "transport": 100.0,
                "home": 50.0,
                "food": 50.0,
                "consumption": 50.0,
                "total": 250.0,
            }
            res = generate_coach_response("urban_commuter", emissions, [])
            assert res["intro"] == "Hello test"
            assert res["highest_category"] == "Transport"
            assert res["tips"][0]["title"] == "Ride bike"
