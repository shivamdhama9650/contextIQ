"use client";

import { Loader2, Search } from "lucide-react";
import { useState } from "react";

import { type SearchHit } from "@/lib/api/search";
import { formatApiError } from "@/lib/api/errors";

type Props = {
  initialQuery?: string;
};

export function SearchForm({ initialQuery = "" }: Props) {
  const [query, setQuery] = useState(initialQuery);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<SearchHit[]>([]);

  async function handleSearch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query.trim(), limit: 5 })
      });
      const body = await response.json().catch(() => null);

      if (!response.ok) {
        setError(formatApiError(body, "Search failed."));
        return;
      }

      setResults(body?.results ?? []);
    } catch {
      setError("Search request failed. Is the backend running?");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div>
      <form className="flex gap-3" onSubmit={handleSearch}>
        <input
          className="flex-1 rounded-md border border-slate-300 bg-white px-4 py-3 text-sm"
          onChange={(event) => setQuery(event.target.value)}
          placeholder="e.g. How do I apply for leave?"
          value={query}
        />
        <button
          className="inline-flex items-center gap-2 rounded-md bg-accent px-5 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:bg-slate-400"
          disabled={isLoading || query.trim().length < 2}
          type="submit"
        >
          {isLoading ? (
            <Loader2 aria-hidden="true" className="animate-spin" size={16} />
          ) : (
            <Search aria-hidden="true" size={16} />
          )}
          Search
        </button>
      </form>

      {error ? (
        <p className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </p>
      ) : null}

      {results.length > 0 ? (
        <div className="mt-8 space-y-4">
          {results.map((hit) => (
            <article
              className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
              key={hit.chunk_id}
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 className="font-semibold">{hit.document_title}</h2>
                <span className="text-xs font-semibold text-accent">
                  {(hit.relevance_score * 100).toFixed(0)}% match
                </span>
              </div>
              <p className="mt-1 text-xs capitalize text-slate-500">
                {hit.category}
                {hit.page_start > 0 ? ` · page ${hit.page_start}` : ""}
              </p>
              <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                {hit.content}
              </p>
            </article>
          ))}
        </div>
      ) : null}

      {!error && !isLoading && query.trim().length >= 2 && results.length === 0 ? (
        <p className="mt-6 text-sm text-slate-600">
          No matches yet. Upload and index documents first, then search again.
        </p>
      ) : null}
    </div>
  );
}
