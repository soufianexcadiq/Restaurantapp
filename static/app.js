const reservationForm = document.querySelector("#reservation-form");
const reservationStatus = document.querySelector("#reservation-status");
const chatToggle = document.querySelector("#chat-toggle");
const chatWindow = document.querySelector("#chat-window");
const chatForm = document.querySelector("#chat-form");
const chatInput = document.querySelector("#chat-input");
const chatMessages = document.querySelector("#chat-messages");
const aiForm = document.querySelector("#ai-form");
const aiResults = document.querySelector("#ai-results");

reservationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  reservationStatus.textContent = "Sending reservation request...";

  const formData = new FormData(reservationForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const response = await fetch("/api/reservations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    reservationStatus.textContent = result.message;

    if (result.ok) {
      reservationForm.reset();
    }
  } catch (error) {
    reservationStatus.textContent = "Something went wrong. Please try again.";
  }
});

chatToggle.addEventListener("click", () => {
  const isOpen = !chatWindow.hidden;
  chatWindow.hidden = isOpen;
  chatToggle.setAttribute("aria-expanded", String(!isOpen));
  chatToggle.querySelector("span").textContent = isOpen ? "Assistant" : "Close";

  if (!isOpen) {
    chatInput.focus();
  }
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = chatInput.value.trim();

  if (!message) {
    return;
  }

  addMessage(message, "user");
  chatInput.value = "";

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const result = await response.json();
    addMessage(result.reply, "bot");
  } catch (error) {
    addMessage("I lost the connection for a moment. Please try again.", "bot");
  }
});

aiForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  aiResults.innerHTML = '<div class="ai-empty"><strong>Thinking through the menu...</strong><span>Matching your mood, diet, spice, and budget.</span></div>';

  const formData = new FormData(aiForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const response = await fetch("/api/recommendations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    renderRecommendations(result.recommendations);
  } catch (error) {
    aiResults.innerHTML = '<div class="ai-empty"><strong>Recommendation failed.</strong><span>Please try again in a moment.</span></div>';
  }
});

function addMessage(text, type) {
  const message = document.createElement("div");
  message.className = `message ${type}`;
  message.textContent = text;
  chatMessages.append(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderRecommendations(recommendations) {
  aiResults.innerHTML = "";

  recommendations.forEach((item, index) => {
    const card = document.createElement("article");
    card.className = "ai-card";
    card.innerHTML = `
      <img src="${item.image}" alt="">
      <div>
        <span class="rank">Match ${index + 1}</span>
        <h3>${item.name}</h3>
        <p>${item.description}</p>
        <strong>${item.price}</strong>
        <small>${item.reason}. Spice ${item.spice}/3, about ${item.calories} calories.</small>
      </div>
    `;
    aiResults.append(card);
  });
}
