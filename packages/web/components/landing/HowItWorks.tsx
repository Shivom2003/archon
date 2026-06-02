const steps = [
  {
    number: "01",
    title: "Answer 8 structured questions",
    description:
      "Project type, scale, which agentic tools you use, your subscription tier, expertise level. Takes under 2 minutes.",
    detail: "No AI needed for this part — it's a form.",
  },
  {
    number: "02",
    title: "Claude interviews you",
    description:
      "An adaptive LLM conversation digs into your tech stack, compliance needs, core features, and the experience you're optimising for.",
    detail: "4–10 turns depending on project complexity.",
  },
  {
    number: "03",
    title: "Build with full context",
    description:
      "Download your .architect/ directory and point your agentic tool at CLAUDE.md or AGENTS.md. Your agent now knows the why, not just the what.",
    detail: "Works with Claude Code, Kiro, Cursor, Codex, and more.",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">How it works</h2>
          <p className="text-zinc-400 text-lg">
            From blank slate to agent-ready spec in under 5 minutes.
          </p>
        </div>

        <div className="space-y-12">
          {steps.map((step, i) => (
            <div key={i} className="flex gap-8 items-start">
              <div className="flex-shrink-0 w-16 h-16 rounded-xl border border-cyan-500/30 bg-cyan-500/5 flex items-center justify-center">
                <span className="text-cyan-400 font-mono text-sm font-bold">{step.number}</span>
              </div>
              <div className="flex-1 pt-2">
                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                <p className="text-zinc-300 mb-1">{step.description}</p>
                <p className="text-zinc-500 text-sm">{step.detail}</p>
              </div>
              {i < steps.length - 1 && (
                <div className="absolute left-8 mt-16 w-px h-12 bg-zinc-800" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
