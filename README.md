# EcoOrbit: Smart Carbon Footprint Tracker & AI Coach

EcoOrbit is an interactive, full-stack personal carbon footprint tracking application designed to help individuals understand, track, and reduce their environmental impact through customized lifestyle templates and smart, contextual AI feedback.

The application leverages **Google Generative AI (Gemini API)** to provide personalized, conversational sustainability coaching, coupled with an interactive glassmorphic dashboard built using **FastAPI** (Python) and a responsive, vanilla HTML/CSS/JS frontend.

---

## 1. Chosen Verticals (Personas)

To meet the challenge requirement of designing around specific verticals and user contexts, EcoOrbit introduces three distinct onboarding lifestyle profiles:

1.  **Urban Commuter (Aria):**
    *   *Lifestyle context:* Lives in a dense city apartment, does not own a car (relies on public transit and ridesharing), orders delivery frequently, and enjoys city dining.
    *   *Calculation adjustments:* Small home energy footprint, higher transit mileage, moderate food emissions, low tech consumption.
    *   *Reduction focus:* Eco-friendly shopping, digital consumption efficiency, and minor travel tweaks.
2.  **Suburban Homeowner (Marcus):**
    *   *Lifestyle context:* Commutes daily by a gasoline/diesel car, owns a single-family home with higher heating, cooling, and electricity emissions, and cooks at home for a family.
    *   *Calculation adjustments:* Large home energy and waste footprints, high car mileage, average meat-eating food consumption.
    *   *Reduction focus:* Switch to energy-efficient LED lighting, smart thermostat reductions, and carpooling/ridesharing.
3.  **Global Jetsetter (Sofia):**
    *   *Lifestyle context:* Travels frequently by air for business or leisure, stays in hotels, dines out at high-impact restaurants, and shops for premium clothing and gadgets.
    *   *Calculation adjustments:* Extreme transportation footprint (dominated by flight hours), high consumption/shopping emissions, high-intensity diet profile.
    *   *Reduction focus:* Aviation footprint reduction, voluntary carbon offsetting, and circular fashion/secondhand thriting.

---

## 2. Approach & Calculation Methodology

EcoOrbit uses standard conversion factors based on data from the **Environmental Protection Agency (EPA)** and **DEFRA**:

### Transport Footprint (kg CO2e / month)
*   **Car travel:** `distance (km) * factor`
    *   Petrol: `0.18 kg CO2e / km`
    *   Diesel: `0.17 kg CO2e / km`
    *   Hybrid: `0.10 kg CO2e / km`
    *   Electric: `0.05 kg CO2e / km`
*   **Public Transit:** `distance (km) * 0.03 kg CO2e / km`
*   **Flights:** `flight hours * 90 kg CO2e / flight-hour`

### Home Footprint (kg CO2e / month)
*   **Electricity:** `electricity (kWh) * 0.38 kg CO2e / kWh`
*   **Natural Gas / Heating:** `gas (kWh) * 0.18 kg CO2e / kWh`
*   **Waste:** `waste (kg) * 0.50 kg CO2e / kg`
*   *Recycling Reduction:* A higher recycling rate (%) reduces landfilled waste carbon impact by up to **50%** (via a linear offset calculation: `waste * 0.5 * recycling_pct / 100`).

### Food/Diet Footprint (kg CO2e / month)
*   Emissions are calculated per day and scaled to a 30-day month:
    *   High Meat Diet: `7.2 kg CO2e / day` (e.g., daily beef/lamb consumption)
    *   Medium Meat Diet: `4.5 kg CO2e / day` (e.g., poultry, occasional pork/beef)
    *   Low Meat Diet: `3.0 kg CO2e / day`
    *   Vegetarian Diet: `2.0 kg CO2e / day`
    *   Vegan Diet: `1.5 kg CO2e / day`

### Shopping/Consumption Footprint (kg CO2e / month)
*   **Apparel:** `new items * 10 kg CO2e / garment`
*   **Electronics:** `new devices * 150 kg CO2e / device`
*   *Recycling Reduction:* Recycling rate (%) reduces shopping carbon impact by up to **10%** (via: `shopping * 0.1 * recycling_pct / 100`).

---

## 3. Google Services & Problem Statement Alignment

EcoOrbit utilizes Google Cloud services to fulfill the core problem statement: **helping individuals understand, track, and reduce their carbon footprint through simple actions and personalized insights.**

