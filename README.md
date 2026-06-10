# 🌍 EcoOrbit — Smart Carbon Footprint Tracker & AI Coach

> **An interactive, full-stack sustainability application** that helps individuals calculate, visualise, and reduce their personal carbon footprint through intelligent lifestyle personas and a conversational AI coach powered by Google Gemini.

**Live Application:** https://ecoorbit-241657976849.us-central1.run.app

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Solution Overview](#2-solution-overview)
3. [Google Services & Problem Statement Alignment](#3-google-services--problem-statement-alignment)
4. [Code Quality](#4-code-quality--structure-readability-maintainability)
5. [Security](#5-security--safe-and-responsible-implementation)
6. [Efficiency](#6-efficiency--optimal-use-of-resources)
7. [Testing](#7-testing--validation-of-functionality)
8. [Accessibility](#8-accessibility--inclusive-and-usable-design)
9. [Chosen Verticals (Personas)](#9-chosen-verticals-personas)
10. [Calculation Methodology](#10-calculation-methodology)
11. [Developer Setup Guide](#11-developer-setup-guide)
12. [GCP Deployment Guide](#12-gcp-deployment-guide)

---

## 1. Problem Statement

Climate change is one of the defining challenges of our era. Yet most individuals have no simple, personalised way to understand their own contribution — or know where to start reducing it. EcoOrbit solves this by:

- **Quantifying** a user's monthly carbon footprint across four key lifestyle dimensions: Transport, Home Energy, Food, and Shopping.
- **Personalising** the experience through lifestyle personas that pre-fill realistic baseline values.
- **Coaching** users with actionable, AI-generated sustainability advice tailored to their specific profile.
- **Motivating** behaviour change through gamified weekly challenges and a real-time Carbon Reduction Planner.

---

## 2. Solution Overview

EcoOrbit is a full-stack application with a **FastAPI (Python) backend** and a **vanilla HTML/CSS/JS frontend**, deployed on Google Cloud Run via Cloud Build.

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (Frontend)                    │
│  HTML5 + Vanilla CSS + Vanilla JS (no framework)        │
│  ┌──────────────┐ ┌─────────────┐ ┌──────────────────┐  │
│  │ Calculator   │ │ SVG Donut  │ │ EcoCoach Chat    │  │
│  │ (4 tabs)     │ │ Chart      │ │ (AI Assistant)   │  │
│  └──────────────┘ └─────────────┘ └──────────────────┘  │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS REST API
┌───────────────────────▼─────────────────────────────────┐
│                FastAPI Backend (Python)                  │
│  ┌────────────┐ ┌─────────────┐ ┌────────────────────┐  │
│  │ /api/      │ │ calculator  │ │ coach.py           │  │
│  │ persona    │ │ .py         │ │ (Gemini + fallback)│  │
│  │ /calculate │ │             │ │                    │  │
│  │ /coach     │ └─────────────┘ └────────────────────┘  │
│  └────────────┘                                          │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────▼───────────────┐
        │      Google Cloud Platform    │
        │  Cloud Run · Cloud Build      │
        │  Artifact Registry · Logging  │
        │  Secret Manager · Gemini API  │
        └───────────────────────────────┘
```

---

## 3. Google Services & Problem Statement Alignment

Every Google service used directly addresses the core problem of helping people understand and reduce their carbon footprint:

| Google Service | Problem Statement Alignment | Implementation Details |
|:---|:---|:---|
| **Gemini API (`gemini-2.0-flash`)** | **Personalised Insights:** Converts raw emissions data into human-readable, persona-specific coaching. Generates 3 actionable reduction tips with estimated CO₂ savings. | Uses the latest `google-genai` SDK (`google-genai>=1.0.0`). Enforces structured JSON output via `response_schema`, system instructions, and safety settings (`BLOCK_MEDIUM_AND_ABOVE` on all harm categories). Falls back to a local rules-based engine if the API is unavailable. |
| **Google Cloud Run** | **Scalable Usability:** Hosts the FastAPI backend as a serverless, auto-scaling HTTPS service. No infrastructure management required — the app scales to zero when idle and handles traffic spikes automatically. | Containerised with Docker, deployed via Cloud Build. Revision `ecoorbit-00015` serves 100% of traffic. Non-root user (`appuser`) runs the container for CIS Docker Benchmark compliance. |
| **Google Cloud Build** | **Maintainability & CI/CD:** Automates the full build → push → deploy pipeline. A single `gcloud builds submit` command builds the Docker image, pushes it to Artifact Registry, and deploys to Cloud Run. | Defined in `cloudbuild.yaml` with three steps: `docker build`, `docker push`, `gcloud run deploy`. Parameterised with substitution variables for region and repository flexibility. |
| **Google Artifact Registry** | **Operational Efficiency:** Stores versioned Docker container images in a private, regional registry (`us-central1`), feeding Cloud Run deployments with immutable, reproducible images. | Repository: `ecoorbit-repo`. Images tagged by `COMMIT_SHA` for traceability and rollback capability. |
| **Google Secret Manager** | **Security & Privacy:** Stores the Gemini API key outside of source code and environment files. The key never appears in logs, `git history`, or container layers. | Mounted as an environment variable in Cloud Run via `--update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest`. The service account requires only `roles/secretmanager.secretAccessor`. |
| **Google Cloud Logging** | **Reliability & Observability:** Captures structured application logs in production, including Gemini API fallback events, calculation errors, and startup diagnostics. Enables proactive monitoring via GCP Log Explorer. | Automatically initialised when `K_SERVICE` env var is detected (Cloud Run environment). Uses `google-cloud-logging` SDK with `client.setup_logging()`. |
| **Google Fonts & Material Symbols** | **Inclusive Design:** Delivers modern, accessible typography (`Outfit`, `Space Grotesk`) and scalable vector icons that remain crisp at all resolutions and work with screen reader text alternatives. | Loaded via `<link rel="preconnect">` for performance, with Material Symbols Outlined for semantic icons throughout the UI. |

---

## 4. Code Quality — Structure, Readability, Maintainability

EcoOrbit achieves a **perfect Pylint score of 10.00/10** across all six Python source files.

### Project Structure

```
eco-orbit/
├── main.py              # FastAPI app: routes, middleware, Pydantic models
├── calculator.py        # Pure calculation logic: emission factors, formulas
├── coach.py             # AI coach: Gemini SDK + rules-based fallback engine
├── requirements.txt     # Pinned dependencies
├── Dockerfile           # Secure, non-root containerisation
├── cloudbuild.yaml      # CI/CD pipeline definition
├── .env.example         # Environment variable template
├── static/
│   ├── index.html       # Semantic HTML5, single-page dashboard
│   ├── styles.css       # Design system: variables, components, utilities
│   └── app.js           # Frontend logic: state, API calls, DOM updates
└── tests/
    ├── test_api.py       # Integration tests: all API endpoints
    ├── test_calculator.py # Unit tests: all calculation categories
    └── test_coach.py     # Unit tests: fallback engine + Gemini mock
```

### Separation of Concerns

Each module has a **single, clearly defined responsibility**:

- **`calculator.py`** — Pure Python calculation functions with no I/O, side effects, or API calls. All emission factors are defined as module-level constants (`EMISSION_FACTORS`, `PERSONA_DEFAULTS`) for easy auditing and updating.
- **`coach.py`** — AI coach logic only. Structured with a `get_rule_based_advice()` fallback function and a `generate_coach_response()` orchestrator. A private `_build_genai_contents()` helper reduces function complexity.
- **`main.py`** — HTTP layer only: routes, Pydantic validation models, middleware, and static file mounting. Zero business logic.
- **`static/app.js`** — All DOM interaction via CSS class toggles (no `element.style.*`), no `innerHTML`, debounced API calls, and `localStorage`-based state persistence.

### Code Standards Applied

| Standard | Tool | Result |
|---|---|---|
| Code style | `black` | ✅ All files formatted |
| Import order | `isort` | ✅ All imports sorted |
| Code quality | `pylint` | ✅ **10.00 / 10** |
| Type hints | Manual | ✅ All function signatures typed |
| Docstrings | Manual | ✅ Every module, class, and function documented |
| Constants | Convention | ✅ `UPPER_CASE` module-level constants throughout |

### Pylint Score Evidence

```bash
$ python -m pylint calculator.py coach.py main.py tests/test_api.py tests/test_calculator.py tests/test_coach.py

--------------------------------------------------------------------
Your code has been rated at 10.00/10
```

---

## 5. Security — Safe and Responsible Implementation

Security is implemented in **layers** across every tier of the application.

### HTTP Security Headers (every response)

All headers are applied by a FastAPI middleware function in `main.py`, covering both API responses and static file responses:

```python
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self'; "                            # No inline scripts
    "style-src 'self' https://fonts.googleapis.com; " # No unsafe-inline styles
    "font-src 'self' https://fonts.gstatic.com; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self';"
)
response.headers["X-Frame-Options"] = "DENY"                         # Clickjacking
response.headers["X-Content-Type-Options"] = "nosniff"               # MIME sniffing
response.headers["X-XSS-Protection"] = "1; mode=block"               # Legacy XSS filter
response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
```

### Input Validation

All API inputs are validated by **Pydantic models with field-level constraints**:

```python
car_distance: float = Field(..., ge=0)        # Cannot be negative
recycling_pct: float = Field(..., ge=0, le=100) # Must be 0-100
clothing_items: int = Field(..., ge=0)         # Must be non-negative
```

Invalid input returns `HTTP 422 Unprocessable Entity` before reaching any business logic.

### XSS Prevention

The AI coach chat interface builds DOM nodes exclusively with safe DOM APIs — **`innerHTML` is never used**:

```javascript
const titleEl = document.createElement("strong");
titleEl.textContent = tip.title;  // textContent escapes all HTML
const descEl = document.createTextNode(tip.description);  // Text node — immune to injection
```

### Responsible AI (Gemini Safety Settings)

All four Gemini harm categories are blocked at `BLOCK_MEDIUM_AND_ABOVE`:

```python
GENAI_TYPES.SafetySetting(
    category=GENAI_TYPES.HarmCategory.HARM_CATEGORY_HARASSMENT,
    threshold=GENAI_TYPES.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
),
# + HATE_SPEECH, SEXUALLY_EXPLICIT, DANGEROUS_CONTENT
```

### Credential Security

- Gemini API key stored in **Google Secret Manager** — never in code, `.env`, or container layers
- CORS restricted to explicit origin list via environment variable (`ALLOWED_ORIGINS`)
- `.env` excluded from git via `.gitignore`

### Container Security

The Dockerfile runs the application as a **non-root system user** (`appuser`):

```dockerfile
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser
```

This prevents privilege escalation if the container is compromised — a CIS Docker Benchmark requirement.

---

## 6. Efficiency — Optimal Use of Resources

### Frontend Efficiency

| Technique | Detail |
|---|---|
| **Debounced API calls** | Slider input events fire recalculation with 250ms debounce — prevents flooding the server during dragging |
| **Client-side fallback** | Both the calculator and coach have full local JavaScript implementations. If the API is unavailable, users see zero disruption |
| **localStorage persistence** | User state (persona, inputs, points, actions) survives page refreshes without requiring a server round-trip |
| **CSS class toggling** | All UI state changes (show/hide modal, animations, active tabs) use `classList.add/remove` — no layout thrashing via inline `style` |
| **SVG chart** | The donut chart is pure inline SVG updated with `setAttribute` — no canvas redraws, no third-party charting library |
| **`<link rel="preconnect">`** | Google Fonts connections are pre-established, reducing font load latency |

### Backend Efficiency

| Technique | Detail |
|---|---|
| **Serverless (Cloud Run)** | Scales to zero when idle; no compute cost between requests |
| **StaticFiles mount** | Frontend assets served directly by FastAPI's StaticFiles — no separate web server needed |
| **Pure functions** | All calculator methods are `@staticmethod` with no state — trivially cacheable and side-effect free |
| **Gemini `gemini-2.0-flash`** | Fastest Gemini model: sub-second response times for coaching advice |
| **Chat history limited to last 6 turns** | Prevents unbounded token growth in multi-turn conversations (`chat_history[-6:]`) |
| **Pydantic model validation** | Input validation runs before any computation, failing fast on invalid data |

### Build Efficiency

- Docker image uses `python:3.11-slim` base — minimal attack surface and fast pull times
- `--no-cache-dir` in `pip install` prevents unnecessary cache files in the image layer
- Cloud Build caches Docker layers between builds, dramatically reducing rebuild times

---

## 7. Testing — Validation of Functionality

EcoOrbit has **18 automated tests** covering integration, unit, and mock-based scenarios.

### Test Results

```
$ python -m pytest tests/ -v

tests/test_api.py::test_get_persona_defaults_success        PASSED
tests/test_api.py::test_get_persona_defaults_not_found      PASSED
tests/test_api.py::test_calculate_footprint_success         PASSED
tests/test_api.py::test_calculate_footprint_invalid_data    PASSED
tests/test_api.py::test_get_coach_advice_mocked             PASSED
tests/test_api.py::test_response_security_headers           PASSED  ← verifies all 7 security headers
tests/test_calculator.py::test_calculate_transport_basic    PASSED
tests/test_calculator.py::test_calculate_transport_zero     PASSED
tests/test_calculator.py::test_calculate_home_basic         PASSED
tests/test_calculator.py::test_calculate_food_diets         PASSED
tests/test_calculator.py::test_calculate_consumption_basic  PASSED
tests/test_calculator.py::test_calculate_total_wrapper      PASSED
tests/test_coach.py::test_fallback_advice_transport_highest PASSED
tests/test_coach.py::test_fallback_advice_home_highest      PASSED
tests/test_coach.py::test_fallback_advice_food_highest      PASSED
tests/test_coach.py::test_fallback_advice_consumption_highest PASSED
tests/test_coach.py::test_generate_coach_response_fallback_no_key PASSED
tests/test_coach.py::test_generate_coach_response_gemini_success  PASSED

======================== 18 passed in 0.97s ========================
```

### Test Coverage by Area

| Test File | What's Tested |
|---|---|
| `test_api.py` | All 3 API endpoints, 404 handling, Pydantic validation rejection (422), all 7 HTTP security headers verified by name and value |
| `test_calculator.py` | All 4 emission categories (transport, home, food, consumption), zero-value edge cases, all 5 diet types, recycling offset logic, `calculate_total()` wrapper |
| `test_coach.py` | All 4 fallback advice branches (one per highest category), graceful degradation when Gemini is disabled, successful Gemini response parsing via mock client |

### Testing Approach

- **Integration tests** (`test_api.py`) use FastAPI's `TestClient` to exercise real HTTP request/response cycles including middleware.
- **Unit tests** (`test_calculator.py`) call pure functions directly with known inputs and assert exact outputs.
- **Mock-based tests** (`test_coach.py`) use `unittest.mock.patch` to simulate both the disabled-Gemini path and a successful Gemini API response, without requiring a real API key in CI.

---

## 8. Accessibility — Inclusive and Usable Design

EcoOrbit targets **WCAG 2.1 Level AA** compliance throughout.

### Semantic HTML Structure

```html
<html lang="en">                  <!-- WCAG 3.1.1: Language of Page -->
  <head>
    <meta name="theme-color">     <!-- Mobile browser UI adaptation -->
    <meta name="color-scheme" content="dark">
  </head>
  <body>
    <a class="skip-link" href="#main-content">Skip to main content</a>  <!-- WCAG 2.4.1 -->
    <header role="banner">…</header>
    <main id="main-content">…</main>  <!-- Skip link target -->
    <footer>…</footer>
  </body>
```

- **Single `<h1>`** per page (`EcoOrbit` in the header) with logical `<h2>` → `<h3>` → `<h4>` hierarchy
- **Semantic sectioning**: `<header>`, `<main>`, `<section>`, `<article>`, `<footer>` used throughout
- **Decorative elements** marked `aria-hidden="true"` (ambient glows, spinning icons)

### ARIA Enhancements

| Element | ARIA Attribute | Purpose |
|---|---|---|
| Onboarding modal | `role="dialog"`, `aria-modal="true"`, `aria-labelledby` | Screen readers announce modal context |
| Tab buttons | `role="tab"`, `aria-selected`, `aria-controls` | Full ARIA tablist pattern |
| Tab panels | `role="tabpanel"`, `aria-labelledby` | Associates panels with their tabs |
| SVG chart | `role="img"`, `aria-label` | Describes chart to screen readers |
| Chat window | `role="log"`, `aria-live="polite"` | Announces new coach messages |
| Metrics section | `aria-live="polite"`, `aria-atomic="false"` | Announces updated footprint values |
| All buttons | `aria-label` on icon-only buttons | Descriptive labels for screen readers |
| Checkboxes | `aria-label` on all action items | Describes each commitment |

### Keyboard Navigation

- **Skip-to-main-content link**: visible on first Tab press — slides in from the top (`WCAG 2.4.1 Bypass Blocks`)
- **Tab order**: logical left-to-right, top-to-bottom throughout the app
- **Arrow key navigation** on calculator tabs: Left/Right arrows move between Transport, Home, Food, Shopping tabs (WCAG ARIA tablist pattern)
- **Escape key**: closes the persona modal (only when a profile has been saved)
- **Modal focus management**: onboarding modal auto-focuses the first persona button on open
- **`:focus-visible`** rings on all interactive elements — buttons, inputs, selects, range sliders, and checkboxes

### Visual Accessibility

| Standard | Implementation |
|---|---|
| **Colour contrast (WCAG 1.4.3)** | Muted text `#8ea0be` on `#0b0f19` background: contrast ratio **5.1:1** (minimum: 4.5:1 ✅) |
| **No colour-only information** | Chart segments use both colour AND legend text labels |
| **Focus visible (WCAG 2.4.7)** | Emerald `2px` outline on all interactive elements; `outline:none` removed from persona cards |
| **Range slider focus** | `input[type="range"]:focus-visible` provides keyboard-visible focus ring |
| **Responsive layout** | CSS Grid collapses to single column at `≤900px` viewport |
| **Animations respect preferences** | Animations are subtle and non-flickering; no strobing effects |

---

## 9. Chosen Verticals (Personas)

EcoOrbit introduces three onboarding lifestyle profiles to personalise the experience:

### 🏙️ Urban Commuter (Aria)
- Relies on public transit and ridesharing; rents an apartment
- Small home energy footprint, higher transit mileage, vegetarian diet
- **Focus**: Eco-friendly shopping, digital consumption, minor travel tweaks

### 🏡 Suburban Homeowner (Marcus)
- Daily car commuter, single-family home, family cooking, average meat diet
- Large home energy and car footprints
- **Focus**: Smart thermostat, LED lighting, carpooling

### ✈️ Global Jetsetter (Sofia)
- Frequent air traveller, hotel stays, high-impact diet, premium shopping
- Extreme transport footprint dominated by flight hours
- **Focus**: Aviation offsets, circular fashion, voluntary carbon credits

---

## 10. Calculation Methodology

All emission factors are sourced from the **US EPA** and **UK DEFRA** standard datasets.

### Transport (kg CO₂e / month)
| Mode | Factor |
|---|---|
| Petrol car | 0.18 kg CO₂e / km |
| Diesel car | 0.17 kg CO₂e / km |
| Hybrid car | 0.10 kg CO₂e / km |
| Electric car | 0.05 kg CO₂e / km |
| Public transit | 0.03 kg CO₂e / km |
| Flights | 90.0 kg CO₂e / flight-hour |

### Home Energy (kg CO₂e / month)
| Source | Factor |
|---|---|
| Electricity | 0.38 kg CO₂e / kWh |
| Natural gas | 0.18 kg CO₂e / kWh |
| Waste | 0.50 kg CO₂e / kg (reduced by recycling rate × 50%) |

### Food/Diet (kg CO₂e / month — 30-day scale)
| Diet | Daily Factor |
|---|---|
| High meat | 7.2 kg CO₂e / day |
| Medium meat | 4.5 kg CO₂e / day |
| Low meat | 3.0 kg CO₂e / day |
| Vegetarian | 2.0 kg CO₂e / day |
| Vegan | 1.5 kg CO₂e / day |

### Shopping/Consumption (kg CO₂e / month)
| Item | Factor |
|---|---|
| Clothing item | 10 kg CO₂e / garment |
| Electronics device | 150 kg CO₂e / device |
| Recycling offset | Up to –10% of shopping total |

---

## 11. Developer Setup Guide

### Prerequisites
- Python 3.10+
- Gemini API Key (optional — app falls back gracefully without one)

### Local Setup

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1
# Activate (Mac/Linux)
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here

# 5. Start the application
python main.py

# 6. Open browser
# http://127.0.0.1:8000
```

### Run Tests

```bash
python -m pytest tests/ -v
# Expected: 18 passed
```

### Code Quality Checks

```bash
# Sort imports
python -m isort .

# Format code
python -m black .

# Lint (target: 10.00/10)
python -m pylint calculator.py coach.py main.py tests/test_api.py tests/test_calculator.py tests/test_coach.py
```

---

## 12. GCP Deployment Guide

### Enable Required APIs

```bash
gcloud services enable run.googleapis.com \
                       cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com \
                       secretmanager.googleapis.com
```

### Create Artifact Registry Repository

```bash
gcloud artifacts repositories create ecoorbit-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="EcoOrbit Container Images"
```

### Store Gemini API Key in Secret Manager

```bash
# Create the secret
echo -n "your_api_key_here" | gcloud secrets create GEMINI_API_KEY \
    --data-file=- \
    --replication-policy="automatic"

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
    --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Deploy via Cloud Build

```bash
# Build, push, and deploy in one command
gcloud builds submit --config=cloudbuild.yaml

# Bind secret to Cloud Run
gcloud run services update ecoorbit \
    --update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest \
    --region=us-central1
```

---

## Summary Scorecard

| Dimension | Achievement |
|---|---|
| **Code Quality** | Pylint **10.00/10** · black compliant · isort compliant · full type hints · docstrings on every function |
| **Security** | 7 HTTP security headers · strict CSP (no `unsafe-inline`) · HSTS preload · non-root Docker user · Secret Manager · Pydantic input validation · no `innerHTML` |
| **Efficiency** | Debounced API calls · client-side fallbacks · localStorage state · `gemini-2.0-flash` · serverless Cloud Run · slim Docker base |
| **Testing** | **18/18 tests passing** · integration + unit + mock-based · security headers verified in tests |
| **Accessibility** | WCAG 2.1 AA · skip link · `lang="en"` · ARIA roles · keyboard nav · 5.1:1 contrast · focus-visible on all inputs |
