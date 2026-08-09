"use client";

import { useState } from "react";
import Editor from "@monaco-editor/react";
import { Code2, Play, CheckCircle2, XCircle, Clock, AlertTriangle } from "lucide-react";
import { useStore } from "@/stores";
import { api } from "@/lib/api";
import { cn, statusColor, statusBg } from "@/lib/utils";

const categoryIcons: Record<string, React.ReactNode> = {
  Unit: <Code2 className="w-3 h-3" />,
  Integration: <Code2 className="w-3 h-3" />,
  E2E: <Code2 className="w-3 h-3" />,
  UAT: <CheckCircle2 className="w-3 h-3" />,
};

const statusIcons: Record<string, React.ReactNode> = {
  Passed: <CheckCircle2 className="w-3 h-3 text-green-400" />,
  Failed: <XCircle className="w-3 h-3 text-red-400" />,
  Running: <Clock className="w-3 h-3 text-blue-400" />,
  Error: <AlertTriangle className="w-3 h-3 text-orange-400" />,
  Ready: <CheckCircle2 className="w-3 h-3 text-yellow-400" />,
  Draft: <Clock className="w-3 h-3 text-muted-foreground" />,
};

export function CanvasPanel() {
  const { testCases, setTestCases, selectedTestId, setSelectedTestId, activeContextId } = useStore();
  const [loading, setLoading] = useState(false);

  const selectedTest = testCases.find((t) => t.test_id === selectedTestId);

  async function handleGenerate(category: string, subCategory: string) {
    if (!activeContextId) return;
    setLoading(true);
    try {
      const tests = await api.tests.generate({
        context_id: activeContextId,
        category,
        sub_category: subCategory,
      });
      setTestCases([...testCases, ...(tests as unknown as typeof testCases)]);
    } catch (err) {
      console.error("Failed to generate tests:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <h2 className="text-sm font-semibold text-foreground">Test Suite Canvas</h2>
        <div className="flex gap-2">
          <button
            onClick={() => handleGenerate("Functional", "Unit")}
            disabled={loading || !activeContextId}
            className="px-2 py-1 text-xs rounded bg-secondary hover:bg-secondary/80 text-foreground disabled:opacity-50"
          >
            + Unit
          </button>
          <button
            onClick={() => handleGenerate("Functional", "Integration")}
            disabled={loading || !activeContextId}
            className="px-2 py-1 text-xs rounded bg-secondary hover:bg-secondary/80 text-foreground disabled:opacity-50"
          >
            + Integration
          </button>
          <button
            onClick={() => handleGenerate("Functional", "E2E")}
            disabled={loading || !activeContextId}
            className="px-2 py-1 text-xs rounded bg-secondary hover:bg-secondary/80 text-foreground disabled:opacity-50"
          >
            + E2E
          </button>
          <button
            onClick={() => handleGenerate("Functional", "UAT")}
            disabled={loading || !activeContextId}
            className="px-2 py-1 text-xs rounded bg-secondary hover:bg-secondary/80 text-foreground disabled:opacity-50"
          >
            + UAT
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="w-72 border-r border-border overflow-y-auto">
          {testCases.length === 0 ? (
            <div className="p-4 text-center text-muted-foreground text-sm">
              <p>No test cases yet.</p>
              <p className="mt-1 text-xs">
                Ingest a PRD and generate tests to get started.
              </p>
            </div>
          ) : (
            <div className="p-2 space-y-1">
              {testCases.map((tc) => (
                <button
                  key={tc.test_id}
                  onClick={() => setSelectedTestId(tc.test_id)}
                  className={cn(
                    "w-full text-left p-2 rounded-md text-xs transition-colors",
                    selectedTestId === tc.test_id
                      ? "bg-primary/10 border border-primary/30"
                      : "hover:bg-secondary border border-transparent"
                  )}
                >
                  <div className="flex items-center gap-1.5">
                    {statusIcons[tc.status] || statusIcons.Draft}
                    <span className="font-medium text-foreground truncate">{tc.title}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1 text-muted-foreground">
                    <span className={cn("px-1 py-0.5 rounded text-[10px]", statusBg(tc.status))}>
                      {tc.sub_category}
                    </span>
                    <span>{tc.target_framework}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="flex-1 flex flex-col overflow-hidden">
          {selectedTest ? (
            <>
              <div className="px-4 py-2 border-b border-border flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-foreground">{selectedTest.title}</h3>
                  <p className="text-xs text-muted-foreground">
                    {selectedTest.script_path} · {selectedTest.target_framework}
                  </p>
                </div>
                <span
                  className={cn(
                    "px-2 py-0.5 rounded text-xs font-medium",
                    statusBg(selectedTest.status),
                    statusColor(selectedTest.status)
                  )}
                >
                  {selectedTest.status}
                </span>
              </div>
              <div className="flex-1">
                <Editor
                  height="100%"
                  defaultLanguage="python"
                  value={selectedTest.code_body}
                  theme="vs-dark"
                  options={{
                    readOnly: false,
                    minimap: { enabled: false },
                    fontSize: 13,
                    lineNumbers: "on",
                    scrollBeyondLastLine: false,
                    wordWrap: "on",
                    padding: { top: 8 },
                  }}
                />
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-muted-foreground text-sm">
              <div className="text-center">
                <Code2 className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>Select a test case to inspect its code</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
