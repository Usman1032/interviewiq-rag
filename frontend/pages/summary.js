import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import SummaryCard from "../components/SummaryCard";
import { api } from "../lib/api";

export default function Summary() {
  const router = useRouter();
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const sid = sessionStorage.getItem("session_id");
    if (!sid) {
      router.replace("/");
      return;
    }
    api.getSummary(sid).then(setSummary).catch((e) => setError(e.message));
  }, [router]);

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <p className="text-xs font-semibold uppercase tracking-widest text-accent">
        Interview Complete
      </p>
      <h1 className="mt-2 text-2xl font-semibold tracking-tight">
        Session summary
      </h1>

      <div className="mt-8">
        {error && <p className="text-sm text-rose-600">{error}</p>}
        {!summary && !error && <p className="text-sm text-ink/50">Loading summary...</p>}
        {summary && <SummaryCard summary={summary} />}
      </div>

      <button
        onClick={() => {
          sessionStorage.clear();
          router.push("/");
        }}
        className="mt-10 rounded-lg border border-black/15 px-5 py-2.5 text-sm font-medium hover:border-black/30"
      >
        Start a new interview
      </button>
    </main>
  );
}
