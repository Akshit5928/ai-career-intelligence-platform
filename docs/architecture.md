# AI Career Intelligence Platform — Architecture

## Goal
Turn internship research into an adaptive learning, portfolio, and application workflow.

## Core flow
Research opportunities → normalize listings → extract recurring skills → match against user skills → identify gaps → recommend learning/projects → track applications → generate approved career updates.

## Backend
- Python / FastAPI for application services
- PostgreSQL / Supabase for persistent state
- LLM + RAG components for career intelligence
- Background workers for research and control-loop execution

## Data domains
- internships and internship sources
- skills and market demand
- projects and project tasks
- applications and interview preparation
- approvals and notifications
- research runs and agent-cycle runs
- GitHub portfolio work and LinkedIn drafts

## Safety and integrity
- No fake GitHub activity or fabricated experience
- No publishing LinkedIn content without approval
- No destructive Git operations without approval
- Secrets stay outside source control
- External changes are reported only after verification

## Runtime
Supabase is the persistent state/control plane. A future hosted worker will provide continuous research and execution; scheduled ChatGPT check-ins are not treated as a permanent daemon.
