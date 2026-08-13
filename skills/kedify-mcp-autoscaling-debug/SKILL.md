---
name: kedify-mcp-autoscaling-debug
description: Use when debugging Kedify autoscaling behavior through the hosted Kedify MCP server, especially when a user asks why a cluster or agent is not scaling, scaling too slowly, scaling unexpectedly, or failing autoscaling checks. Start with `clusters.debug_autoscaling_checks`, then expand to history, trigger health, scaled objects, workload CPU, workload memory, or logs as needed.
---

# Kedify MCP Autoscaling Debug

Use this skill for diagnosis through the hosted Kedify MCP plugin. Prefer it when the user wants to understand current autoscaling health, recent autoscaling failures, trigger behavior, replica pressure, or workload resource pressure.

## Entry point

Start with `clusters.debug_autoscaling_checks` when the user gives a cluster ID or asks a cluster-level debugging question.

If the user gives only an agent ID, start with `agents.debug_scaling_overview`.

## Minimum inputs

You usually need one of:

- `cluster_id`
- `agent_id`

If both are missing, ask for the cluster or agent the user wants to debug.

## Default workflow

1. Run `clusters.debug_autoscaling_checks`.
2. Summarize failing or degraded checks first.
3. If the result suggests a persistent or intermittent issue, run `clusters.debug_autoscaling_check_history`.
4. If the issue looks agent-specific, drill down with:
   - `agents.debug_scaling_overview`
   - `agents.debug_trigger_health`
   - `agents.debug_scaled_objects`
5. If the issue may be caused by workload saturation or missing demand signals, inspect:
   - `agents.debug_workload_cpu`
   - `agents.debug_workload_memory`
6. If the checks suggest controller, webhook, or runtime problems, inspect `agents.logs`.

Read `references/autoscaling-checks.md` when you need help interpreting common patterns.

## Response style

When reporting findings:

- lead with the most actionable failing condition
- separate current-state observations from history-based observations
- say which MCP tool produced each conclusion
- if there is no clear fault, say what was ruled out and what the next best probe is

## Scope

This skill is for diagnosis, not mutation. Prefer read-only debugging guidance unless the user explicitly asks for a remediation plan.
