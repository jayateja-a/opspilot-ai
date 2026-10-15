export type Scenario = {
  id: string;
  service: string;
  title: string;
  severity: string;
  description: string;
};
export type Analysis = {
  mode: string;
  root_cause: string;
  reasoning: string;
  confidence: number;
  evidence: { id: string; type: string; data: unknown }[];
  citations: {
    chunk_id: string;
    runbook_id: string;
    title: string;
    content: string;
    score: number;
  }[];
  recommendation: {
    action: string;
    risk: string;
    executable: boolean;
    explanation: string;
  };
  warnings: string[];
  tool_calls: { tool: string; status: string }[];
};
export type Incident = {
  id: string;
  service: string;
  title: string;
  description: string;
  severity: string;
  scenario_id: string;
  status: string;
  created_at: string;
  analysis: Analysis | null;
  last_error: string | null;
  events?: { id: number; event: string; created_at: string }[];
  approval?: { reviewer: string; note: string; decision: string } | null;
  execution?: {
    result: {
      receipt: string;
      before: unknown;
      after: unknown;
      verification: string;
    };
  } | null;
};
export type Runbook = {
  id: string;
  service: string;
  title: string;
  content: string;
};
export async function api<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch("/api" + path, {
    method: body === undefined ? "GET" : "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok)
    throw new Error(
      result.error || result.detail || `Request failed (${response.status})`,
    );
  return result;
}
export function canApprove(incident: Incident): boolean {
  return (
    incident.status === "AWAITING_APPROVAL" &&
    incident.analysis?.recommendation.executable === true
  );
}
