# Runbook: Deployment Rollback

## Overview
Use this runbook when a production deployment needs to be reverted due to errors,
performance regression, or failed health checks.

## Prerequisites
- Access to the CI/CD pipeline dashboard
- Write access to the deployment repository
- Credentials for the container registry

## Steps

### 1. Identify the Last Stable Build
```bash
git log --oneline --tags --decorate | head -20
```
Note the tag of the last known-good release.

### 2. Trigger a Rollback via CI
Navigate to the pipeline dashboard and re-run the deployment job for the target tag.

Or via CLI:
```bash
./scripts/deploy.sh --tag <previous-tag> --env production
```

### 3. Verify Health
- Check the `/health` endpoint returns `200 OK`
- Monitor error rate in Grafana for 10 minutes
- Confirm no new alerts are firing

### 4. Notify Stakeholders
Post in `#incidents` Slack channel with:
- What was rolled back
- Reason for rollback
- Current status

## Post-Rollback
Open a follow-up ticket to investigate the failed deployment before re-attempting.