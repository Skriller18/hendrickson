import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function statusColor(status: string): string {
  switch (status?.toLowerCase()) {
    case "passed":
      return "text-green-400";
    case "failed":
      return "text-red-400";
    case "running":
      return "text-blue-400";
    case "error":
      return "text-orange-400";
    case "ready":
      return "text-yellow-400";
    case "draft":
      return "text-muted-foreground";
    default:
      return "text-muted-foreground";
  }
}

export function statusBg(status: string): string {
  switch (status?.toLowerCase()) {
    case "passed":
      return "bg-green-400/10";
    case "failed":
      return "bg-red-400/10";
    case "running":
      return "bg-blue-400/10";
    case "error":
      return "bg-orange-400/10";
    case "ready":
      return "bg-yellow-400/10";
    default:
      return "bg-muted";
  }
}
