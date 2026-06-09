"""
Carbon Footprint Calculator logic for EcoOrbit.
Provides calculation methods based on EPA, DEFRA, and other standard carbon factors.
"""

from typing import Any, Dict

# Carbon Emission Factors (in kg CO2e per unit)
EMISSION_FACTORS = {
    # Transport (per km)
    "car_petrol": 0.18,
    "car_diesel": 0.17,
    "car_electric": 0.05,
    "car_hybrid": 0.10,
    "public_transit": 0.03,
    # Flight (per hour)
    "flight_hour": 90.0,
    # Home Energy (per kWh / kg)
    "electricity_kwh": 0.38,
    "gas_kwh": 0.18,
    "waste_kg": 0.50,
    # Food (per day, multiplied by 30 for monthly)
    "diet_vegan": 1.5,
    "diet_vegetarian": 2.0,
    "diet_low_meat": 3.0,
    "diet_medium_meat": 4.5,
    "diet_high_meat": 7.2,
    # Shopping (per item)
    "clothing_item": 10.0,
    "electronics_item": 150.0,
}

# Persona defaults for onboarding
PERSONA_DEFAULTS = {
    "urban_commuter": {
        "car_distance": 100.0,
        "car_fuel": "car_hybrid",
        "transit_distance": 600.0,
        "flight_hours": 1.0,
        "electricity_kwh": 150.0,
        "gas_kwh": 100.0,
        "waste_kg": 15.0,
        "diet_type": "diet_vegetarian",
        "clothing_items": 2,
        "electronics_items": 0,
        "recycling_pct": 75.0,
    },
    "suburban_homeowner": {
        "car_distance": 1200.0,
        "car_fuel": "car_petrol",
        "transit_distance": 50.0,
        "flight_hours": 2.0,
        "electricity_kwh": 450.0,
        "gas_kwh": 600.0,
        "waste_kg": 40.0,
        "diet_type": "diet_medium_meat",
        "clothing_items": 4,
        "electronics_items": 1,
        "recycling_pct": 50.0,
    },
    "global_jetsetter": {
        "car_distance": 300.0,
        "car_fuel": "car_diesel",
        "transit_distance": 100.0,
        "flight_hours": 15.0,
        "electricity_kwh": 250.0,
        "gas_kwh": 200.0,
        "waste_kg": 25.0,
        "diet_type": "diet_high_meat",
        "clothing_items": 8,
        "electronics_items": 2,
        "recycling_pct": 30.0,
    },
}


class CarbonCalculator:
    """Calculates carbon footprint categories based on user inputs."""

    @staticmethod
    def calculate_transport(
        car_distance: float, car_fuel: str, transit_distance: float, flight_hours: float
    ) -> float:
        """Calculate transport emissions in kg CO2e/month."""
        car_factor = EMISSION_FACTORS.get(car_fuel, EMISSION_FACTORS["car_petrol"])
        car_emissions = car_distance * car_factor
        transit_emissions = transit_distance * EMISSION_FACTORS["public_transit"]
        flight_emissions = flight_hours * EMISSION_FACTORS["flight_hour"]
        return float(round(car_emissions + transit_emissions + flight_emissions, 2))

    @staticmethod
    def calculate_home(
        electricity_kwh: float, gas_kwh: float, waste_kg: float, recycling_pct: float
    ) -> float:
        """Calculate home energy and waste emissions in kg CO2e/month, with recycling offset."""
        elec_emissions = electricity_kwh * EMISSION_FACTORS["electricity_kwh"]
        gas_emissions = gas_kwh * EMISSION_FACTORS["gas_kwh"]

        # Recycling reduces waste emissions by up to 50%
        waste_emissions = waste_kg * EMISSION_FACTORS["waste_kg"]
        recycling_offset = (recycling_pct / 100.0) * 0.50 * waste_emissions
        net_waste_emissions = max(0.0, waste_emissions - recycling_offset)

        return float(round(elec_emissions + gas_emissions + net_waste_emissions, 2))

    @staticmethod
    def calculate_food(diet_type: str) -> float:
        """Calculate food emissions in kg CO2e/month (based on a 30-day month)."""
        diet_factor = EMISSION_FACTORS.get(
            diet_type, EMISSION_FACTORS["diet_medium_meat"]
        )
        return float(round(diet_factor * 30.0, 2))

    @staticmethod
    def calculate_consumption(
        clothing_items: int, electronics_items: int, recycling_pct: float
    ) -> float:
        """Calculate consumption emissions in kg CO2e/month, with recycling offset."""
        clothing_emissions = clothing_items * EMISSION_FACTORS["clothing_item"]
        electronics_emissions = electronics_items * EMISSION_FACTORS["electronics_item"]
        total_emissions = clothing_emissions + electronics_emissions

        # Recycling reduces shopping footprint by up to 10%
        recycling_offset = (recycling_pct / 100.0) * 0.10 * total_emissions
        return float(round(total_emissions - recycling_offset, 2))

    def calculate_total(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # pylint: disable=too-many-locals
        """Calculate all emissions categories and return details and total."""
        try:
            car_dist = float(data.get("car_distance", 0.0))
            car_fuel = str(data.get("car_fuel", "car_petrol"))
            transit_dist = float(data.get("transit_distance", 0.0))
            flight_hrs = float(data.get("flight_hours", 0.0))

            elec = float(data.get("electricity_kwh", 0.0))
            gas = float(data.get("gas_kwh", 0.0))
            waste = float(data.get("waste_kg", 0.0))
            recycle = float(data.get("recycling_pct", 0.0))

            diet = str(data.get("diet_type", "diet_medium_meat"))
            clothes = int(data.get("clothing_items", 0))
            electronics = int(data.get("electronics_items", 0))
        except (ValueError, TypeError):
            # Fallback if typing is incorrect
            car_dist = transit_dist = flight_hrs = elec = gas = waste = recycle = 0.0
            clothes = electronics = 0
            car_fuel = "car_petrol"
            diet = "diet_medium_meat"

        transport_total = self.calculate_transport(
            car_dist, car_fuel, transit_dist, flight_hrs
        )
        home_total = self.calculate_home(elec, gas, waste, recycle)
        food_total = self.calculate_food(diet)
        consumption_total = self.calculate_consumption(clothes, electronics, recycle)

        grand_total = float(
            round(transport_total + home_total + food_total + consumption_total, 2)
        )

        return {
            "transport": transport_total,
            "home": home_total,
            "food": food_total,
            "consumption": consumption_total,
            "total": grand_total,
        }
