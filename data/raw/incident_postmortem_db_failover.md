# Incident Postmortem: Primary Database Failover

## Summary
On 2026-01-12, the primary PostgreSQL instance experienced elevated write latency
that caused cascading timeouts across the API tier.

## Detection
The issue was detected by p95 write latency alerts firing at 08:43 UTC.
On-call engineer was paged within 2 minutes.

## Immediate Mitigation
Traffic was shifted to the replica after confirming replication lag was below threshold.
Write latency returned to baseline within 5 minutes of failover.

## Failover Procedure
1. Confirm replica health
2. Freeze schema changes
3. Promote replica
4. Update service connection strings
5. Restart write-heavy workers
6. Monitor error rate and write latency

## Root Cause
A long-running analytics query held a table lock, blocking subsequent write transactions
from completing. The query originated from a misconfigured BI connector with no timeout set.

## Follow-up
- Added query timeout of 30s on the analytics read replica
- Added automated replica health checks
- Runbook updated with lock investigation steps