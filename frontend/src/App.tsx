import { useState } from "react";

type HintResponse = { hint: string; source: string };

export default function App() {
  const [hint, setHint] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);

  async function requestHint() {
    setBusy(true);
    try {
      const res = await fetch("/api/v1/hint", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ misconception_id: "demo.misconception" })
      });
      const data = (await res.json()) as HintResponse;
      setHint(`${data.hint}  (source: ${data.source})`);
    } catch (e) {
      setHint(`error: ${String(e)}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{ fontFamily: "system-ui, sans-serif", padding: 24, maxWidth: 720 }}>
      <h1>Agelgil-AI</h1>
      <p>Split-stack dev surface. Replaced in P3.05.</p>
      <button onClick={requestHint} disabled={busy}>
        {busy ? "asking mock SLM…" : "ask mock SLM for a hint"}
      </button>
      {hint && <pre style={{ marginTop: 16, padding: 12, background: "#f4f4f4" }}>{hint}</pre>}
    </main>
  );
}
