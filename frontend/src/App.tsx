import React from 'react'
import { api, type AgentCycle, type MarketSkill, type Opportunity, type ResearchRun } from './lib/api'

export default function App() {
  const [tab, setTab] = React.useState('Overview')
  const [matches, setMatches] = React.useState<Opportunity[]>([])
  const [skills, setSkills] = React.useState<MarketSkill[]>([])
  const [cycles, setCycles] = React.useState<AgentCycle[]>([])
  const [runs, setRuns] = React.useState<ResearchRun[]>([])
  const [busy, setBusy] = React.useState(false)
  const [error, setError] = React.useState('')

  const load = React.useCallback(async () => {
    setError('')
    try {
      const [m, s, c, r] = await Promise.all([api.getMatches(), api.getMarketSkills(), api.getAgentCycles(), api.getResearchRuns()])
      setMatches(m); setSkills(s); setCycles(c); setRuns(r)
    } catch (e) { setError(e instanceof Error ? e.message : 'Unable to connect to FastAPI') }
  }, [])

  React.useEffect(() => { load() }, [load])

  const runCycle = async () => {
    setBusy(true); setError('')
    try { await api.runCycle(); await load() }
    catch (e) { setError(e instanceof Error ? e.message : 'Agent cycle failed') }
    finally { setBusy(false) }
  }

  const high = matches.filter(x => x.score >= 75).length
  const readiness = skills.length ? Math.round(skills.reduce((a, x) => a + x.user_proficiency, 0) / skills.length) : 0
  const expiring = matches.filter(x => x.internships.deadline && new Date(x.internships.deadline).getTime() - Date.now() < 7 * 86400000 && new Date(x.internships.deadline).getTime() > Date.now()).length

  return <div className="app">
    <aside className="sidebar">
      <div className="brand"><div className="logo">AI</div><div><b>Career Intelligence</b><span>Personal Agent</span></div></div>
      <nav>{['Overview','Opportunities','Skill Intelligence','Applications','GitHub','LinkedIn','Research Agent'].map(x => <button key={x} className={tab === x ? 'nav active' : 'nav'} onClick={() => setTab(x)}><span>{icon(x)}</span>{x}</button>)}</nav>
      <div className="agent-card"><div className="live"><i/> Agent connected</div><strong>AI ranking is automatic</strong><p>No manual role filtering. The system ranks every relevant opportunity against your profile.</p><button onClick={runCycle} disabled={busy}>{busy ? 'Running research…' : 'Run agent cycle'}</button></div>
    </aside>
    <main>
      <header><div><p className="eyebrow">CAREER INTELLIGENCE · LIVE</p><h1>{tab}</h1><p className="sub">One ranked feed across AI/ML, Data, GenAI, Software, Research and more.</p></div><div className="header-actions"><button className="ghost" onClick={runCycle} disabled={busy}>↻ {busy ? 'Syncing' : 'Sync now'}</button><div className="avatar">AJ</div></div></header>
      {error && <div className="error">{error}<br/><small>Make sure FastAPI is running and VITE_API_BASE_URL points to it.</small></div>}
      {tab === 'Overview' && <Overview matches={matches} skills={skills} high={high} readiness={readiness} expiring={expiring} setTab={setTab} />}
      {tab === 'Opportunities' && <Opportunities matches={matches} />}
      {tab === 'Skill Intelligence' && <Skills skills={skills} />}
      {tab === 'Research Agent' && <Research cycles={cycles} runs={runs} busy={busy} runCycle={runCycle} />}
      {['Applications','GitHub','LinkedIn'].includes(tab) && <section className="panel page-placeholder"><div className="big-icon">{icon(tab)}</div><h2>{tab}</h2><p>This module is wired into the dashboard navigation and will use the same persistent career profile. The live opportunity and market intelligence modules are already connected.</p></section>}
    </main>
  </div>
}

function Overview({matches,skills,high,readiness,expiring,setTab}:{matches:Opportunity[];skills:MarketSkill[];high:number;readiness:number;expiring:number;setTab:(x:string)=>void}) {
 return <>
  <section className="stats"><Stat label="Apply-now matches" value={String(high)} delta="75%+ automatic ranking"/><Stat label="Opportunities tracked" value={String(matches.length)} delta="Across all relevant roles"/><Stat label="Skill readiness" value={`${readiness}%`} delta="Current market skills"/><Stat label="Closing soon" value={String(expiring)} delta="Deadline within 7 days"/></section>
  <div className="grid two"><section className="panel"><Head title="Top opportunities" sub="AI-ranked — no manual role filters" action="View all →" onClick={()=>setTab('Opportunities')}/><div className="opps">{matches.slice(0,5).map(x=><OpportunityCard key={x.internship_id} match={x}/>)}{!matches.length&&<Empty text="No matches yet. Run an agent cycle."/>}</div></section>
  <section className="panel"><Head title="Learn next" sub="Skills with the strongest market gap" action="Explore →" onClick={()=>setTab('Skill Intelligence')}/><div className="skill-list">{skills.slice(0,6).map(x=><SkillRow key={x.skill_name} s={x}/>)}</div></section></div>
  <div className="grid three"><section className="panel compact"><Head title="Agent status" sub="Persistent intelligence loop"/><div className="activity"><p><i/> Discovery sources connected <time>live</time></p><p><i/> Match engine connected <time>live</time></p><p><i/> Skill intelligence connected <time>live</time></p></div></section><section className="panel compact"><Head title="Priority" sub="What to do now"/><div className="actions"><p><b>01</b> Open your highest match</p><p><b>02</b> Apply before a deadline expires</p><p><b>03</b> Close the largest skill gap</p></div></section><section className="panel compact"><Head title="Coverage" sub="Roles are scored automatically"/><div className="tags role-tags"><label>AI/ML</label><label>AI Engineer</label><label>Data Science</label><label>Data Analyst</label><label>GenAI / LLM</label><label>RAG</label><label>Research</label><label>MLOps</label><label>Software</label></div></section></div>
 </>
}

