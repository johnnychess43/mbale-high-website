document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("assistant-toggle");
  const panel = document.getElementById("assistant-panel");
  const close = document.getElementById("assistant-close");
  const form = document.getElementById("assistant-form");
  const input = document.getElementById("assistant-message");
  const answer = document.getElementById("assistant-answer");
  if (!toggle || !panel || !form) return;
  const setOpen = (open) => { panel.hidden = !open; toggle.setAttribute("aria-expanded", String(open)); if (open) input.focus(); };
  toggle.addEventListener("click", () => setOpen(panel.hidden));
  close.addEventListener("click", () => setOpen(false));
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;
    answer.textContent = "Looking through the school's published information…";
    try {
      const response = await fetch("/api/assistant", {
        method: "POST", headers: {"Content-Type": "application/json", "Accept": "application/json"},
        body: JSON.stringify({message})
      });
      const data = await response.json();
      answer.textContent = data.answer || "I could not find an answer. Please contact the school.";
      if (data.link) {
        const link = document.createElement("a");
        link.href = data.link; link.textContent = "Open related page"; link.className = "assistant-related-link";
        answer.append(document.createElement("br"), link);
      }
    } catch (_) {
      answer.textContent = "The assistant is temporarily unavailable. Please use the website navigation or contact the school.";
    }
  });
});