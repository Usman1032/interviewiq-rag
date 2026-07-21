import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import RoleSelector from "../components/RoleSelector";
import ResumeUpload from "../components/ResumeUpload";
import { api } from "../lib/api";

export default function Home() {
  const router = useRouter();
  const [roles, setRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getRoles().then(setRoles).catch((e) => setError(e.message));
  }, []);

  const canSubmit = file && selectedRole && !loading;

  const handleStart = async () => {
    setError(null);
    setLoading(true);
    try {
      const { candidate_id } = await api.uploadResume(file);
      const session = await api.startInterview(candidate_id, selectedRole);
      sessionStorage.setItem("session_id", session.session_id);
      sessionStorage.setItem("role_label", session.role_label);
      sessionStorage.setItem("current_question", JSON.stringify(session.first_question));
      sessionStorage.setItem("transcript", JSON.stringify([]));
      router.push("/interview");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <p className="text-xs font-semibold uppercase tracking-widest text-accent">
        AI Candidate Screening
      </p>
      <h1 className="mt-2 text-3xl font-semibold tracking-tight">
        Let's set up your interview
      </h1>
      <p className="mt-2 text-sm text-ink/60">
        Upload your resume and pick a role. Questions are generated live from a
        role-specific knowledge base and your background.
      </p>

      <div className="mt-10 space-y-8">
        <section>
          <h2 className="mb-3 text-sm font-medium text-ink/70">1. Select a role</h2>
          <RoleSelector roles={roles} selectedRole={selectedRole} onSelect={setSelectedRole} />
        </section>

        <section>
          <h2 className="mb-3 text-sm font-medium text-ink/70">2. Upload your resume</h2>
          <ResumeUpload onFileSelected={setFile} fileName={file?.name} />
        </section>

        {error && <p className="text-sm text-rose-600">{error}</p>}

        <button
          onClick={handleStart}
          disabled={!canSubmit}
          className="w-full rounded-lg bg-accent px-5 py-3 text-sm font-medium text-white transition disabled:opacity-40"
        >
          {loading ? "Preparing your interview..." : "Start interview"}
        </button>
      </div>
    </main>
  );
}
