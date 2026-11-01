import { useState } from "react";
import Hero from "./components/Hero.jsx";
import InputPanel from "./components/InputPanel.jsx";
import Results from "./components/Results.jsx";
import { getSample, scoreResume } from "./api.js";

const initial = {
  resumeFile: null,
  resumeText: "",
  jdFile: null,
  jdText: "",
  includeExplanation: false,
};

export default function App() {
  const [state, setState] = useState(initial);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function onSubmit() {
    setError("");
    if (!state.resumeFile && !state.resumeText.trim()) return setError("Add a resume: upload a file or paste the text in.");
    if (!state.jdFile && !state.jdText.trim()) return setError("Add a job description: upload a file or paste the text in.");

    setLoading(true);
    try {
      const data = await scoreResume(state);
      setResult(data);
      setTimeout(() => document.getElementById("results")?.scrollIntoView({ behavior: "smooth" }), 50);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function onSample() {
    setError("");
    try {
      const s = await getSample();
      setState((p) => ({ ...p, resumeFile: null, jdFile: null, resumeText: s.resume_text, jdText: s.jd_text }));
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div className="min-h-screen pb-24">
      <Hero />
      <InputPanel state={state} setState={setState} onSubmit={onSubmit} onSample={onSample} loading={loading} />

      {error && (
        <div className="mx-auto mt-5 max-w-6xl px-6">
          <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>
        </div>
      )}

      <div id="results">{result && <Results data={result} />}</div>
    </div>
  );
}
