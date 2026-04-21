const form = document.getElementById("chatForm");
const input = document.getElementById("chatInput");
const log = document.getElementById("chatLog");

function addBubble(text, cls) {
  const div = document.createElement("div");
  div.className = `bubble ${cls}`;
  div.textContent = text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  addBubble(message, "user");
  input.value = "";

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });
  const data = await res.json();
  addBubble(data.reply || "No reply available.", "bot");
});

