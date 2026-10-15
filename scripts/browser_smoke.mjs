import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
const { chromium } = createRequire(
  new URL("../frontend/package.json", import.meta.url),
)("playwright");
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1080 } });
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
await page.goto(process.env.UI_URL || "http://127.0.0.1:3000");
await page.getByRole("button", { name: "New incident" }).waitFor();
await page.getByRole("button", { name: "New incident" }).click();
await page.getByRole("combobox").selectOption("db-pool");
await page
  .getByRole("button", { name: "Create incident", exact: true })
  .click();
await page.getByRole("button", { name: "Investigate incident" }).click();
await page
  .getByRole("heading", { name: "Review this recommendation" })
  .waitFor();
await page.getByRole("tab", { name: "evidence" }).click();
await page.getByText("Collected telemetry", { exact: true }).waitFor();
await page.getByRole("tab", { name: "analysis" }).click();
await page
  .getByLabel("Decision note")
  .fill("Reviewed retrieved evidence and database connection budget.");
await page.getByRole("button", { name: "Approve plan" }).click();
await page.getByRole("button", { name: "Execute simulation" }).click();
await page.getByRole("heading", { name: "Simulation verified" }).waitFor();
await page.evaluate(() => window.scrollTo(0, 0));
await page.screenshot({
  path: fileURLToPath(
    new URL("../docs/dashboard-desktop.png", import.meta.url),
  ),
  fullPage: true,
});
await page.getByRole("tab", { name: "activity" }).click();
await page.getByText("simulation executed", { exact: true }).waitFor();
await page.setViewportSize({ width: 390, height: 844 });
await page.getByRole("tab", { name: "analysis" }).click();
await page.evaluate(() => window.scrollTo(0, 0));
await page.screenshot({
  path: fileURLToPath(new URL("../docs/dashboard-mobile.png", import.meta.url)),
  fullPage: true,
});
if (
  await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth,
  )
)
  throw Error("Mobile horizontal overflow");
if (errors.length) throw Error(errors.join("; "));
console.log(
  "PASS: browser create/investigate/evidence/approve/execute/audit + 390px mobile viewport.",
);
await browser.close();
