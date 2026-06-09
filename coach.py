"""
AI Coach logic for EcoOrbit.
Uses Google Generative AI SDK (Gemini API) if configured,
and falls back to a rules-based expert system otherwise.
"""

# pylint: disable=line-too-long, too-many-locals

import json
import logging
import os
from typing import Any, Dict, List

import google.generativeai as genai
from dotenv import load_dotenv

# Load env variables from .env if present
load_dotenv()

# Check if Gemini API key is configured
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
has_gemini = False

if GEMINI_API_KEY and GEMINI_API_KEY != "your_google_gemini_api_key_here":
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        has_gemini = True
    except Exception as e:  # pylint: disable=broad-except
        logging.warning("Failed to configure Gemini API: %s", e)


def get_rule_based_advice(persona: str, emissions: Dict[str, float]) -> Dict[str, Any]:
    """Fallback expert rules-based sustainability advice based on emissions details."""
    total = emissions.get("total", 0.0)
    transport = emissions.get("transport", 0.0)
    home = emissions.get("home", 0.0)
    food = emissions.get("food", 0.0)
    consumption = emissions.get("consumption", 0.0)

    # Identify the highest emission category
    categories = {
        "Transport": transport,
        "Home Energy": home,
        "Food": food,
        "Shopping/Consumption": consumption,
    }
    highest_category = max(categories, key=categories.get)
    highest_val = categories[highest_category]

    persona_name = persona.replace("_", " ").title()

    intro = (
        f"Hello! I am EcoCoach, your virtual sustainability guide. "
        f"I've analyzed your profile as a {persona_name} with a monthly carbon footprint of {total} kg CO2e. "
        f"Your highest source of emissions is {highest_category} at {highest_val} kg CO2e ({round(highest_val / (total or 1) * 100, 1)}% of your footprint)."
    )

    tips = []
    # Category-specific suggestions
    if highest_category == "Transport":
        tips = [
            {
                "title": "Carpool or use EV options",
                "description": "Carpooling just 2 days a week or shifting to hybrid/electric rides can slash transport emissions.",
                "estimated_reduction": "-45 kg CO2e/month",
            },
            {
                "title": "Active Transport",
                "description": "For distances under 3km, walk or bike. It is zero-carbon and healthier.",
                "estimated_reduction": "-20 kg CO2e/month",
            },
            {
                "title": "Mindful Flying",
                "description": "Combine multiple business meetings into one trip or take trains for short-haul trips where possible.",
                "estimated_reduction": "-180 kg CO2e/flight-hour saved",
            },
        ]
    elif highest_category == "Home Energy":
        tips = [
            {
                "title": "Smart Thermostat Adjustments",
                "description": "Lowering your heating thermostat by just 1-2°C in winter can cut energy footprint by up to 10%.",
                "estimated_reduction": "-35 kg CO2e/month",
            },
            {
                "title": "LED Retrofit",
                "description": "Replace traditional bulbs with ENERGY STAR certified LED bulbs.",
                "estimated_reduction": "-15 kg CO2e/month",
            },
            {
                "title": "Eliminate Phantom Loads",
                "description": "Unplug chargers and appliances when not in use or use smart power strips.",
                "estimated_reduction": "-8 kg CO2e/month",
            },
        ]
    elif highest_category == "Food":
        tips = [
            {
                "title": "Meatless Days",
                "description": "Swapping beef or lamb for plant-based meals (like beans, tofu, or grains) 3 times a week yields huge savings.",
                "estimated_reduction": "-50 kg CO2e/month",
            },
            {
                "title": "Zero Food Waste",
                "description": "Plan meals in advance. Food waste in landfills produces methane, which has high warming potential.",
                "estimated_reduction": "-18 kg CO2e/month",
            },
            {
                "title": "Eat Local & Seasonal",
                "description": "Choosing local seasonal produce reduces food transport (food miles) and packaging emissions.",
                "estimated_reduction": "-12 kg CO2e/month",
            },
        ]
    else:  # Shopping/Consumption
        tips = [
            {
                "title": "Thrift & Secondhand",
                "description": "Buy secondhand clothes or extend the life of your wardrobe. Fast fashion is carbon-intensive.",
                "estimated_reduction": "-10 kg CO2e/item avoided",
            },
            {
                "title": "Repair Over Replace",
                "description": "Extend the lifespan of smartphones and laptops. Electronics manufacturing is highly energy-intensive.",
                "estimated_reduction": "-150 kg CO2e/device saved",
            },
            {
                "title": "Optimize Recycling",
                "description": "Increase your recycling rate to reclaim resources like aluminum, paper, and plastic.",
                "estimated_reduction": "-5 kg CO2e/month",
            },
        ]

    conclusion = (
        "Keep up the great work! Try selecting some of these actions in your Action Planner "
        "to visually see your carbon footprint reduce in real-time."
    )

    return {
        "intro": intro,
        "highest_category": highest_category,
        "tips": tips,
        "conclusion": conclusion,
    }


