#!/usr/bin/env python3
"""
AgentBrake website generator — programmatic, SEO-first static site.

One template + data -> a hub-and-spoke site:
  /                         hub: stop runaway LangChain & CrewAI agents
  /langchain/ /crewai/      framework intent pages
  /vs/<tool>/               comparison pages (highest AI-citation format)
  /glossary/<term>/         definition pages ("what is ...")

Every page ships: one clear H1/intent, unique title+meta, canonical, OpenGraph,
JSON-LD (SoftwareApplication + FAQPage + BreadcrumbList), semantic HTML, and
internal links. No client JS required — fast LCP, fully crawlable & extractable.

Run:  python3 website/build.py   ->  writes static files under website/
"""
from __future__ import annotations

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://agentbrake.dev"
GITHUB = "https://github.com/marcoschulz7/agentbrake"
PYPI = "https://pypi.org/project/agentbrake-sdk/"
PIP = "pip install agentbrake-sdk"

# --------------------------------------------------------------------------- #
# Shared layout
# --------------------------------------------------------------------------- #

CSS = """
:root{
  --bg:#0F172A; --surface:#1E293B; --surface-2:#172033; --border:#334155;
  --text:#F8FAFC; --muted:#94A3B8; --green:#22C55E; --green-700:#15803D;
  --cyan:#56C2E6; --red:#F36E82; --maxw:1080px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0;background:var(--bg);color:var(--text);
  font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  font-size:17px;line-height:1.65;-webkit-font-smoothing:antialiased;
}
.mono{font-family:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace}
a{color:var(--green);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 24px}
h1,h2,h3{line-height:1.2;letter-spacing:-0.02em;font-weight:700}
h1{font-size:clamp(2.1rem,5vw,3.4rem);margin:0 0 18px}
h2{font-size:clamp(1.5rem,3vw,2.1rem);margin:56px 0 18px}
h3{font-size:1.2rem;margin:32px 0 10px}
p{color:#E2E8F0}
.muted{color:var(--muted)}
.lead{font-size:1.2rem;color:#CBD5E1;max-width:60ch}
/* header */
header.site{position:sticky;top:0;z-index:30;background:rgba(15,23,42,.85);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--border)}
.nav{display:flex;align-items:center;justify-content:space-between;height:64px}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;color:var(--text)}
.brand:hover{text-decoration:none}
.brand .dot{width:14px;height:14px;border-radius:4px;background:var(--green);
  box-shadow:0 0 0 4px rgba(34,197,94,.18)}
.nav nav{display:flex;align-items:center;gap:26px}
.nav nav a{color:var(--muted);font-size:.95rem}
.nav nav a:hover{color:var(--text);text-decoration:none}
.btn{display:inline-flex;align-items:center;gap:8px;font-weight:600;
  border-radius:10px;padding:11px 18px;cursor:pointer;transition:all .2s;
  border:1px solid transparent;font-size:.95rem}
.btn-primary{background:var(--green);color:#04210f}
.btn-primary:hover{background:#34D26A;text-decoration:none}
.btn-ghost{background:var(--surface);border-color:var(--border);color:var(--text)}
.btn-ghost:hover{border-color:var(--muted);text-decoration:none}
/* hero */
.hero{padding:72px 0 40px}
.eyebrow{display:inline-block;font-size:.8rem;font-weight:600;letter-spacing:.04em;
  text-transform:uppercase;color:var(--green);background:rgba(34,197,94,.1);
  border:1px solid rgba(34,197,94,.25);border-radius:999px;padding:5px 13px;margin-bottom:22px}
.cta-row{display:flex;flex-wrap:wrap;gap:14px;margin:28px 0 16px;align-items:center}
.install{display:flex;align-items:center;gap:14px;background:#0B1120;
  border:1px solid var(--border);border-radius:12px;padding:14px 18px;max-width:420px}
.install code{color:var(--cyan);font-size:1.02rem}
.install .prompt{color:var(--muted)}
.copy{margin-left:auto;background:transparent;border:1px solid var(--border);
  color:var(--muted);border-radius:8px;padding:6px 10px;cursor:pointer;font-size:.85rem}
.copy:hover{color:var(--text);border-color:var(--muted)}
.hero-note{font-size:.92rem;color:var(--muted)}
figure{margin:36px 0 0}
figure img{width:100%;border:1px solid var(--border);border-radius:14px;display:block}
figcaption{color:var(--muted);font-size:.9rem;margin-top:10px}
/* generic blocks */
.section{padding:8px 0}
.answer{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--green);
  border-radius:10px;padding:18px 20px;margin:18px 0;font-size:1.05rem}
.grid{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));margin-top:24px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:22px}
.card h3{margin:0 0 8px;font-size:1.05rem}
.card p{margin:0;color:var(--muted);font-size:.96rem}
pre{background:#0B1120;border:1px solid var(--border);border-radius:12px;padding:20px;
  overflow:auto;font-size:.92rem;line-height:1.6}
pre .mono{color:#E2E8F0}
code{font-family:"JetBrains Mono",ui-monospace,monospace}
.tok-k{color:#C792EA}.tok-s{color:#C3E88D}.tok-c{color:#637777;font-style:italic}.tok-f{color:#82AAFF}
table{width:100%;border-collapse:collapse;margin:22px 0;font-size:.96rem}
th,td{text-align:left;padding:13px 14px;border-bottom:1px solid var(--border);vertical-align:top}
th{color:var(--muted);font-weight:600;font-size:.85rem;text-transform:uppercase;letter-spacing:.03em}
td .yes{color:var(--green);font-weight:600}
td .no{color:var(--red)}
.faq dt{font-weight:600;margin-top:22px;font-size:1.08rem}
.faq dd{margin:8px 0 0;color:#CBD5E1}
.crumbs{font-size:.85rem;color:var(--muted);padding:22px 0 0}
.crumbs a{color:var(--muted)}
.cta-band{background:linear-gradient(180deg,var(--surface),var(--surface-2));
  border:1px solid var(--border);border-radius:16px;padding:40px;margin:64px 0;text-align:center}
.cta-band h2{margin:0 0 10px}
.related{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
.related a{background:var(--surface);border:1px solid var(--border);border-radius:8px;
  padding:8px 13px;color:var(--text);font-size:.9rem}
.related a:hover{border-color:var(--green);text-decoration:none}
footer.site{border-top:1px solid var(--border);margin-top:72px;padding:44px 0;color:var(--muted)}
.fcols{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:28px}
.fcols h4{color:var(--text);font-size:.85rem;text-transform:uppercase;letter-spacing:.04em;margin:0 0 12px}
.fcols a{display:block;color:var(--muted);font-size:.92rem;margin-bottom:8px}
.fcols a:hover{color:var(--text);text-decoration:none}
.fbottom{margin-top:32px;padding-top:20px;border-top:1px solid var(--border);font-size:.88rem}
@media(max-width:720px){.nav nav a:not(.btn){display:none}.fcols{grid-template-columns:1fr 1fr}}
@media(prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto}}
:focus-visible{outline:2px solid var(--green);outline-offset:2px;border-radius:4px}
"""