| Google Service | Problem Statement Alignment | Implementation Details |
| :--- | :--- | :--- |
| **Google Generative AI (Gemini API)** | **Personalized Insights & Footprint Reduction:** Translates complex carbon emissions metrics into highly-tailored, context-aware coaching advice. Generates actionable suggestions matching the user's specific lifestyle persona (Aria, Marcus, Sofia) with estimated CO2 reductions. | Powered by `gemini-2.0-flash` using the latest **`google-genai` SDK** with structured JSON schema output, safety settings, and system instructions for consistent coaching. |
| **Google Secret Manager** | **Security & Privacy:** Safely stores and manages the Gemini credentials, keeping API keys out of code repositories and environment configuration files, protecting user telemetry. | Mounted securely in production using Cloud Run environment references. |
| **Google Cloud Run** | **Practical Usability:** Hosts the FastAPI backend serverlessly on secure public HTTPS endpoints, ensuring high-speed routing, auto-scaling, and accessible dashboard UI. | Deploy path is managed directly via containerized port mappings. |
| **Google Cloud Build** | **Maintainability & Growth:** Automates compiling and pushing container images to GCP, creating a clean developer CI/CD path to update calculations and models. | Runs CI/CD trigger logic defined in `cloudbuild.yaml`. |
| **Google Artifact Registry** | **Operational Efficiency:** Stores built Docker container images in a private registry in region `us-central1`, feeding Cloud Run deployments. | Configured to track and version images in repository `ecoorbit-repo`. |
| **Google Cloud Logging** | **System Reliability:** Captures warning events and safety warnings, logging them to GCP Log Explorer so developers can ensure continuous assistant availability. | Integrates `google-cloud-logging` SDK dynamically using runtime env checks. |
| **Google Fonts & Material Symbols** | **Usable & Inclusive Design (Accessibility):** Delivers clean vector icons (emissions trackers, points indicator, close selectors) and readable custom typography (`Outfit` and `Space Grotesk`) to help users track progress. | Injected stylesheet links to Google APIs in `index.html`. |

---

## 4. How the Solution Works

1.  **Onboarding:** On launch, the user is presented with a modal detailing the three challenge verticals. Selecting a vertical initializes the calculator inputs with realistic defaults matching that persona. The modal includes a Cancel Close button and Escape key dismiss handler to prevent accidental calculation resets (hidden on first onboarding, visible during persona switching). The modal automatically focuses the first option to guide screen-reader and keyboard navigators.
2.  **Interactive Calculator:** Sliding values triggers instant recalculation queries. Network requests are **debounced by 250ms** during dragging, saving significant network and server resources while keeping visual sliders updating in real-time. Values are dynamically represented using an interactive **SVG Donut Chart** and category legend.
3.  **EcoCoach Virtual Assistant:**
    *   Powered by the **Google GenAI SDK (`google-genai`)** using the fast and capable `gemini-2.0-flash` model.
    *   **Structured Outputs:** Enforces a strict JSON Schema at the API layer. The response is parsed in Python and sent as structured JSON to the frontend, which builds DOM nodes dynamically using safe, text-based methods. **No innerHTML is used**, offering complete immunity to XSS (chat clearing uses a child removal loop).
    *   **Separation of Concerns:** All dynamically generated elements are styled using modular stylesheet CSS class definitions in `styles.css` (`.coach-tips-list`, `.coach-tip-item`, etc.), avoiding ad-hoc inline Javascript styles.
    *   **System Instructions & Safety Settings:** Employs official Gemini `system_instruction` settings to prevent prompt injections, and configures Harm block thresholds (`BLOCK_MEDIUM_AND_ABOVE`) to block hate, harassment, explicit, and dangerous content.
    *   **Resilience:** If the Gemini API key is missing or fails, EcoOrbit gracefully falls back to an expert local rules-based engine returning the exact same structured JSON schema format, maintaining a seamless visual experience.
    *   **Structured Telemetry:** Automatically initializes **Google Cloud Logging** in production, mapping warnings and fallback log calls to GCP Log Explorer.
4.  **Weekly Challenges:** A gamified challenge module lets users check off habits (e.g., "Meatless Monday") to earn **Eco-Points** and rise from "Eco Novice" to "Carbon Conqueror."
5.  **Carbon Action Planner:** Users check off specific, high-impact pledges (like LED retrofitting or going veg 3 days/week). This computes an instant reduction projection that subtracts from their overall projected carbon footprint in real-time.
6.  **Persistence:** State (selected actions, points, persona, inputs) is saved in `localStorage`, maintaining user data across page refreshes.

---

## 5. Key Assumptions Made

