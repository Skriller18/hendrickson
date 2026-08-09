"use client";

import { useState } from "react";
import { FileText, Upload, X, ChevronRight } from "lucide-react";
import { useStore } from "@/stores";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

export function DrawerPanel() {
  const { prdContent, setPrdContent, requirements, setRequirements, setActiveContextId } = useStore();
  const [isOpen, setIsOpen] = useState(true);
  const [loading, setLoading] = useState(false);
  const [text, setText] = useState("");

  async function handleUpload() {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const result = await api.contexts.triangulate({ prd_content: text });
      setActiveContextId(result.context_id);
      setRequirements(result.requirements);
      setPrdContent(text);
    } catch (err) {
      console.error("Failed to triangulate:", err);
    } finally {
      setLoading(false);
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
            <button
              onClick={handleUpload}
              disabled={loading || !text.trim()}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-md bg-primary text-primary-foreground text-sm hover:bg-primary/90 disabled:opacity-50"
            >
              <Upload className="w-4 h-4" />
              {loading ? "Processing..." : "Ingest PRD"}
            </button>
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
