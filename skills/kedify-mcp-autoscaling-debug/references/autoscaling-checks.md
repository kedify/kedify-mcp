# Autoscaling Checks Reference

Use this reference when `clusters.debug_autoscaling_checks` or `agents.debug_trigger_health` returns checks that need interpretation.

## Reading order

1. Look for failing checks.
2. Look for degraded or warning-like checks.
3. Only after that, read passing checks for confirmation.

## Useful patterns

### Current checks are failing

This usually means there is an active problem worth describing immediately.

Common next steps:

- inspect history to see whether the problem is new or recurring
- inspect agent trigger health to see whether triggers are unhealthy
- inspect logs if the failure looks like controller or webhook behavior

### Current checks are healthy, but the user reports problems

This often means:

- the issue is intermittent
- the issue already recovered
- the issue is outside the current autoscaling control-plane view

Next step: run `clusters.debug_autoscaling_check_history`.

### Results are sparse or empty

This can indicate:

- autoscaling inputs are missing
- no scaled objects are active for the target
- metrics are unavailable
- the selected cluster or agent is not the right scope

Next steps:

- inspect scaled objects
- inspect workload CPU and memory
- confirm the target cluster or agent

### Trigger health is bad, but resource pressure is low

This points more toward trigger configuration, scaler wiring, or metrics ingestion than raw workload saturation.

Next steps:

- inspect `agents.debug_trigger_health`
- inspect `agents.debug_scaled_objects`
- inspect `agents.logs`

### Resource pressure is high, but checks are healthy

This suggests the autoscaling control plane may be healthy while workload sizing or trigger thresholds are not aligned with expectations.

Next steps:

- inspect CPU and memory series
- compare usage with requests and limits
- inspect scaled object bounds and current replicas
