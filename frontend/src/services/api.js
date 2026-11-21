async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  const data = await response.json();

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

