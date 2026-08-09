"use client";

import { useState } from "react";
import { MessageSquare, FileText, Code2, Terminal, Activity } from "lucide-react";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { DrawerPanel } from "@/components/drawer/DrawerPanel";
import { CanvasPanel } from "@/components/canvas/CanvasPanel";
import { RunnerPanel } from "@/components/runner/RunnerPanel";
import { TelemetryPanel } from "@/components/telemetry/TelemetryPanel";
import { cn } from "@/lib/utils";

type Tab = "chat" | "canvas" | "runner" | "telemetry";

const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: "chat", label: "AI Assistant", icon: <MessageSquare className="w-4 h-4" /> },
  { id: "canvas", label: "Test Canvas", icon: <Code2 className="w-4 h-4" /> },
  { id: "runner", label: "Runner", icon: <Terminal className="w-4 h-4" /> },
  { id: "telemetry", label: "Telemetry", icon: <Activity className="w-4 h-4" /> },
];

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<Tab>("chat");

  return (
    <div className="h-screen flex flex-col">
      <header className="flex items-center justify-between px-4 py-2 border-b border-border bg-card/50">
        <div className="flex items-center gap-3">
          <h1 className="text-sm font-bold text-foreground tracking-tight">
            HENDRICKSON
          </h1>
          <span className="text-[10px] text-muted-foreground bg-secondary px-1.5 py-0.5 rounded">
            QA HARNESS
          </span>
        </div>

        <nav className="flex items-center gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-colors",
                activeTab === tab.id
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary"
              )}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <DrawerPanel />

        <div className="flex-1 flex flex-col overflow-hidden">
          {activeTab === "chat" && <ChatPanel />}
          {activeTab === "canvas" && <CanvasPanel />}
          {activeTab === "runner" && <RunnerPanel />}
          {activeTab === "telemetry" && <TelemetryPanel />}
        </div>
      </div>
    </div>
  );
}
