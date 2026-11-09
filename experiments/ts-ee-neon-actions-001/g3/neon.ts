import { defineConfig } from "@neon/config/v1";

// G3: disposable branch-only policy. No auth, storage or external domain services.
export default defineConfig({
  functions: {
    g3pulse: {
      name: "TS EE G3 synthetic pulse",
      source: "./functions/pulse.ts",
    },
  },
});