COPY_JS = """
document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',()=>{
  navigator.clipboard.writeText(b.getAttribute('data-copy'));
  const t=b.textContent;b.textContent='copied';setTimeout(()=>b.textContent=t,1200);
}));
"""

NAV = f"""<header class="site"><div class="wrap nav">
  <a class="brand" href="/"><span class="dot"></span><span>AgentBrake</span></a>
  <nav>
    <a href="/langchain/">LangChain</a>
    <a href="/crewai/">CrewAI</a>
    <a href="/#how">How it works</a>
    <a href="/glossary/runaway-agent-loop/">Glossary</a>
    <a class="btn btn-primary" href="{GITHUB}" rel="noopener">Star on GitHub</a>
  </nav>
</div></header>"""

FOOTER = f"""<footer class="site"><div class="wrap">
  <div class="fcols">
    <div>
      <h4>AgentBrake</h4>
      <p class="muted" style="max-width:34ch">The emergency brake for multi-agent
      systems. Stop runaway LangChain &amp; CrewAI agents in real time, free and source-available.</p>
    </div>
    <div><h4>Product</h4>
      <a href="/langchain/">LangChain</a><a href="/crewai/">CrewAI</a>
      <a href="/#what">What it catches</a><a href="{PYPI}" rel="noopener">PyPI</a></div>
    <div><h4>Compare</h4>
      <a href="/vs/langfuse/">vs Langfuse</a><a href="/vs/helicone/">vs Helicone</a>
      <a href="/vs/langsmith/">vs LangSmith</a><a href="/vs/galileo/">vs Galileo</a></div>
    <div><h4>Learn</h4>
      <a href="/glossary/runaway-agent-loop/">Runaway agent loop</a>
      <a href="/glossary/llm-agent-cost-control/">Agent cost control</a>
      <a href="/glossary/ai-agent-guardrails/">Agent guardrails</a>
      <a href="{GITHUB}" rel="noopener">GitHub</a></div>
  </div>
  <div class="fbottom">© 2026 AgentBrake · FSL-1.1-MIT ·
    <a href="{GITHUB}" rel="noopener">GitHub</a> ·
    <a href="{PYPI}" rel="noopener">PyPI</a> · <code>{PIP}</code></div>
</div></footer>"""


