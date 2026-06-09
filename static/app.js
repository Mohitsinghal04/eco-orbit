// ECOORBIT FRONTEND STATE & LOGIC

const STATE_KEY = "ecoorbit_state";

// Default local state (restored from localStorage if available)
let appState = {
  persona: "urban_commuter",
  ecoPoints: 0,
  completedChallenges: [],
  selectedActions: [],
  emissions: {
    transport: 0,
    home: 0,
    food: 0,
    consumption: 0,
    total: 0
  },
  chatHistory: []
};

// Hardcoded defaults as local fallback if API fails
const LOCAL_PERSONA_DEFAULTS = {
  urban_commuter: {
    car_distance: 100,
    car_fuel: "car_hybrid",
    transit_distance: 600,
    flight_hours: 1,
    electricity_kwh: 150,
    gas_kwh: 100,
    waste_kg: 15,
    diet_type: "diet_vegetarian",
    clothing_items: 2,
    electronics_items: 0,
    recycling_pct: 75
  },
  suburban_homeowner: {
    car_distance: 1200,
    car_fuel: "car_petrol",
    transit_distance: 50,
    flight_hours: 2,
    electricity_kwh: 450,
    gas_kwh: 600,
    waste_kg: 40,
    diet_type: "diet_medium_meat",
    clothing_items: 4,
    electronics_items: 1,
    recycling_pct: 50
  },
  global_jetsetter: {
    car_distance: 300,
    car_fuel: "car_diesel",
    transit_distance: 100,
    flight_hours: 15,
    electricity_kwh: 250,
    gas_kwh: 200,
    waste_kg: 25,
    diet_type: "diet_high_meat",
    clothing_items: 8,
    electronics_items: 2,
    recycling_pct: 30
  }
};

// DOM Elements
const onboardingModal = document.getElementById("onboarding-modal");
const changePersonaBtn = document.getElementById("change-persona-btn");
const activePersonaText = document.getElementById("active-persona-text");

// Metric display nodes
const metricTotalFootprint = document.getElementById("metric-total-footprint");
const metricProjectedReduction = document.getElementById("metric-projected-reduction");
const metricEcoPoints = document.getElementById("metric-eco-points");
const metricRank = document.getElementById("metric-rank");

// SVG Segment nodes
const chartCenterVal = document.getElementById("chart-center-val");

// Chat nodes
const chatMessages = document.getElementById("chat-messages");
const chatInputForm = document.getElementById("chat-input-form");
const chatInputText = document.getElementById("chat-input-text");

// Initialize application
document.addEventListener("DOMContentLoaded", () => {
  loadState();
  initUIListeners();
  
  // If no onboarding history, open modal
  if (!localStorage.getItem(STATE_KEY)) {
    showOnboarding();
  } else {
    // Apply state and recalculate
    applyPersonaUI();
    recalculateEmissions();
    updatePointsUI();
    updateActionsUI();
    hideOnboarding();
  }
});

// Load state from localStorage
function loadState() {
  const saved = localStorage.getItem(STATE_KEY);
  if (saved) {
    try {
      appState = { ...appState, ...JSON.parse(saved) };
    } catch (e) {
      console.error("Failed to parse local state", e);
    }
  }
}

// Save state to localStorage
function saveState() {
  localStorage.setItem(STATE_KEY, JSON.stringify(appState));
}

// Show onboarding modal
function showOnboarding() {
  onboardingModal.classList.remove("hidden");
  onboardingModal.setAttribute("aria-hidden", "false");
  
  // Show close button only if user has already saved a profile (not first launch)
  const closeBtn = document.getElementById("modal-close-btn");
  if (closeBtn) {
    if (localStorage.getItem(STATE_KEY)) {
      closeBtn.classList.remove("hidden");
    } else {
      closeBtn.classList.add("hidden");
    }
  }
  
  // Set focus on first interactive button inside the modal for accessibility
  const firstBtn = document.getElementById("btn-urban-commuter");
  if (firstBtn) {
    firstBtn.focus();
  }
}

// Hide onboarding modal
function hideOnboarding() {
  onboardingModal.classList.add("hidden");
  onboardingModal.setAttribute("aria-hidden", "true");
}

