"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { createProject, submitPhase1 } from "@/lib/api";
import type { Phase1Data } from "@/lib/types";

const PROJECT_TYPES = [
  { value: "web_app", label: "Web Application" },
  { value: "mobile_app", label: "Mobile Application" },
  { value: "cli_tool", label: "CLI Tool" },
  { value: "api_service", label: "API / Backend Service" },
  { value: "data_pipeline", label: "Data Pipeline" },
  { value: "ml_ai_system", label: "ML / AI System" },
  { value: "library_sdk", label: "Library / SDK" },
  { value: "other", label: "Other" },
];

const CONSUMER_SCALES = [
  { value: "personal", label: "Personal (just me)" },
  { value: "small_team", label: "Small Team (2–20 users)" },
  { value: "small_business", label: "Small Business (20–500 users)" },
  { value: "mid_market", label: "Mid-Market (500–50k users)" },
  { value: "enterprise", label: "Enterprise (50k+ users)" },
];

const DEV_SCALES = [
  { value: "solo", label: "Solo Developer" },
  { value: "small_team", label: "Small Team (2–5 devs)" },
  { value: "startup", label: "Startup (5–20 devs)" },
  { value: "sme", label: "SME / Agency (20–100 devs)" },
  { value: "enterprise", label: "Enterprise (100+ devs)" },
];

const AGENTIC_TOOLS = [
  { value: "claude_code", label: "Claude Code (Anthropic)" },
  { value: "codex", label: "Codex / ChatGPT (OpenAI)" },
  { value: "cursor", label: "Cursor" },
  { value: "kiro", label: "Kiro (Amazon)" },
  { value: "antigravity", label: "Antigravity" },
  { value: "windsurf", label: "Windsurf" },
  { value: "copilot", label: "GitHub Copilot" },
];

const SUBSCRIPTION_TIERS = [
  { value: "free", label: "Free" },
  { value: "pro", label: "Pro" },
  { value: "max", label: "Max" },
  { value: "team", label: "Team" },
  { value: "enterprise", label: "Enterprise" },
  { value: "api", label: "API (direct)" },
];

const EXPERTISE_LEVELS = [
  { value: "novice", label: "Novice — help me choose a stack" },
  { value: "intermediate", label: "Intermediate — some guidance welcome" },
  { value: "expert", label: "Expert — minimal recommendations" },
];

