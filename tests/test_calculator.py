"""
Unit tests for the CarbonCalculator class in EcoOrbit.
Run tests using: pytest
"""

from calculator import CarbonCalculator


def test_calculate_transport_basic():
    """Verify standard transport calculations."""
    # Car: 100km * 0.10 (hybrid) = 10 kg
    # Transit: 100km * 0.03 = 3 kg
    # Flights: 2 hrs * 90.0 = 180 kg
    # Total = 193.0
    val = CarbonCalculator.calculate_transport(100.0, "car_hybrid", 100.0, 2.0)
    assert val == 193.0


def test_calculate_transport_zero():
    """Verify transport calculation handles zeros."""
    val = CarbonCalculator.calculate_transport(0.0, "car_petrol", 0.0, 0.0)
    assert val == 0.0


def test_calculate_home_basic():
    """Verify standard home emissions with recycling offset."""
    # Electricity: 200 kWh * 0.38 = 76.0 kg
    # Gas: 100 kWh * 0.18 = 18.0 kg
    # Waste: 10 kg * 0.5 = 5.0 kg
    # Recycling: 50% reduces waste emissions by 50% * 0.5 * 5.0 = 1.25 kg
    # Net Waste: 5.0 - 1.25 = 3.75 kg
    # Total: 76.0 + 18.0 + 3.75 = 97.75
    val = CarbonCalculator.calculate_home(200.0, 100.0, 10.0, 50.0)
    assert val == 97.75


def test_calculate_food_diets():
    """Verify food emissions scale by diet type."""
    # Vegan factor: 1.5 * 30 days = 45.0 kg
    assert CarbonCalculator.calculate_food("diet_vegan") == 45.0

    # Vegetarian factor: 2.0 * 30 days = 60.0 kg
    assert CarbonCalculator.calculate_food("diet_vegetarian") == 60.0

    # High meat factor: 7.2 * 30 days = 216.0 kg
    assert CarbonCalculator.calculate_food("diet_high_meat") == 216.0


def test_calculate_consumption_basic():
    """Verify shopping emissions with recycling offset."""
    # Clothes: 2 items * 10 = 20.0 kg
    # Tech: 1 item * 150 = 150.0 kg
    # Base: 170.0 kg
    # Recycling: 20% reduces consumption emissions by 20% * 0.10 * 170.0 = 3.4 kg
    # Net: 170.0 - 3.4 = 166.6
    val = CarbonCalculator.calculate_consumption(2, 1, 20.0)
    assert val == 166.6


def test_calculate_total_wrapper():
    """Verify the grand total calculator aggregates all categories correctly."""
    calculator = CarbonCalculator()
    input_data = {
        "car_distance": 500.0,
        "car_fuel": "car_electric",  # 500 * 0.05 = 25 kg
        "transit_distance": 200.0,  # 200 * 0.03 = 6 kg
        "flight_hours": 0.0,
        "electricity_kwh": 300.0,  # 300 * 0.38 = 114 kg
        "gas_kwh": 0.0,
        "waste_kg": 20.0,  # 20 * 0.5 = 10 kg
        "recycling_pct": 100.0,  # 100% recycling reduces waste by 50% -> net 5 kg
        # Also reduces consumption by 10%
        "diet_type": "diet_vegan",  # 1.5 * 30 = 45 kg
        "clothing_items": 3,  # 3 * 10 = 30 kg
        "electronics_items": 0,  # 0 kg
        # Consumption base: 30 kg, offset 10% -> net 27 kg
    }

    # Transport = 31.0
    # Home = 114.0 + 5.0 = 119.0
    # Food = 45.0
    # Consumption = 27.0
    # Total = 31 + 119 + 45 + 27 = 222.0
    res = calculator.calculate_total(input_data)
    assert res["transport"] == 31.0
    assert res["home"] == 119.0
    assert res["food"] == 45.0
    assert res["consumption"] == 27.0
    assert res["total"] == 222.0