// Setup Onboarding Button Actions & Sliders
function initUIListeners() {
  // Close onboarding button
  const closeBtn = document.getElementById("modal-close-btn");
  if (closeBtn) {
    closeBtn.addEventListener("click", hideOnboarding);
  }

  // Escape key handler to close onboarding
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !onboardingModal.classList.contains("hidden")) {
      // Only close if user has a profile saved
      if (localStorage.getItem(STATE_KEY)) {
        hideOnboarding();
      }
    }
  });

  // Keyboard Arrow navigation on tab buttons list for WCAG tablist compliance
  const tabContainer = document.querySelector(".tab-buttons");
  if (tabContainer) {
    tabContainer.addEventListener("keydown", (e) => {
      const tabBtns = Array.from(document.querySelectorAll(".tab-btn"));
      const activeIdx = tabBtns.findIndex(b => b.classList.contains("active"));
      let targetIdx = -1;
      
      if (e.key === "ArrowRight") {
        targetIdx = (activeIdx + 1) % tabBtns.length;
      } else if (e.key === "ArrowLeft") {
        targetIdx = (activeIdx - 1 + tabBtns.length) % tabBtns.length;
      }
      
      if (targetIdx !== -1) {
        tabBtns[targetIdx].click();
        tabBtns[targetIdx].focus();
        e.preventDefault();
      }
    });
  }

  // Persona button selectors
  document.getElementById("btn-urban-commuter").addEventListener("click", () => selectPersona("urban_commuter"));
  document.getElementById("btn-suburban-homeowner").addEventListener("click", () => selectPersona("suburban_homeowner"));
  document.getElementById("btn-global-jetsetter").addEventListener("click", () => selectPersona("global_jetsetter"));
  
  changePersonaBtn.addEventListener("click", showOnboarding);

  // Tab switching
  const tabs = ["transport", "home", "food", "shopping"];
  tabs.forEach(tab => {
    const btn = document.getElementById(`tab-btn-${tab}`);
    btn.addEventListener("click", () => {
      // Toggle buttons and update accessibility attributes
      document.querySelectorAll(".tab-btn").forEach(b => {
        b.classList.remove("active");
        b.setAttribute("aria-selected", "false");
      });
      btn.classList.add("active");
      btn.setAttribute("aria-selected", "true");
      
      // Toggle panels
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      document.getElementById(`tab-${tab}`).classList.add("active");
    });
  });

  // Slider inputs value syncing & auto-calculation
  const sliders = [
    { id: "input-car-distance", bubble: "val-car-distance", suffix: " km" },
    { id: "input-transit-distance", bubble: "val-transit-distance", suffix: " km" },
    { id: "input-flight-hours", bubble: "val-flight-hours", suffix: " hrs" },
    { id: "input-electricity-kwh", bubble: "val-electricity-kwh", suffix: " kWh" },
    { id: "input-gas-kwh", bubble: "val-gas-kwh", suffix: " kWh" },
    { id: "input-waste-kg", bubble: "val-waste-kg", suffix: " kg" },
    { id: "input-recycling-pct", bubble: "val-recycling-pct", suffix: "%" },
    { id: "input-clothing-items", bubble: "val-clothing-items", suffix: " items" },
    { id: "input-electronics-items", bubble: "val-electronics-items", suffix: " devices" }
  ];

  const debouncedRecalculate = debounce(recalculateEmissions, 250);

  sliders.forEach(slider => {
    const el = document.getElementById(slider.id);
    const bubble = document.getElementById(slider.bubble);
    el.addEventListener("input", () => {
      bubble.textContent = el.value + slider.suffix;
      debouncedRecalculate();
    });
  });

  // Select dropdowns
  document.getElementById("input-car-fuel").addEventListener("change", recalculateEmissions);
  document.getElementById("input-diet-type").addEventListener("change", recalculateEmissions);

  // Chat submission
  chatInputForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const query = chatInputText.value.trim();
    if (!query) return;
    sendMessage(query);
    chatInputText.value = "";
  });

  // Prompt chips
  document.querySelectorAll(".chip-btn").forEach(chip => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-prompt");
      sendMessage(prompt);
    });
  });

  // Challenges complete
  document.querySelectorAll(".complete-challenge-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-target");
      const pts = parseInt(btn.getAttribute("data-points"), 10);
      completeChallenge(target, pts);
    });
  });

  // Action Planner checklists
  document.querySelectorAll(".reduction-checkbox").forEach(box => {
    box.addEventListener("change", () => {
      updateProjectedReductions();
    });
  });
}

