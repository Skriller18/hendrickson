const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

type LogCallback = (log: Record<string, unknown>) => void;

export function connectRunLogs(runId: string, onLog: LogCallback): () => void {
  const ws = new WebSocket(`${WS_URL}/ws/runs/${runId}/logs`);

  ws.onopen = () => {
    console.log(`WebSocket connected for run ${runId}`);
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onLog(data);
    } catch {
      onLog({ raw: event.data });
    }
  };

  ws.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  ws.onclose = () => {
    console.log(`WebSocket disconnected for run ${runId}`);
  };

  return () => {
    ws.close();
  };
}
