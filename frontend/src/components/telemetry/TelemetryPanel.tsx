"use client";

import { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from "recharts";
import { Activity, Shield, Target, Zap } from "lucide-react";
import { useStore } from "@/stores";
import { cn } from "@/lib/utils";

const COLORS = ["#22c55e", "#ef4444", "#f59e0b", "#3b82f6"];

export function TelemetryPanel() {
  const { testCases, testRuns } = useStore();

  const metrics = useMemo(() => {
    const total = testCases.length;
    const passed = testCases.filter((t) => t.status === "Passed").length;
    const failed = testCases.filter((t) => t.status === "Failed").length;
    const ready = testCases.filter((t) => t.status === "Ready").length;
    const draft = testCases.filter((t) => t.status === "Draft").length;

    const lastRun = testRuns[0];
    const runHistory = testRuns.slice(0, 10).reverse().map((r) => ({
      name: r.run_id?.slice(-6) || "N/A",
      passed: r.passed,
      failed: r.failed,
    }));

    return { total, passed, failed, ready, draft, lastRun, runHistory };
  }, [testCases, testRuns]);

  const pieData = [
    { name: "Passed", value: metrics.passed },
    { name: "Failed", value: metrics.failed },
    { name: "Ready", value: metrics.ready },
    { name: "Draft", value: metrics.draft },
  ].filter((d) => d.value > 0);

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      <div className="px-4 py-3 border-b border-border">
        <h2 className="text-sm font-semibold text-foreground">Telemetry & Metrics</h2>
      </div>

      <div className="p-4 space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <MetricCard
            icon={<Target className="w-4 h-4" />}
            label="Total Tests"
            value={metrics.total}
            color="text-blue-400"
          />
          <MetricCard
            icon={<Activity className="w-4 h-4" />}
            label="Pass Rate"
            value={metrics.total > 0 ? `${Math.round((metrics.passed / metrics.total) * 100)}%` : "N/A"}
            color="text-green-400"
          />
          <MetricCard
            icon={<Zap className="w-4 h-4" />}
            label="Last Run"
            value={metrics.lastRun ? `${metrics.lastRun.duration_ms}ms` : "N/A"}
            color="text-yellow-400"
          />
          <MetricCard
            icon={<Shield className="w-4 h-4" />}
            label="Coverage"
            value="N/A"
            color="text-purple-400"
          />
        </div>

        {pieData.length > 0 && (
          <div className="bg-card rounded-lg border border-border p-3">
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
              Test Status Distribution
            </h3>
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {pieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "6px",
                    fontSize: "12px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-4 mt-1">
              {pieData.map((d, i) => (
                <div key={d.name} className="flex items-center gap-1 text-xs text-muted-foreground">
                  <div
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: COLORS[i % COLORS.length] }}
                  />
                  {d.name} ({d.value})
                </div>
              ))}
            </div>
          </div>
        )}

        {metrics.runHistory.length > 0 && (
          <div className="bg-card rounded-lg border border-border p-3">
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
              Run History
            </h3>
            <ResponsiveContainer width="100%" height={140}>
              <BarChart data={metrics.runHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} />
                <YAxis tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} />
                <Tooltip
                  contentStyle={{
                    background: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "6px",
                    fontSize: "12px",
                  }}
                />
                <Bar dataKey="passed" fill="#22c55e" radius={[2, 2, 0, 0]} />
                <Bar dataKey="failed" fill="#ef4444" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {testCases.length === 0 && (
          <div className="text-center text-muted-foreground text-sm py-8">
            <Activity className="w-6 h-6 mx-auto mb-2 opacity-30" />
            <p>No metrics available yet.</p>
            <p className="text-xs mt-1">Generate and run tests to see telemetry.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color: string;
}) {
  return (
    <div className="bg-card rounded-lg border border-border p-3">
      <div className={cn("flex items-center gap-1.5 mb-1", color)}>
        {icon}
        <span className="text-xs text-muted-foreground">{label}</span>
      </div>
      <p className="text-lg font-semibold text-foreground">{value}</p>
    </div>
  );
}
