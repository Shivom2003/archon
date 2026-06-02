import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { Features } from "@/components/landing/Features";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Pricing } from "@/components/landing/Pricing";
import { Waitlist } from "@/components/landing/Waitlist";

export default function LandingPage() {
  return (
    <>
      <Navbar />
      <main className="pt-16">
        <Hero />
        <Features />
        <HowItWorks />
        <Pricing />
        <Waitlist />
      </main>
      <footer className="border-t border-zinc-800 py-8 text-center text-sm text-zinc-500">
        <p>
          © {new Date().getFullYear()} Archon ·{" "}
          <a
            href="https://github.com/Shivom2003/archon"
            className="hover:text-zinc-300 transition-colors"
          >
            GitHub
          </a>{" "}
          ·{" "}
          <a href="/privacy" className="hover:text-zinc-300 transition-colors">
            Privacy
          </a>
        </p>
      </footer>
    </>
  );
}
