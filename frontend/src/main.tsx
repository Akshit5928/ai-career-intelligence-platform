import React from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

type Match = { company: string; role: string; score: number; skills: string[]; location: string }
type Skill = { name: string; demand: number; proficiency: number; gap: number }

const matches: Match[] = [
  { company: 'Teal India', role: 'AI/ML Engineer Intern', score: 82, skills: ['RAG', 'LLM', 'FastAPI', 'Docker'], location: 'India / Remote' },
  { company: 'Gravity AI', role: 'AI Intern', score: 78, skills: ['Python', 'LLM', 'RAG', 'MLOps'], location: 'India' },
  { company: 'MediNex Workforce', role: 'Data Analyst Intern', score: 96, skills: ['Python', 'SQL', 'Power BI', 'Excel'], location: 'Delhi NCR' },
  { company: 'Wake Up Whistle', role: 'Data Analyst Intern', score: 91, skills: ['SQL', 'Power BI', 'Python'], location: 'Remote' },
]

const skills: Skill[] = [
  { name: 'Python', demand: 86, proficiency: 72, gap: 14 },
  { name: 'SQL', demand: 71, proficiency: 55, gap: 16 },
  { name: 'Power BI', demand: 57, proficiency: 45, gap: 12 },
  { name: 'RAG / LLM', demand: 64, proficiency: 52, gap: 12 },
  { name: 'FastAPI', demand: 43, proficiency: 25, gap: 18 },
  { name: 'Docker', demand: 39, proficiency: 20, gap: 19 },
]

function App() {
  const [tab, setTab] = React.useState('Overview')
  const [refreshing, setRefreshing] = React.useState(false)

  const refresh = () => {
    setRefreshing(true)
    window.setTimeout(() => setRefreshing(false), 900)
  }

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

      {tab === 'Overview' ? <>
        <section className="stats">
          <Stat label="High-match opportunities" value="12" delta="+4 this week" />
          <Stat label="Applications active" value="6" delta="2 interviews" />
          <Stat label="Skill readiness" value="68%" delta="+7% this month" />
          <Stat label="Research sources" value="28" delta="Last scan 18m ago" />
        </section>

        <div className="grid two">
          <section className="panel"><div className="panel-head"><div><h2>Top opportunities</h2><p>Ranked by your current profile and urgency</p></div><button className="link" onClick={() => setTab('Opportunities')}>View all →</button></div>
            <div className="opps">{matches.map(m => <Opportunity key={m.company} match={m} />)}</div>
          </section>
          <section className="panel"><div className="panel-head"><div><h2>Skill intelligence</h2><p>Where the market is pulling you next</p></div><button className="link" onClick={() => setTab('Skill Intelligence')}>Explore →</button></div>
            <div className="skill-list">{skills.slice(0, 5).map(s => <SkillRow key={s.name} skill={s} />)}</div>
            <div className="next-skill"><span>Next best skill</span><strong>Docker</strong><small>High demand · largest gap</small></div>
          </section>
        </div>

        <div className="grid three">
          <section className="panel compact"><div className="panel-head"><div><h2>Application pipeline</h2><p>Current momentum</p></div></div><div className="pipeline"><b>Discovered <em>24</em></b><b>Matched <em>12</em></b><b>Applied <em>6</em></b><b>Interview <em>2</em></b></div></section>
          <section className="panel compact"><div className="panel-head"><div><h2>Agent activity</h2><p>Latest autonomous work</p></div></div><div className="activity"><p><i/>Scanned 28 research sources <time>18m</time></p><p><i/>Updated 12 opportunity matches <time>18m</time></p><p><i/>Detected Docker demand increase <time>42m</time></p></div></section>
          <section className="panel compact"><div className="panel-head"><div><h2>Today</h2><p>Recommended actions</p></div></div><div className="actions"><p><b>01</b>Review 3 high-priority applications</p><p><b>02</b>Finish Docker fundamentals</p><p><b>03</b>Approve LinkedIn draft</p></div></section>
        </div>
      </> : <section className="panel page-placeholder"><div className="big-icon">{icon(tab)}</div><h2>{tab}</h2><p>This module is wired into the Career Intelligence frontend shell. The next backend integration will populate this view from Supabase.</p><button className="primary" onClick={refresh}>{refreshing ? 'Running…' : 'Run intelligence cycle'}</button></section>}
    </main>
  </div>
}

function Stat({ label, value, delta }: { label: string; value: string; delta: string }) { return <div className="stat"><span>{label}</span><strong>{value}</strong><small>{delta}</small></div> }
function Opportunity({ match }: { match: Match }) { return <article className="opportunity"><div className="company-logo">{match.company.slice(0,2).toUpperCase()}</div><div className="opp-main"><strong>{match.role}</strong><span>{match.company} · {match.location}</span><div className="tags">{match.skills.map(s => <label key={s}>{s}</label>)}</div></div><div className="score"><strong>{match.score}</strong><span>match</span></div></article> }
function SkillRow({ skill }: { skill: Skill }) { return <div className="skill-row"><div className="skill-title"><strong>{skill.name}</strong><span>{skill.proficiency}% ready</span></div><div className="bar"><i style={{ width: `${skill.proficiency}%` }} /><b style={{ left: `${skill.demand}%` }} /></div><small>Market demand {skill.demand}% · gap {skill.gap} pts</small></div> }
function icon(item: string) { return ({ Overview:'⌂', Opportunities:'◈', 'Skill Intelligence':'◎', Applications:'✓', GitHub:'◉', LinkedIn:'in', 'Research Agent':'⌁' } as Record<string,string>)[item] || '•' }

createRoot(document.getElementById('root')!).render(<App />)
