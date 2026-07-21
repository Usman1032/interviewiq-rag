const DIFFICULTY_STYLES = {
  easy: "bg-emerald-100 text-emerald-700",
  medium: "bg-amber-100 text-amber-700",
  hard: "bg-rose-100 text-rose-700",
};

export default function InterviewChat({
  question,
  transcript,
  answerDraft,
  onAnswerChange,
  onSubmit,
  submitting,
}) {
  return (
    <div className="space-y-6">
      {transcript.map((item, idx) => (
        <div key={idx} className="space-y-2">
          <div className="rounded-xl rounded-tl-none bg-white border border-black/10 px-4 py-3 text-sm">
            {item.question}
          </div>
          <div className="ml-8 rounded-xl rounded-tr-none bg-accent/10 px-4 py-3 text-sm text-ink/80">
            {item.answer}
          </div>
        </div>
      ))}

      {question && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-ink/40">
              Question {question.order_index + 1} of {question.total_questions}
            </span>
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                DIFFICULTY_STYLES[question.difficulty] || "bg-black/5"
              }`}
            >
              {question.difficulty}
            </span>
            {question.topic && (
              <span className="rounded-full bg-black/5 px-2 py-0.5 text-xs text-ink/50">
                {question.topic}
              </span>
            )}
          </div>
          <div className="rounded-xl rounded-tl-none border border-black/10 bg-white px-4 py-3 text-sm">
            {question.text}
          </div>
          <textarea
            value={answerDraft}
            onChange={(e) => onAnswerChange(e.target.value)}
            rows={4}
            placeholder="Type your answer..."
            className="w-full rounded-xl border border-black/15 bg-white px-4 py-3 text-sm outline-none focus:border-accent"
          />
          <button
            onClick={onSubmit}
            disabled={submitting || !answerDraft.trim()}
            className="rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-white transition disabled:opacity-40"
          >
            {submitting ? "Submitting..." : "Submit answer"}
          </button>
        </div>
      )}
    </div>
  );
}
