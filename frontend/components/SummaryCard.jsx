export default function SummaryCard({ summary }) {
  return (
    <div className="space-y-8">
      <div className="rounded-xl border border-black/10 bg-white p-6">
        <h2 className="text-sm font-semibold text-ink/40 uppercase tracking-wide">
          Overall
        </h2>
        <p className="mt-2 text-base leading-relaxed">{summary.overall_summary}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
          <h3 className="text-sm font-semibold text-emerald-700">Strengths</h3>
          <ul className="mt-2 space-y-1 text-sm text-emerald-900">
            {summary.strengths.map((s, i) => (
              <li key={i}>• {s}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-5">
          <h3 className="text-sm font-semibold text-amber-700">Growth areas</h3>
          <ul className="mt-2 space-y-1 text-sm text-amber-900">
            {summary.growth_areas.map((s, i) => (
              <li key={i}>• {s}</li>
            ))}
          </ul>
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-ink/40 uppercase tracking-wide mb-3">
          Full transcript
        </h3>
        <div className="space-y-4">
          {summary.transcript.map((item) => (
            <div key={item.order_index} className="rounded-xl border border-black/10 bg-white p-4">
              <div className="flex items-center gap-2 text-xs text-ink/40 mb-2">
                <span>Q{item.order_index + 1}</span>
                <span className="rounded-full bg-black/5 px-2 py-0.5">{item.difficulty}</span>
                {item.topic && <span className="rounded-full bg-black/5 px-2 py-0.5">{item.topic}</span>}
              </div>
              <p className="text-sm font-medium">{item.question}</p>
              <p className="mt-2 text-sm text-ink/70">{item.answer}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
