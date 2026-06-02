"use client";

import { useState } from "react";

const plans = [
  {
    name: "Free",
    price: "$0",
    description: "For individuals exploring the tool",
    features: [
      "CLI tool (pip install archon-arch-ai)",
      "Bring your own API key",
      "Unlimited specs locally",
      "All output formats",
    ],
    cta: "Install now",
    ctaHref: "https://pypi.org/project/archon-arch-ai/",
    highlight: false,
  },
  {
    name: "Pro",
    price: "Coming soon",
    description: "Hosted product with no API key needed",
    features: [
      "Web UI interview flow",
      "Archon pays the API costs",
      "Spec storage + history",
      "Shareable spec links",
      "Priority support",
    ],
    cta: "Join waitlist",
    ctaHref: "#waitlist",
    highlight: true,
  },
  {
    name: "Team",
    price: "Coming soon",
    description: "For teams building with multiple agents",
    features: [
      "Everything in Pro",
      "Team workspace",
      "Shared spec library",
      "SAML SSO",
      "Dedicated support",
    ],
    cta: "Join waitlist",
    ctaHref: "#waitlist",
    highlight: false,
  },
];

export function Pricing() {
  return (
    <section id="pricing" className="py-24 px-4 bg-zinc-900">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Pricing</h2>
          <p className="text-zinc-400 text-lg">
            The Python library is free and open source forever.
            The hosted product is in private beta.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`p-6 rounded-xl border ${
                plan.highlight
                  ? "border-cyan-500/50 bg-cyan-500/5"
                  : "border-zinc-800 bg-zinc-950"
              }`}
            >
              {plan.highlight && (
                <div className="text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-3">
                  Most popular
                </div>
              )}
              <h3 className="text-xl font-bold mb-1">{plan.name}</h3>
              <div className="text-3xl font-bold mb-1">{plan.price}</div>
              <p className="text-zinc-400 text-sm mb-6">{plan.description}</p>
              <ul className="space-y-2 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-zinc-300">
                    <span className="text-green-400">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
              <a
                href={plan.ctaHref}
                className={`block text-center py-2.5 px-4 rounded-lg font-semibold text-sm transition-colors ${
                  plan.highlight
                    ? "bg-cyan-500 hover:bg-cyan-400 text-black"
                    : "border border-zinc-700 hover:border-zinc-500 text-zinc-300"
                }`}
              >
                {plan.cta}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
