"""
Unit tests for the rules-based sustainability fallback engine in EcoOrbit.
Run tests using: pytest
"""

from coach import get_rule_based_advice


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
