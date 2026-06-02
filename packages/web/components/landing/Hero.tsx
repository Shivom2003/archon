"use client";

import Link from "next/link";
import { useUser } from "@clerk/nextjs";

const TERMINAL_LINES = [
  { delay: 0, text: "$ archon init", className: "text-zinc-400" },
  { delay: 400, text: "── Phase 1: Structured intake ──", className: "text-cyan-400" },
  { delay: 800, text: "Project: task-manager API", className: "text-zinc-300" },
  { delay: 1100, text: "Tools: Claude Code (Pro) + Kiro", className: "text-zinc-300" },
  { delay: 1400, text: "── Phase 2: AI Interview ──", className: "text-cyan-400" },
  { delay: 1800, text: "Archon: What's your DB strategy?", className: "text-blue-400" },
  { delay: 2200, text: "You: PostgreSQL + Redis cache", className: "text-zinc-300" },
  { delay: 2600, text: "── Generating architecture... ──", className: "text-cyan-400" },
  { delay: 3000, text: "✓ .architect/SPEC.md", className: "text-green-400" },
  { delay: 3200, text: "✓ .architect/ROADMAP.md", className: "text-green-400" },
  { delay: 3400, text: "✓ .architect/CLAUDE.md", className: "text-green-400" },
  { delay: 3600, text: "✓ Checkpoints set for Claude Pro", className: "text-green-400" },
];

export function Hero() {
  const { isSignedIn } = useUser();
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center px-4 text-center overflow-hidden">
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 pointer-events-none" />
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-zinc-700 bg-zinc-800/50 text-xs text-zinc-400 mb-8">
          <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
          Open source · Private beta
        </div>

        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-6">
          Architecture specs your{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
            AI agents
          </span>{" "}
          can actually use
        </h1>

        <p className="text-xl text-zinc-400 max-w-2xl mx-auto mb-10">
          Archon interviews you, then generates a complete{" "}
          <code className="text-cyan-400 font-mono text-sm">.architect/</code> directory
          — with agent task assignments, checkpoint markers, and ADRs — before a single
          line of code is written.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          {isSignedIn ? (
            <Link
              href="/dashboard"
              className="px-6 py-3 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-semibold transition-colors"
            >
              Go to dashboard →
            </Link>
          ) : (
            <Link
              href="#waitlist"
              className="px-6 py-3 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-semibold transition-colors"
            >
              Join the waitlist
            </Link>
          )}
          <a
            href="https://github.com/Shivom2003/archon"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 rounded-lg border border-zinc-700 hover:border-zinc-500 text-zinc-300 hover:text-white font-semibold transition-colors"
          >
            View on GitHub
          </a>
        </div>

        {/* Terminal */}
        <div className="mx-auto max-w-2xl rounded-xl border border-zinc-800 bg-zinc-900 text-left overflow-hidden shadow-2xl">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-zinc-800">
            <div className="w-3 h-3 rounded-full bg-red-500/70" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
            <div className="w-3 h-3 rounded-full bg-green-500/70" />
            <span className="ml-2 text-xs text-zinc-500 font-mono">archon</span>
          </div>
          <div className="p-4 font-mono text-sm space-y-1 min-h-[220px]">
            {TERMINAL_LINES.map((line, i) => (
              <p key={i} className={line.className}>
                {line.text}
              </p>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