def page(*, path, title, description, body, jsonld, og_type="website"):
    """Render one HTML page. `path` like '' (home) or 'vs/langfuse'."""
    canonical = SITE + "/" + (path + "/" if path else "")
    ld = "\n".join(
        f'<script type="application/ld+json">{j}</script>' for j in jsonld
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/og.png">
<meta property="og:site_name" content="AgentBrake">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
{ld}
</head>
<body>
{NAV}
<main>
{body}
</main>
{FOOTER}
<script src="/copy.js" defer></script>
</body>
</html>"""
    outdir = os.path.join(HERE, path)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w") as f:
        f.write(html)
    return canonical


def org_ld():
    return ('{"@context":"https://schema.org","@type":"Organization","name":"AgentBrake",'
            f'"url":"{SITE}","logo":"{SITE}/og.png","sameAs":["{GITHUB}","{PYPI}"]}}')


def software_ld():
    return ('{"@context":"https://schema.org","@type":"SoftwareApplication",'
            '"name":"AgentBrake","applicationCategory":"DeveloperApplication",'
            '"operatingSystem":"Python 3.9+","description":"Real-time emergency brake '
            'that stops runaway LangChain and CrewAI agents before they cause cost '
            'blowouts.","offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},'
            f'"softwareVersion":"0.1.1","url":"{SITE}","downloadUrl":"{PYPI}",'
            '"license":"https://github.com/marcoschulz7/agentbrake/blob/main/LICENSE"}')


def faq_ld(qa):
    items = ",".join(
        '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
        % (jstr(q), jstr(a)) for q, a in qa
    )
    return '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}' % items


def breadcrumb_ld(trail):
    items = ",".join(
        '{"@type":"ListItem","position":%d,"name":%s,"item":%s}' % (i + 1, jstr(n), jstr(u))
        for i, (n, u) in enumerate(trail)
    )
    return '{"@context":"https://schema.org","@type":"BreadcrumbList","itemElement":[%s]}'.replace(
        "itemElement", "itemListElement") % items


def jstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


def faq_html(qa):
    rows = "".join(f"<dt>{q}</dt><dd>{a}</dd>" for q, a in qa)
    return f'<section class="section"><h2>Frequently asked questions</h2><dl class="faq">{rows}</dl></section>'


def crumbs(trail):
    parts = " / ".join(
        f'<a href="{u}">{n}</a>' if u else n for n, u in trail
    )
    return f'<div class="wrap crumbs">{parts}</div>'


def cta_band(heading="Stop your next runaway agent"):
    return f"""<div class="wrap"><div class="cta-band">
      <h2>{heading}</h2>
      <p class="muted" style="max-width:46ch;margin:0 auto 22px">One line of code. Open
      source. Works on LangChain 1.x, CrewAI 1.x, and the classic AgentExecutor.</p>
      <div class="install" style="margin:0 auto 16px">
        <span class="prompt mono">$</span><code class="mono">{PIP}</code>
        <button class="copy" data-copy="{PIP}">copy</button>
      </div>
      <a class="btn btn-primary" href="{GITHUB}" rel="noopener">Star on GitHub</a>
    </div></div>"""


# --------------------------------------------------------------------------- #
# Code snippets (syntax-tinted, static)
# --------------------------------------------------------------------------- #

LC_CODE = """<span class="tok-k">from</span> agentbrake <span class="tok-k">import</span> LangChainBrakeMiddleware
<span class="tok-k">from</span> langchain.agents <span class="tok-k">import</span> create_agent

agent = <span class="tok-f">create_agent</span>(
    model, tools=tools,
    middleware=[<span class="tok-f">LangChainBrakeMiddleware</span>(max_cost_usd=<span class="tok-s">2.00</span>, repeat_tool_limit=<span class="tok-s">5</span>)],
)"""

CREW_CODE = """<span class="tok-k">from</span> agentbrake <span class="tok-k">import</span> CrewAIBrake

<span class="tok-c"># right before crew.kickoff()</span>
<span class="tok-f">CrewAIBrake</span>(max_cost_usd=<span class="tok-s">3.00</span>, repeat_tool_limit=<span class="tok-s">5</span>).<span class="tok-f">install</span>()"""


def codeblock(code):
    return f'<pre><code class="mono">{code}</code></pre>'


# --------------------------------------------------------------------------- #
# Pages
# --------------------------------------------------------------------------- #

def build_home():
    qa = [
        ("What is AgentBrake?",
         "AgentBrake is a free, source-available Python package that stops runaway LangChain and "
         "CrewAI agents in real time. You set limits — cost ceiling, identical-tool-loop "
         "detection, max steps, tool calls, and duration — and it halts the run before "
         "the next expensive call goes out."),
        ("How is it different from observability tools?",
         "Observability tools like Langfuse, Helicone, and LangSmith record what an agent "
         "did. AgentBrake intercepts and stops it. It runs in-process and per-run, so it "
         "halts this agent now, before the next call — not after the bill arrives."),
        ("Does it work with LangChain 1.x and CrewAI 1.x?",
         "Yes. On LangChain 1.x (create_agent / LangGraph) it uses middleware that runs "
         "inside the agent graph, because callbacks can only observe a LangGraph run, not "
         "stop it. On CrewAI 1.x it patches the provider call path and uses a "
         "BaseException so the framework's retry loop can't swallow the brake."),
        ("Is AgentBrake free?",
         "Yes, it is free to use and source-available under the FSL (non-compete; converts to MIT after two years). Install it "
         "with pip install agentbrake-sdk."),
        ("How much code does it take?",
         "One line. You add the middleware (LangChain) or call .install() (CrewAI). No "
         "refactor, no proxy, no account."),
    ]
    body = f"""
<section class="hero"><div class="wrap">
  <span class="eyebrow">Free, source available · LangChain &amp; CrewAI</span>
  <h1>Stop runaway AI agents before they burn your budget.</h1>
  <p class="lead">AgentBrake is the emergency brake for LangChain &amp; CrewAI. One line of
  code stops infinite loops, cost blowouts, and endless reasoning — in real time,
  before the next expensive call goes out.</p>
  <div class="cta-row">
    <div class="install">
      <span class="prompt mono">$</span><code class="mono">{PIP}</code>
      <button class="copy" data-copy="{PIP}">copy</button>
    </div>
    <a class="btn btn-ghost" href="{GITHUB}" rel="noopener">Star on GitHub</a>
  </div>
  <p class="hero-note">Imports as <code class="mono">agentbrake</code>. Free, source-available (FSL).
  Works on LangChain 1.x, CrewAI 1.x, and the classic AgentExecutor.</p>
  <figure>
    <img src="/agentbrake.gif" width="1278" height="484" loading="eager"
      alt="AgentBrake stopping a real LangChain (LangGraph) agent caught in a loop at step 3">
    <figcaption>A real LangGraph agent caught in a loop — stopped at step 3, before the bill grows.</figcaption>
  </figure>
</div></section>

<section class="section" id="problem"><div class="wrap">
  <h2>Agents fail expensively, not loudly</h2>
  <div class="answer">In November 2025, four LangChain agents entered an infinite loop.
  They ran for 11 days. The bill was <strong>$47,000</strong>. Nobody noticed until it
  was over.</div>
  <p class="muted">This is not rare. An agent calls the same tool 14,000 times with
  identical arguments. A planner expands one task into dozens of subagent calls. A
  reasoning loop never hits its stopping condition and runs all night. Observability
  tools record it. They don't stop it — and the gap between "the alert fired" and "the
  run stopped" is exactly where the money goes.</p>
</div></section>

<section class="section" id="how"><div class="wrap">
  <h2>How it works</h2>
  <p class="lead">AgentBrake watches every step in real time. When a run crosses a limit
  you set, it raises a clean exception that halts the agent before the next expensive
  call goes out.</p>
  <div class="grid" style="margin-bottom:8px">
    <div class="card"><h3>LangChain</h3>{codeblock(LC_CODE)}
      <p style="margin-top:12px"><a href="/langchain/">LangChain guide →</a></p></div>
    <div class="card"><h3>CrewAI</h3>{codeblock(CREW_CODE)}
      <p style="margin-top:12px"><a href="/crewai/">CrewAI guide →</a></p></div>
  </div>
</div></section>

<section class="section" id="what"><div class="wrap">
  <h2>What it catches</h2>
  <table>
    <thead><tr><th>Runaway pattern</th><th>How AgentBrake stops it</th></tr></thead>
    <tbody>
      <tr><td><strong>Identical-tool loops</strong><br><span class="muted">same call, same args, over and over</span></td><td><code class="mono">repeat_tool_limit</code> — trips after N identical calls in a row</td></tr>
      <tr><td><strong>Cost blowouts</strong><br><span class="muted">the $47k overnight run</span></td><td><code class="mono">max_cost_usd</code> — a hard ceiling, enforced live as tokens are spent</td></tr>
      <tr><td><strong>Endless reasoning</strong><br><span class="muted">no stopping condition</span></td><td><code class="mono">max_steps</code> — caps total reasoning steps</td></tr>
      <tr><td><strong>Tool-call storms</strong></td><td><code class="mono">max_tool_calls</code> — caps total tool invocations</td></tr>
      <tr><td><strong>Hung runs</strong></td><td><code class="mono">max_duration_s</code> — wall-clock ceiling</td></tr>
    </tbody>
  </table>
  <p class="muted">It warns at 80% of any limit and stops at 100%.</p>
</div></section>

<section class="section"><div class="wrap">
  <h2>Why not just set a provider spend cap?</h2>
  <div class="answer">Provider caps are monthly and account-wide — they fire after the
  damage, across everything. AgentBrake is per-run and in-process: it stops this agent
  now, before the next call. It's the difference between a smoke alarm and a sprinkler.</div>
  <div class="related">
    <a href="/vs/langfuse/">AgentBrake vs Langfuse</a>
    <a href="/vs/helicone/">vs Helicone</a>
    <a href="/vs/langsmith/">vs LangSmith</a>
    <a href="/vs/galileo/">vs Galileo</a>
  </div>
</div></section>

{cta_band()}
{f'<div class="wrap">{faq_html(qa)}</div>'}
"""
    page(path="", title="AgentBrake — Stop runaway LangChain & CrewAI agents",
         description="Open-source emergency brake for AI agents. Stop runaway LangChain "
                     "& CrewAI loops and cost blowouts in real time, before the next "
                     "expensive call. One line of code, Free, source-available (FSL).",
         body=body, jsonld=[org_ld(), software_ld(), faq_ld(qa)])


def build_framework(slug, name, code, patterns, intro, qa):
    trail = [("Home", "/"), (name, "")]
    pat_rows = "".join(
        f'<tr><td><strong>{p[0]}</strong></td><td>{p[1]}</td></tr>' for p in patterns
    )
    body = crumbs(trail) + f"""
<section class="hero" style="padding-top:36px"><div class="wrap">
  <h1>Stop runaway {name} agents in real time</h1>
  <p class="lead">{intro}</p>
  <div class="cta-row"><div class="install">
    <span class="prompt mono">$</span><code class="mono">{PIP}</code>
    <button class="copy" data-copy="{PIP}">copy</button>
  </div><a class="btn btn-ghost" href="{GITHUB}" rel="noopener">GitHub</a></div>
</div></section>

<section class="section"><div class="wrap">
  <h2>One line to wire it in</h2>
  {codeblock(code)}
</div></section>

<section class="section"><div class="wrap">
  <h2>{name} runaway patterns it catches</h2>
  <table><thead><tr><th>Pattern</th><th>How it stops</th></tr></thead>
  <tbody>{pat_rows}</tbody></table>
</div></section>

{cta_band(f"Add the brake to your {name} agent")}
{f'<div class="wrap">{faq_html(qa)}</div>'}
"""
    page(path=slug,
         title=f"Stop runaway {name} agents — AgentBrake",
         description=f"Add a real-time brake to your {name} agents. AgentBrake halts "
                     f"loops, cost blowouts and endless reasoning before the next call. "
                     f"One line, free to use.",
         body=body, jsonld=[software_ld(), faq_ld(qa), breadcrumb_ld(
             [("Home", SITE + "/"), (name, SITE + "/" + slug + "/")])])


def build_vs(slug, tool, tool_cat, intro, rows, when, qa):
    trail = [("Home", "/"), ("Compare", None), (f"vs {tool}", "")]
    table_rows = "".join(
        f'<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>' for r in rows
    )
    body = crumbs(trail) + f"""
<section class="hero" style="padding-top:36px"><div class="wrap">
  <h1>AgentBrake vs {tool}</h1>
  <p class="lead">{intro}</p>
</div></section>

<section class="section"><div class="wrap">
  <h2>AgentBrake vs {tool} at a glance</h2>
  <table>
    <thead><tr><th></th><th>AgentBrake</th><th>{tool}</th></tr></thead>
    <tbody>{table_rows}</tbody>
  </table>
  <p class="muted">{tool} is {tool_cat}. The two are complementary, not mutually
  exclusive — most teams keep their observability stack and add AgentBrake as the
  control layer that actually stops a run.</p>
</div></section>

<section class="section"><div class="wrap">
  <h2>When to use which</h2>
  <div class="answer">{when}</div>
  <div class="related">
    <a href="/langchain/">AgentBrake for LangChain</a>
    <a href="/crewai/">AgentBrake for CrewAI</a>
    <a href="/glossary/llm-agent-cost-control/">LLM agent cost control</a>
  </div>
</div></section>

{cta_band()}
{f'<div class="wrap">{faq_html(qa)}</div>'}
"""
    page(path="vs/" + slug,
         title=f"AgentBrake vs {tool} — stop agents vs observe them",
         description=f"AgentBrake vs {tool}: {tool} is {tool_cat}; AgentBrake stops "
                     f"runaway agents in real time. See how they compare and when to use "
                     f"each.",
         body=body, og_type="article",
         jsonld=[faq_ld(qa), breadcrumb_ld(
             [("Home", SITE + "/"), ("Compare", SITE + "/vs/"),
              (f"vs {tool}", SITE + "/vs/" + slug + "/")])])


def build_glossary(slug, term, answer, detail, related, qa):
    trail = [("Home", "/"), ("Glossary", None), (term, "")]
    rel = "".join(f'<a href="{u}">{n}</a>' for n, u in related)
    body = crumbs(trail) + f"""
<section class="hero" style="padding-top:36px"><div class="wrap">
  <h1>{term}</h1>
  <div class="answer">{answer}</div>
</div></section>
<section class="section"><div class="wrap">
  {detail}
  <h2>Related</h2><div class="related">{rel}</div>
</div></section>
{cta_band()}
{f'<div class="wrap">{faq_html(qa)}</div>'}
"""
    page(path="glossary/" + slug,
         title=f"{term} — definition & how to prevent it | AgentBrake",
         description=answer[:155],
         body=body, og_type="article",
         jsonld=[faq_ld(qa), breadcrumb_ld(
             [("Home", SITE + "/"), ("Glossary", SITE + "/glossary/"),
              (term, SITE + "/glossary/" + slug + "/")])])


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #

def build_all():
    build_home()

    build_framework(
        "langchain", "LangChain", LC_CODE,
        [("Identical-tool loops", "Loop detector trips after N identical tool calls in a row, across both the classic AgentExecutor and 1.x LangGraph agents."),
         ("Cost blowouts", "Live cost ceiling from real token usage on each model call."),
         ("Endless reasoning", "Step and tool-call caps stop a run that never converges."),
         ("Swallowed brakes", "On LangChain 1.x, callbacks can only observe a LangGraph run — a raised exception is logged and dropped. AgentBrake uses middleware, which runs inside the graph and actually halts it.")],
        "On LangChain 1.x (create_agent / LangGraph) a callback can watch a runaway loop "
        "but cannot stop it — the framework swallows exceptions raised from callbacks. "
        "AgentBrake ships LangChainBrakeMiddleware, which runs inside the agent graph and "
        "halts the run. For the classic AgentExecutor (0.x), use the LangChainBrake callback.",
        [("Why can't a LangChain callback stop a LangGraph agent?",
          "LangGraph runs callback handlers as fire-and-forget observers. An exception "
          "raised from a callback is logged and swallowed, so the agent keeps looping. "
          "Middleware runs inside the execution graph, so a raise from it actually unwinds the run."),
         ("Which class do I use?",
          "LangChain 1.x (create_agent): LangChainBrakeMiddleware. Classic AgentExecutor "
          "(0.x): the LangChainBrake callback via config={'callbacks': [brake]}."),
         ("Does it need an API key or proxy?",
          "No. AgentBrake runs in-process. There's a runnable example that brakes a real "
          "LangGraph loop with no API key at all.")])

    build_framework(
        "crewai", "CrewAI", CREW_CODE,
        [("Identical-tool loops", "Loop detector patches ToolUsage and trips after N identical tool calls in a row."),
         ("Cost blowouts", "Per-instance token-delta accounting from each provider call drives a live cost ceiling."),
         ("Retry-swallowed brakes", "CrewAI wraps execution in except-Exception retry loops. AgentBrakeError is a BaseException, so it sails past them and actually halts crew.kickoff()."),
         ("Provider drift", "CrewAI 1.x routes calls through a provider factory; AgentBrake patches the real provider classes, not the dead LLM.call entry point.")],
        "CrewAI 1.x routes LLM calls through provider classes and wraps execution in "
        "retry loops, so naive guards silently no-op. AgentBrake patches the real provider "
        "call path plus ToolUsage, and raises a BaseException the retry loop can't catch — "
        "verified live against a real crew.kickoff().",
        [("Does the brake really stop a CrewAI crew?",
          "Yes. A live run on real OpenAI confirmed it halts crew.kickoff(). CrewAI's "
          "retry loop used to swallow the brake; AgentBrakeError is now a BaseException, "
          "so it can't be caught by the framework's except Exception."),
         ("When do I call install()?",
          "Right before crew.kickoff(), after your agents and LLMs are constructed — "
          "CrewAI lazy-loads provider classes, so installing late guarantees they're patched."),
         ("How accurate is the cost ceiling?",
          "It reads real token usage the provider reports. Loop, step, tool-call and "
          "duration limits are exact regardless.")])

    vs_rows_common = lambda tool, observes: [
        ("Stops a runaway run in real time", '<span class="yes">Yes — in-process, per run</span>', observes),
        ("Records / traces runs", '<span class="muted">Basic live stats</span>', '<span class="yes">Yes — its core strength</span>'),
        ("Identical-loop detection that halts", '<span class="yes">Yes</span>', '<span class="no">Observe only</span>'),
        ("Hard per-run cost ceiling that halts", '<span class="yes">Yes</span>', '<span class="no">Alerts, not stops</span>'),
        ("Free, source-available (FSL)", '<span class="yes">Yes</span>', "Varies"),
        ("Setup", '<span class="yes">One line, no proxy</span>', "SDK / proxy / dashboard"),
        ("Frameworks", "LangChain 1.x &amp; 0.x, CrewAI 1.x", "Many"),
    ]

    build_vs("langfuse", "Langfuse", "an open-source LLM observability and tracing platform",
             "Langfuse traces and analyzes what your agents did. AgentBrake stops a "
             "runaway agent while it's happening. They solve different halves of the "
             "problem — observe vs. intercept — and work well together.",
             vs_rows_common("Langfuse", '<span class="no">No — observes &amp; traces</span>'),
             "Use Langfuse to understand and debug agent behavior over time. Use "
             "AgentBrake to put a hard, real-time limit on any single run so a loop or "
             "cost blowout can't complete. Most teams run both.",
             [("Is AgentBrake a Langfuse alternative?",
               "Not exactly — Langfuse is observability (it records), AgentBrake is "
               "control (it stops). If your goal is to prevent a runaway run from "
               "finishing, AgentBrake is the tool; keep Langfuse for tracing."),
              ("Can I use both?",
               "Yes. They're complementary: Langfuse traces the run, AgentBrake halts it "
               "when it crosses a limit.")])

    build_vs("helicone", "Helicone", "an LLM observability platform and proxy/gateway",
             "Helicone logs and monitors LLM calls through a proxy. AgentBrake runs "
             "in-process and stops the agent itself when it loops or blows a cost "
             "ceiling — no proxy in the path.",
             vs_rows_common("Helicone", '<span class="no">No — logs &amp; monitors</span>'),
             "Use Helicone for centralized logging, caching and gateway features. Use "
             "AgentBrake to enforce a per-run kill-switch in the agent process itself, "
             "with no extra network hop.",
             [("Does AgentBrake proxy my LLM calls?",
               "No. It hooks the agent in-process, so there's no proxy and no added "
               "latency in the request path."),
              ("Helicone has cost alerts — isn't that enough?",
               "Alerts tell you after the spend. AgentBrake stops the run before the next "
               "call, so the spend never happens.")])

    build_vs("langsmith", "LangSmith", "LangChain's observability and evaluation platform",
             "LangSmith traces and evaluates LangChain runs. AgentBrake enforces hard "
             "real-time limits that halt a run. On LangChain 1.x, AgentBrake uses "
             "middleware specifically because callbacks can observe but not stop a "
             "LangGraph agent.",
             vs_rows_common("LangSmith", '<span class="no">No — traces &amp; evaluates</span>'),
             "Use LangSmith to debug, test and evaluate your chains and agents. Use "
             "AgentBrake to guarantee a single run can't loop forever or exceed a cost "
             "ceiling. They cover different stages — development vs. runtime safety.",
             [("Is AgentBrake tied to LangChain like LangSmith?",
               "No. AgentBrake supports LangChain (1.x and 0.x) and CrewAI, with a "
               "framework-agnostic core engine."),
              ("Does it work with LangGraph?",
               "Yes — via middleware, which runs inside the LangGraph execution graph so "
               "it can actually halt the run.")])

    build_vs("galileo", "Galileo", "an LLM evaluation and observability platform",
             "Galileo focuses on evaluation, monitoring and guardrail scoring of LLM "
             "output quality. AgentBrake focuses on one thing: stopping a runaway agent "
             "run before it spends more money.",
             vs_rows_common("Galileo", '<span class="no">No — evaluates &amp; monitors</span>'),
             "Use Galileo to measure and improve output quality and catch hallucinations. "
             "Use AgentBrake as the runtime circuit breaker that caps cost, loops and "
             "duration per run. Quality tooling and a kill-switch solve different risks.",
             [("Is AgentBrake a guardrails tool?",
               "It's a runtime cost-and-loop guardrail — a circuit breaker. It doesn't "
               "score output quality; it stops a run from running away."),
              ("Can I combine it with an eval platform?",
               "Yes. Evaluate quality with your eval platform; cap runaway cost and loops "
               "with AgentBrake.")])

    build_glossary(
        "runaway-agent-loop", "What is a runaway agent loop?",
        "A runaway agent loop is when an autonomous AI agent repeats actions — often the "
        "same tool call with identical arguments — without ever reaching its stopping "
        "condition. Because each step makes a paid LLM call, the loop quietly accumulates "
        "cost until something external stops it.",
        """<p>Runaway loops are the most expensive failure mode of autonomous agents
        because they fail quietly. A documented LangChain case ran four agents in a loop
        for 11 days and cost $47,000 before anyone noticed.</p>
        <h3>Common shapes</h3>
        <ul><li>The same tool called thousands of times with identical arguments.</li>
        <li>A reasoning loop that never satisfies its stop condition.</li>
        <li>A planner that fans one task out into ever more subagent calls.</li></ul>
        <h3>How to prevent one</h3>
        <p>Put a hard, per-run limit in the agent process: detect identical-call repeats,
        cap total steps and tool calls, set a wall-clock ceiling, and enforce a maximum
        spend per run. <a href="/">AgentBrake</a> does exactly this in one line.</p>""",
        [("LLM agent cost control", "/glossary/llm-agent-cost-control/"),
         ("AI agent guardrails", "/glossary/ai-agent-guardrails/"),
         ("Stop runaway LangChain agents", "/langchain/")],
        [("How do you stop a runaway agent loop?",
          "Detect identical repeated calls and enforce hard per-run limits (cost, steps, "
          "tool calls, duration) in-process, so the run halts before the next call. A "
          "tool like AgentBrake adds this in one line."),
         ("Why are runaway loops so expensive?",
          "Each loop iteration is a paid LLM call, and the failure is silent — there's no "
          "crash, so the run can continue for hours or days before anyone notices.")])

    build_glossary(
        "llm-agent-cost-control", "What is LLM agent cost control?",
        "LLM agent cost control is the practice of capping how much money a single AI "
        "agent run can spend. Unlike monthly provider spend caps, which are account-wide "
        "and fire after the fact, per-run control stops an individual agent in real time "
        "once it crosses a cost or loop limit.",
        """<p>Autonomous agents make many chained LLM calls, so cost is driven by runtime
        behavior, not a fixed price. Effective cost control happens <em>per run</em> and
        <em>in-process</em>.</p>
        <h3>Levels of control</h3>
        <table><thead><tr><th>Mechanism</th><th>When it fires</th></tr></thead><tbody>
        <tr><td>Provider monthly cap</td><td>After the spend, account-wide</td></tr>
        <tr><td>Observability alert</td><td>After the spend, on a dashboard</td></tr>
        <tr><td><strong>Per-run brake (AgentBrake)</strong></td><td><span class="yes">Before the next call, in real time</span></td></tr>
        </tbody></table>
        <p><a href="/">AgentBrake</a> enforces a live cost ceiling from real token usage and
        stops the run the moment it's crossed.</p>""",
        [("Runaway agent loop", "/glossary/runaway-agent-loop/"),
         ("AI agent guardrails", "/glossary/ai-agent-guardrails/"),
         ("AgentBrake vs Helicone", "/vs/helicone/")],
        [("How is per-run cost control different from a provider spend cap?",
          "A provider cap is monthly and account-wide and fires after the damage. Per-run "
          "control stops this specific agent the moment it crosses a limit, before the "
          "next call."),
         ("Can you cap cost inside the agent process?",
          "Yes. AgentBrake tracks token spend live and raises a stop the instant a run "
          "exceeds your cost ceiling — no proxy required.")])

    build_glossary(
        "ai-agent-guardrails", "What are AI agent guardrails?",
        "AI agent guardrails are constraints that keep an autonomous agent within safe "
        "bounds. They range from output-quality checks (filtering, validation) to runtime "
        "control guardrails — hard limits on cost, loops, steps and duration that stop a "
        "run before it goes off the rails.",
        """<p>Guardrails fall into two broad families: <strong>content guardrails</strong>
        that judge what an agent says or does, and <strong>runtime guardrails</strong>
        that bound how long and how expensively it runs.</p>
        <p>AgentBrake is a runtime control guardrail — a circuit breaker. It doesn't score
        output; it stops a run that loops, blows a cost ceiling, or never terminates. It
        works on <a href="/langchain/">LangChain</a> and <a href="/crewai/">CrewAI</a> in
        one line.</p>""",
        [("Runaway agent loop", "/glossary/runaway-agent-loop/"),
         ("LLM agent cost control", "/glossary/llm-agent-cost-control/"),
         ("AgentBrake vs Galileo", "/vs/galileo/")],
        [("Are guardrails the same as a kill-switch?",
          "A kill-switch is one kind of runtime guardrail. AgentBrake is a runtime "
          "guardrail that acts as a per-run kill-switch for cost and loops."),
         ("Do guardrails slow my agent down?",
          "Runtime control guardrails like AgentBrake run in-process with negligible "
          "overhead and no proxy in the request path.")])


