import {
  render,
  screen,
  fireEvent,
  waitFor,
  cleanup,
} from "@testing-library/react";
import { describe, it, expect, vi, afterEach } from "vitest";
import App from "./App";
import { canApprove, type Incident } from "./api";
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});
describe("approval policy", () => {
  it("needs both awaiting state and executable evidence", () => {
    const i = {
      status: "AWAITING_APPROVAL",
      analysis: { recommendation: { executable: true } },
    } as Incident;
    expect(canApprove(i)).toBe(true);
    expect(canApprove({ ...i, status: "OPEN" })).toBe(false);
    expect(canApprove({ ...i, analysis: null })).toBe(false);
  });
});
describe("dashboard", () => {
  it("creates a scenario through the control plane", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockImplementation(async (url, options) => {
        const path = String(url);
        let data: unknown = [];
        if (path === "/api/scenarios")
          data = [
            {
              id: "commerce-db-pool",
              service: "checkout-service",
              title: "E-commerce checkout pool exhaustion",
              severity: "P1",
              description: "Investigate",
            },
          ];
        if (path === "/api/incidents" && options?.method === "POST")
          data = {
            id: "123",
            service: "checkout-service",
            title: "E-commerce checkout pool exhaustion",
            description: "Investigate",
            severity: "P1",
            status: "OPEN",
            analysis: null,
            created_at: new Date().toISOString(),
          };
        return { ok: true, json: async () => data } as Response;
      });
    render(<App />);
    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: "New incident" }),
      ).toBeEnabled(),
    );
    fireEvent.click(screen.getByRole("button", { name: "New incident" }));
    fireEvent.click(screen.getByRole("button", { name: "Create incident" }));
    await screen.findByRole("button", { name: "Investigate incident" });
    expect(screen.getByRole("tablist")).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /analysis/i })).toHaveAttribute(
      "aria-selected",
      "true",
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/incidents",
      expect.objectContaining({
        method: "POST",
        body: expect.stringContaining('"scenarioId":"commerce-db-pool"'),
      }),
    );
  });

  it("filters the expanded scenario catalog by priority and symptom", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(async (url) => {
      const path = String(url);
      const data = path === "/api/scenarios" ? [
        { id: "commerce-db-pool-p0", service: "checkout", title: "Database pool exhaustion", severity: "P0", description: "Connections exhausted" },
        { id: "commerce-queue-p5", service: "worker", title: "Queue backlog", severity: "P5", description: "Queue depth elevated" },
      ] : [];
      return { ok: true, json: async () => data } as Response;
    });
    render(<App />);
    fireEvent.click(await screen.findByRole("button", { name: "New incident" }));
    fireEvent.change(screen.getByPlaceholderText(/search service/i), { target: { value: "P0" } });
    expect(screen.getByText("1 matching scenarios")).toBeInTheDocument();
    expect(screen.getByRole("option", { name: /P0 · Database pool exhaustion/ })).toBeInTheDocument();
    expect(screen.queryByRole("option", { name: /P5 · Queue backlog/ })).not.toBeInTheDocument();
  });

  it("opens the ITSM workspace for CIs, Problems, and Changes", async () => {
    vi.spyOn(globalThis,"fetch").mockImplementation(async()=>({ok:true,json:async()=>[]} as Response));
    render(<App/>);
    await screen.findByRole("button",{name:/ITSM records/});
    fireEvent.click(screen.getByRole("button",{name:/ITSM records/}));
    expect(await screen.findByText("Configuration items")).toBeInTheDocument();
    expect(screen.getByRole("button",{name:"Create Problem"})).toBeEnabled();
    expect(screen.getByRole("button",{name:"Create Change"})).toBeEnabled();
  });
});
