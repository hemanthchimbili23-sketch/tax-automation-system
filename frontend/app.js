const state = {
  apiBase: localStorage.getItem("apiBase") || "http://localhost:5000",
};

const apiBaseInput = document.getElementById("apiBase");
const saveConfigButton = document.getElementById("saveConfig");
apiBaseInput.value = state.apiBase;

saveConfigButton.addEventListener("click", () => {
  state.apiBase = apiBaseInput.value.trim().replace(/\/$/, "");
  localStorage.setItem("apiBase", state.apiBase);
  alert("API base URL saved");
});

function showJSON(el, data) {
  el.textContent = JSON.stringify(data, null, 2);
}

async function request(path, options = {}) {
  const res = await fetch(`${state.apiBase}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  let body;
  try {
    body = await res.json();
  } catch {
    body = { error: "Non-JSON response from server" };
  }

  if (!res.ok) {
    throw new Error(body.error || `Request failed with status ${res.status}`);
  }

  return body;
}

function formToObject(form) {
  const formData = new FormData(form);
  return Object.fromEntries(formData.entries());
}

document.getElementById("recordForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const resultEl = document.getElementById("recordResult");
  resultEl.textContent = "Loading...";
  const payload = formToObject(e.target);
  payload.tax_year = Number(payload.tax_year);
  payload.income = Number(payload.income);
  payload.deductions = Number(payload.deductions);

  try {
    const data = await request("/records", { method: "POST", body: JSON.stringify(payload) });
    showJSON(resultEl, data);
  } catch (err) {
    resultEl.textContent = err.message;
  }
});

document.getElementById("summaryForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const resultEl = document.getElementById("summaryResult");
  resultEl.textContent = "Loading...";
  const { record_id } = formToObject(e.target);

  try {
    const data = await request(`/records/${Number(record_id)}/summary`);
    showJSON(resultEl, data);
  } catch (err) {
    resultEl.textContent = err.message;
  }
});

document.getElementById("reminderForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const resultEl = document.getElementById("reminderResult");
  resultEl.textContent = "Loading...";
  const payload = formToObject(e.target);
  payload.record_id = Number(payload.record_id);
  if (!payload.message) delete payload.message;

  try {
    const data = await request("/reminders", { method: "POST", body: JSON.stringify(payload) });
    showJSON(resultEl, data);
  } catch (err) {
    resultEl.textContent = err.message;
  }
});

document.getElementById("upcomingForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const resultEl = document.getElementById("upcomingResult");
  resultEl.textContent = "Loading...";
  const { days } = formToObject(e.target);

  try {
    const data = await request(`/reminders/upcoming?days=${Number(days)}`);
    showJSON(resultEl, data);
  } catch (err) {
    resultEl.textContent = err.message;
  }
});
