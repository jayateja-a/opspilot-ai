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
              id: "db-pool",
              service: "payment-service",
              title: "Pool exhaustion",
              severity: "P1",
              description: "Investigate",
            },
          ];
        if (path === "/api/incidents" && options?.method === "POST")
          data = {
            id: "123",
            service: "payment-service",
            title: "Pool exhaustion",
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
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/incidents",
      expect.objectContaining({
        method: "POST",
        body: expect.stringContaining('"scenarioId":"db-pool"'),
      }),
    );
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
