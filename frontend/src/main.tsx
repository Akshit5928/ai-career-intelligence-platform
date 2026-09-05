import React from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'
import { api, type MarketSkill, type Opportunity } from './lib/api'

type Skill = { name: string; demand: number; proficiency: number; gap: number }

function App() {
  const [tab, setTab] = React.useState('Overview')
  const [refreshing, setRefreshing] = React.useState(false)
  const [matches, setMatches] = React.useState<Opportunity[]>([])
  const [skills, setSkills] = React.useState<MarketSkill[]>([])
  const [error, setError] = React.useState('')

  const loadLiveData = React.useCallback(async () => {
    setError('')
    try {
      const [liveMatches, liveSkills] = await Promise.all([api.getMatches(), api.getMarketSkills()])
      setMatches(liveMatches)
      setSkills(liveSkills)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to connect to the career API')
    }
  }, [])

  React.useEffect(() => { loadLiveData() }, [loadLiveData])

  const refresh = async () => {
    setRefreshing(true)
    try {
      await Promise.all([api.refreshMatches(), api.refreshMarket()])
      await loadLiveData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Refresh failed')
    } finally { setRefreshing(false) }
  }

  const highMatches = matches.filter(m => m.score >= 75).length
  const readiness = skills.length ? Math.round(skills.reduce((sum, s) => sum + s.user_proficiency, 0) / skills.length) : 0

  return <div className="app">
    <aside className="sidebar">
      <div className="brand"><div className="logo">AI</div><div><b>Career Intelligence</b><span>Personal Agent</span></div></div>
      <nav>{['Overview', 'Opportunities', 'Skill Intelligence', 'Applications', 'GitHub', 'LinkedIn', 'Research Agent'].map(item =>
        <button className={tab === item ? 'nav active' : 'nav'} onClick={() => setTab(item)} key={item}><span>{icon(item)}</span>{item}</button>
      )}</nav>
      <div className="agent-card"><div className="live"><i /> Agent online</div><strong>Continuous monitoring</strong><p>Research, matching and skill intelligence are connected.</p><button onClick={refresh}>{refreshing ? 'Refreshing…' : 'Run cycle now'}</button></div>
    </aside>

    <main>
      <header><div><p className="eyebrow">SUNDAY · SEPTEMBER 6, 2026</p><h1>{tab}</h1><p className="sub">Your career command center — opportunities, skills and actions in one place.</p></div><div className="header-actions"><button className="ghost" onClick={refresh}>↻ {refreshing ? 'Syncing' : 'Sync now'}</button><div className="avatar">AJ</div></div></header>
      {error && <div className="error">API connection issue: {error}. Start the FastAPI backend and set <code>VITE_API_BASE_URL</code> if it is not running on port 8000.</div>}

      {tab === 'Overview' && <Overview matches={matches} skills={skills} highMatches={highMatches} readiness={readiness} setTab={setTab} refresh={refresh} />}
      {tab === 'Opportunities' && <Opportunities matches={matches} />}
      {tab === 'Skill Intelligence' && <SkillIntelligence skills={skills} />}
      {!['Overview', 'Opportunities', 'Skill Intelligence'].includes(tab) && <section className="panel page-placeholder"><div className="big-icon">{icon(tab)}</div><h2>{tab}</h2><p>This module is next in the integration queue. The live Opportunities and Skill Intelligence modules are now connected to the backend.</p><button className="primary" onClick={refresh}>{refreshing ? 'Running…' : 'Run intelligence cycle'}</button></section>}
    </main>
  </div>
}

function Overview({ matches, skills, highMatches, readiness, setTab, refresh }: { matches: Opportunity[]; skills: MarketSkill[]; highMatches: number; readiness: number; setTab: (tab: string) => void; refresh: () => void }) {
  const top = matches.slice(0, 4)
  const topSkills = skills.slice(0, 5)
  return <>
    <section className="stats"><Stat label="High-match opportunities" value={String(highMatches)} delta="Live from match engine" /><Stat label="Opportunities tracked" value={String(matches.length)} delta="Active opportunity pool" /><Stat label="Skill readiness" value={`${readiness}%`} delta="Average current proficiency" /><Stat label="Market skills" value={String(skills.length)} delta="Live demand analysis" /></section>
    <div className="grid two">
      <section className="panel"><div className="panel-head"><div><h2>Top opportunities</h2><p>Ranked by your persisted match scores</p></div><button className="link" onClick={() => setTab('Opportunities')}>View all →</button></div><div className="opps">{top.length ? top.map(m => <Opportunity key={m.internship_id} match={m} />) : <Empty text="No persisted matches yet. Run a cycle to calculate them." />}</div></section>
      <section className="panel"><div className="panel-head"><div><h2>Skill intelligence</h2><p>Where the live market is pulling you next</p></div><button className="link" onClick={() => setTab('Skill Intelligence')}>Explore →</button></div><div className="skill-list">{topSkills.map(s => <SkillRow key={s.skill_name} skill={{ name: s.skill_name, demand: s.demand_share, proficiency: s.user_proficiency, gap: s.gap_score }} />)}</div>{topSkills[0] && <div className="next-skill"><span>Learn next</span><strong>{topSkills[0].skill_name}</strong><small>{topSkills[0].priority} priority · {topSkills[0].demand_share}% market demand</small></div>}</section>
    </div>
    <div className="grid three"><section className="panel compact"><div className="panel-head"><div><h2>Application pipeline</h2><p>Pipeline module coming next</p></div></div><div className="pipeline"><b>Discovered <em>{matches.length}</em></b><b>Matched <em>{highMatches}</em></b><b>Applied <em>—</em></b><b>Interview <em>—</em></b></div></section><section className="panel compact"><div className="panel-head"><div><h2>Agent activity</h2><p>Latest live data state</p></div></div><div className="activity"><p><i/>Loaded {matches.length} persisted matches <time>live</time></p><p><i/>Loaded {skills.length} market skills <time>live</time></p><p><i/>Match + market refresh available <time>now</time></p></div></section><section className="panel compact"><div className="panel-head"><div><h2>Today</h2><p>Recommended actions</p></div></div><div className="actions"><p><b>01</b>Review high-match opportunities</p><p><b>02</b>Close the largest skill gap</p><p><b>03</b>Run the intelligence cycle</p></div></section></div>
  </>
}

