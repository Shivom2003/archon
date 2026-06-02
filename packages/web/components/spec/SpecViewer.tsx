"use client";

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import useSWR from "swr";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getSpecFile, getDownloadUrl } from "@/lib/api";
import { SPEC_FILES, type SpecFilename } from "@/lib/types";

interface Props {
  projectId: string;
  projectName: string;
}

export function SpecViewer({ projectId, projectName }: Props) {
  const { getToken } = useAuth();
  const [activeTab, setActiveTab] = useState<SpecFilename>("SPEC.md");

  const { data, isLoading, error } = useSWR(
    `spec-${projectId}-${activeTab}`,
    async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return getSpecFile(token, projectId, activeTab);
    },
    { revalidateOnFocus: false },
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{projectName}</h1>
          <p className="text-zinc-400 text-sm">Architecture specification</p>
        </div>
        <a
          href={getDownloadUrl(projectId)}
          download={`${projectName}-architect.zip`}
          className="px-4 py-2 rounded-lg border border-zinc-700 hover:border-zinc-500 text-sm text-zinc-300 transition-colors flex items-center gap-2"
        >
          ↓ Download .zip
        </a>
      </div>

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as SpecFilename)}>
        <TabsList className="bg-zinc-900 border border-zinc-800 flex-wrap h-auto gap-1 p-1">
          {SPEC_FILES.map((f) => (
            <TabsTrigger
              key={f}
              value={f}
              className="text-xs font-mono data-[state=active]:bg-zinc-700"
            >
              {f}
            </TabsTrigger>
          ))}
        </TabsList>

        {SPEC_FILES.map((f) => (
          <TabsContent key={f} value={f}>
            {activeTab === f && (
              <div className="mt-4 p-6 rounded-xl border border-zinc-800 bg-zinc-950 min-h-[400px]">
                {isLoading && <div className="text-zinc-400 text-sm">Loading…</div>}
                {error && (
                  <div className="text-red-400 text-sm">{error.message}</div>
                )}
                {data && (
                  <div className="prose prose-invert prose-zinc max-w-none prose-sm">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {data.content}
                    </ReactMarkdown>
                  </div>
                )}
              </div>
            )}
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