export function Phase1Form() {
  const router = useRouter();
  const { getToken } = useAuth();
  const [step, setStep] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<Partial<Phase1Data>>({
    agentic_tools: [],
    distribute_across_agents: false,
    tool_subscriptions: [],
  });

  const update = (patch: Partial<Phase1Data>) =>
    setForm((prev) => ({ ...prev, ...patch }));

  const toggleTool = (value: string) => {
    const tools = form.agentic_tools ?? [];
    update({
      agentic_tools: tools.includes(value) ? tools.filter((t) => t !== value) : [...tools, value],
    });
  };

  const setTier = (tool: string, tier: string) => {
    const subs = (form.tool_subscriptions ?? []).filter((s) => s.tool !== tool);
    update({ tool_subscriptions: [...subs, { tool, tier }] });
  };

  const getTier = (tool: string) =>
    form.tool_subscriptions?.find((s) => s.tool === tool)?.tier ?? "";

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");

      // Create project first
      const project = await createProject(token, form.name!, form.description ?? "");

      // Submit Phase 1 data
      await submitPhase1(token, project.id, form as Phase1Data);

      // Navigate to Phase 2 interview
      router.push(`/projects/${project.id}/interview`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setSubmitting(false);
    }
  };

  const steps = [
    // Step 0 — Identity
    <div key="identity" className="space-y-4">
      <h2 className="text-xl font-semibold">Project identity</h2>
      <div>
        <label className="block text-sm text-zinc-400 mb-1">Project name</label>
        <input
          className="w-full px-4 py-2.5 rounded-lg border border-zinc-700 bg-zinc-900 text-zinc-100 focus:outline-none focus:border-cyan-500"
          placeholder="my-awesome-api"
          value={form.name ?? ""}
          onChange={(e) => update({ name: e.target.value })}
        />
      </div>
      <div>
        <label className="block text-sm text-zinc-400 mb-1">One-sentence description</label>
        <input
          className="w-full px-4 py-2.5 rounded-lg border border-zinc-700 bg-zinc-900 text-zinc-100 focus:outline-none focus:border-cyan-500"
          placeholder="A task management API for small teams"
          value={form.description ?? ""}
          onChange={(e) => update({ description: e.target.value })}
        />
      </div>
    </div>,

    // Step 1 — Project type
    <div key="type" className="space-y-4">
      <h2 className="text-xl font-semibold">What type of project?</h2>
      <div className="grid grid-cols-2 gap-3">
        {PROJECT_TYPES.map((t) => (
          <button
            key={t.value}
            type="button"
            onClick={() => update({ project_type: t.value })}
            className={`p-3 rounded-lg border text-sm text-left transition-colors ${
              form.project_type === t.value
                ? "border-cyan-500 bg-cyan-500/10 text-cyan-400"
                : "border-zinc-700 hover:border-zinc-600 text-zinc-300"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>
    </div>,

    // Step 2 — Consumer scale
    <div key="consumer" className="space-y-4">
      <h2 className="text-xl font-semibold">Consumer scale</h2>
      <p className="text-zinc-400 text-sm">How many end-users will this serve?</p>
      <div className="space-y-2">
        {CONSUMER_SCALES.map((s) => (
          <button
            key={s.value}
            type="button"
            onClick={() => update({ consumer_scale: s.value })}
            className={`w-full p-3 rounded-lg border text-sm text-left transition-colors ${
              form.consumer_scale === s.value
                ? "border-cyan-500 bg-cyan-500/10 text-cyan-400"
                : "border-zinc-700 hover:border-zinc-600 text-zinc-300"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>
    </div>,

    // Step 3 — Dev scale
    <div key="dev" className="space-y-4">
      <h2 className="text-xl font-semibold">Development scale</h2>
      <p className="text-zinc-400 text-sm">Who's building this?</p>
      <div className="space-y-2">
        {DEV_SCALES.map((s) => (
          <button
            key={s.value}
            type="button"
            onClick={() => update({ dev_scale: s.value })}
            className={`w-full p-3 rounded-lg border text-sm text-left transition-colors ${
              form.dev_scale === s.value
                ? "border-cyan-500 bg-cyan-500/10 text-cyan-400"
                : "border-zinc-700 hover:border-zinc-600 text-zinc-300"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>
    </div>,

    // Step 4 — Agentic tools
    <div key="tools" className="space-y-4">
      <h2 className="text-xl font-semibold">Agentic tools</h2>
      <p className="text-zinc-400 text-sm">Which AI coding tools will you use? (select all that apply)</p>
      <div className="grid grid-cols-2 gap-3">
        {AGENTIC_TOOLS.map((t) => (
          <button
            key={t.value}
            type="button"
            onClick={() => toggleTool(t.value)}
            className={`p-3 rounded-lg border text-sm text-left transition-colors ${
              form.agentic_tools?.includes(t.value)
                ? "border-cyan-500 bg-cyan-500/10 text-cyan-400"
                : "border-zinc-700 hover:border-zinc-600 text-zinc-300"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>
      {(form.agentic_tools?.length ?? 0) > 1 && (
        <label className="flex items-center gap-3 mt-2 cursor-pointer">
          <input
            type="checkbox"
            checked={form.distribute_across_agents}
            onChange={(e) => update({ distribute_across_agents: e.target.checked })}
            className="w-4 h-4 accent-cyan-500"
          />
          <span className="text-sm text-zinc-300">
            Distribute tasks across tools (agent assignment matrix)
          </span>
        </label>
      )}
    </div>,

    // Step 5 — Subscription tiers
    <div key="tiers" className="space-y-4">
      <h2 className="text-xl font-semibold">Subscription tiers</h2>
      <p className="text-zinc-400 text-sm">Used to plan checkpoints in your roadmap.</p>
      {(form.agentic_tools ?? []).map((tool) => {
        const toolLabel = AGENTIC_TOOLS.find((t) => t.value === tool)?.label ?? tool;
        return (
          <div key={tool}>
            <label className="block text-sm text-zinc-300 mb-2">{toolLabel}</label>
            <div className="flex flex-wrap gap-2">
              {SUBSCRIPTION_TIERS.map((tier) => (
                <button
                  key={tier.value}
                  type="button"
                  onClick={() => setTier(tool, tier.value)}
                  className={`px-3 py-1.5 rounded-lg border text-xs transition-colors ${
                    getTier(tool) === tier.value
                      ? "border-cyan-500 bg-cyan-500/10 text-cyan-400"
                      : "border-zinc-700 hover:border-zinc-600 text-zinc-400"
                  }`}
                >
                  {tier.label}
                </button>
              ))}
            </div>
          </div>
        );
      })}
    </div>,

    // Step 6 — Expertise
    <div key="expertise" className="space-y-4">
      <h2 className="text-xl font-semibold">Your expertise level</h2>
      <p className="text-zinc-400 text-sm">
        This affects how the AI interviewer guides you on tech stack choices.
      </p>
      <div className="space-y-2">
        {EXPERTISE_LEVELS.map((e) => (
          <button
            key={e.value}
            type="button"
            onClick={() => update({ expertise_level: e.value })}
            className={`w-full p-4 rounded-lg border text-sm text-left transition-colors ${
              form.expertise_level === e.value
                ? "border-cyan-500 bg-cyan-500/10 text-cyan-400"
                : "border-zinc-700 hover:border-zinc-600 text-zinc-300"
            }`}
          >
            {e.label}
          </button>
        ))}
      </div>
    </div>,
  ];

  const isLastStep = step === steps.length - 1;

  const canProceed = (): boolean => {
    switch (step) {
      case 0: return !!(form.name?.trim() && form.description?.trim());
      case 1: return !!form.project_type;
      case 2: return !!form.consumer_scale;
      case 3: return !!form.dev_scale;
      case 4: return (form.agentic_tools?.length ?? 0) > 0;
      case 5: return (form.agentic_tools ?? []).every((t) => getTier(t));
      case 6: return !!form.expertise_level;
      default: return true;
    }
  };

  return (
    <div className="max-w-xl mx-auto">
      {/* Progress */}
      <div className="flex gap-1 mb-8">
        {steps.map((_, i) => (
          <div
            key={i}
            className={`h-1 flex-1 rounded-full transition-colors ${
              i <= step ? "bg-cyan-500" : "bg-zinc-800"
            }`}
          />
        ))}
      </div>

      <div className="p-6 rounded-xl border border-zinc-800 bg-zinc-950 min-h-[360px]">
        {steps[step]}
      </div>

      {error && (
        <div className="mt-4 p-3 rounded-lg border border-red-500/30 bg-red-500/5 text-red-400 text-sm">
          {error}
        </div>
      )}

      <div className="flex justify-between mt-6">
        <button
          type="button"
          onClick={() => setStep((s) => Math.max(0, s - 1))}
          disabled={step === 0}
          className="px-4 py-2 rounded-lg border border-zinc-700 text-zinc-400 text-sm disabled:opacity-30 hover:border-zinc-500 transition-colors"
        >
          Back
        </button>

        {isLastStep ? (
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canProceed() || submitting}
            className="px-6 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-semibold text-sm disabled:opacity-50 transition-colors"
          >
            {submitting ? "Starting interview…" : "Start AI interview →"}
          </button>
        ) : (
          <button
            type="button"
            onClick={() => setStep((s) => s + 1)}
            disabled={!canProceed()}
            className="px-6 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-semibold text-sm disabled:opacity-50 transition-colors"
          >
            Continue →
          </button>
        )}
      </div>
    </div>
  );
}
