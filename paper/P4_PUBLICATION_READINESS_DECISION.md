# P4 Publication Readiness Decision

## Current Direction

The evidence does not support a full recovery-policy empirical paper. The most
defensible near-term output is a narrower technical report or artifact and
experience paper about a reproducible development harness for ambiguous
external effects, with explicit limitations. An evaluation-framework paper
requires independent benchmark and correctness review.

An algorithmic novelty claim is not supported. RETRO and durable workflow
systems already motivate semantic dependencies, selective repair, retries, and
application logic. Temporal is a capability-matched programmable baseline.

## External Validation Gate

Human-dependent requirements:

- An independent curator selects licensed held-out workflows and approves
  annotations, invariants, and hidden truth.
- A distributed-systems reviewer assesses safety assumptions, UNKNOWN rules,
  receipt persistence assumptions, and counterexamples.
- A statistical reviewer approves the template-level estimand, sensitivity,
  missing-data, multiplicity, and stopping rules.
- Temporal and RETRO reviewers assess baseline fidelity and capability mapping.

Technical requirements:

- Complete shared-provider fault exposure for restart, interruption, deadline,
  retry exhaustion, compensation, duplicate, and irreversible controls.
- Persist provider audit references in both runtime traces.
- Deliver a curator-sealed evaluator and one-command reproducible analysis.
- Freeze a confirmatory protocol only after external signoff.

## Publication Choice

Do not submit a comparative superiority paper at this stage. A technical report
can transparently present the implementation and the one verified witness. A
workshop or artifact/experience venue is more realistic than an ICSE/FSE
research-track claim until the external-validation gate is satisfied.

DEVELOPMENT EVIDENCE INCOMPLETE — NARROW PUBLICATION SCOPE