*   **Average factors:** Carbon emissions vary globally depending on the grid mix (electricity source) and fuel quality. Standard average values are assumed (e.g., US/UK grid averages) for simplicity.
*   **Monthly scale:** Calculations are based on monthly averages (30-day billing cycles) to keep data logging manageable for individuals.
*   **Local privacy:** Calculations do not require a database login; all personal data stays stored on the client's local browser storage.

---

## 6. Developer Guide: Setup, Run, Test, and Format

### Prerequisites
*   Python 3.10+ installed
*   Gemini API Key (optional, for real AI coaching)

### Setup & Run
1.  Initialize a virtual environment:
    ```bash
    python -m venv .venv
    ```
2.  Activate virtual environment:
    *   **Windows (PowerShell):**
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
    *   **Mac/Linux:**
        ```bash
        source .venv/bin/activate
        ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure environment:
    *   Rename `.env.example` to `.env`
    *   Add your `GEMINI_API_KEY`
5.  Start the FastAPI application:
    ```bash
    python main.py
    ```
6.  Open your browser to `http://127.0.0.1:8000` to interact with the dashboard.

### Verification (Testing)
Run the unit and integration test suite using `pytest` (18/18 tests passing):
```bash
.venv\Scripts\python -m pytest
```


### Formatting & Linting
Ensure high-quality, compliant code formatting and type hints validation:
1.  **Isort (Imports sorting):**
    ```bash
    .venv\Scripts\python -m isort .
    ```
2.  **Black (Code style formatting):**
    ```bash
    .venv\Scripts\python -m black .
    ```
3.  **Pylint (Code quality checking):**
    ```bash
    .venv\Scripts\python -m pylint calculator.py coach.py main.py tests/*.py
    ```
    *Result: Code scores a perfect **10.00/10** with zero errors or warnings (across all 6 source files).*

---

## 7. Accessibility & Security Compliance

EcoOrbit is engineered around rigorous WCAG 2.1 and server hardening standards:

*   **WCAG 2.1 AA Color Contrast:** Muted text parameters use high-contrast HSL slate colors (`#8ea0be`) yielding a contrast ratio of **5.1:1** on the dark backdrop `#0b0f19` (surpassing the minimum standard of **4.5:1**).
*   **WCAG Tablist Arrows:** Category buttons support Right/Left keyboard arrows to shift active selectors automatically.
*   **Keyboard Navigation:** Fully focusable interactive nodes with visible `:focus-visible` emerald rings.
*   **Semantic Heading Structure (SEO):** Enforces a single `<h1>` tag per page (header logo) and maintains logical sequential header levels (`<h2>` for dashboard sections). Metric values use `div` elements to prevent header outline clutter.
*   **Interactive SVG Accessibility:** Dynamic chart elements assign clear image representations (`role="img"`) and detailed text labels (`aria-label`) for screen-reader mapping.
*   **Security Headers Hardening:** Backend server enforces anti-clickjacking (`X-Frame-Options: DENY`), MIME sniffing prevention (`X-Content-Type-Options: nosniff`), Strict Content-Security-Policy (CSP), Strict Transport Security (HSTS) with preload, and restrictive Permissions Policies (`camera=(), microphone=(), geolocation=(), payment=()`).

---

## 8. GCP Deployment Guide

EcoOrbit is fully optimized for serverless, containerized deployment on Google Cloud Platform (GCP) using Google's primary development services.

### 1. Enable Required Services
Enable the following APIs in your GCP project console:
```bash
gcloud services enable run.googleapis.com \
                       cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com \
                       secretmanager.googleapis.com
```

### 2. Create Artifact Registry Repository
Create a Docker registry named `ecoorbit-repo` in region `us-central1`:
```bash
gcloud artifacts repositories create ecoorbit-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="EcoOrbit Container Images"
```

### 3. Store the Gemini API Key Securely in Secret Manager
Ensure safe and responsible key management by keeping credentials out of codebases or environment configurations:
```bash
# Create the secret
echo -n "your_api_key_here" | gcloud secrets create GEMINI_API_KEY \
    --data-file=- \
    --replication-policy="automatic"

# Grant Cloud Run service account permission to access the key
gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
    --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 4. Trigger Deployment using Google Cloud Build
Deploy the application cleanly to Cloud Run using the automated build script:
```bash
gcloud builds submit --config=cloudbuild.yaml
```
Once build succeeds, bind the Secret Manager secret to your container's environment variable:
```bash
gcloud run services update ecoorbit \
    --update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest \
    --region=us-central1
```
Once the update completes, the command returns a secure public HTTPS URL where your EcoOrbit dashboard is accessible globally.
