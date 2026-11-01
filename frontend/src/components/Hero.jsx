function MiniMockup() {
  // decorative preview of the results UI, shown in the frosted card
  const bars = [
    ["Keyword", 72, "bg-emerald-400"],
    ["Semantic", 81, "bg-teal-400"],
    ["Structural", 64, "bg-cyan-400"],
  ];
  const r = 42, c = 2 * Math.PI * r;
  return (
    <div className="overflow-hidden rounded-t-2xl bg-white shadow-xl shadow-teal-900/10 ring-1 ring-black/5">
      <div className="flex items-center gap-1.5 border-b border-slate-100 px-4 py-2.5">
        <span className="h-2 w-2 rounded-full bg-rose-300" />
        <span className="h-2 w-2 rounded-full bg-amber-300" />
        <span className="h-2 w-2 rounded-full bg-emerald-300" />
        <span className="ml-3 rounded-full bg-slate-100 px-3 py-0.5 text-[10px] text-slate-400">semantic-ats / results</span>
      </div>
      <div className="grid grid-cols-[130px_1fr] items-center gap-6 bg-gradient-to-br from-amber-50 via-white to-emerald-50 p-6">
        <div className="relative h-[120px] w-[120px]">
          <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
            <circle cx="50" cy="50" r={r} fill="none" stroke="#e2e8f0" strokeWidth="8" />
            <circle cx="50" cy="50" r={r} fill="none" stroke="#10b981" strokeWidth="8" strokeLinecap="round"
              strokeDasharray={c} strokeDashoffset={c * 0.27} />
          </svg>
          <div className="absolute inset-0 grid place-items-center text-center">
            <div><div className="text-2xl font-extrabold">73.0</div><div className="text-[9px] text-slate-400">out of 100</div></div>
          </div>
        </div>
        <div className="space-y-3">
          {bars.map(([l, v, cl]) => (
            <div key={l}>
              <div className="mb-1 flex justify-between text-[10px] font-medium text-slate-500"><span>{l}</span><span>{v}%</span></div>
              <div className="h-1.5 rounded-full bg-slate-100"><div className={`h-full rounded-full ${cl}`} style={{ width: `${v}%` }} /></div>
            </div>
          ))}
        </div>
      </div>
      <div className="flex flex-wrap gap-1.5 bg-white px-6 pb-7 pt-4">
        {["Python", "FastAPI", "Docker", "PostgreSQL"].map((s) => (
          <span key={s} className="rounded-full bg-emerald-50 px-2.5 py-1 text-[10px] font-semibold text-emerald-700">{s}</span>
        ))}
        {["Kubernetes", "Kafka"].map((s) => (
          <span key={s} className="rounded-full bg-rose-50 px-2.5 py-1 text-[10px] font-semibold text-rose-600">{s}</span>
        ))}
      </div>
    </div>
  );
}

export default function Hero() {
  return (
    <header className="relative overflow-hidden bg-gradient-to-b from-emerald-200 via-teal-100 to-white">
      <div className="pointer-events-none absolute -left-32 top-24 h-96 w-96 rounded-full bg-cyan-200/60 blur-3xl" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-white to-transparent" />

      {/* navbar */}
      <nav className="relative z-10 border-b border-black/5 bg-white shadow-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
          <div className="flex items-center gap-5">
            <span className="text-lg font-bold tracking-tight">semantic<span className="text-slate-400"> / </span>ats</span>
            <span className="hidden h-5 w-px bg-slate-200 sm:block" />
            <a href="#scorer" className="hidden items-center gap-2 rounded-lg border border-emerald-100 bg-emerald-50 px-3 py-1.5 text-sm font-medium text-slate-700 sm:flex">
              <span className="text-teal-500">✦</span> Score a resume
            </a>
            <a href="#how" className="hidden text-sm font-medium text-slate-600 hover:text-black md:block">How it works</a>
          </div>
          <div className="flex items-center gap-2">
            <a href="https://github.com/Anishkachawla/Semantic-ATS-Resume-Matching-System" target="_blank" rel="noreferrer"
              className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50">GitHub</a>
            <a href="#scorer" className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-black">Get started</a>
          </div>
        </div>
      </nav>

      <div className="relative mx-auto grid max-w-6xl items-center gap-10 px-6 pb-24 pt-16 lg:grid-cols-[1fr_1.05fr]">
        <div className="animate-rise">
          <div className="flex flex-wrap gap-2">
            <span className="rounded-full bg-white/80 px-3.5 py-1.5 text-sm font-medium shadow-sm"><span className="mr-1.5 text-sky-500">≋</span>Hybrid NLP</span>
            <span className="rounded-full bg-white/50 px-3.5 py-1.5 text-sm font-medium"><span className="mr-1.5 text-emerald-500">✓</span>Explainable scores</span>
          </div>
          <h1 className="mt-7 text-5xl font-semibold leading-[1.1] tracking-tight text-ink sm:text-6xl">
            Tired of black-box ATS scores? Try one that shows its work
          </h1>
          <p className="mt-6 max-w-lg text-lg leading-relaxed text-slate-600">
            A resume matcher that blends keyword, semantic and structural signals,
            then shows exactly which skills match and which are missing.
          </p>
          <div className="mt-9 flex flex-wrap gap-3">
            <a href="#scorer" className="flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-semibold shadow-sm ring-1 ring-black/5 hover:shadow-md">
              <span className="text-teal-500">✦</span> Try sample data
            </a>
            <a href="#scorer" className="flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-black">
              Score a resume <span>→</span>
            </a>
          </div>
        </div>

        <div className="animate-rise rounded-[2rem] border border-white/70 bg-white/40 p-6 pb-0 shadow-xl shadow-teal-900/5 backdrop-blur-md lg:translate-x-8">
          <MiniMockup />
        </div>
      </div>
    </header>
  );
}
