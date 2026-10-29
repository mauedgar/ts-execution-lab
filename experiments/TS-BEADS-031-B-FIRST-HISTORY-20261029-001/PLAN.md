# TS Beads 031 — B-first audit, provider identity, UNKNOWN and alternate writer

**Authority:** Experimental Control only, no Product adoption. Product frozen read-only at `mauedgar/tecnotron-ai:tools@d4154bd43f26515c39a41be974e462a0c7406a2d` tree `cbfb71ad8632047e8e64fe2665d8614d835a2c8b`; SOT blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`. Shared Dolt ref `1f72d68797114170a97fee27641858f2e55a4571` must stay unchanged.

Reproduce on isolated native Beads v1.3.1/Dolt v2.2.0: (1) audit/history and restart readback, (2) frozen external-effect identity as synthetic provider receipt and UNKNOWN reconciliation without retry, (3) causal guard with concurrent gate revision, (4) bypass by privileged direct dependency writer and classification of limits. Use one bounded native Actions attempt and Product-qualified IR-TXT-CARRIER/1. No new state kernel, scheduler, remote provider claim, adoption or TaskCycle.

**Evidence limits:** A local mock or immutable receipt is not a true remote provider; Dolt history requires explicit audit qualification and not an assumption of automatic Product event journal. No privileged writer confinement is proven merely by a secure launcher. Distinguish true native results from simulated evidence.
