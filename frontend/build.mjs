import { buildSync } from "esbuild";
import {
  mkdirSync,
  rmSync,
  readFileSync,
  writeFileSync,
  cpSync,
} from "node:fs";
rmSync("dist", { recursive: true, force: true });
mkdirSync("dist/assets", { recursive: true });
buildSync({
  entryPoints: ["src/main.tsx"],
  bundle: true,
  minify: true,
  sourcemap: true,
  target: "es2022",
  format: "esm",
  jsx: "automatic",
  outfile: "dist/assets/app.js",
  define: { "process.env.NODE_ENV": '"production"' },
});
cpSync("public", "dist", { recursive: true });
writeFileSync(
  "dist/index.html",
  readFileSync("index.html", "utf8").replace("/src/main.tsx", "/assets/app.js"),
);
console.log("React production bundle built in dist/");