// Handle persona selection
async function selectPersona(personaId) {
  appState.persona = personaId;
  hideOnboarding();
  applyPersonaUI();
  
  // Load defaults from FastAPI backend
  try {
    const response = await fetch(`/api/persona/${personaId}`);
    if (!response.ok) throw new Error("API error");
    const defaults = await response.json();
    populateForm(defaults);
  } catch (error) {
    console.warn("FastAPI persona fetch failed. Using local fallback defaults:", error);
    populateForm(LOCAL_PERSONA_DEFAULTS[personaId]);
  }
  
  // Calculate and reset chatbot context
  recalculateEmissions();
  appState.chatHistory = [];
  while (chatMessages.firstChild) {
    chatMessages.removeChild(chatMessages.firstChild);
  }
  appendCoachBubble("I've initialized your profile. What would you like to know about your footprint?");
  saveState();
}

// Display persona in Header
function applyPersonaUI() {
  const pName = appState.persona.replace("_", " ").toUpperCase();
  activePersonaText.textContent = `Persona: ${pName}`;
}

// Populate calculator sliders with values
function populateForm(data) {
  const fields = [
    { id: "input-car-distance", bubble: "val-car-distance", suffix: " km" },
    { id: "input-transit-distance", bubble: "val-transit-distance", suffix: " km" },
    { id: "input-flight-hours", bubble: "val-flight-hours", suffix: " hrs" },
    { id: "input-electricity-kwh", bubble: "val-electricity-kwh", suffix: " kWh" },
    { id: "input-gas-kwh", bubble: "val-gas-kwh", suffix: " kWh" },
    { id: "input-waste-kg", bubble: "val-waste-kg", suffix: " kg" },
    { id: "input-recycling-pct", bubble: "val-recycling-pct", suffix: "%" },
    { id: "input-clothing-items", bubble: "val-clothing-items", suffix: " items" },
    { id: "input-electronics-items", bubble: "val-electronics-items", suffix: " devices" }
  ];

  fields.forEach(field => {
    const val = data[field.id.replace("input-", "").replace("-", "_")];
    const el = document.getElementById(field.id);
    const bubble = document.getElementById(field.bubble);
    if (el && bubble) {
      el.value = val !== undefined ? val : 0;
      bubble.textContent = el.value + field.suffix;
    }
  });

  // Populate dropdown selects
  if (data.car_fuel) document.getElementById("input-car-fuel").value = data.car_fuel;
  if (data.diet_type) document.getElementById("input-diet-type").value = data.diet_type;
}

// Serialize current form inputs
function serializeForm() {
  return {
    car_distance: parseFloat(document.getElementById("input-car-distance").value),
    car_fuel: document.getElementById("input-car-fuel").value,
    transit_distance: parseFloat(document.getElementById("input-transit-distance").value),
    flight_hours: parseFloat(document.getElementById("input-flight-hours").value),
    electricity_kwh: parseFloat(document.getElementById("input-electricity-kwh").value),
    gas_kwh: parseFloat(document.getElementById("input-gas-kwh").value),
    waste_kg: parseFloat(document.getElementById("input-waste-kg").value),
    recycling_pct: parseFloat(document.getElementById("input-recycling-pct").value),
    diet_type: document.getElementById("input-diet-type").value,
    clothing_items: parseInt(document.getElementById("input-clothing-items").value, 10),
    electronics_items: parseInt(document.getElementById("input-electronics-items").value, 10)
  };
}

// Send inputs to backend and update visual stats
async function recalculateEmissions() {
  const formData = serializeForm();
  
  try {
    const response = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });
    if (!response.ok) throw new Error("API calculation error");
    
    const results = await response.json();
    appState.emissions = results;
  } catch (error) {
    console.warn("Calculations API failed. Running local fallback calculation formulas:", error);
    appState.emissions = runLocalCalculations(formData);
  }
  
  updateEmissionsUI();
  updateProjectedReductions();
  saveState();
}

