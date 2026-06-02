"use client";

import { useState } from "react";

export function Waitlist() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // TODO Phase 4: POST to Resend / your waitlist endpoint
    // For now, just show success state
    setSubmitted(true);
  };

  return (
    <section id="waitlist" className="py-24 px-4">
      <div className="max-w-xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-4">Get early access</h2>
        <p className="text-zinc-400 text-lg mb-8">
          The web product is in private beta. Join the waitlist and we'll reach
          out when your spot is ready.
        </p>

        {submitted ? (
          <div className="p-6 rounded-xl border border-green-500/30 bg-green-500/5 text-green-400">
            You're on the list. We'll be in touch!
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              className="flex-1 px-4 py-3 rounded-lg border border-zinc-700 bg-zinc-900 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
            <button
              type="submit"
              className="px-6 py-3 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-semibold transition-colors whitespace-nowrap"
            >
              Join waitlist
            </button>
          </form>
        )}
      </div>
    </section>
  );
}
