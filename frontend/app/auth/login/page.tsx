"use client";

import { LogIn } from "lucide-react";
import { useState } from "react";

import { createClient } from "@/lib/supabase/browser";

export default function LoginPage() {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleGoogleLogin() {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const supabase = createClient();
      const origin = window.location.origin;
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: `${origin}/auth/callback`
        }
      });

      if (error) {
        setErrorMessage(error.message);
        setIsLoading(false);
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unable to start Google login.";
      setErrorMessage(message);
      setIsLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-surface px-6 py-12 text-ink">
      <section className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-accent">
          Secure Access
        </p>
        <h1 className="mt-3 text-3xl font-semibold">Sign in to continue</h1>
        <p className="mt-4 text-sm leading-6 text-slate-600">
          Use your company Google account to access approved knowledge sources.
        </p>

        <button
          className="mt-8 flex w-full items-center justify-center gap-2 rounded-md bg-accent px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          disabled={isLoading}
          onClick={handleGoogleLogin}
          type="button"
        >
          <LogIn aria-hidden="true" size={18} />
          {isLoading ? "Redirecting..." : "Continue with Google"}
        </button>

        {errorMessage ? (
          <p className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {errorMessage}
          </p>
        ) : null}
      </section>
    </main>
  );
}