def generate_coach_response(
    persona: str, emissions: Dict[str, float], chat_history: List[Dict[str, str]]
) -> Dict[str, Any]:
    """Generates structured advice using Gemini API with JSON output schema, falling back to rule-based engine if unavailable."""
    if not has_gemini:
        return get_rule_based_advice(persona, emissions)

    try:
        # Define the expected JSON output schema for Gemini structured response
        schema = {
            "type": "OBJECT",
            "properties": {
                "intro": {
                    "type": "STRING",
                    "description": "Greeting and analysis of user's highest emissions category and total emissions.",
                },
                "highest_category": {
                    "type": "STRING",
                    "description": "The highest category of emissions, e.g. Transport, Home Energy, Food, Shopping.",
                },
                "tips": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "title": {
                                "type": "STRING",
                                "description": "Short action title.",
                            },
                            "description": {
                                "type": "STRING",
                                "description": "Specific description of how to accomplish this.",
                            },
                            "estimated_reduction": {
                                "type": "STRING",
                                "description": "Estimated impact or savings, e.g. -50 kg CO2e/month.",
                            },
                        },
                        "required": ["title", "description", "estimated_reduction"],
                    },
                    "description": "Three highly specific tips tailored to user persona and highest emissions category.",
                },
                "conclusion": {
                    "type": "STRING",
                    "description": "Encouraging final remark.",
                },
            },
            "required": ["intro", "highest_category", "tips", "conclusion"],
        }

        # Apply safety settings to prevent unsafe content generation (responsible AI practices)
        safety_settings = [
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
        ]

        # Define model with system instruction and generation config matching JSON schema
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=(
                "You are EcoCoach, an expert virtual sustainability assistant. "
                "Provide a personalized, encouraging response to the user. "
                "You must output JSON conforming to the requested schema structure."
            ),
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": schema,
            },
            safety_settings=safety_settings,
        )

        # Format metrics and context for the AI model prompt
        prompt = (
            f"User Profile: {persona.replace('_', ' ').title()}\n"
            f"Current Carbon Emissions (kg CO2e/month):\n"
            f"- Transport: {emissions.get('transport', 0.0)} kg CO2e\n"
            f"- Home Energy & Waste: {emissions.get('home', 0.0)} kg CO2e\n"
            f"- Food/Diet: {emissions.get('food', 0.0)} kg CO2e\n"
            f"- Shopping/Consumption: {emissions.get('consumption', 0.0)} kg CO2e\n"
            f"- Total Footprint: {emissions.get('total', 0.0)} kg CO2e\n\n"
            f"Generate 3 highly specific, actionable tips to reduce their carbon footprint."
        )

        # Build contents list including chat history for context
        contents = []
        for msg in chat_history[-6:]:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [msg["content"]]})

        contents.append({"role": "user", "parts": [prompt]})

        response = model.generate_content(contents)
        return json.loads(response.text)
    except Exception as e:  # pylint: disable=broad-except
        logging.error(
            "Gemini API call failed: %s. Falling back to rule-based engine.", e
        )
        return get_rule_based_advice(persona, emissions)
