import { defineConfig } from "@neon/config/v1";

// Separate G5 synthetic candidate: one Function, no Product service toggles.
export default defineConfig({
  functions: {
    g5failure: {name:"TS EE G5 synthetic first-failure/recovery",source:"./functions/failure.ts"},
  },
});
