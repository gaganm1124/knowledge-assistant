# Engineering Onboarding Guide

## Welcome
This guide covers everything you need to get productive in the first two weeks.

## Week 1: Setup and Orientation

### Dev Environment
1. Clone the main repository: `git clone git@github.com:org/knowledge-assistant.git`
2. Copy `.env.example` to `.env` and fill in local values
3. Start local services: `docker compose up -d`
4. Run migrations: `make db-migrate`
5. Confirm the API is healthy: `curl http://localhost:8000/health`

### Key Contacts
| Role | Name | Slack |
|------|------|-------|
| Engineering Lead | Priya S. | @priya |
| Platform On-call | Rotation | #oncall |
| Product Manager | Dario F. | @dario |

### Codebase Tour
- `app/` — FastAPI application code
- `ingestion/` — document chunking and embedding pipeline
- `data/raw/` — source documents (markdown)
- `tests/` — pytest test suite

## Week 2: First Contribution
- Pick up a `good-first-issue` ticket from the backlog
- Open a draft PR early for feedback
- All PRs require one approval before merge
- CI must be green (lint + tests) before merge

## Resources
- Internal wiki: `confluence.internal/engineering`
- Incident history: `#incidents` Slack channel
- Architecture decisions: `docs/adr/`