function Opportunities({ matches }: { matches: Opportunity[] }) {
  const [query, setQuery] = React.useState('')
  const [minScore, setMinScore] = React.useState(0)
  const [category, setCategory] = React.useState('All')
  const categories = ['All', ...Array.from(new Set(matches.map(m => m.internships.role_category).filter(Boolean)))]
  const filtered = matches.filter(m => {
    const text = `${m.internships.company_name} ${m.internships.role_title} ${m.internships.location || ''}`.toLowerCase()
    return text.includes(query.toLowerCase()) && m.score >= minScore && (category === 'All' || m.internships.role_category === category)
  })
  return <section className="panel page"><div className="panel-head"><div><h2>Live opportunity feed</h2><p>{filtered.length} of {matches.length} persisted matches</p></div></div><div className="filters"><input placeholder="Search company, role, location…" value={query} onChange={e => setQuery(e.target.value)} /><select value={category} onChange={e => setCategory(e.target.value)}>{categories.map(c => <option key={c}>{c}</option>)}</select><select value={minScore} onChange={e => setMinScore(Number(e.target.value))}><option value={0}>Any match</option><option value={50}>50+ match</option><option value={75}>75+ match</option><option value={90}>90+ match</option></select></div><div className="opps full">{filtered.map(m => <Opportunity key={m.internship_id} match={m} detailed />)}{!filtered.length && <Empty text="No opportunities match these filters." />}</div></section>
}

function SkillIntelligence({ skills }: { skills: MarketSkill[] }) { return <section className="panel page"><div className="panel-head"><div><h2>Market skill intelligence</h2><p>Demand and your proficiency calculated from the current opportunity pool.</p></div></div><div className="skill-list large">{skills.map(s => <SkillRow key={s.skill_name} skill={{ name: s.skill_name, demand: s.demand_share, proficiency: s.user_proficiency, gap: s.gap_score }} priority={s.priority} count={s.demand_count} />)}</div></section> }

function Stat({ label, value, delta }: { label: string; value: string; delta: string }) { return <div className="stat"><span>{label}</span><strong>{value}</strong><small>{delta}</small></div> }
function Opportunity({ match, detailed = false }: { match: Opportunity; detailed?: boolean }) { const i = match.internships; return <article className={`opportunity ${detailed ? 'detailed' : ''}`}><div className="company-logo">{i.company_name.slice(0,2).toUpperCase()}</div><div className="opp-main"><strong>{i.role_title}</strong><span>{i.company_name} · {i.location || 'Location not specified'}{i.work_mode ? ` · ${i.work_mode}` : ''}</span><div className="tags">{(match.missing_skills || []).slice(0, 5).map(s => <label key={s} className="missing">Missing {s}</label>)}{match.reasons.slice(0, detailed ? 2 : 1).map(r => <label key={r}>{r}</label>)}</div>{detailed && <small className="deadline">{i.deadline ? `Deadline: ${new Date(i.deadline).toLocaleDateString('en-IN')}` : 'No deadline listed'}</small>}</div><div className="score"><strong>{Math.round(match.score)}</strong><span>match</span>{detailed && i.application_url && <a href={i.application_url} target="_blank" rel="noreferrer">Apply ↗</a>}</div></article> }
function SkillRow({ skill, priority, count }: { skill: Skill; priority?: string; count?: number }) { return <div className="skill-row"><div className="skill-title"><strong>{skill.name}</strong><span>{skill.proficiency}% ready{priority ? ` · ${priority}` : ''}</span></div><div className="bar"><i style={{ width: `${Math.min(skill.proficiency,100)}%` }} /><b style={{ left: `${Math.min(skill.demand,100)}%` }} /></div><small>Market demand {skill.demand}% · gap {skill.gap} pts{count !== undefined ? ` · ${count} roles` : ''}</small></div> }
function Empty({ text }: { text: string }) { return <div className="empty">{text}</div> }
function icon(item: string) { return ({ Overview:'⌂', Opportunities:'◈', 'Skill Intelligence':'◎', Applications:'✓', GitHub:'◉', LinkedIn:'in', 'Research Agent':'⌁' } as Record<string,string>)[item] || '•' }

createRoot(document.getElementById('root')!).render(<App />)
