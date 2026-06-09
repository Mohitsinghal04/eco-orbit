"""
FastAPI Backend Application for EcoOrbit.
Exposes endpoints for carbon footprint calculation, AI coach suggestions,
and mounts the static files for the dashboard frontend.
"""

import logging
import os
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from calculator import PERSONA_DEFAULTS, CarbonCalculator
from coach import generate_coach_response

# Set up Google Cloud Logging if running in production GCP environment
if os.getenv("K_SERVICE"):
    try:
        import google.cloud.logging

        client = google.cloud.logging.Client()
        client.setup_logging()
        logging.info("Google Cloud Logging successfully initialized for Cloud Run.")
    except Exception as e:  # pylint: disable=broad-except
        logging.basicConfig(level=logging.INFO)
        logging.warning("Google Cloud Logging initialization bypassed: %s", e)
else:
    logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="EcoOrbit API",
    description="Carbon footprint tracking and AI coach backend.",
    version="1.0.0",
)

# Restrict CORS to specific local origins or env-configured ports
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom Middleware to inject security headers (responsible server hardening)
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add standard secure HTTP headers to prevent Clickjacking, XSS, and MIME-sniffing."""
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = (
        "max-age=63072000; includeSubDomains; preload"
    )
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), payment=()"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self';"
    )
    return response


# Request and Response schemas
class FootprintData(BaseModel):
    """Pydantic model validating footprint calculator input data."""

    car_distance: float = Field(..., ge=0, description="Monthly car distance in km")
    car_fuel: str = Field(
        ..., description="Car fuel type (e.g. car_petrol, car_electric)"
    )
    transit_distance: float = Field(
        ..., ge=0, description="Monthly public transit distance in km"
    )
    flight_hours: float = Field(..., ge=0, description="Monthly flight hours")
    electricity_kwh: float = Field(
        ..., ge=0, description="Monthly electricity usage in kWh"
    )
    gas_kwh: float = Field(..., ge=0, description="Monthly gas usage in kWh")
    waste_kg: float = Field(..., ge=0, description="Monthly waste generated in kg")
    diet_type: str = Field(
        ..., description="Diet classification (e.g. diet_vegan, diet_medium_meat)"
    )
    clothing_items: int = Field(
        ..., ge=0, description="New clothing items purchased per month"
    )
    electronics_items: int = Field(
        ..., ge=0, description="New electronics purchased per month"
    )
    recycling_pct: float = Field(
        ..., ge=0, le=100, description="Recycling rate percentage"
    )


class ChatMessage(BaseModel):
    """Represents a message in the chat history."""

    role: str = Field(..., description="Either 'user' or 'assistant'")
    content: str = Field(..., description="Text content of the message")


class CoachRequest(BaseModel):
    """Payload for asking the coach for advice."""

    persona: str = Field(..., description="Active user persona key")
    emissions: Dict[str, float] = Field(
        ..., description="Current emission categories breakdown"
    )
    chat_history: List[ChatMessage] = Field(
        default_factory=list, description="Recent conversation history"
    )


class CoachTip(BaseModel):
    """Represents a single tip suggested by the coach."""

    title: str = Field(..., description="Action title")
    description: str = Field(..., description="Specific action details")
    estimated_reduction: str = Field(..., description="Impact description")


class CoachResponse(BaseModel):
    """Response payload for coach suggestions."""

    intro: str = Field(..., description="Greeting and high level analysis")
    highest_category: str = Field(..., description="Highest emission category")
    tips: List[CoachTip] = Field(..., description="List of tips")
    conclusion: str = Field(..., description="Final encouraging remark")


@app.get("/api/persona/{persona_id}", response_model=Dict[str, Any])
def get_persona_defaults(persona_id: str):
    """Fetch default calculator inputs for a specific onboarding persona."""
    if persona_id not in PERSONA_DEFAULTS:
        raise HTTPException(
            status_code=404, detail=f"Persona '{persona_id}' not found."
        )
    return PERSONA_DEFAULTS[persona_id]


@app.post("/api/calculate", response_model=Dict[str, float])
def calculate_footprint(data: FootprintData):
    """Compute carbon footprint values from input metrics."""
    calculator = CarbonCalculator()
    # Convert FootprintData Pydantic model to dictionary
    data_dict = data.model_dump()
    return calculator.calculate_total(data_dict)


@app.post("/api/coach", response_model=CoachResponse)
def get_coach_advice(payload: CoachRequest):
    """Request personalized sustainability insights from the AI coach."""
    history = [msg.model_dump() for msg in payload.chat_history]
    advice = generate_coach_response(payload.persona, payload.emissions, history)
    return advice


# Mount the frontend static files at root
# Ensure index.html exists in static folder first
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    # Read port/host from env or default
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "127.0.0.1")
    uvicorn.run("main:app", host=host, port=port, reload=True)
