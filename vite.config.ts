import { defineConfig } from "vite";
import { resolve } from "node:path";

export default defineConfig({
  build: {
    outDir: "src/cf_workbench/static/ide",
    emptyOutDir: true,
    sourcemap: false,
    lib: {
      entry: resolve(__dirname, "frontend/ide/main.ts"),
      name: "cfwIdeBundle",
      formats: ["iife"],
      fileName: () => "cfw-ide.iife.js",
    },
  },
});
