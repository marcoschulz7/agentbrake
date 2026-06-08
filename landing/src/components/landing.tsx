"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Repeat,
  DollarSign,
  Brain,
  Zap,
  Timer,
  Check,
  Copy,
  ArrowRight,
} from "lucide-react";
import { AuroraBackground } from "@/components/ui/aurora-background";

function GitHubIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
      className={className}
    >
      <path d="M12 .5C5.37.5 0 5.87 0 12.5c0 5.3 3.44 9.8 8.21 11.39.6.11.82-.26.82-.58 0-.29-.01-1.04-.02-2.05-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.73.08-.73 1.2.09 1.84 1.24 1.84 1.24 1.07 1.83 2.81 1.3 3.5.99.11-.78.42-1.3.76-1.6-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.13-.3-.54-1.52.12-3.18 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 0 1 6.01 0c2.29-1.55 3.3-1.23 3.3-1.23.66 1.66.25 2.88.12 3.18.77.84 1.24 1.91 1.24 3.22 0 4.61-2.81 5.62-5.49 5.92.43.37.81 1.1.81 2.22 0 1.61-.01 2.9-.01 3.29 0 .32.21.7.83.58A12.01 12.01 0 0 0 24 12.5C24 5.87 18.63.5 12 .5Z" />
    </svg>
  );
}

const GITHUB = "https://github.com/marcoschulz7/agentbrake";
const PYPI = "https://pypi.org/project/agentbrake-sdk/";
const PIP = "pip install agentbrake-sdk";

function CopyInstall({ className = "" }: { className?: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(PIP);
        setCopied(true);
        setTimeout(() => setCopied(false), 1400);
      }}
      className={`group flex items-center gap-3 rounded-xl border border-slate-200 bg-white/90 px-4 py-3 shadow-sm backdrop-blur transition hover:border-slate-300 cursor-pointer ${className}`}
      aria-label="Copy install command"
    >
      <span className="font-mono text-slate-400">$</span>
      <code className="font-mono text-[15px] text-slate-900">{PIP}</code>
      <span className="ml-1 text-slate-400 group-hover:text-slate-600">
        {copied ? (
          <Check className="h-4 w-4 text-green-600" />
        ) : (
          <Copy className="h-4 w-4" />
        )}
      </span>
    </button>
  );
}

const CATCHES = [
  {
    icon: Repeat,
    title: "Identical-tool loops",
    body: "Same call, same args, over and over. Trips after N identical calls in a row.",
    tag: "repeat_tool_limit",
  },
  {
    icon: DollarSign,
    title: "Cost blowouts",
    body: "The $47k overnight run. A hard ceiling, enforced live as tokens are spent.",
    tag: "max_cost_usd",
  },
  {
    icon: Brain,
    title: "Endless reasoning",
    body: "A loop that never hits its stopping condition. Caps total reasoning steps.",
    tag: "max_steps",
  },
  {
    icon: Zap,
    title: "Tool-call storms",
    body: "Runaway tool fan-out. Caps total tool invocations per run.",
    tag: "max_tool_calls",
  },
  {
    icon: Timer,
    title: "Hung runs",
    body: "A run that just keeps going all night. A wall-clock ceiling per run.",
    tag: "max_duration_s",
  },
];

const FAQ = [
  {
    q: "What is AgentBrake?",
    a: "AgentBrake is an open-source Python package that stops runaway LangChain and CrewAI agents in real time. You set limits — cost ceiling, identical-tool-loop detection, max steps, tool calls, and duration — and it halts the run before the next expensive call goes out.",
  },
  {
    q: "How is it different from observability tools?",
    a: "Observability tools like Langfuse, Helicone, and LangSmith record what an agent did. AgentBrake intercepts and stops it. It runs in-process and per-run, so it halts this agent now — not after the bill arrives.",
  },
  {
    q: "Does it work with LangChain 1.x and CrewAI 1.x?",
    a: "Yes. On LangChain 1.x (create_agent / LangGraph) it uses middleware that runs inside the agent graph, because callbacks can only observe a LangGraph run, not stop it. On CrewAI 1.x it patches the provider call path and raises a BaseException the framework's retry loop cannot swallow.",
  },
  {
    q: "How much code does it take?",
    a: "One line. You add the middleware (LangChain) or call .install() (CrewAI). No refactor, no proxy, no account. It's MIT licensed and free.",
  },
];

const fade = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-80px" },
  transition: { duration: 0.5, ease: "easeOut" },
} as const;

