# AI Career Intelligence Platform

An engineering-first career intelligence system that connects internship research, market skill demand, personalized skill gaps, portfolio projects, and application tracking.

## What it does

- Tracks internship opportunities across AI/ML, Data Science, Data Analyst, GenAI, LLM/RAG, AI Engineer, Python/backend, and research roles.
- Extracts recurring skills from real opportunity data.
- Scores opportunities against the user's current skills and constraints.
- Converts skill gaps into learning and portfolio actions.
- Tracks applications, interview preparation, approvals, and reminders.
- Maintains a real GitHub portfolio and approval-gated LinkedIn content workflow.

## Architecture

Research → Normalize → Skill Intelligence → Match → Skill Gap → Project/Learning Plan → Application Pipeline → Career Updates

Persistent state is stored in Supabase. Short-lived API work belongs in FastAPI/Edge Functions; long-running research/execution will run in a hosted worker when the continuous runtime is provisioned.

## Repository layout

```text
backend/       API and application services
research/      opportunity ingestion and source adapters
matching/      opportunity scoring and skill-gap logic
analytics/     market and skill-demand analysis
tests/         automated tests
docs/          architecture and engineering documentation
.github/       CI/CD workflows
```

## Engineering rules

1. Never fabricate GitHub activity, internship data, experience, or metrics.
2. Never publish LinkedIn content without explicit approval.
3. Never commit secrets, tokens, credentials, or private keys.
4. Prefer small, testable modules and deterministic scoring logic.
5. Verify external changes after execution.

## Status

The project foundation is being built incrementally. Supabase already contains the career-agent data model and control-loop backend; this repository is the production engineering layer that will consume it.
