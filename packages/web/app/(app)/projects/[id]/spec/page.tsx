"use client";

import { useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import useSWR from "swr";
import { getProject } from "@/lib/api";
import { SpecViewer } from "@/components/spec/SpecViewer";

export default function SpecPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const { getToken } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const isSynthesizing = searchParams.get("synthesizing") === "1";

  const { data: project } = useSWR(
    `project-${id}`,
    async () => {
      const token = await getToken();
      if (!token) return null;
      return getProject(token, id);
    },
    {
      refreshInterval: (data) =>
        data?.state === "synthesizing" ? 3000 : 0,
    },
  );

  // Redirect away from ?synthesizing once done
  useEffect(() => {
    if (project?.state === "complete" && isSynthesizing) {
      router.replace(`/projects/${id}/spec`);
    }
  }, [project?.state, isSynthesizing, id, router]);

  if (!project || project.state === "synthesizing") {
    return (
      <div className="flex flex-col items-center justify-center py-32 gap-4">
        <div className="w-10 h-10 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin" />
        <p className="text-zinc-400 text-sm">
          Generating your architecture specification…
        </p>
        <p className="text-zinc-600 text-xs">This takes about 30 seconds</p>
      </div>
    );
  }

  if (project.state === "failed") {
    return (
      <div className="p-6 rounded-xl border border-red-500/30 bg-red-500/5 text-red-400">
        <h2 className="font-semibold mb-2">Synthesis failed</h2>
        <p className="text-sm">{project.error || "An unknown error occurred."}</p>
      </div>
    );
  }

  return (
    <SpecViewer
      projectId={id}
      projectName={project.name}
    />
  );
}
