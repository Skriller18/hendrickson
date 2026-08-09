const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  health: () => request<{ status: string; version: string }>("/api/health"),

  chat: {
    send: (message: string, contextId?: string, model?: string) =>
      request<{ reply: string; actions: Array<Record<string, unknown>> }>("/api/chat/send", {
        method: "POST",
        body: JSON.stringify({ message, context_id: contextId, model }),
      }),
  },

  contexts: {
    triangulate: (data: {
      prd_content?: string;
      prd_path?: string;
      repo_url?: string;
      branch?: string;
      jira_keys?: string[];
      linear_issue_ids?: string[];
    }) =>
      request<{
        context_id: string;
        requirements: Array<Record<string, unknown>>;
        code_entities: Array<Record<string, unknown>>;
        tickets: Array<Record<string, unknown>>;
        codebase?: Record<string, unknown>;
      }>("/api/contexts/triangulate", {
        method: "POST",
        body: JSON.stringify(data),
      }),

    get: (contextId: string) => request<Record<string, unknown>>(`/api/contexts/${contextId}`),

    list: () => request<Array<Record<string, unknown>>>("/api/contexts"),
  },

  tests: {
    generate: (data: {
      context_id: string;
      category?: string;
      sub_category?: string;
      language?: string;
      framework?: string;
    }) =>
      request<Array<Record<string, unknown>>>("/api/tests/generate", {
        method: "POST",
        body: JSON.stringify(data),
      }),

    list: (contextId?: string) =>
      request<Array<Record<string, unknown>>>(
        `/api/tests${contextId ? `?context_id=${contextId}` : ""}`
      ),

    get: (testId: string) => request<Record<string, unknown>>(`/api/tests/${testId}`),

    update: (testId: string, update: Record<string, unknown>) =>
      request<{ status: string }>(`/api/tests/${testId}`, {
        method: "PUT",
        body: JSON.stringify(update),
      }),
  },

  runs: {
    execute: (data: {
      context_id: string;
      test_ids?: string[];
      environment?: string;
    }) =>
      request<{
        run_id: string;
        status: string;
        total_tests: number;
        passed: number;
        failed: number;
        errors: number;
        duration_ms: number;
      }>("/api/runs/execute", {
        method: "POST",
        body: JSON.stringify(data),
      }),

    get: (runId: string) => request<Record<string, unknown>>(`/api/runs/${runId}`),

    list: (contextId?: string) =>
      request<Array<Record<string, unknown>>>(
        `/api/runs${contextId ? `?context_id=${contextId}` : ""}`
      ),
  },

  models: {
    list: () =>
      request<{
        providers: Record<string, { name: string; models: Array<Record<string, unknown>> }>;
        all: Array<Record<string, unknown>>;
      }>("/api/models"),
    providers: () =>
      request<Record<string, { name: string; model_count: number }>>("/api/models/providers"),
  },

  settings: {
    get: () =>
      request<{
        settings_id: string;
        provider_keys: Array<{ provider: string; api_key: string; label: string }>;
        connectors: Record<string, unknown>;
        default_model: string;
      }>("/api/settings"),

    addProviderKey: (provider: string, apiKey: string) =>
      request<{ status: string; provider: string }>("/api/settings/provider-keys", {
        method: "POST",
        body: JSON.stringify({ provider, api_key: apiKey }),
      }),

    removeProviderKey: (provider: string) =>
      request<{ status: string }>(`/api/settings/provider-keys/${provider}`, {
        method: "DELETE",
      }),

    configureJira: (url: string, email: string, apiToken: string) =>
      request<{ status: string }>("/api/settings/jira", {
        method: "POST",
        body: JSON.stringify({ url, email, api_token: apiToken }),
      }),

    configureLinear: (apiKey: string) =>
      request<{ status: string }>("/api/settings/linear", {
        method: "POST",
        body: JSON.stringify({ api_key: apiKey }),
      }),

    configureGitHub: (token: string) =>
      request<{ status: string; username: string; connected: boolean }>("/api/settings/github", {
        method: "POST",
        body: JSON.stringify({ token }),
      }),

    disconnectGitHub: () =>
      request<{ status: string }>("/api/settings/github", {
        method: "DELETE",
      }),

    configureGemini: (apiKey: string, useVertex: boolean, vertexProject: string, vertexLocation: string) =>
      request<{ status: string }>("/api/settings/gemini", {
        method: "POST",
        body: JSON.stringify({
          api_key: apiKey,
          use_vertex: useVertex,
          vertex_project: vertexProject,
          vertex_location: vertexLocation,
        }),
      }),
  },

  connectors: {
    listGitHubRepos: () =>
      request<Array<Record<string, unknown>>>("/api/connectors/github/repos"),

    listRepoBranches: (owner: string, repo: string) =>
      request<Array<{ name: string; sha: string }>>(`/api/connectors/github/repos/${owner}/${repo}/branches`),

    getJiraIssue: (issueKey: string) =>
      request<Record<string, unknown>>("/api/connectors/jira/issue", {
        method: "POST",
        body: JSON.stringify({ issue_key: issueKey }),
      }),

    searchJira: (jql: string, maxResults: number = 50) =>
      request<Array<Record<string, unknown>>>("/api/connectors/jira/search", {
        method: "POST",
        body: JSON.stringify({ jql, max_results: maxResults }),
      }),

    getLinearIssue: (issueId: string) =>
      request<Record<string, unknown>>("/api/connectors/linear/issue", {
        method: "POST",
        body: JSON.stringify({ issue_id: issueId }),
      }),

    listLinearTeams: () =>
      request<Array<Record<string, unknown>>>("/api/connectors/linear/teams"),

    searchLinear: (teamId: string, maxResults: number = 50) =>
      request<Array<Record<string, unknown>>>("/api/connectors/linear/search", {
        method: "POST",
        body: JSON.stringify({ team_id: teamId, max_results: maxResults }),
      }),
  },
};