function Opportunities({matches}:{matches:Opportunity[]}) { return <section className="panel page"><Head title="All ranked opportunities" sub={`${matches.length} opportunities sorted by match score — role categories are handled automatically.`}/><div className="opps full">{matches.map(x=><OpportunityCard key={x.internship_id} match={x} detailed/>)}{!matches.length&&<Empty text="Run an agent cycle to discover opportunities."/>}</div></section> }
function Skills({skills}:{skills:MarketSkill[]}) { return <section className="panel page"><Head title="Market skill intelligence" sub="Learn what employers are repeatedly asking for, then prioritize the gaps that matter most."/><div className="skill-list large">{skills.map(x=><SkillRow key={x.skill_name} s={x} count/>)}</div></section> }
function Research({cycles,runs,busy,runCycle}:{cycles:AgentCycle[];runs:ResearchRun[];busy:boolean;runCycle:()=>void}) { return <section className="panel page"><div className="panel-head"><div><h2>Research Agent</h2><p>Auditable discovery cycles and source health.</p></div><button className="primary" onClick={runCycle} disabled={busy}>{busy?'Running…':'Run full cycle'}</button></div><h3>Recent agent cycles</h3><div className="table">{cycles.slice(0,8).map(c=><div className="table-row" key={c.id}><b>{c.status}</b><span>{c.discovered_count} discovered</span><span>{c.new_matches} new</span><time>{new Date(c.started_at).toLocaleString('en-IN')}</time></div>)}</div><h3>Recent source runs</h3><div className="table">{runs.slice(0,12).map(r=><div className="table-row" key={r.id}><b>{r.status}</b><span>{r.opportunities_found} found</span><span>{r.opportunities_new} new</span><time>{new Date(r.started_at).toLocaleString('en-IN')}</time></div>)}</div></section> }
function OpportunityCard({match,detailed=false}:{match:Opportunity;detailed?:boolean}) { const i=match.internships; const apply=match.score>=75?'APPLY NOW':match.score>=60?'STRONG MATCH':'REVIEW'; return <article className={`opportunity ${detailed?'detailed':''}`}><div className="company-logo">{(i.company_name||'AI').slice(0,2).toUpperCase()}</div><div className="opp-main"><div className="opp-title"><strong>{i.role_title}</strong><label className={match.score>=75?'hot':''}>{apply}</label></div><span>{i.company_name} · {i.location||'Location not specified'}{i.work_mode?` · ${i.work_mode}`:''}</span><div className="tags"><label>{i.role_category}</label>{(match.missing_skills||[]).slice(0,4).map(s=><label className="missing" key={s}>Missing {s}</label>)}</div>{detailed&&<small className="deadline">{i.stipend?`Stipend: ₹${i.stipend} · `:''}{i.deadline?`Deadline: ${new Date(i.deadline).toLocaleDateString('en-IN')}`:'No deadline listed'}</small>}</div><div className="score"><strong>{Math.round(match.score)}%</strong><span>match</span>{i.application_url&&<a href={i.application_url} target="_blank" rel="noreferrer">Apply ↗</a>}</div></article> }
function SkillRow({s,count=false}:{s:MarketSkill;count?:boolean}) { return <div className="skill-row"><div className="skill-title"><strong>{s.skill_name}</strong><span>{s.priority} · {s.user_proficiency}% ready</span></div><div className="bar"><i style={{width:`${Math.min(s.user_proficiency,100)}%`}}/><b style={{left:`${Math.min(s.demand_share,100)}%`}}/></div><small>{s.demand_share}% market demand · gap {s.gap_score} pts{count?` · ${s.demand_count} roles`:''}</small></div> }
function Stat({label,value,delta}:{label:string;value:string;delta:string}){return <div className="stat"><span>{label}</span><strong>{value}</strong><small>{delta}</small></div>}
function Head({title,sub,action,onClick}:{title:string;sub:string;action?:string;onClick?:()=>void}){return <div className="panel-head"><div><h2>{title}</h2><p>{sub}</p></div>{action&&<button className="link" onClick={onClick}>{action}</button>}</div>}
function Empty({text}:{text:string}){return <div className="empty">{text}</div>}
function icon(x:string){return ({Overview:'⌂',Opportunities:'◈','Skill Intelligence':'◎',Applications:'✓',GitHub:'◉',LinkedIn:'in','Research Agent':'⌁'} as Record<string,string>)[x]||'•'}
