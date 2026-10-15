import { useEffect, useState } from "react";
import {
  Activity,
  ArrowRight,
  BookOpen,
  Check,
  ChevronRight,
  CircleDot,
  ClipboardCheck,
  Cpu,
  LoaderCircle,
  Play,
  Plus,
  Radar,
  ShieldCheck,
  Terminal,
  X,
} from "./icons";
import {
  api,
  canApprove,
  type Scenario,
  type Incident,
  type Runbook,
} from "./api";
const readable = (s: string) => s.replaceAll("_", " ").toLowerCase();
export default function App() {
  const [incidents, setIncidents] = useState<Incident[]>([]),
    [scenarios, setScenarios] = useState<Scenario[]>([]),
    [books, setBooks] = useState<Runbook[]>([]);
  const [selected, setSelected] = useState<Incident | null>(null),
    [page, setPage] = useState<"incidents" | "runbooks">("incidents");
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [createOpen, setCreateOpen] = useState(false),
    [scenarioId, setScenarioId] = useState("db-pool");
  const [reviewer, setReviewer] = useState("Local operator"),
    [note, setNote] = useState(""),
    [tab, setTab] = useState<"analysis" | "evidence" | "activity">("analysis");
  const [bookTitle, setBookTitle] = useState(""),
    [bookService, setBookService] = useState("payment-service"),
    [bookContent, setBookContent] = useState("");
  async function load() {
    const [i, s, b] = await Promise.all([
      api<Incident[]>("/incidents"),
      api<Scenario[]>("/scenarios"),
      api<Runbook[]>("/runbooks"),
    ]);
    setIncidents(i);
    setScenarios(s);
    setBooks(b);
    return i;
  }
  useEffect(() => {
    load().catch((e) => setError(e.message));
  }, []);
  async function work(fn: () => Promise<void>) {
    setBusy(true);
    setError("");
    try {
      await fn();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }
  async function choose(i: Incident) {
    await work(async () => {
      setSelected(await api<Incident>("/incidents/" + i.id));
      setNote("");
      setTab("analysis");
    });
  }
  async function create() {
    await work(async () => {
      const s = scenarios.find((x) => x.id === scenarioId);
      if (!s) throw new Error("Select a scenario");
      const i = await api<Incident>("/incidents", {
        service: s.service,
        title: s.title,
        description: s.description,
        severity: s.severity,
        scenarioId: s.id,
      });
      setSelected(i);
      setCreateOpen(false);
      setTab("analysis");
      await load();
    });
  }
  async function action(suffix: string, body: unknown = {}) {
    if (!selected) return;
    await work(async () => {
      setSelected(
        await api<Incident>(`/incidents/${selected.id}/${suffix}`, body),
      );
      await load();
    });
  }
  const a = selected?.analysis;
  const resolved = incidents.filter((x) => x.status === "RESOLVED").length;
  const pending = incidents.filter(
    (x) => x.status === "AWAITING_APPROVAL",
  ).length;
  return (
    <div className="shell">
      <aside className="sidebar">
        <a className="brand" href="#" onClick={(e) => e.preventDefault()}>
          <span className="brand-icon">
            <Radar size={24} />
          </span>
          OpsPilot<span className="ai-label">AI</span>
        </a>
        <div className="workspace-label">
          LOCAL WORKSPACE <span className="live-dot" />
        </div>
        <nav aria-label="Main navigation">
          <button
            className={page === "incidents" ? "active" : ""}
            onClick={() => setPage("incidents")}
          >
            <Activity size={18} />
            Incidents<span>{incidents.length}</span>
          </button>
          <button
            className={page === "runbooks" ? "active" : ""}
            onClick={() => setPage("runbooks")}
          >
            <BookOpen size={18} />
            Runbook library<span>{books.length}</span>
          </button>
        </nav>
        <div className="side-note">
          <ShieldCheck size={20} />
          <strong>Human control, always.</strong>
          <p>
            Every action needs your approval. Remediation runs in a simulation.
          </p>
        </div>
        <div className="sidebar-footer">
          <span className="avatar">OP</span>
          <div>
            Local operator<small>Development environment</small>
          </div>
        </div>
      </aside>
      <main>
        <header className="topbar">
          <span>
            Workspace <ChevronRight size={14} />
            <b>
              {page === "incidents" ? "Incident operations" : "Runbook library"}
            </b>
          </span>
          <span className="environment">
            <span className="live-dot" /> LOCAL SIMULATION
          </span>
        </header>
        <div className="content">
          <div className="heading">
            <div className="eyebrow">
              OPERATIONS / {page === "incidents" ? "OVERVIEW" : "KNOWLEDGE"}
            </div>
            <h1>
              {page === "incidents"
                ? "A clearer path to resolution."
                : "Your operational knowledge."}
            </h1>
            <p>
              {page === "incidents"
                ? "Investigate with evidence. Review the plan. Stay in control."
                : "Versioned procedures, retrieved with PostgreSQL + pgvector."}
            </p>
            {page === "incidents" && (
              <button
                className="primary heading-button"
                onClick={() => setCreateOpen(true)}
                disabled={busy || !scenarios.length}
              >
                <Plus size={16} />
                New incident
              </button>
            )}
          </div>
          {error && (
            <div className="error" role="alert">
              <X size={16} />
              {error}
              <button onClick={() => setError("")} aria-label="Dismiss error">
                <X size={16} />
              </button>
            </div>
          )}
          {page === "incidents" ? (
            <>
              <div className="stats">
                <div>
                  <span>INCIDENTS</span>
                  <strong>{String(incidents.length).padStart(2, "0")}</strong>
                  <small>Total in this workspace</small>
                </div>
                <div>
                  <span>AWAITING APPROVAL</span>
                  <strong className="amber">
                    {String(pending).padStart(2, "0")}
                  </strong>
                  <small>Decisions in your hands</small>
                </div>
                <div>
                  <span>RESOLVED</span>
                  <strong className="mint">
                    {String(resolved).padStart(2, "0")}
                  </strong>
                  <small>Verified in simulation</small>
                </div>
                <div className="system-status">
                  <Cpu size={22} />
                  <span>10 reproducible scenarios</span>
                  <small>Demo reasoning / optional OpenAI</small>
                </div>
              </div>
              <div className="incident-grid">
                <section className="incident-list panel">
                  <div className="panel-heading">
                    <h2>Incident queue</h2>
                    <span className="muted">{incidents.length} total</span>
                  </div>
                  {incidents.length === 0 ? (
                    <div className="empty">
                      <CircleDot size={30} />
                      <h3>Your workspace is ready.</h3>
                      <p>Create an incident to start investigating.</p>
                      <button
                        className="text-button"
                        onClick={() => setCreateOpen(true)}
                      >
                        Try a sample scenario <ArrowRight size={14} />
                      </button>
                    </div>
                  ) : (
                    incidents.map((i) => (
                      <button
                        key={i.id}
                        className={
                          "incident-row " +
                          (selected?.id === i.id ? "selected" : "")
                        }
                        onClick={() => choose(i)}
                        disabled={busy}
                      >
                        <div>
                          <span className={"severity " + i.severity}>
                            {i.severity}
                          </span>
                          <span className={"status " + i.status}>
                            {readable(i.status)}
                          </span>
                        </div>
                        <strong>{i.title}</strong>
                        <small>
                          <Terminal size={12} />
                          {i.service}
                        </small>
                      </button>
                    ))
                  )}
                </section>
                <section className="detail panel">
                  {selected ? (
                    <>
                      <div className="detail-heading">
                        <div>
                          <span className="eyebrow">
                            INCIDENT / {selected.id.slice(0, 8)}
                          </span>
                          <h2>{selected.title}</h2>
                          <p>
                            {selected.service} <span>·</span>{" "}
                            {selected.severity}
                          </p>
                        </div>
                        <span className={"status " + selected.status}>
                          {readable(selected.status)}
                        </span>
                      </div>
                      <div className="tabs" role="tablist">
                        {(["analysis", "evidence", "activity"] as const).map(
                          (t) => (
                            <button
                              key={t}
                              role="tab"
                              aria-selected={tab === t}
                              className={tab === t ? "active" : ""}
                              onClick={() => setTab(t)}
                            >
                              {t}
                            </button>
                          ),
                        )}
                      </div>
                      {tab === "analysis" ? (
                        <div className="detail-content">
                          {!a ? (
                            <div className="investigate">
                              <span className="investigate-icon">
                                <Radar size={34} />
                              </span>
                              <h3>Start with the evidence.</h3>
                              <p>{selected.description}</p>
                              {selected.last_error && (
                                <div className="error">
                                  {selected.last_error}
                                </div>
                              )}
                              <button
                                className="primary"
                                disabled={busy}
                                onClick={() => action("analyze")}
                              >
                                {busy ? (
                                  <LoaderCircle className="spin" size={16} />
                                ) : (
                                  <Play size={16} />
                                )}
                                Investigate incident
                              </button>
                              <small>
                                Logs + metrics → runbook retrieval →
                                recommendation
                              </small>
                            </div>
                          ) : (
                            <>
                              <div className="analysis-meta">
                                <span>
                                  <span className="live-dot" />
                                  {a.mode === "demo"
                                    ? "Deterministic demo"
                                    : "OpenAI reasoning"}
                                </span>
                                <span>
                                  {Math.round(a.confidence * 100)}%{" "}
                                  {a.mode === "demo"
                                    ? "fixture score"
                                    : "model confidence"}
                                </span>
                              </div>
                              <div className="root-cause">
                                <div className="eyebrow">
                                  ROOT CAUSE HYPOTHESIS
                                </div>
                                <h3>{a.root_cause}</h3>
                                <p>{a.reasoning}</p>
                              </div>
                              <div className="recommendation">
                                <div className="panel-heading">
                                  <h3>
                                    <ClipboardCheck size={17} />
                                    Recommended action
                                  </h3>
                                  <span
                                    className={"risk " + a.recommendation.risk}
                                  >
                                    {a.recommendation.risk} RISK
                                  </span>
                                </div>
                                <code>{a.recommendation.action}</code>
                                <p>{a.recommendation.explanation}</p>
                                <div className="safety">
                                  <ShieldCheck size={14} />
                                  Human approval required · simulated execution
                                </div>
                              </div>
                              {selected.status === "AWAITING_APPROVAL" && (
                                <div className="approval-form">
                                  <h3>Review this recommendation</h3>
                                  <label>
                                    Reviewer
                                    <input
                                      value={reviewer}
                                      onChange={(e) =>
                                        setReviewer(e.target.value)
                                      }
                                      maxLength={80}
                                    />
                                  </label>
                                  <label>
                                    Decision note
                                    <textarea
                                      placeholder="What did you verify before deciding?"
                                      value={note}
                                      onChange={(e) => setNote(e.target.value)}
                                      maxLength={2000}
                                    />
                                  </label>
                                  <div className="button-row">
                                    <button
                                      className="primary"
                                      disabled={
                                        busy ||
                                        !canApprove(selected) ||
                                        !note.trim() ||
                                        !reviewer.trim()
                                      }
                                      onClick={() =>
                                        action("approval", {
                                          decision: "APPROVE",
                                          reviewer,
                                          note,
                                        })
                                      }
                                    >
                                      <Check size={15} />
                                      Approve plan
                                    </button>
                                    <button
                                      className="secondary"
                                      disabled={
                                        busy || !note.trim() || !reviewer.trim()
                                      }
                                      onClick={() =>
                                        action("approval", {
                                          decision: "REJECT",
                                          reviewer,
                                          note,
                                        })
                                      }
                                    >
                                      <X size={15} />
                                      Reject
                                    </button>
                                  </div>
                                </div>
                              )}
                              {selected.status === "APPROVED" && (
                                <div className="execution-ready">
                                  <p>
                                    Approved by {selected.approval?.reviewer}.
                                    Ready for simulated execution.
                                  </p>
                                  <button
                                    className="primary"
                                    disabled={busy}
                                    onClick={() => action("execute")}
                                  >
                                    <Play size={15} />
                                    Execute simulation
                                  </button>
                                </div>
                              )}
                              {selected.status === "REJECTED" && (
                                <div className="safety">
                                  Recommendation rejected. No action executed.
                                </div>
                              )}
                              {selected.execution && (
                                <div className="execution-result">
                                  <h3>
                                    <Check size={18} />
                                    Simulation verified
                                  </h3>
                                  <p>
                                    {selected.execution.result.verification}
                                  </p>
                                  <div className="metrics-compare">
                                    <div>
                                      <span>BEFORE</span>
                                      <pre>
                                        {JSON.stringify(
                                          selected.execution.result.before,
                                          null,
                                          2,
                                        )}
                                      </pre>
                                    </div>
                                    <div>
                                      <span>AFTER</span>
                                      <pre>
                                        {JSON.stringify(
                                          selected.execution.result.after,
                                          null,
                                          2,
                                        )}
                                      </pre>
                                    </div>
                                  </div>
                                  <small>
                                    Receipt{" "}
                                    {selected.execution.result.receipt.slice(
                                      0,
                                      16,
                                    )}
                                    …
                                  </small>
                                </div>
                              )}
                              <p className="fineprint">
                                {a.warnings.join(" ")}
                              </p>
                            </>
                          )}
                        </div>
                      ) : tab === "evidence" ? (
                        <div className="detail-content">
                          <h3>Collected telemetry</h3>
                          {a?.evidence.map((e) => (
                            <div className="evidence" key={e.id}>
                              <span className="eyebrow">{e.id}</span>
                              <pre>{JSON.stringify(e.data, null, 2)}</pre>
                            </div>
                          ))}
                          <h3>Retrieved runbooks</h3>
                          {a?.citations.map((c) => (
                            <details className="citation" key={c.chunk_id}>
                              <summary>
                                <BookOpen size={16} />
                                {c.title}
                                <small>{c.score.toFixed(3)} similarity</small>
                              </summary>
                              <p>{c.content}</p>
                              <code>{c.runbook_id}</code>
                            </details>
                          ))}
                          {!a && (
                            <p className="muted">
                              Run an investigation to collect evidence.
                            </p>
                          )}
                        </div>
                      ) : (
                        <div className="detail-content">
                          <h3>Audit trail</h3>
                          <div className="timeline">
                            {selected.events?.map((e) => (
                              <div key={e.id}>
                                <span className="timeline-dot" />
                                <strong>{readable(e.event)}</strong>
                                <small>
                                  {new Date(e.created_at).toLocaleString()}
                                </small>
                              </div>
                            ))}
                          </div>
                          {a && (
                            <>
                              <h3>Agent tool calls</h3>
                              {a.tool_calls.map((t, n) => (
                                <div className="tool-call" key={n}>
                                  <code>{t.tool}</code>
                                  <span>{t.status}</span>
                                </div>
                              ))}
                            </>
                          )}
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="empty large">
                      <Radar size={44} />
                      <h3>Every incident has a story.</h3>
                      <p>
                        Select an incident to see its evidence,
                        <br />
                        investigation, and next steps.
                      </p>
                      <span className="safety">
                        <ShieldCheck size={14} />
                        Approval comes before action
                      </span>
                    </div>
                  )}
                </section>
              </div>
            </>
          ) : (
            <div className="books-grid">
              <section className="panel book-list">
                <div className="panel-heading">
                  <h2>Runbooks</h2>
                  <span>{books.length} procedures</span>
                </div>
                {books.map((b) => (
                  <details key={b.id} className="book">
                    <summary>
                      <BookOpen size={17} />
                      <div>
                        <strong>{b.title}</strong>
                        <small>{b.service}</small>
                      </div>
                      <ChevronRight size={16} />
                    </summary>
                    <p>{b.content}</p>
                    <code>{b.id}</code>
                  </details>
                ))}
              </section>
              <form
                className="panel ingest-form"
                onSubmit={(e) => {
                  e.preventDefault();
                  work(async () => {
                    await api("/runbooks", {
                      id: "custom-" + crypto.randomUUID(),
                      service: bookService,
                      title: bookTitle,
                      content: bookContent,
                    });
                    setBookTitle("");
                    setBookContent("");
                    await load();
                  });
                }}
              >
                <h2>Add knowledge</h2>
                <p>
                  Runbooks are chunked, embedded, and indexed for retrieval.
                  Custom procedures require manual review.
                </p>
                <label>
                  Service
                  <input
                    required
                    value={bookService}
                    onChange={(e) => setBookService(e.target.value)}
                    maxLength={80}
                  />
                </label>
                <label>
                  Title
                  <input
                    required
                    value={bookTitle}
                    onChange={(e) => setBookTitle(e.target.value)}
                    maxLength={160}
                  />
                </label>
                <label>
                  Procedure
                  <textarea
                    required
                    value={bookContent}
                    onChange={(e) => setBookContent(e.target.value)}
                    maxLength={16000}
                    rows={9}
                  />
                </label>
                <button className="primary" disabled={busy}>
                  <Plus size={15} />
                  Ingest runbook
                </button>
              </form>
            </div>
          )}
          <footer className="footer">
            <span>
              OpsPilot AI <span> / </span> Local MVP
            </span>
            <span>Evidence first. Human approved.</span>
          </footer>
        </div>
      </main>
      {createOpen && (
        <div className="modal-overlay">
          <section
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="new-title"
          >
            <div className="panel-heading">
              <h2 id="new-title">Create an incident</h2>
              <button
                className="icon-button"
                aria-label="Close"
                onClick={() => setCreateOpen(false)}
              >
                <X size={20} />
              </button>
            </div>
            <p>
              Choose a reproducible scenario. Each includes telemetry and a
              matching runbook.
            </p>
            <label>
              Scenario
              <select
                value={scenarioId}
                onChange={(e) => setScenarioId(e.target.value)}
              >
                {scenarios.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.title} · {s.service}
                  </option>
                ))}
              </select>
            </label>
            <div className="scenario-preview">
              <span className="eyebrow">SIMULATED INCIDENT</span>
              <h3>{scenarios.find((s) => s.id === scenarioId)?.title}</h3>
              <p>{scenarios.find((s) => s.id === scenarioId)?.description}</p>
            </div>
            <button className="primary" disabled={busy} onClick={create}>
              <Plus size={15} />
              {busy ? "Creating…" : "Create incident"}
            </button>
          </section>
        </div>
      )}
    </div>
  );
}
