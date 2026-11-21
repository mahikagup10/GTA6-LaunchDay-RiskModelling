async function request(path, options = {}) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), 15_000);
  let response;

  try {
    response = await fetch(path, {
      headers: { "Content-Type": "application/json", ...options.headers },
      ...options,
      signal: controller.signal,
    });
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("The risk model took too long to respond. Check that Flask is running, then retry.");
    }
    throw new Error("The Flask risk model could not be reached. Start the backend, then retry.");
  } finally {
    window.clearTimeout(timeoutId);
  }

  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error("The risk model returned an unreadable response. Restart Flask, then retry.");
  }

  if (!response.ok) {
    throw new Error(data.error || `Request failed with status ${response.status}`);
  }

  return data;
}

export function getConfig() {
  return request("/api/config");
}

export function simulateRisk(payload) {
  return request("/api/simulate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function simulatePortfolio(payload) {
  return request("/api/portfolio", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

