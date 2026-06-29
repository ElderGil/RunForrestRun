import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { readFileSync, readdirSync, mkdirSync, copyFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const dataDir = resolve(here, "..", "data");

// Arquivos em data/ que NÃO devem ir para a página: o store bruto (intermediário,
// não é lido pelo app) e qualquer coisa que não seja JSON de raiz. A subpasta
// data/private/ já é ignorada naturalmente (não termina em .json).
const PUBLISH_SKIP = new Set(["activities_raw.json"]);

// Serves /data/*.json from the repo's /data folder in dev, and copies those
// JSONs into the build output so GitHub Pages publishes them alongside the
// app (ADR-002 loaders fetch from BASE_URL + 'data/...'; ADR-004 only ships
// the build, so the data must travel with it).
function serveData() {
  return {
    name: "serve-data",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const m = req.url && req.url.match(/\/data\/([\w.-]+\.json)$/);
        if (!m) return next();
        try {
          const body = readFileSync(resolve(dataDir, m[1]));
          res.setHeader("Content-Type", "application/json");
          res.end(body);
        } catch {
          next();
        }
      });
    },
    closeBundle() {
      const out = resolve(here, "dist", "data");
      mkdirSync(out, { recursive: true });
      for (const f of readdirSync(dataDir)) {
        if (f.endsWith(".json") && !PUBLISH_SKIP.has(f)) {
          copyFileSync(resolve(dataDir, f), resolve(out, f));
        }
      }
    },
  };
}

export default defineConfig(({ command }) => ({
  // Em produção (GitHub Pages) a app vive sob /RunForrestRun/; em dev, na raiz.
  base: command === "build" ? "/RunForrestRun/" : "/",
  plugins: [react(), serveData()],
}));