// Local carbon calculation logic for robust client-side fallback
function runLocalCalculations(data) {
  const factors = {
    car_petrol: 0.18, car_diesel: 0.17, car_electric: 0.05, car_hybrid: 0.10,
    public_transit: 0.03, flight_hour: 90.0, electricity_kwh: 0.38,
    gas_kwh: 0.18, waste_kg: 0.50, diet_vegan: 1.5, diet_vegetarian: 2.0,
    diet_low_meat: 3.0, diet_medium_meat: 4.5, diet_high_meat: 7.2,
    clothing_item: 10.0, electronics_item: 150.0
  };

  const carFactor = factors[data.car_fuel] || factors.car_petrol;
  const transport = (data.car_distance * carFactor) + (data.transit_distance * factors.public_transit) + (data.flight_hours * factors.flight_hour);
  
  const wasteEmissions = data.waste_kg * factors.waste_kg;
  const recycleOffset = (data.recycling_pct / 100) * 0.5 * wasteEmissions;
  const home = (data.electricity_kwh * factors.electricity_kwh) + (data.gas_kwh * factors.gas_kwh) + Math.max(0, wasteEmissions - recycleOffset);

  const dietFactor = factors[data.diet_type] || factors.diet_medium_meat;
  const food = dietFactor * 30.0;

  const clothesCost = data.clothing_items * factors.clothing_item;
  const techCost = data.electronics_items * factors.electronics_item;
  const shopping = (clothesCost + techCost) - ((data.recycling_pct / 100) * 0.1 * (clothesCost + techCost));

  const total = transport + home + food + shopping;

  return {
    transport: Math.round(transport * 100) / 100,
    home: Math.round(home * 100) / 100,
    food: Math.round(food * 100) / 100,
    consumption: Math.round(shopping * 100) / 100,
    total: Math.round(total * 100) / 100
  };
}

// Update dashboard metrics and SVG segments
function updateEmissionsUI() {
  const e = appState.emissions;
  metricTotalFootprint.textContent = `${e.total.toFixed(1)} `;
  const unitSpan = document.createElement("span");
  unitSpan.className = "unit";
  unitSpan.textContent = "kg CO2e";
  metricTotalFootprint.appendChild(unitSpan);
  chartCenterVal.textContent = Math.round(e.total);

  // Update SVG donut chart segments
  // Circumference = 2 * PI * r = 2 * PI * 80 = 502.65
  const C = 502.65;
  const categories = ["transport", "home", "food", "consumption"];
  let cumulativePercent = 0;

  categories.forEach(cat => {
    const val = e[cat];
    const percent = e.total > 0 ? val / e.total : 0;
    const dashLength = percent * C;
    const offset = -cumulativePercent * C;
    
    const segment = document.getElementById(`segment-${cat}`);
    if (segment) {
      segment.setAttribute("stroke-dasharray", `${dashLength} ${C}`);
      segment.setAttribute("stroke-dashoffset", `${offset}`);
    }

    // Update legend UI
    const pctStr = (percent * 100).toFixed(0);
    document.getElementById(`legend-val-${cat}`).textContent = `${val.toFixed(0)} kg (${pctStr}%)`;

    cumulativePercent += percent;
  });
}

// Update point count and level rank
function updatePointsUI() {
  metricEcoPoints.textContent = `${appState.ecoPoints} `;
  const unitSpan = document.createElement("span");
  unitSpan.className = "unit";
  unitSpan.textContent = "pts";
  metricEcoPoints.appendChild(unitSpan);
  
  let rank = "Eco Novice";
  if (appState.ecoPoints > 200) {
    rank = "Carbon Conqueror";
    metricRank.className = "font-bold text-emerald";
  } else if (appState.ecoPoints > 100) {
    rank = "Green Guardian";
    metricRank.className = "font-bold text-teal";
  } else {
    metricRank.className = "font-bold text-purple";
  }
  metricRank.textContent = rank;

  // Restore completed challenges styling
  document.querySelectorAll(".challenge-item").forEach(item => {
    const id = item.id;
    if (appState.completedChallenges.includes(id)) {
      item.classList.add("completed");
      const btn = item.querySelector("button");
      if (btn) btn.textContent = "Done";
    }
  });
}

