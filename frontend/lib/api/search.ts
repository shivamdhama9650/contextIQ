import { env } from "@/lib/env";
import { formatApiError } from "@/lib/api/errors";

export type SearchHit = {
  chunk_id: string;
  document_id: string;
  document_title: string;
  category: string;
  content: string;
  page_start: number;
  page_end: number;
  relevance_score: number;
};

export type SearchResponse = {
  query: string;
  results: SearchHit[];
};

export async function semanticSearch(
  accessToken: string,
  query: string,
  limit = 5
): Promise<SearchResponse> {
  const response = await fetch(`${env.apiBaseUrl}/search`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ query, limit }),
    cache: "no-store"
  });

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(formatApiError(body, `Search failed (${response.status})`));
  }

  return body as SearchResponse;
}
