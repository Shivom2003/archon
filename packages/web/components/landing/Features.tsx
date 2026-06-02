const features = [
  {
    icon: "🎤",
    title: "Interview-driven spec",
    description:
      "A two-phase interview — structured intake then a Claude-powered conversation — captures your tech stack, constraints, compliance needs, and the magic moment you're optimising for.",
  },
  {
    icon: "🤖",
    title: "Agent assignment matrix",
    description:
      "When you use multiple agentic tools, Archon distributes tasks based on each tool's real strengths. Claude Code for reasoning-heavy work, Kiro for spec-driven phases, Codex for boilerplate.",
  },
  {
    icon: "⚠️",
    title: "Usage-limit checkpoints",
    description:
      "Archon knows your subscription tier. It inserts checkpoint markers with copy-pasteable resume prompts at natural stopping points — so your agent never gets cut off mid-task.",
  },
  {
    icon: "📋",
    title: "Architecture Decision Records",
    description:
      "Every significant architectural choice is captured as an ADR with full rationale. AI agents understand why decisions were made — not just what they are.",
  },
  {
    icon: "🔀",
    title: "AGENTS.md + CLAUDE.md",
    description:
      "Outputs the emerging cross-tool AGENTS.md standard alongside Claude Code's native CLAUDE.md format — compatible with every major agentic coding tool out of the box.",
  },
  {
    icon: "📦",
    title: "Open source core",
    description:
      "The Python library is MIT-licensed. Run archon init from your terminal with your own API key, or use the hosted web product for a no-friction browser experience.",
  },
];

export function Features() {
  return (
    <section id="features" className="py-24 px-4 bg-zinc-900">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">
            What makes Archon different
          </h2>
          <p className="text-zinc-400 text-lg max-w-2xl mx-auto">
            Every other architecture tool generates diagrams or docs for humans.
            Archon generates specs for AI agents.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <div
              key={f.title}
              className="p-6 rounded-xl border border-zinc-800 bg-zinc-950 hover:border-zinc-700 transition-colors"
            >
              <div className="text-3xl mb-4">{f.icon}</div>
              <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
              <p className="text-zinc-400 text-sm leading-relaxed">{f.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
