"use client";

import { useState, useEffect } from "react";
import { Settings, Key, Link2, Trash2, Check, AlertCircle, Github, GitBranch, ExternalLink } from "lucide-react";
import { useStore } from "@/stores";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Repo {
  id: number;
  name: string;
  full_name: string;
  private: boolean;
  html_url: string;
  clone_url: string;
  default_branch: string;
  description: string;
  language: string;
  updated_at: string;
}

interface Branch {
  name: string;
  sha: string;
}

export function SettingsPanel() {
  const {
    providerKeys, setProviderKeys,
    jiraConfig, setJiraConfig,
    linearConfig, setLinearConfig,
    githubConfig, setGitHubConfig,
    geminiConfig, setGeminiConfig,
    selectedRepo, setSelectedRepo,
    selectedBranch, setSelectedBranch,
    selectedJiraKeys, setSelectedJiraKeys,
    selectedLinearIds, setSelectedLinearIds,
  } = useStore();

  const [activeSection, setActiveSection] = useState<string>("providers");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const [openaiKey, setOpenaiKey] = useState("");
  const [anthropicKey, setAnthropicKey] = useState("");
  const [deepseekKey, setDeepseekKey] = useState("");
  const [openrouterKey, setOpenrouterKey] = useState("");

  const [jiraUrl, setJiraUrl] = useState("");
  const [jiraEmail, setJiraEmail] = useState("");
  const [jiraApiToken, setJiraApiToken] = useState("");

  const [linearApiKey, setLinearApiKey] = useState("");

  const [githubToken, setGithubToken] = useState("");
  const [repos, setRepos] = useState<Repo[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [loadingRepos, setLoadingRepos] = useState(false);
  const [loadingBranches, setLoadingBranches] = useState(false);

  const [geminiApiKey, setGeminiApiKey] = useState("");
  const [geminiUseVertex, setGeminiUseVertex] = useState(false);
  const [geminiVertexProject, setGeminiVertexProject] = useState("");
  const [geminiVertexLocation, setGeminiVertexLocation] = useState("us-central1");

  const [jiraSearchJql, setJiraSearchJql] = useState("");
  const [jiraSearchResults, setJiraSearchResults] = useState<Array<Record<string, unknown>>>([]);
  const [loadingJiraSearch, setLoadingJiraSearch] = useState(false);

  const [linearTeamId, setLinearTeamId] = useState("");
  const [linearTeams, setLinearTeams] = useState<Array<Record<string, unknown>>>([]);
  const [linearSearchResults, setLinearSearchResults] = useState<Array<Record<string, unknown>>>([]);
  const [loadingLinearSearch, setLoadingLinearSearch] = useState(false);

  useEffect(() => {
    api.settings.get().then((s) => {
      const keys = s.provider_keys as Array<{ provider: string; api_key: string; label: string }>;
      setProviderKeys(keys);
      for (const k of keys) {
        if (k.provider === "openai") setOpenaiKey(k.api_key);
        if (k.provider === "anthropic") setAnthropicKey(k.api_key);
        if (k.provider === "deepseek") setDeepseekKey(k.api_key);
        if (k.provider === "openrouter") setOpenrouterKey(k.api_key);
      }
      const conn = s.connectors as Record<string, unknown>;
      if (conn) {
        const j = conn.jira as Record<string, string> | undefined;
        if (j) {
          setJiraConfig(j as any);
          setJiraUrl(j.url || "");
          setJiraEmail(j.email || "");
          setJiraApiToken(j.api_token || "");
        }
        const l = conn.linear as Record<string, string> | undefined;
        if (l) {
          setLinearConfig(l as any);
          setLinearApiKey(l.api_key || "");
        }
        const g = conn.github as Record<string, unknown> | undefined;
        if (g) {
          setGitHubConfig(g as any);
          setGithubToken(g.token as string || "");
        }
        const gm = conn.gemini as Record<string, unknown> | undefined;
        if (gm) {
          setGeminiConfig(gm as any);
          setGeminiApiKey(gm.api_key as string || "");
          setGeminiUseVertex((gm.use_vertex as boolean) || false);
          setGeminiVertexProject(gm.vertex_project as string || "");
          setGeminiVertexLocation(gm.vertex_location as string || "us-central1");
        }
      }
    }).catch(() => {});
  }, []);

  function showMessage(type: "success" | "error", text: string) {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 3000);
  }

  async function saveProviderKey(provider: string, key: string) {
    if (!key.trim()) return;
    setLoading(true);
    try {
      await api.settings.addProviderKey(provider, key);
      const updated = providerKeys.filter(k => k.provider !== provider);
      updated.push({ provider, api_key: key, label: "" });
      setProviderKeys(updated);
      showMessage("success", `${provider} key saved`);
    } catch {
      showMessage("error", `Failed to save ${provider} key`);
    } finally {
      setLoading(false);
    }
  }

  async function removeProviderKey(provider: string) {
    setLoading(true);
    try {
      await api.settings.removeProviderKey(provider);
      setProviderKeys(providerKeys.filter(k => k.provider !== provider));
      if (provider === "openai") setOpenaiKey("");
      if (provider === "anthropic") setAnthropicKey("");
      if (provider === "deepseek") setDeepseekKey("");
      if (provider === "openrouter") setOpenrouterKey("");
      showMessage("success", `${provider} key removed`);
    } catch {
      showMessage("error", `Failed to remove ${provider} key`);
    } finally {
      setLoading(false);
    }
  }

  async function saveJira() {
    if (!jiraUrl.trim() || !jiraEmail.trim() || !jiraApiToken.trim()) return;
    setLoading(true);
    try {
      await api.settings.configureJira(jiraUrl, jiraEmail, jiraApiToken);
      setJiraConfig({ url: jiraUrl, email: jiraEmail, api_token: jiraApiToken });
      showMessage("success", "JIRA configured");
    } catch {
      showMessage("error", "Failed to configure JIRA");
    } finally {
      setLoading(false);
    }
  }

  async function saveLinear() {
    if (!linearApiKey.trim()) return;
    setLoading(true);
    try {
      await api.settings.configureLinear(linearApiKey);
      setLinearConfig({ api_key: linearApiKey });
      showMessage("success", "Linear configured");
    } catch {
      showMessage("error", "Failed to configure Linear");
    } finally {
      setLoading(false);
    }
  }

  async function connectGitHub() {
    if (!githubToken.trim()) return;
    setLoading(true);
    try {
      const res = await api.settings.configureGitHub(githubToken);
      setGitHubConfig({ token: githubToken, connected: true, username: res.username || "" });
      showMessage("success", `Connected as ${res.username || "GitHub user"}`);
    } catch {
      showMessage("error", "Failed to connect GitHub");
    } finally {
      setLoading(false);
    }
  }

  async function disconnectGitHub() {
    setLoading(true);
    try {
      await api.settings.disconnectGitHub();
      setGitHubConfig({ token: "", connected: false, username: "" });
      setGithubToken("");
      setRepos([]);
      setBranches([]);
      setSelectedRepo(null);
      setSelectedBranch(null);
      showMessage("success", "GitHub disconnected");
    } catch {
      showMessage("error", "Failed to disconnect GitHub");
    } finally {
      setLoading(false);
    }
  }

  async function saveGemini() {
    setLoading(true);
    try {
      await api.settings.configureGemini(
        geminiApiKey,
        geminiUseVertex,
        geminiVertexProject,
        geminiVertexLocation,
      );
      setGeminiConfig({
        api_key: geminiApiKey,
        use_vertex: geminiUseVertex,
        vertex_project: geminiVertexProject,
        vertex_location: geminiVertexLocation,
      });
      showMessage("success", "Gemini configured");
    } catch {
      showMessage("error", "Failed to configure Gemini");
    } finally {
      setLoading(false);
    }
  }

  async function fetchRepos() {
    setLoadingRepos(true);
    try {
      const data = await api.connectors.listGitHubRepos();
      setRepos(data as unknown as Repo[]);
    } catch {
      showMessage("error", "Failed to fetch repos");
    } finally {
      setLoadingRepos(false);
    }
  }

  async function selectRepoAndFetchBranches(repo: Repo) {
    setSelectedRepo(repo);
    setLoadingBranches(true);
    try {
      const [owner, name] = repo.full_name.split("/");
      const data = await api.connectors.listRepoBranches(owner, name);
      setBranches(data as Branch[]);
      if (data.length > 0) {
        setSelectedBranch(data[0] as Branch);
      }
    } catch {
      showMessage("error", "Failed to fetch branches");
    } finally {
      setLoadingBranches(false);
    }
  }

  async function searchJira() {
    if (!jiraSearchJql.trim()) return;
    setLoadingJiraSearch(true);
    try {
      const data = await api.connectors.searchJira(jiraSearchJql, 50);
      setJiraSearchResults(data as Array<Record<string, unknown>>);
    } catch {
      showMessage("error", "Failed to search JIRA");
    } finally {
      setLoadingJiraSearch(false);
    }
  }

  async function fetchLinearTeams() {
    setLoadingLinearSearch(true);
    try {
      const data = await api.connectors.listLinearTeams();
      setLinearTeams(data as Array<Record<string, unknown>>);
    } catch {
      showMessage("error", "Failed to fetch Linear teams");
    } finally {
      setLoadingLinearSearch(false);
    }
  }

  async function searchLinear() {
    if (!linearTeamId.trim()) return;
    setLoadingLinearSearch(true);
    try {
      const data = await api.connectors.searchLinear(linearTeamId, 50);
      setLinearSearchResults(data as Array<Record<string, unknown>>);
    } catch {
      showMessage("error", "Failed to search Linear");
    } finally {
      setLoadingLinearSearch(false);
    }
  }

  function toggleJiraKey(key: string) {
    const current = selectedJiraKeys || [];
    if (current.includes(key)) {
      setSelectedJiraKeys(current.filter(k => k !== key));
    } else {
      setSelectedJiraKeys([...current, key]);
    }
  }

  function toggleLinearId(id: string) {
    const current = selectedLinearIds || [];
    if (current.includes(id)) {
      setSelectedLinearIds(current.filter(k => k !== id));
    } else {
      setSelectedLinearIds([...current, id]);
    }
  }

  const sections = [
    { id: "providers", label: "AI Providers", icon: <Key className="w-3.5 h-3.5" /> },
    { id: "github", label: "GitHub", icon: <Github className="w-3.5 h-3.5" /> },
    { id: "jira", label: "JIRA", icon: <Link2 className="w-3.5 h-3.5" /> },
    { id: "linear", label: "Linear", icon: <Link2 className="w-3.5 h-3.5" /> },
  ];

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-3 border-b border-border">
        <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
          <Settings className="w-4 h-4" /> Settings & Connectors
        </h2>
        <p className="text-xs text-muted-foreground mt-0.5">
          Configure AI providers, GitHub, JIRA, and Linear
        </p>
      </div>

      {message && (
        <div className={cn(
          "mx-4 mt-3 px-3 py-2 rounded-md text-xs flex items-center gap-2",
          message.type === "success" ? "bg-green-400/10 text-green-400" : "bg-red-400/10 text-red-400"
        )}>
          {message.type === "success" ? <Check className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
          {message.text}
        </div>
      )}

      <div className="flex gap-1 px-4 pt-3 pb-2 border-b border-border">
        {sections.map((s) => (
          <button
            key={s.id}
            onClick={() => setActiveSection(s.id)}
            className={cn(
              "flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs transition-colors",
              activeSection === s.id
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:text-foreground hover:bg-secondary"
            )}
          >
            {s.icon}
            {s.label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {activeSection === "providers" && (
          <div className="space-y-4">
            <p className="text-xs text-muted-foreground">
              Bring your own API keys for any AI provider. Keys are stored securely and used for test generation and chat.
            </p>
            {[
              { provider: "openai", label: "OpenAI", value: openaiKey, setter: setOpenaiKey, placeholder: "sk-..." },
              { provider: "anthropic", label: "Anthropic", value: anthropicKey, setter: setAnthropicKey, placeholder: "sk-ant-..." },
              { provider: "deepseek", label: "DeepSeek", value: deepseekKey, setter: setDeepseekKey, placeholder: "sk-..." },
              { provider: "openrouter", label: "OpenRouter", value: openrouterKey, setter: setOpenrouterKey, placeholder: "sk-or-..." },
            ].map(({ provider, label, value, setter, placeholder }) => (
              <div key={provider} className="p-3 rounded-md bg-secondary/50 border border-border space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-foreground">{label}</span>
                  {providerKeys.some(k => k.provider === provider) && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-400/10 text-green-400">Configured</span>
                  )}
                </div>
                <div className="flex gap-2">
                  <input
                    type="password"
                    value={value}
                    onChange={(e) => setter(e.target.value)}
                    placeholder={placeholder}
                    className="flex-1 bg-background border border-border rounded-md px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                  />
                  <button
                    onClick={() => saveProviderKey(provider, value)}
                    disabled={loading || !value.trim()}
                    className="px-3 py-1.5 rounded-md bg-primary text-primary-foreground text-xs hover:bg-primary/90 disabled:opacity-50"
                  >
                    Save
                  </button>
                  {providerKeys.some(k => k.provider === provider) && (
                    <button
                      onClick={() => removeProviderKey(provider)}
                      disabled={loading}
                      className="p-1.5 rounded-md text-muted-foreground hover:text-red-400 hover:bg-red-400/10"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            ))}
            <div className="border-t border-border pt-4 mt-2">
              <h3 className="text-sm font-semibold text-foreground mb-3">Google Gemini</h3>
              <p className="text-xs text-muted-foreground mb-3">
                Configure via AI Studio API key or Vertex AI for enterprise workloads.
              </p>
              <div className="p-3 rounded-md bg-secondary/50 border border-border space-y-3">
                <div className="flex items-center gap-3">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      checked={!geminiUseVertex}
                      onChange={() => setGeminiUseVertex(false)}
                      className="text-primary"
                    />
                    <span className="text-xs text-foreground">AI Studio (API Key)</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      checked={geminiUseVertex}
                      onChange={() => setGeminiUseVertex(true)}
                      className="text-primary"
                    />
                    <span className="text-xs text-foreground">Vertex AI</span>
                  </label>
                </div>

                {!geminiUseVertex ? (
                  <div>
                    <label className="text-xs text-muted-foreground">Gemini API Key</label>
                    <input
                      type="password"
                      value={geminiApiKey}
                      onChange={(e) => setGeminiApiKey(e.target.value)}
                      placeholder="AIza..."
                      className="w-full mt-1 bg-background border border-border rounded-md px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                    />
                    <p className="text-[10px] text-muted-foreground mt-1">
                      Get your key at{" "}
                      <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                        aistudio.google.com
                      </a>
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <div>
                      <label className="text-xs text-muted-foreground">GCP Project ID</label>
                      <input
                        type="text"
                        value={geminiVertexProject}
                        onChange={(e) => setGeminiVertexProject(e.target.value)}
                        placeholder="my-gcp-project"
                        className="w-full mt-1 bg-background border border-border rounded-md px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-muted-foreground">Location</label>
                      <input
                        type="text"
                        value={geminiVertexLocation}
                        onChange={(e) => setGeminiVertexLocation(e.target.value)}
                        placeholder="us-central1"
                        className="w-full mt-1 bg-background border border-border rounded-md px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                      />
                    </div>
                    <p className="text-[10px] text-muted-foreground">
                      Requires gcloud auth application-default login or GOOGLE_APPLICATION_CREDENTIALS set.
                    </p>
                  </div>
                )}

                <button
                  onClick={saveGemini}
                  disabled={loading || (!geminiUseVertex && !geminiApiKey.trim()) || (geminiUseVertex && !geminiVertexProject.trim())}
                  className="w-full px-3 py-2 rounded-md bg-primary text-primary-foreground text-sm hover:bg-primary/90 disabled:opacity-50"
                >
                  Save Gemini Configuration
                </button>

                {geminiConfig?.api_key && (
                  <div className="p-2 rounded-md bg-green-400/10 border border-green-400/20 text-xs text-green-400">
                    Gemini configured via {geminiConfig.use_vertex ? `Vertex AI (${geminiConfig.vertex_project})` : "AI Studio API Key"}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeSection === "github" && (
          <div className="space-y-4">
            <p className="text-xs text-muted-foreground">
              Connect your GitHub account to browse repositories and link them to test contexts.
            </p>

            {githubConfig?.connected ? (
              <div className="space-y-3">
                <div className="p-3 rounded-md bg-green-400/10 border border-green-400/20">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Github className="w-4 h-4 text-green-400" />
                      <span className="text-sm text-green-400">
                        Connected as {githubConfig.username || "GitHub user"}
                      </span>
                    </div>
                    <button
                      onClick={disconnectGitHub}
                      disabled={loading}
                      className="text-xs text-red-400 hover:text-red-300"
                    >
                      Disconnect
                    </button>
                  </div>
                </div>

                <button
                  onClick={fetchRepos}
                  disabled={loadingRepos}
                  className="w-full px-3 py-2 rounded-md bg-primary text-primary-foreground text-sm hover:bg-primary/90 disabled:opacity-50"
                >
                  {loadingRepos ? "Loading..." : "Browse Repositories"}
                </button>

                {repos.length > 0 && (
                  <div className="space-y-1.5 max-h-64 overflow-y-auto">
                    {repos.map((repo) => (
                      <button
                        key={repo.id}
                        onClick={() => selectRepoAndFetchBranches(repo)}
                        className={cn(
                          "w-full text-left p-2.5 rounded-md border text-xs transition-colors",
                          selectedRepo?.id === repo.id
                            ? "border-primary bg-primary/10"
                            : "border-border hover:bg-secondary"
                        )}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-foreground">{repo.full_name}</span>
                          <span className="text-[10px] text-muted-foreground">{repo.language}</span>
                        </div>
                        {repo.description && (
                          <p className="text-muted-foreground mt-0.5 line-clamp-1">{repo.description}</p>
                        )}
                      </button>
                    ))}
                  </div>
                )}

                {selectedRepo && branches.length > 0 && (
                  <div className="space-y-1.5">
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase flex items-center gap-1">
                      <GitBranch className="w-3 h-3" /> Branches
                    </h4>
                    {branches.map((b) => (
                      <button
                        key={b.name}
                        onClick={() => setSelectedBranch(b)}
                        className={cn(
                          "w-full text-left px-2.5 py-1.5 rounded-md text-xs border transition-colors",
                          selectedBranch?.name === b.name
                            ? "border-primary bg-primary/10 text-foreground"
                            : "border-border text-muted-foreground hover:text-foreground hover:bg-secondary"
                        )}
                      >
                        {b.name}
                      </button>
                    ))}
                  </div>
                )}

                {selectedRepo && (
                  <div className="p-3 rounded-md bg-secondary/50 border border-border text-xs space-y-1">
                    <p className="text-foreground font-medium">Selected Repository</p>
                    <p className="text-muted-foreground">{selectedRepo.full_name}</p>
                    {selectedBranch && <p className="text-muted-foreground">Branch: {selectedBranch.name}</p>}
                    <a
                      href={selectedRepo.html_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline flex items-center gap-1"
                    >
                      <ExternalLink className="w-3 h-3" /> Open on GitHub
                    </a>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-3 rounded-md bg-secondary/50 border border-border space-y-2">
                <label className="text-xs text-muted-foreground">GitHub Personal Access Token</label>
                <div className="flex gap-2">
                  <input
                    type="password"
                    value={githubToken}
                    onChange={(e) => setGithubToken(e.target.value)}
                    placeholder="ghp_..."
                    className="flex-1 bg-background border border-border rounded-md px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                  />
                  <button
                    onClick={connectGitHub}
                    disabled={loading || !githubToken.trim()}
                    className="px-3 py-1.5 rounded-md bg-primary text-primary-foreground text-xs hover:bg-primary/90 disabled:opacity-50"
                  >
                    Connect
                  </button>
                </div>
                <p className="text-[10px] text-muted-foreground">
                  Create a token at GitHub Settings &rarr; Developer settings &rarr; Personal access tokens. Needs <code>repo</code> and <code>read:user</code> scopes.
                </p>
              </div>
            )}
          </div>
        )}

        {activeSection === "jira" && (
          <div className="space-y-4">
            <p className="text-xs text-muted-foreground">
              Connect JIRA to pull tickets and link them to test contexts.
            </p>

            <div className="p-3 rounded-md bg-secondary/50 border border-border space-y-2">
              <div>
                <label className="text-xs text-muted-foreground">JIRA URL</label>
                <input
                  type="text"
                  value={jiraUrl}
                  onChange={(e) => setJiraUrl(e.target.value)}
                  placeholder="https://your-org.atlassian.net"
                  className="w-full mt-1 bg-background border border-border rounded-md px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                />
              </div>
              <div>
                <label className="text-xs text-muted-foreground">Email</label>
                <input
                  type="email"
                  value={jiraEmail}
                  onChange={(e) => setJiraEmail(e.target.value)}
                  placeholder="you@company.com"
                  className="w-full mt-1 bg-background border border-border rounded-md px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                />
              </div>
              <div>
                <label className="text-xs text-muted-foreground">API Token</label>
                <input
                  type="password"
                  value={jiraApiToken}
                  onChange={(e) => setJiraApiToken(e.target.value)}
                  placeholder="JIRA API token"
                  className="w-full mt-1 bg-background border border-border rounded-md px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                />
              </div>
              <button
                onClick={saveJira}
                disabled={loading || !jiraUrl.trim() || !jiraEmail.trim() || !jiraApiToken.trim()}
                className="w-full px-3 py-2 rounded-md bg-primary text-primary-foreground text-sm hover:bg-primary/90 disabled:opacity-50"
              >
                Save JIRA Configuration
              </button>
            </div>

            {jiraConfig?.url && (
              <div className="space-y-2">
                <div className="p-2 rounded-md bg-green-400/10 border border-green-400/20 text-xs text-green-400">
                  JIRA connected: {jiraConfig.url}
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs text-muted-foreground">Search Issues (JQL)</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={jiraSearchJql}
                      onChange={(e) => setJiraSearchJql(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && searchJira()}
                      placeholder='project = "PROJ" AND status = "In Progress"'
                      className="flex-1 bg-background border border-border rounded-md px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                    />
                    <button
                      onClick={searchJira}
                      disabled={loadingJiraSearch || !jiraSearchJql.trim()}
                      className="px-3 py-1.5 rounded-md bg-primary text-primary-foreground text-xs hover:bg-primary/90 disabled:opacity-50"
                    >
                      Search
                    </button>
                  </div>
                </div>

                {jiraSearchResults.length > 0 && (
                  <div className="space-y-1 max-h-64 overflow-y-auto">
                    {jiraSearchResults.map((issue: any, i) => (
                      <button
                        key={i}
                        onClick={() => toggleJiraKey(issue.external_id)}
                        className={cn(
                          "w-full text-left p-2 rounded-md border text-xs transition-colors",
                          (selectedJiraKeys || []).includes(issue.external_id)
                            ? "border-primary bg-primary/10"
                            : "border-border hover:bg-secondary"
                        )}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-foreground">{issue.external_id}</span>
                          <span className="text-[10px] text-muted-foreground">{issue.status}</span>
                        </div>
                        <p className="text-foreground mt-0.5 line-clamp-1">{issue.title}</p>
                      </button>
                    ))}
                  </div>
                )}

                {(selectedJiraKeys || []).length > 0 && (
                  <div className="p-2 rounded-md bg-secondary/50 border border-border text-xs">
                    <span className="text-muted-foreground">Selected: </span>
                    {(selectedJiraKeys || []).join(", ")}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeSection === "linear" && (
          <div className="space-y-4">
            <p className="text-xs text-muted-foreground">
              Connect Linear to pull issues and link them to test contexts.
            </p>

            <div className="p-3 rounded-md bg-secondary/50 border border-border space-y-2">
              <div>
                <label className="text-xs text-muted-foreground">Linear API Key</label>
                <div className="flex gap-2 mt-1">
                  <input
                    type="password"
                    value={linearApiKey}
                    onChange={(e) => setLinearApiKey(e.target.value)}
                    placeholder="lin_api_..."
                    className="flex-1 bg-background border border-border rounded-md px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                  />
                  <button
                    onClick={saveLinear}
                    disabled={loading || !linearApiKey.trim()}
                    className="px-3 py-1.5 rounded-md bg-primary text-primary-foreground text-xs hover:bg-primary/90 disabled:opacity-50"
                  >
                    Save
                  </button>
                </div>
              </div>
            </div>

            {linearConfig?.api_key && (
              <div className="space-y-2">
                <div className="p-2 rounded-md bg-green-400/10 border border-green-400/20 text-xs text-green-400">
                  Linear connected
                </div>

                <button
                  onClick={fetchLinearTeams}
                  disabled={loadingLinearSearch}
                  className="w-full px-3 py-2 rounded-md bg-primary text-primary-foreground text-sm hover:bg-primary/90 disabled:opacity-50"
                >
                  {loadingLinearSearch ? "Loading..." : "Fetch Teams"}
                </button>

                {linearTeams.length > 0 && (
                  <div className="space-y-1.5">
                    <label className="text-xs text-muted-foreground">Select Team</label>
                    {linearTeams.map((team: any) => (
                      <button
                        key={team.id}
                        onClick={() => { setLinearTeamId(team.id); searchLinear(); }}
                        className={cn(
                          "w-full text-left px-2.5 py-1.5 rounded-md text-xs border transition-colors",
                          linearTeamId === team.id
                            ? "border-primary bg-primary/10 text-foreground"
                            : "border-border text-muted-foreground hover:text-foreground hover:bg-secondary"
                        )}
                      >
                        {team.name} ({team.key})
                      </button>
                    ))}
                  </div>
                )}

                {linearSearchResults.length > 0 && (
                  <div className="space-y-1 max-h-64 overflow-y-auto">
                    {linearSearchResults.map((issue: any, i) => (
                      <button
                        key={i}
                        onClick={() => toggleLinearId(issue.external_id)}
                        className={cn(
                          "w-full text-left p-2 rounded-md border text-xs transition-colors",
                          (selectedLinearIds || []).includes(issue.external_id)
                            ? "border-primary bg-primary/10"
                            : "border-border hover:bg-secondary"
                        )}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-foreground">{issue.external_id}</span>
                          <span className="text-[10px] text-muted-foreground">{issue.status}</span>
                        </div>
                        <p className="text-foreground mt-0.5 line-clamp-1">{issue.title}</p>
                      </button>
                    ))}
                  </div>
                )}

                {(selectedLinearIds || []).length > 0 && (
                  <div className="p-2 rounded-md bg-secondary/50 border border-border text-xs">
                    <span className="text-muted-foreground">Selected: </span>
                    {(selectedLinearIds || []).join(", ")}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
