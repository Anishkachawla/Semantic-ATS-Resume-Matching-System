function verdict(score) {
  if (score >= 75) return { label: "Strong match", color: "#10b981", chip: "bg-emerald-100 text-emerald-700" };
  if (score >= 50) return { label: "Partial match", color: "#f59e0b", chip: "bg-amber-100 text-amber-700" };
  return { label: "Weak match", color: "#ef4444", chip: "bg-rose-100 text-rose-700" };
}

function ScoreRing({ score }) {
  const v = verdict(score);
  const r = 70;
  const c = 2 * Math.PI * r;
  return (
    <div className="flex flex-col items-center">
      <div className="relative h-44 w-44">
        <svg viewBox="0 0 160 160" className="h-full w-full -rotate-90">
          <circle cx="80" cy="80" r={r} fill="none" stroke="#e2e8f0" strokeWidth="10" />
          <circle
            cx="80" cy="80" r={r} fill="none" stroke={v.color} strokeWidth="10" strokeLinecap="round"
            strokeDasharray={c} strokeDashoffset={c * (1 - score / 100)}
            style={{ transition: "stroke-dashoffset 1s ease-out" }}
          />
        </svg>
        <div className="absolute inset-0 grid place-items-center text-center">
          <div>
            <div className="text-5xl font-extrabold text-ink">{score.toFixed(1)}</div>
            <div className="text-xs text-slate-400">out of 100</div>
          </div>
        </div>
      </div>
      <span className={`mt-4 rounded-full px-4 py-1 text-sm font-semibold ${v.chip}`}>{v.label}</span>
    </div>
  );
}

function Bar({ label, score, weight, from, to }) {
  const pct = Math.round(score * 100);
  return (
    <div>
      <div className="mb-1.5 flex justify-between text-sm">
        <span className="text-slate-600">
          {label} <span className="text-slate-400">· weight {Math.round(weight * 100)}%</span>
        </span>
        <span className="font-semibold text-ink">{pct}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${from} ${to}`}
          style={{ width: `${pct}%`, transition: "width 1s ease-out" }}
        />
      </div>
    </div>
  );
}

function Chips({ items, tone }) {
  if (!items?.length) return <span className="text-sm text-slate-400">None</span>;
  const cls = tone === "good" ? "bg-emerald-50 text-emerald-700 ring-emerald-200" : "bg-rose-50 text-rose-600 ring-rose-200";
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((s) => (
        <span key={s} className={`rounded-full px-3 py-1 text-xs font-medium ring-1 ${cls}`}>{s}</span>
      ))}
    </div>
  );
}

const Card = ({ title, children, className = "" }) => (
  <div className={`rounded-3xl border border-slate-200 bg-white p-6 shadow-sm ${className}`}>
    {title && <h3 className="mb-4 text-base font-semibold text-ink">{title}</h3>}
    {children}
  </div>
);

function List({ title, items }) {
  if (!items?.length) return null;
  return (
    <div className="mt-4">
      <div className="mb-1.5 text-sm font-semibold text-ink">{title}</div>
      <ul className="list-disc space-y-1 pl-5 text-sm text-slate-600">
        {items.map((i, k) => <li key={k}>{i}</li>)}
      </ul>
    </div>
  );
}

export default function Results({ data }) {
  const { final_score, breakdown: b, gap_analysis: g, explanation } = data;
  const w = b.weights_used;

  return (
    <section className="mx-auto mt-14 max-w-6xl animate-rise px-6">
      <div className="grid gap-5 lg:grid-cols-[320px_1fr]">
        <Card className="grid place-items-center"><ScoreRing score={final_score} /></Card>

        <Card title="Score breakdown">
          <div className="space-y-5">
            <Bar label="Keyword match" score={b.keyword.score} weight={w.keyword} from="from-emerald-400" to="to-teal-400" />
            <Bar label="Semantic similarity" score={b.semantic.score} weight={w.semantic} from="from-teal-400" to="to-cyan-400" />
            <Bar label="Structural fit" score={b.structural.score} weight={w.structural} from="from-cyan-400" to="to-sky-400" />
          </div>
        </Card>
      </div>

      <div className="mt-5 grid gap-5 md:grid-cols-2">
        <Card title={`Matched skills (${g.matched_skills.length})`}><Chips items={g.matched_skills} tone="good" /></Card>
        <Card title={`Missing skills (${g.missing_skills.length})`}><Chips items={g.missing_skills} tone="bad" /></Card>
      </div>

      <Card title="Written explanation" className="mt-5">
        {explanation ? (
          <>
            <p className="text-sm leading-relaxed text-slate-600">{explanation.summary}</p>
            <List title="Strengths" items={explanation.strengths} />
            <List title="Gaps" items={explanation.gaps} />
            <List title="Suggestions" items={explanation.suggestions} />
          </>
        ) : (
          <p className="text-sm text-slate-400">
            Not requested. Tick “Generate written explanation” and score again to get one from Gemini.
          </p>
        )}
      </Card>
    </section>
  );
}
