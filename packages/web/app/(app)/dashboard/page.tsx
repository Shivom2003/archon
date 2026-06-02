"use client";

import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import useSWR from "swr";
import { listProjects } from "@/lib/api";
import type { ProjectSummary } from "@/lib/types";

const STATE_LABELS: Record<string, string> = {
  phase1: "Intake",
  phase2: "Interview",
  synthesizing: "Generating…",
  complete: "Ready",
  failed: "Failed",
};

const STATE_COLORS: Record<string, string> = {
  phase1: "text-zinc-400",
  phase2: "text-blue-400",
  synthesizing: "text-yellow-400 animate-pulse",
  complete: "text-green-400",
  failed: "text-red-400",
};

export default function DashboardPage() {
  const { getToken } = useAuth();

  const { data: projects, isLoading, error } = useSWR(
    "projects",
    async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return listProjects(token);
    },
    { refreshInterval: 5000 }, // poll while any project is synthesizing
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Your specs</h1>
        <Link
          href="/new"
          className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-semibold text-sm transition-colors"
        >
          + New spec
        </Link>
      </div>

      {isLoading && (
        <div className="text-zinc-400 text-sm">Loading…</div>
      )}

      {error && (
        <div className="p-4 rounded-lg border border-red-500/30 bg-red-500/5 text-red-400 text-sm">
          {error.message}
        </div>
      )}

      {projects && projects.length === 0 && (
        <div className="text-center py-24 border border-dashed border-zinc-800 rounded-xl">
          <p className="text-zinc-400 mb-4">No specs yet.</p>
          <Link href="/new" className="text-cyan-400 hover:text-cyan-300 text-sm">
            Create your first spec →
          </Link>
        </div>
      )}

      {projects && projects.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((p: ProjectSummary) => (
            <Link
              key={p.id}
              href={p.state === "complete" ? `/projects/${p.id}/spec` : `/projects/${p.id}/interview`}
              className="p-5 rounded-xl border border-zinc-800 hover:border-zinc-700 bg-zinc-950 transition-colors block"
            >
              <div className="flex items-start justify-between mb-2">
                <h2 className="font-semibold truncate">{p.name}</h2>
                <span className={`text-xs font-medium ml-2 flex-shrink-0 ${STATE_COLORS[p.state]}`}>
                  {STATE_LABELS[p.state]}
                </span>
              </div>
              {p.description && (
                <p className="text-zinc-400 text-sm line-clamp-2 mb-3">{p.description}</p>
              )}
              <p className="text-zinc-600 text-xs">
                {new Date(p.updated_at).toLocaleDateString()}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
