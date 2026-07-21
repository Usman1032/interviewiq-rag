const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  getRoles: () => request("/api/roles"),

  uploadResume: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_URL}/api/resume/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || "Resume upload failed");
    }
    return res.json();
  },

  startInterview: (candidateId, roleKey) =>
    request("/api/interview/start", {
      method: "POST",
      body: JSON.stringify({ candidate_id: candidateId, role_key: roleKey }),
    }),

  submitAnswer: (sessionId, answerText) =>
    request(`/api/interview/${sessionId}/answer`, {
      method: "POST",
      body: JSON.stringify({ answer_text: answerText }),
    }),

  getSummary: (sessionId) => request(`/api/interview/${sessionId}/summary`),
};
