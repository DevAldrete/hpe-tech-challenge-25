# Project AEGIS Roadmap

**Version:** 2.1.0  
**Last Updated:** 2026-03-08

## Current Implemented Baseline

- Runtime contracts in place: `Clock`, `MessageBus`, telemetry/alert persistence sinks.
- Transport adapters in place: Redis runtime and in-memory deterministic test bus.
- Explicit registration + telemetry + alert + alert-cleared flow implemented.
- Dispatch lifecycle implemented with ack tracking, ETA estimate, and unit-role assignment.
- Emergency lifecycle automation implemented (cancel, auto-resolve, dismiss rules).
- Fast-forward simulation mode integrated into API runtime and E2E tests.
- Navigation provider abstraction implemented with geometric default and optional OSMnx pathing.

## Near-Term Priorities

### 1) Dispatch quality and realism

- Improve ETA model beyond static average-speed heuristics.
- Incorporate route quality metadata (distance source, confidence).
- Add configurable dispatch strategy options beyond nearest-available.

### 2) Reliability and resilience coverage

- Add E2E for partial dispatch acknowledgments and ack timeouts.
- Add E2E for high alert volume and persistence lag behavior.
- Add E2E for sweeper transitions across all terminal statuses.

### 3) Observability and operational diagnostics

- Add metrics for dispatch latency, ack latency, and unresolved emergency age.
- Add metrics for telemetry buffer depth and flush failures.
- Expand health diagnostics to include message bus and persistence readiness.

## Medium-Term

- Add replay-ready event archive for post-incident analysis.
- Introduce richer domain event taxonomy for analytics consumers.
- Isolate heavy analytics/reporting workloads from orchestrator process.

## Background Job Queue Position

Task queue adoption remains optional and must stay out of the real-time dispatch control path.

- Keep pub/sub channels as source for control events.
- Use queue workers only for non-latency-critical tasks such as:
  - analytics rollups,
  - enrichment pipelines,
  - route precomputation,
  - scheduled offline maintenance workflows.
