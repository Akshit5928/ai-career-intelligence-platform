const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '').replace(/\/api$/, '')

export type Opportunity = { id: string; internship_id: string; score: number; skill_score: number; role_score: number; location_score: number; eligibility_score: number; deadline_score: number; missing_skills: string[]; reasons: string[]; calculated_at: string; internships: { company_name: string; role_title: string; role_category: string; location: string | null; work_mode: string | null; stipend: string | number | null; deadline: string | null; application_url: string | null } }
export type MarketSkill = { skill_name: string; demand_count: number; demand_share: number; user_proficiency: number; target_proficiency: number; gap_score: number; priority: string }
export type AgentCycle = { id: string; started_at: string; finished_at: string | null; status: string; discovered_count: number; new_matches: number; alerts_created: number; skill_updates: number; applications_due: number; error_message: string | null }
export type ResearchRun = { id: string; source_id: string; started_at: string; finished_at: string | null; status: string; opportunities_found: number; opportunities_new: number; error_message: string | null }

const DIRECT_API_BASE = 'http://127.0.0.1:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const options = { ...init, headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) } }
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, options)
  } catch (firstError) {
    if (API_BASE_URL === '') {
      response = await fetch(`${DIRECT_API_BASE}${path}`, options)
    } else throw firstError
  }
  if (!response.ok) throw new Error(`${path} → API ${response.status}: ${await response.text()}`)
  return response.json()
}

export const api = {
  getMatches: (limit = 100) => request<Opportunity[]>(`/api/v1/matches?limit=${limit}`),
  getMarketSkills: (limit = 100) => request<MarketSkill[]>(`/api/v1/market/skills?limit=${limit}`),
  getAgentCycles: (limit = 10) => request<AgentCycle[]>(`/api/v1/agent/cycles?limit=${limit}`),
  getResearchRuns: (limit = 20) => request<ResearchRun[]>(`/api/v1/research/runs?limit=${limit}`),
  refreshMatches: () => request<{ processed: number; calculated_at: string }>('/api/v1/match/refresh', { method: 'POST' }),
  refreshMarket: () => request('/api/v1/market/refresh', { method: 'POST' }),
  runCycle: () => request('/api/v1/agent/cycle', { method: 'POST' }),
  getLinkedInDrafts: (limit = 20) => request<any[]>(`/api/v1/linkedin/drafts?limit=${limit}`),
  getProjects: (limit = 30) => request<any[]>(`/api/v1/portfolio/projects?limit=${limit}`),
  getSystemStatus: () => request<any>('/api/v1/system/status'),
}
