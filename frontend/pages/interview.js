import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import InterviewChat from "../components/InterviewChat";
import { api } from "../lib/api";

export default function Interview() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState(null);
  const [roleLabel, setRoleLabel] = useState("");
  const [question, setQuestion] = useState(null);
  const [transcript, setTranscript] = useState([]);
  const [answerDraft, setAnswerDraft] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const sid = sessionStorage.getItem("session_id");
    if (!sid) {
      router.replace("/");
      return;
    }
    setSessionId(sid);
    setRoleLabel(sessionStorage.getItem("role_label") || "");
    setQuestion(JSON.parse(sessionStorage.getItem("current_question") || "null"));
    setTranscript(JSON.parse(sessionStorage.getItem("transcript") || "[]"));
  }, [router]);

  const handleSubmit = async () => {
    if (!answerDraft.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const result = await api.submitAnswer(sessionId, answerDraft);

      const newTranscript = [
        ...transcript,
        { question: question.text, answer: answerDraft },
      ];
      setTranscript(newTranscript);
      sessionStorage.setItem("transcript", JSON.stringify(newTranscript));
      setAnswerDraft("");

      if (result.status === "completed") {
        router.push("/summary");
        return;
      }

      setQuestion(result.next_question);
      sessionStorage.setItem("current_question", JSON.stringify(result.next_question));
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <p className="text-xs font-semibold uppercase tracking-widest text-accent">
        {roleLabel} Interview
      </p>
      <h1 className="mt-2 text-2xl font-semibold tracking-tight">
        Live technical interview
      </h1>

      <div className="mt-8">
        {error && <p className="mb-4 text-sm text-rose-600">{error}</p>}
        {question ? (
          <InterviewChat
            question={question}
            transcript={transcript}
            answerDraft={answerDraft}
            onAnswerChange={setAnswerDraft}
            onSubmit={handleSubmit}
            submitting={submitting}
          />
        ) : (
          <p className="text-sm text-ink/50">Loading question...</p>
        )}
      </div>
    </main>
  );
}