// Restore checkboxes and update reduction planning metrics
function updateActionsUI() {
  const checkboxes = document.querySelectorAll(".reduction-checkbox");
  checkboxes.forEach((box, index) => {
    if (appState.selectedActions.includes(index)) {
      box.checked = true;
    }
  });
  updateProjectedReductions();
}

// Complete weekly challenge and award points
function completeChallenge(challengeId, points) {
  if (appState.completedChallenges.includes(challengeId)) return;
  
  appState.ecoPoints += points;
  appState.completedChallenges.push(challengeId);
  
  // Flash effect on points card
  const card = metricEcoPoints.parentElement.parentElement;
  card.classList.add("flash-scale");
  setTimeout(() => card.classList.remove("flash-scale"), 300);

  updatePointsUI();
  saveState();
}

// Calculate sum of reduction checklist and subtract from total footprint
function updateProjectedReductions() {
  let totalReduction = 0;
  appState.selectedActions = [];

  const checkboxes = document.querySelectorAll(".reduction-checkbox");
  checkboxes.forEach((box, index) => {
    if (box.checked) {
      totalReduction += parseFloat(box.getAttribute("data-kg"));
      appState.selectedActions.push(index);
    }
  });

  metricProjectedReduction.textContent = `-${totalReduction.toFixed(0)} `;
  const unitSpan = document.createElement("span");
  unitSpan.className = "unit";
  unitSpan.textContent = "kg CO2e";
  metricProjectedReduction.appendChild(unitSpan);
  
  // Calculate adjusted projection value and reflect in central chart value
  const adjustedTotal = Math.max(0, appState.emissions.total - totalReduction);
  chartCenterVal.textContent = Math.round(adjustedTotal);
  
  saveState();
}

// Helper for debouncing execution of a function
function debounce(func, delay) {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      func.apply(this, args);
    }, delay);
  };
}

// Append chat messages
function appendCoachBubble(content, isUser = false) {
  const bubble = document.createElement("div");
  bubble.className = `message ${isUser ? "user-message" : "assistant-message"}`;
  
  const bubbleContent = document.createElement("div");
  bubbleContent.className = "message-bubble";
  
  if (isUser || typeof content === "string") {
    // For user messages, escape HTML and set as text to prevent XSS
    bubbleContent.textContent = content;
  } else {
    // For structured assistant response objects, build the DOM elements safely to guarantee no XSS
    const introEl = document.createElement("p");
    introEl.textContent = content.intro || "";
    bubbleContent.appendChild(introEl);
    
    if (content.tips && content.tips.length > 0) {
      const listEl = document.createElement("ul");
      listEl.className = "coach-tips-list";
      
      content.tips.forEach(tip => {
        const itemEl = document.createElement("li");
        itemEl.className = "coach-tip-item";
        
        const titleEl = document.createElement("strong");
        titleEl.textContent = (tip.title || "") + ": ";
        
        const descEl = document.createTextNode(tip.description || "");
        
        const spacing = document.createTextNode(" ");
        
        const reductionEl = document.createElement("code");
        reductionEl.className = "coach-reduction-badge";
        reductionEl.textContent = tip.estimated_reduction || "";
        
        itemEl.appendChild(titleEl);
        itemEl.appendChild(descEl);
        itemEl.appendChild(spacing);
        itemEl.appendChild(reductionEl);
        
        listEl.appendChild(itemEl);
      });
      bubbleContent.appendChild(listEl);
    }
    
    const conclusionEl = document.createElement("p");
    conclusionEl.className = "coach-conclusion";
    conclusionEl.textContent = content.conclusion || "";
    bubbleContent.appendChild(conclusionEl);
  }
  
  bubble.appendChild(bubbleContent);
  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send message to coach and handle responses
async function sendMessage(messageText) {
  // Append user message
  appendCoachBubble(messageText, true);
  appState.chatHistory.push({ role: "user", content: messageText });

  // Add temporary typing bubble
  const typingBubble = document.createElement("div");
  typingBubble.className = "message assistant-message";
  const bubbleInner = document.createElement("div");
  bubbleInner.className = "message-bubble analyzing";
  bubbleInner.textContent = "EcoCoach is analyzing...";
  typingBubble.appendChild(bubbleInner);
  chatMessages.appendChild(typingBubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const response = await fetch("/api/coach", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        persona: appState.persona,
        emissions: appState.emissions,
        chat_history: appState.chatHistory
      })
    });
    
    // Remove typing bubble
    chatMessages.removeChild(typingBubble);

    if (!response.ok) throw new Error("API coach response error");
    const result = await response.json();
    
    appendCoachBubble(result);
    
    // Construct textual format for context mapping in subsequent chatbot turns
    let historyText = `${result.intro}\n`;
    if (result.tips) {
      result.tips.forEach(t => {
        historyText += `- **${t.title}**: ${t.description} [${t.estimated_reduction}]\n`;
      });
    }
    historyText += result.conclusion;
    
    appState.chatHistory.push({ role: "assistant", content: historyText });
  } catch (error) {
    console.warn("AI Coach API failed. Processing fallback advice:", error);
    chatMessages.removeChild(typingBubble);
    
    // Call client-side fallback advice
    const fallbackAdvice = runLocalCoachAdvice(appState.persona, appState.emissions);
    appendCoachBubble(fallbackAdvice);
    
    // Construct textual format for fallback context mapping
    let historyText = `${fallbackAdvice.intro}\n`;
    if (fallbackAdvice.tips) {
      fallbackAdvice.tips.forEach(t => {
        historyText += `- **${t.title}**: ${t.description} [${t.estimated_reduction}]\n`;
      });
    }
    historyText += fallbackAdvice.conclusion;
    
    appState.chatHistory.push({ role: "assistant", content: historyText });
  }
  saveState();
}