ALL_PATHS = [
    "", "langchain", "crewai",
    "vs/langfuse", "vs/helicone", "vs/langsmith", "vs/galileo",
    "glossary/runaway-agent-loop", "glossary/llm-agent-cost-control",
    "glossary/ai-agent-guardrails",
]


def emit_assets():
    def w(name, content):
        with open(os.path.join(HERE, name), "w") as f:
            f.write(content)

    w("styles.css", CSS.strip() + "\n")
    w("copy.js", COPY_JS.strip() + "\n")

    # robots.txt — explicitly welcome AI crawlers so we can be cited
    ai_bots = ["GPTBot", "ChatGPT-User", "OAI-SearchBot", "PerplexityBot",
               "ClaudeBot", "anthropic-ai", "Google-Extended", "Bingbot",
               "Applebot-Extended"]
    allows = "\n".join(f"User-agent: {b}\nAllow: /\n" for b in ai_bots)
    w("robots.txt",
      "User-agent: *\nAllow: /\n\n"
      + allows
      + f"\nSitemap: {SITE}/sitemap.xml\n")

    # sitemap.xml
    urls = "".join(
        f"<url><loc>{SITE}/{(p + '/') if p else ''}</loc>"
        f"<changefreq>weekly</changefreq>"
        f"<priority>{'1.0' if p == '' else '0.8'}</priority></url>"
        for p in ALL_PATHS
    )
    w("sitemap.xml",
      '<?xml version="1.0" encoding="UTF-8"?>\n'
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
      + urls + "</urlset>\n")

    # llms.txt — context file for AI systems (llmstxt.org)
    w("llms.txt", f"""# AgentBrake

> The emergency brake for multi-agent systems. AgentBrake is a free, source-available
> Python package that stops runaway LangChain and CrewAI agents in real
> time — before infinite loops or cost blowouts burn your budget. Install:
> `pip install agentbrake-sdk` (imports as `agentbrake`).

## What it does
- Detects identical-tool loops and halts the run before the next call.
- Enforces a per-run cost ceiling from real token usage.
- Caps total steps, tool calls, and wall-clock duration.
- Runs in-process — it stops the agent, it does not just observe it.

## Frameworks
- LangChain 1.x (create_agent / LangGraph): LangChainBrakeMiddleware.
- LangChain 0.x (AgentExecutor): LangChainBrake callback.
- CrewAI 1.x: CrewAIBrake().install().

## Key pages
- Home: {SITE}/
- LangChain: {SITE}/langchain/
- CrewAI: {SITE}/crewai/
- Runaway agent loop (definition): {SITE}/glossary/runaway-agent-loop/
- LLM agent cost control: {SITE}/glossary/llm-agent-cost-control/
- Comparisons: {SITE}/vs/langfuse/ , /vs/helicone/ , /vs/langsmith/ , /vs/galileo/

## Source
- GitHub: {GITHUB}
- PyPI: {PYPI}
""")

    # pricing.md — machine-readable for AI buying agents
    w("pricing.md", f"""# Pricing — AgentBrake

AgentBrake is free to use and source-available (FSL).

## Open Source
- Price: /forever
- License: FSL-1.1-MIT (free use, no competing resale; becomes MIT after 2 years)
- Install: `pip install agentbrake-sdk`
- Features: real-time loop detection, per-run cost ceiling, step/tool/duration
  limits, LangChain (1.x + 0.x) and CrewAI (1.x) support.

## Source
- GitHub: {GITHUB}
- PyPI: {PYPI}
""")


if __name__ == "__main__":
    build_all()
    emit_assets()
    print("built site + assets under", HERE)
