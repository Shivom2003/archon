"use client";

import Link from "next/link";
import { useClerk } from "@clerk/nextjs";

interface Props {
  isSignedIn: boolean;
}

export function NavbarClient({ isSignedIn }: Props) {
  const { signOut, user } = useClerk();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-sm">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="font-bold text-lg tracking-tight">
          <span className="text-cyan-400">arch</span>on
        </Link>

        <div className="hidden md:flex items-center gap-6 text-sm text-zinc-400">
          <Link href="#features" className="hover:text-white transition-colors">Features</Link>
          <Link href="#how-it-works" className="hover:text-white transition-colors">How it works</Link>
          <Link href="#pricing" className="hover:text-white transition-colors">Pricing</Link>
          <a
            href="https://github.com/Shivom2003/archon"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-white transition-colors"
          >
            GitHub
          </a>
        </div>

        <div className="flex items-center gap-3">
          {!isSignedIn ? (
            <>
              <Link href="/sign-in" className="text-sm text-zinc-400 hover:text-white transition-colors">
                Sign in
              </Link>
              <Link
                href="#waitlist"
                className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black text-sm font-semibold transition-colors"
              >
                Join waitlist
              </Link>
            </>
          ) : (
            <>
              <Link
                href="/dashboard"
                className="px-4 py-2 rounded-lg border border-zinc-700 hover:border-zinc-500 text-sm text-zinc-300 transition-colors"
              >
                Dashboard
              </Link>
              <button
                onClick={() => signOut({ redirectUrl: "/" })}
                className="text-sm text-zinc-400 hover:text-white transition-colors"
              >
                Sign out
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
