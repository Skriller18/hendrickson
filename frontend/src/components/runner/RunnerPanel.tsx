"use client";

import { useState, useEffect, useRef } from "react";
import { Play, Square, Terminal, Loader2, CheckCircle2, XCircle } from "lucide-react";
import { useStore } from "@/stores";
import { api } from "@/lib/api";
import { connectRunLogs } from "@/lib/ws";
import { cn, formatDuration } from "@/lib/utils";

export function RunnerPanel() {
  const {
    activeContextId,
    testCases,
    isRunning,
    setIsRunning,
    runLogs,
    addRunLog,
    clearRunLogs,
    setActiveRunId,
    setTestRuns,
  } = useStore();
  const [environment, setEnvironment] = useState("sandbox");
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [runLogs]);

  async function handleRun() {
    if (!activeContextId || isRunning) return;

    setIsRunning(true);
    clearRunLogs();
    addRunLog("Starting test execution...\n");

    try {
      const result = await api.runs.execute({
        context_id: activeContextId,
        environment,
      });

      setActiveRunId(result.run_id);
      addRunLog(`Run ID: ${result.run_id}\n`);
      addRunLog(`Total: ${result.total_tests} | Passed: ${result.passed} | Failed: ${result.failed} | Errors: ${result.errors}\n`);
      addRunLog(`Duration: ${formatDuration(result.duration_ms)}\n`);
      addRunLog("\nExecution complete.\n");

      const runs = await api.runs.list(activeContextId);
      setTestRuns(runs as unknown as Parameters<typeof setTestRuns>[0]);
    } catch (err) {
      addRunLog(`\nError: ${err instanceof Error ? err.message : "Execution failed"}\n`);
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
          <Terminal className="w-4 h-4" /> Execution Runner
        </h2>
        <div className="flex items-center gap-2">
          <select
            value={environment}
            onChange={(e) => setEnvironment(e.target.value)}
            className="bg-secondary border border-border rounded px-2 py-1 text-xs text-foreground"
          >
            <option value="sandbox">Sandbox</option>
            <option value="staging">Staging</option>
            <option value="docker">Docker</option>
          </select>
          <button
            onClick={handleRun}
            disabled={isRunning || !activeContextId || testCases.length === 0}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-green-600 text-white text-xs hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRunning ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Play className="w-3.5 h-3.5" />
            )}
            {isRunning ? "Running..." : "Run Test Suite"}
          </button>
        </div>
      </div>

      <div
        ref={logRef}
        className="flex-1 overflow-y-auto p-4 font-mono text-xs bg-black/30"
      >
        {runLogs.length === 0 ? (
          <div className="text-muted-foreground text-center py-8">
            <Terminal className="w-6 h-6 mx-auto mb-2 opacity-30" />
            <p>Click &quot;Run Test Suite&quot; to execute tests</p>
            <p className="mt-1 opacity-50">Live logs will appear here</p>
          </div>
        ) : (
          runLogs.map((log, i) => (
            <div
              key={i}
              className={cn(
                "whitespace-pre-wrap",
                log.includes("PASSED") || log.includes("Passed")
                  ? "text-green-400"
                  : log.includes("FAILED") || log.includes("Failed") || log.includes("Error")
                  ? "text-red-400"
                  : "text-foreground/80"
              )}
            >
              {log}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
