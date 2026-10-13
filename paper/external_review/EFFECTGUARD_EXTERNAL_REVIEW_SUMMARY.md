# EffectGuard External Review Summary

## Purpose

EffectGuard studies development-only recovery policies for workflows that may
have ambiguous external effects. A tool call may have committed even when its
acknowledgement is lost; treating that ambiguity as success or failure can
cause duplicate effects or unsafe downstream work.

## Research Question

Under explicit provider receipt, idempotency, verification, compensation, and
invariant assumptions, which recovery-policy tradeoffs arise when external
operation outcomes remain `UNKNOWN`? This is a framework and policy-study
question, not a claim of a new semantic selective-recovery algorithm.

## System and Safety Model

EffectGuard records stable logical operation IDs and provider observations.
Runtime predicates produce `VALID`, `INVALID`, or `UNKNOWN` certificates for
downstream actions. `UNKNOWN` blocks conflicting work or ends unresolved at a
declared evidence deadline; invalid compensable work is planned for repair;
invalid irreversible work is unsupported. The independent evaluator checks
provider state and final invariants rather than terminal status alone. See
`P4_C2_FORMAL_SAFETY_SPECIFICATION.md` and `P4_DEVELOPMENT_EVIDENCE_FREEZE.md`.

## Development Evidence

A real Temporal Java Workflow/Worker/Activity and the EffectGuard runtime ran
one shared provider-script witness with separate fresh local providers. Both
received a retryable pre-commit failure and a lost acknowledgement after a
commit. Provider audits recorded the physical events; both arms recovered with
one retry, two submissions, two verifications, and one valid descendant effect.
This supports only that one development witness, not general correctness,
availability, restart behavior, or superiority.

## Boundaries and Negative Evidence

P3-C9 contains mixed results and is preserved without pooling. P4 restart,
provider interruption, deadline exhaustion, and broad fault-matrix cases are
unverified. S9 UNKNOWN counterexamples remain design tests, not proof. RETRO
already provides history-based repair and selective re-execution; a capable
Temporal application can implement receipt verification and UNKNOWN-aware
application policy. The RETRO-inspired baseline is an adaptation, not RETRO.

## Questions for Independent Review

1. Are the safety assumptions and terminal-state conditions coherent?
2. Does the UNKNOWN receipt policy differ meaningfully from existing repair
   and durable-workflow practice, or is it best treated as a framework?
3. Can an independent curator construct sealed external-effect scenarios from
   WfCommons topology without author bias?
4. What minimum paired evaluation and statistical design would justify a
   research-paper claim?

No independent review has occurred. The requested deliverable is critical
feedback, counterexamples, and limitations, not endorsement or authorship.