// Client-side local coach reasoning engine (fallback)
function runLocalCoachAdvice(persona, emissions) {
  const total = emissions.total;
  const categories = {
    "Transport": emissions.transport,
    "Home Energy": emissions.home,
    "Food": emissions.food,
    "Shopping/Consumption": emissions.consumption
  };
  const highest = Object.keys(categories).reduce((a, b) => categories[a] > categories[b] ? a : b);
  const highestVal = categories[highest];
  const pName = persona.replace("_", " ").toUpperCase();

  const intro = `I've analyzed your profile (${pName}) with a footprint of ${total} kg CO2e. Your highest source is ${highest} at ${highestVal} kg CO2e (${Math.round(highestVal / (total || 1) * 100)}%).`;
  
  let tips = [];
  if (highest === "Transport") {
    tips = [
      {
        title: "Active Transport",
        description: "Commute by bicycle or walking for short trips.",
        estimated_reduction: "-20 kg CO2e"
      },
      {
        title: "Carpooling",
        description: "Carpool to work 3 days a week.",
        estimated_reduction: "-80 kg CO2e"
      }
    ];
  } else if (highest === "Home Energy") {
    tips = [
      {
        title: "Smart Thermostat",
        description: "Lower your home heating target by 2°C in cold months.",
        estimated_reduction: "-35 kg CO2e"
      },
      {
        title: "LED Bulbs",
        description: "Switch household lightbulbs to LED.",
        estimated_reduction: "-15 kg CO2e"
      }
    ];
  } else if (highest === "Food") {
    tips = [
      {
        title: "Vegetarian shift",
        description: "Switch to vegetarian or plant-based meals 3 days a week.",
        estimated_reduction: "-50 kg CO2e"
      },
      {
        title: "Food Waste Reduction",
        description: "Minimize food waste via conscious meal prepping.",
        estimated_reduction: "-18 kg CO2e"
      }
    ];
  } else {
    tips = [
      {
        title: "Repair Over Replace",
        description: "Choose repair over replacement for tech gadgets.",
        estimated_reduction: "-150 kg CO2e"
      },
      {
        title: "Secondhand Wardrobe",
        description: "Opt for secondhand/thrifting clothes.",
        estimated_reduction: "-10 kg CO2e/item"
      }
    ];
  }
  
  const conclusion = "Keep up the great work! Try selecting some of these actions in your Action Planner to see your carbon footprint reduce in real-time.";
  
  return {
    intro: intro,
    tips: tips,
    conclusion: conclusion
  };
}
