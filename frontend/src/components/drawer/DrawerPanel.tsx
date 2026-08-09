"use client";

import { useState, useRef } from "react";
import { FileText, Upload, X, ChevronRight, Link2, Loader2, FileUp } from "lucide-react";
import { useStore } from "@/stores";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

export function DrawerPanel() {
  const {
    prdContent, setPrdContent,
    requirements, setRequirements,
    setActiveContextId,
    selectedRepo, selectedBranch,
    selectedJiraKeys, selectedLinearIds,
  } = useStore();

  const [isOpen, setIsOpen] = useState(true);
  const [loading, setLoading] = useState(false);
  const [text, setText] = useState("");
  const [uploading, setUploading] = useState(false);
  const [googleDocUrl, setGoogleDocUrl] = useState("");
  const [googleDocLoading, setGoogleDocLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleIngest() {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const result = await api.contexts.triangulate({
        prd_content: text,
        repo_url: selectedRepo?.clone_url,
        branch: selectedBranch?.name || "main",
        jira_keys: selectedJiraKeys || undefined,
        linear_issue_ids: selectedLinearIds || undefined,
      });
      setActiveContextId(result.context_id);
      setRequirements(result.requirements);
      setPrdContent(text);
    } catch (err) {
      console.error("Failed to triangulate:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/prd/upload`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Upload failed");
      const data = await res.json();
      setText(data.content);
      setRequirements(data.requirements);
      setPrdContent(data.content);
    } catch (err) {
      console.error("File upload failed:", err);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleGoogleDoc() {
    if (!googleDocUrl.trim()) return;
    setGoogleDocLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/prd/google-doc`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ doc_url: googleDocUrl }),
      });
      if (!res.ok) throw new Error("Failed to fetch Google Doc");
      const data = await res.json();
      setText(data.content);
      setRequirements(data.requirements);
      setPrdContent(data.content);
    } catch (err) {
      console.error("Google Doc fetch failed:", err);
    } finally {
      setGoogleDocLoading(false);
    }
  }

  return (
    <div className={cn("flex flex-col h-full border-r border-border", isOpen ? "w-80" : "w-10")}>
      <div className="flex items-center justify-between px-3 py-3 border-b border-border">
        {isOpen && (
          <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <FileText className="w-4 h-4" /> PRD Drawer
          </h2>
        )}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-1 rounded hover:bg-secondary text-muted-foreground"
        >
          <ChevronRight className={cn("w-4 h-4 transition-transform", isOpen && "rotate-180")} />
        </button>
      </div>

      {isOpen && (
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="p-3 space-y-3">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste PRD content or requirements here..."
              className="w-full h-32 bg-secondary border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring resize-none"
            />

            <div className="flex gap-2">
              <button
                onClick={handleIngest}
                disabled={loading || !text.trim()}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-md bg-primary text-primary-foreground text-sm hover:bg-primary/90 disabled:opacity-50"
              >
                <Upload className="w-4 h-4" />
                {loading ? "Processing..." : "Ingest PRD"}
              </button>
            </div>

            <div className="flex gap-2">
              <input
                ref={fileInputRef}
                type="file"
                accept=".md,.txt,.pdf"
                onChange={handleFileUpload}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="flex-1 flex items-center justify-center gap-1.5 px-2 py-1.5 rounded-md bg-secondary border border-border text-xs text-foreground hover:bg-secondary/80 disabled:opacity-50"
              >
                {uploading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <FileUp className="w-3.5 h-3.5" />}
                {uploading ? "Uploading..." : "Upload .md/.txt/.pdf"}
              </button>
            </div>

            <div className="space-y-1.5">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={googleDocUrl}
                  onChange={(e) => setGoogleDocUrl(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleGoogleDoc()}
                  placeholder="Google Doc URL..."
                  className="flex-1 bg-secondary border border-border rounded-md px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                />
                <button
                  onClick={handleGoogleDoc}
                  disabled={googleDocLoading || !googleDocUrl.trim()}
                  className="px-3 py-1.5 rounded-md bg-secondary border border-border text-xs text-foreground hover:bg-secondary/80 disabled:opacity-50 flex items-center gap-1"
                >
                  {googleDocLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Link2 className="w-3 h-3" />}
                  Fetch
                </button>
              </div>
            </div>

            {(selectedRepo || (selectedJiraKeys || []).length > 0 || (selectedLinearIds || []).length > 0) && (
              <div className="p-2 rounded-md bg-secondary/50 border border-border text-xs space-y-1">
                <span className="text-muted-foreground font-semibold">Linked to context:</span>
                {selectedRepo && (
                  <p className="text-foreground">Repo: {selectedRepo.full_name} ({selectedBranch?.name || "main"})</p>
                )}
                {(selectedJiraKeys || []).length > 0 && (
                  <p className="text-foreground">JIRA: {(selectedJiraKeys || []).join(", ")}</p>
                )}
                {(selectedLinearIds || []).length > 0 && (
                  <p className="text-foreground">Linear: {(selectedLinearIds || []).join(", ")}</p>
                )}
              </div>
            )}
          </div>

          {requirements.length > 0 && (
            <div className="flex-1 overflow-y-auto px-3 pb-3">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                Extracted Requirements ({requirements.length})
              </h3>
              <div className="space-y-1.5">
                {requirements.map((req, i) => (
                  <div
                    key={i}
                    className="p-2 rounded-md bg-secondary/50 border border-border text-xs"
                  >
                    <span className="text-primary font-mono">{req.tag as string}</span>
                    <p className="text-foreground mt-0.5 line-clamp-2">
                      {req.description as string}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {prdContent && requirements.length === 0 && (
            <div className="flex-1 overflow-y-auto px-3 pb-3">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                PRD Content
              </h3>
              <div className="p-3 rounded-md bg-secondary/50 border border-border text-xs text-foreground whitespace-pre-wrap max-h-96 overflow-y-auto">
                {prdContent}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
