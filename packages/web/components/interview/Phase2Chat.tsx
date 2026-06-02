"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { triggerSynthesis } from "@/lib/api";
import { useSSE } from "@/lib/sse";
import type { ChatMessage } from "@/lib/sse";

interface Props {
  projectId: string;
}

export function Phase2Chat({ projectId }: Props) {
  const router = useRouter();
  const { getToken } = useAuth();
  const [token, setToken] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [synthesizing, setSynthesizing] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Fetch token once
  useEffect(() => {
    getToken().then(setToken);
  }, [getToken]);

  const { messages, isWaiting, isComplete, error, sendMessage } = useSSE(
    projectId,
    token ?? "",
  );

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isWaiting]);

  // When interview is complete, trigger synthesis automatically
  useEffect(() => {
    if (!isComplete || synthesizing || !token) return;
    setSynthesizing(true);
    triggerSynthesis(token, projectId)
      .then(() => router.push(`/projects/${projectId}/spec?synthesizing=1`))
      .catch(console.error);
  }, [isComplete, synthesizing, token, projectId, router]);

  if (!token) {
    return <div className="text-zinc-400 text-sm">Loading…</div>;
  }

  const handleSend = async () => {
    if (!input.trim() || isWaiting) return;
    const msg = input.trim();
    setInput("");
    await sendMessage(msg);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] max-w-2xl mx-auto">
      <div className="mb-4">
        <h1 className="text-xl font-bold">AI Interview</h1>
        <p className="text-zinc-400 text-sm">
          Claude is gathering details about your project. Answer naturally.
        </p>
      </div>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((msg: ChatMessage, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-cyan-500 text-black rounded-br-none"
                  : "bg-zinc-800 text-zinc-100 rounded-bl-none"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {isWaiting && (
          <div className="flex justify-start">
            <div className="bg-zinc-800 px-4 py-3 rounded-2xl rounded-bl-none">
              <span className="flex gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-zinc-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-1.5 h-1.5 rounded-full bg-zinc-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-1.5 h-1.5 rounded-full bg-zinc-400 animate-bounce" style={{ animationDelay: "300ms" }} />
              </span>
            </div>
          </div>
        )}

        {synthesizing && (
          <div className="text-center py-4 text-cyan-400 text-sm animate-pulse">
            Interview complete — generating your architecture spec…
          </div>
        )}

        {error && (
          <div className="p-3 rounded-lg border border-red-500/30 bg-red-500/5 text-red-400 text-sm">
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      {!isComplete && !synthesizing && (
        <div className="mt-4 flex gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isWaiting}
            rows={2}
            placeholder="Type your answer… (Enter to send)"
            className="flex-1 px-4 py-3 rounded-xl border border-zinc-700 bg-zinc-900 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-cyan-500 resize-none text-sm disabled:opacity-50 transition-colors"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isWaiting}
            className="px-5 py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-semibold text-sm disabled:opacity-50 transition-colors self-end"
          >
            Send
          </button>
        </div>
      )}
    </div>
  );
}