export default function Landing() {
  return (
    <>
      {/* Header */}
      <header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <a href="/" className="flex items-center gap-2.5 font-semibold">
            <span className="grid h-7 w-7 place-items-center rounded-lg bg-green-600 text-white">
              <span className="h-2.5 w-2.5 rounded-sm bg-white" />
            </span>
            AgentBrake
          </a>
          <nav className="flex items-center gap-7 text-sm text-slate-600">
            <a className="hidden hover:text-slate-900 sm:block" href="#how">
              How it works
            </a>
            <a className="hidden hover:text-slate-900 sm:block" href="#catches">
              What it catches
            </a>
            <a className="hidden hover:text-slate-900 sm:block" href="#faq">
              FAQ
            </a>
            <a
              href={GITHUB}
              rel="noopener"
              className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-3.5 py-2 font-medium text-white transition hover:bg-slate-700"
            >
              <GitHubIcon className="h-4 w-4" /> Star
            </a>
          </nav>
        </div>
      </header>

      <main>
        {/* Hero with aurora */}
        <AuroraBackground className="min-h-[88vh] px-6">
          <motion.div
            initial={{ opacity: 0, y: 36 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="relative z-10 mx-auto flex max-w-3xl flex-col items-center text-center"
          >
            <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-green-200 bg-green-50 px-3.5 py-1.5 text-xs font-semibold uppercase tracking-wide text-green-700">
              Open source · MIT · LangChain &amp; CrewAI
            </span>
            <h1 className="text-balance text-4xl font-bold leading-[1.08] tracking-tight text-slate-900 md:text-6xl">
              Stop runaway AI agents before they burn your budget.
            </h1>
            <p className="mt-6 max-w-xl text-pretty text-lg text-slate-600">
              AgentBrake is the emergency brake for LangChain &amp; CrewAI. One
              line of code stops infinite loops, cost blowouts and endless
              reasoning — in real time, before the next expensive call goes out.
            </p>
            <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row">
              <CopyInstall />
              <a
                href={GITHUB}
                rel="noopener"
                className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-5 py-3 font-semibold text-white shadow-sm transition hover:bg-green-700"
              >
                <GitHubIcon className="h-4 w-4" /> Star on GitHub
              </a>
            </div>
            <p className="mt-4 font-mono text-xs text-slate-500">
              imports as <span className="text-slate-700">agentbrake</span> ·
              LangChain 1.x &amp; 0.x · CrewAI 1.x
            </p>
          </motion.div>
        </AuroraBackground>

        {/* Demo */}
        <section className="relative z-10 mx-auto -mt-16 max-w-4xl px-6">
          <motion.figure
            {...fade}
            className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl shadow-slate-900/5"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/agentbrake.gif"
              width={1278}
              height={484}
              alt="AgentBrake stopping a real LangChain (LangGraph) agent caught in a loop at step 3"
              className="w-full"
            />
          </motion.figure>
          <p className="mt-3 text-center text-sm text-slate-500">
            A real LangGraph agent caught in a loop — stopped at step 3, before
            the bill grows.
          </p>
        </section>

        {/* Problem */}
        <section className="mx-auto max-w-3xl px-6 py-24">
          <motion.div {...fade}>
            <h2 className="text-3xl font-bold tracking-tight text-slate-900">
              Agents fail expensively, not loudly
            </h2>
            <div className="mt-6 rounded-2xl border-l-4 border-green-600 bg-slate-50 p-6 text-lg text-slate-800">
              In November 2025, four LangChain agents entered an infinite loop.
              They ran for 11 days. The bill was <strong>$47,000</strong>. Nobody
              noticed until it was over.
            </div>
            <p className="mt-6 text-slate-600">
              This is not rare. An agent calls the same tool 14,000 times with
              identical arguments. A planner expands one task into dozens of
              subagent calls. A reasoning loop never terminates and runs all
              night. Observability tools record it — they don&apos;t stop it. The
              gap between &ldquo;the alert fired&rdquo; and &ldquo;the run
              stopped&rdquo; is exactly where the money goes.
            </p>
          </motion.div>
        </section>

        {/* How it works */}
        <section id="how" className="border-y border-slate-100 bg-slate-50/60">
          <div className="mx-auto max-w-6xl px-6 py-24">
            <motion.div {...fade} className="max-w-2xl">
              <h2 className="text-3xl font-bold tracking-tight text-slate-900">
                One line to wire it in
              </h2>
              <p className="mt-4 text-slate-600">
                AgentBrake watches every step in real time and raises a clean
                exception that halts the agent before the next expensive call.
              </p>
            </motion.div>
            <div className="mt-10 grid gap-6 md:grid-cols-2">
              <motion.div
                {...fade}
                className="rounded-2xl border border-slate-200 bg-white p-1 shadow-sm"
              >
                <div className="flex items-center justify-between px-5 pt-4">
                  <span className="text-sm font-semibold text-slate-900">
                    LangChain 1.x
                  </span>
                  <span className="font-mono text-xs text-slate-400">
                    LangGraph
                  </span>
                </div>
                <pre className="mt-3 overflow-x-auto rounded-xl bg-slate-900 p-5 text-[13.5px] leading-relaxed text-slate-100">
                  <code className="font-mono">{`from agentbrake import LangChainBrakeMiddleware
from langchain.agents import create_agent

agent = create_agent(
    model, tools=tools,
    middleware=[
        LangChainBrakeMiddleware(
            max_cost_usd=2.00,
            repeat_tool_limit=5,
        )
    ],
)`}</code>
                </pre>
              </motion.div>

              <motion.div
                {...fade}
                className="rounded-2xl border border-slate-200 bg-white p-1 shadow-sm"
              >
                <div className="flex items-center justify-between px-5 pt-4">
                  <span className="text-sm font-semibold text-slate-900">
                    CrewAI 1.x
                  </span>
                  <span className="font-mono text-xs text-slate-400">
                    before kickoff
                  </span>
                </div>
                <pre className="mt-3 overflow-x-auto rounded-xl bg-slate-900 p-5 text-[13.5px] leading-relaxed text-slate-100">
                  <code className="font-mono">{`from agentbrake import CrewAIBrake

# right before crew.kickoff()
CrewAIBrake(
    max_cost_usd=3.00,
    repeat_tool_limit=5,
).install()`}</code>
                </pre>
              </motion.div>
            </div>
          </div>
        </section>

        {/* What it catches */}
        <section id="catches" className="mx-auto max-w-6xl px-6 py-24">
          <motion.div {...fade} className="max-w-2xl">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900">
              What it catches
            </h2>
            <p className="mt-4 text-slate-600">
              Five runaway patterns, one brake. It warns at 80% of any limit and
              stops at 100%.
            </p>
          </motion.div>
          <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {CATCHES.map((c) => (
              <motion.div
                key={c.title}
                {...fade}
                className="group rounded-2xl border border-slate-200 bg-white p-6 transition hover:border-green-300 hover:shadow-md hover:shadow-green-900/5"
              >
                <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 text-green-600">
                  <c.icon className="h-5 w-5" />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-slate-900">
                  {c.title}
                </h3>
                <p className="mt-2 text-sm text-slate-600">{c.body}</p>
                <code className="mt-4 inline-block rounded-md bg-slate-100 px-2 py-1 font-mono text-xs text-slate-700">
                  {c.tag}
                </code>
              </motion.div>
            ))}
            <motion.div
              {...fade}
              className="flex flex-col justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-6"
            >
              <p className="text-sm text-slate-600">
                Provider spend caps are monthly and account-wide — they fire
                after the damage. AgentBrake is{" "}
                <strong className="text-slate-900">per-run and in-process</strong>
                : it stops this agent now.
              </p>
              <p className="mt-3 text-xs font-medium text-slate-500">
                A sprinkler, not a smoke alarm.
              </p>
            </motion.div>
          </div>
        </section>

        {/* FAQ */}
        <section id="faq" className="border-t border-slate-100 bg-slate-50/60">
          <div className="mx-auto max-w-3xl px-6 py-24">
            <motion.h2
              {...fade}
              className="text-3xl font-bold tracking-tight text-slate-900"
            >
              Frequently asked questions
            </motion.h2>
            <div className="mt-8 divide-y divide-slate-200">
              {FAQ.map((f) => (
                <details key={f.q} className="group py-5">
                  <summary className="flex cursor-pointer list-none items-center justify-between text-lg font-semibold text-slate-900">
                    {f.q}
                    <ArrowRight className="h-5 w-5 shrink-0 text-slate-400 transition group-open:rotate-90" />
                  </summary>
                  <p className="mt-3 text-slate-600">{f.a}</p>
                </details>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="mx-auto max-w-4xl px-6 py-24">
          <motion.div
            {...fade}
            className="rounded-3xl border border-slate-200 bg-gradient-to-b from-white to-slate-50 p-10 text-center shadow-sm"
          >
            <h2 className="text-3xl font-bold tracking-tight text-slate-900">
              Stop your next runaway agent
            </h2>
            <p className="mx-auto mt-3 max-w-md text-slate-600">
              One line of code. Open source. Works on LangChain 1.x, CrewAI 1.x,
              and the classic AgentExecutor.
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <CopyInstall />
              <a
                href={GITHUB}
                rel="noopener"
                className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-5 py-3 font-semibold text-white shadow-sm transition hover:bg-green-700"
              >
                <GitHubIcon className="h-4 w-4" /> Star on GitHub
              </a>
            </div>
          </motion.div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-10 text-sm text-slate-500 sm:flex-row">
          <div className="flex items-center gap-2.5 font-semibold text-slate-700">
            <span className="grid h-6 w-6 place-items-center rounded-md bg-green-600 text-white">
              <span className="h-2 w-2 rounded-sm bg-white" />
            </span>
            AgentBrake
          </div>
          <div className="flex items-center gap-6">
            <a className="hover:text-slate-900" href={GITHUB} rel="noopener">
              GitHub
            </a>
            <a className="hover:text-slate-900" href={PYPI} rel="noopener">
              PyPI
            </a>
            <span>MIT License</span>
          </div>
        </div>
      </footer>
    </>
  );
}
