import Landing from "@/components/landing";

const SITE = "https://agentbrake.dev";
const GITHUB = "https://github.com/marcoschulz7/agentbrake";
const PYPI = "https://pypi.org/project/agentbrake-sdk/";

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      name: "AgentBrake",
      url: SITE,
      logo: `${SITE}/og.png`,
      sameAs: [GITHUB, PYPI],
    },
    {
      "@type": "SoftwareApplication",
      name: "AgentBrake",
      applicationCategory: "DeveloperApplication",
      operatingSystem: "Python 3.9+",
      description:
        "Real-time emergency brake that stops runaway LangChain and CrewAI agents before they cause cost blowouts.",
      offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
      softwareVersion: "0.1.1",
      url: SITE,
      downloadUrl: PYPI,
      license: "https://opensource.org/licenses/MIT",
    },
    {
      "@type": "FAQPage",
      mainEntity: [
        {
          "@type": "Question",
          name: "What is AgentBrake?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "AgentBrake is an open-source Python package that stops runaway LangChain and CrewAI agents in real time. You set limits — cost ceiling, identical-tool-loop detection, max steps, tool calls, and duration — and it halts the run before the next expensive call goes out.",
          },
        },
        {
          "@type": "Question",
          name: "How is it different from observability tools?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Observability tools like Langfuse, Helicone, and LangSmith record what an agent did. AgentBrake intercepts and stops it. It runs in-process and per-run, so it halts this agent now, before the next call.",
          },
        },
        {
          "@type": "Question",
          name: "Does it work with LangChain 1.x and CrewAI 1.x?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Yes. On LangChain 1.x (create_agent / LangGraph) it uses middleware that runs inside the agent graph, because callbacks can only observe a LangGraph run, not stop it. On CrewAI 1.x it patches the provider call path and raises a BaseException the framework's retry loop cannot swallow.",
          },
        },
        {
          "@type": "Question",
          name: "How much code does it take?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "One line. You add the middleware (LangChain) or call .install() (CrewAI). No refactor, no proxy, no account. It is MIT licensed and free.",
          },
        },
      ],
    },
  ],
};

export default function Page() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Landing />
    </>
  );
}
