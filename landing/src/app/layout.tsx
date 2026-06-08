import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const jbMono = JetBrains_Mono({
  variable: "--font-jbmono",
  subsets: ["latin"],
});

const SITE = "https://agentbrake.dev";

export const metadata: Metadata = {
  metadataBase: new URL(SITE),
  title: {
    default: "AgentBrake — Stop runaway LangChain & CrewAI agents",
    template: "%s | AgentBrake",
  },
  description:
    "A real-time, in-process brake for AI agents. Stop runaway LangChain & CrewAI loops and cost blowouts before the next expensive call. One line of code, private by design, free to use.",
  keywords: [
    "LangChain cost control",
    "CrewAI guardrails",
    "AI agent cost control",
    "runaway agent loop",
    "LLM agent guardrails",
    "stop runaway agents",
  ],
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    url: SITE,
    siteName: "AgentBrake",
    title: "AgentBrake — Stop runaway LangChain & CrewAI agents",
    description:
      "Stop runaway AI agents before they burn your budget. One line of code, in-process and private by design.",
    images: [{ url: "/og.png", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "AgentBrake — Stop runaway LangChain & CrewAI agents",
    description:
      "Stop runaway AI agents before they burn your budget. One line of code, in-process and private by design.",
    images: ["/og.png"],
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jbMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-white text-slate-900">
        {children}
      </body>
    </html>
  );
}
