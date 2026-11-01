const BASE = "/api/v1";

async function handle(res) {
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") msg = body.detail;
    } catch {}
    throw new Error(msg);
  }
  return res.json();
}

export const getSample = () => fetch(`${BASE}/sample`).then(handle);

export function scoreResume({ resumeFile, resumeText, jdFile, jdText, includeExplanation }) {
  const form = new FormData();
  if (resumeFile) form.append("resume_file", resumeFile);
  if (jdFile) form.append("jd_file", jdFile);
  form.append("resume_text", resumeText);
  form.append("jd_text", jdText);
  form.append("include_explanation", String(includeExplanation));
  return fetch(`${BASE}/score`, { method: "POST", body: form }).then(handle);
}
