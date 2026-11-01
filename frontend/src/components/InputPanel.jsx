import { useRef, useState } from "react";

function DropBox({ title, file, onFile, text, onText, placeholder }) {
  const inputRef = useRef(null);
  const [drag, setDrag] = useState(false);

  const pick = (f) => f && onFile(f);

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="mb-3 text-base font-semibold text-ink">{title}</h3>

      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => { e.preventDefault(); setDrag(false); pick(e.dataTransfer.files[0]); }}
        className={`flex cursor-pointer items-center justify-between gap-3 rounded-xl border border-dashed px-4 py-4 text-sm transition ${
          drag ? "border-teal-400 bg-teal-50" : "border-slate-300 hover:border-teal-400 hover:bg-emerald-50/50"
        }`}
      >
        <span className="truncate text-slate-400">
          {file ? <span className="text-ink font-medium">{file.name}</span> : "Drop PDF / DOCX / TXT, or click to upload"}
        </span>
        {file && (
          <button
            onClick={(e) => { e.stopPropagation(); onFile(null); if (inputRef.current) inputRef.current.value = ""; }}
            className="rounded-md px-2 py-1 text-xs text-slate-400 hover:bg-slate-100 hover:text-black"
          >
            Remove
          </button>
        )}
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          className="hidden"
          onChange={(e) => pick(e.target.files[0])}
        />
      </div>

      <div className="my-3 flex items-center gap-3 text-xs text-slate-400">
        <span className="h-px flex-1 bg-slate-200" /> or paste <span className="h-px flex-1 bg-slate-200" />
      </div>

      <textarea
        value={text}
        onChange={(e) => onText(e.target.value)}
        rows={9}
        placeholder={placeholder}
        disabled={!!file}
        className="w-full resize-y rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-ink placeholder:text-slate-400 focus:border-teal-400 focus:outline-none disabled:opacity-40"
      />
    </div>
  );
}

export default function InputPanel({ state, setState, onSubmit, onSample, loading }) {
  const set = (k) => (v) => setState((s) => ({ ...s, [k]: v }));

  return (
    <section id="scorer" className="relative mx-auto mt-4 max-w-6xl scroll-mt-4 px-6">
      <div className="grid gap-5 md:grid-cols-2">
        <DropBox
          title="Resume"
          file={state.resumeFile}
          onFile={set("resumeFile")}
          text={state.resumeText}
          onText={set("resumeText")}
          placeholder="Paste resume text here"
        />
        <DropBox
          title="Job description"
          file={state.jdFile}
          onFile={set("jdFile")}
          text={state.jdText}
          onText={set("jdText")}
          placeholder="Paste job description text here"
        />
      </div>

      <div className="mt-5 flex flex-wrap items-center justify-between gap-4">
        <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-600">
          <input
            type="checkbox"
            checked={state.includeExplanation}
            onChange={(e) => set("includeExplanation")(e.target.checked)}
            className="h-4 w-4 accent-teal-500"
          />
          Generate written explanation <span className="text-slate-400">(calls Gemini)</span>
        </label>

        <div className="flex gap-3">
          <button
            onClick={onSample}
            className="rounded-xl bg-white px-5 py-3 text-sm font-semibold text-ink shadow-sm ring-1 ring-black/10 transition hover:shadow-md"
          >
            Load sample data
          </button>
          <button
            onClick={onSubmit}
            disabled={loading}
            className="rounded-xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-black disabled:opacity-60"
          >
            {loading ? "Scoring…" : "Score resume"}
          </button>
        </div>
      </div>
    </section>
  );
}
