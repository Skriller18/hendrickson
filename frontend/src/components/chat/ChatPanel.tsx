"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Cpu } from "lucide-react";
import { useStore } from "@/stores";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

export function ChatPanel() {
  const { chatMessages, addChatMessage, activeContextId, selectedModel, setSelectedModel, availableModels, setAvailableModels, modelProviders, setModelProviders } = useStore();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showModelPicker, setShowModelPicker] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const pickerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatMessages]);

  useEffect(() => {
    if (availableModels.length === 0) {
      api.models.list().then((data) => {
        setAvailableModels(data.all as any);
        setModelProviders(data.providers as any);
      }).catch(() => {});
    }
  }, []);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (pickerRef.current && !pickerRef.current.contains(e.target as Node)) {
        setShowModelPicker(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function handleSend() {
    const message = input.trim();
    if (!message || loading) return;

    setInput("");
    addChatMessage({ role: "user", content: message, timestamp: new Date().toISOString() });
    setLoading(true);

    try {
      const res = await api.chat.send(message, activeContextId ?? undefined, selectedModel);
      addChatMessage({ role: "assistant", content: res.reply, timestamp: new Date().toISOString() });
    } catch (err) {
      addChatMessage({
        role: "assistant",
        content: `Error: ${err instanceof Error ? err.message : "Failed to get response"}`,
        timestamp: new Date().toISOString(),
      });
    } finally {
      setLoading(false);
    }
  }

  const currentModel = availableModels.find((m) => m.id === selectedModel);
  const providerNames: Record<string, string> = {
    openai: "OpenAI",
    anthropic: "Anthropic",
    deepseek: "DeepSeek",
    openrouter: "OpenRouter",
    ollama: "Ollama",
  };

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-3 border-b border-border">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-foreground">AI QA Assistant</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Ask me to generate tests, run suites, or analyze results
            </p>
          </div>
          <div className="relative" ref={pickerRef}>
            <button
              onClick={() => setShowModelPicker(!showModelPicker)}
              className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-secondary border border-border text-xs text-foreground hover:bg-secondary/80"
            >
              <Cpu className="w-3 h-3" />
              {currentModel?.name || selectedModel}
            </button>
            {showModelPicker && (
              <div className="absolute right-0 top-full mt-1 w-72 max-h-80 overflow-y-auto rounded-md border border-border bg-card shadow-lg z-50">
                {Object.entries(modelProviders).map(([key, provider]) => (
                  <div key={key}>
                    <div className="px-3 py-1.5 text-[10px] font-semibold text-muted-foreground uppercase bg-secondary/50 sticky top-0">
                      {provider.name}
                    </div>
                    {provider.models.map((model: any) => (
                      <button
                        key={model.id}
                        onClick={() => {
                          setSelectedModel(model.id);
                          setShowModelPicker(false);
                        }}
                        className={cn(
                          "w-full text-left px-3 py-2 text-xs hover:bg-secondary transition-colors",
                          selectedModel === model.id && "bg-primary/10 border-l-2 border-primary"
                        )}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-foreground">{model.name}</span>
                          <span className={cn(
                            "text-[10px] px-1 py-0.5 rounded",
                            model.cost_level === "free" ? "bg-green-400/10 text-green-400" :
                            model.cost_level === "low" ? "bg-blue-400/10 text-blue-400" :
                            model.cost_level === "medium" ? "bg-yellow-400/10 text-yellow-400" :
                            "bg-red-400/10 text-red-400"
                          )}>
                            {model.cost_level}
                          </span>
                        </div>
                        <p className="text-muted-foreground mt-0.5 line-clamp-1">{model.description}</p>
                      </button>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3">
        {chatMessages.length === 0 && (
          <div className="text-center text-muted-foreground text-sm py-8">
            <p>No messages yet. Try:</p>
            <p className="mt-2 text-xs">
              &quot;Generate a full test suite for my PRD&quot;
            </p>
            <p className="text-xs">&quot;Run sanity check on JIRA-402&quot;</p>
            <p className="text-xs">&quot;Show me test coverage metrics&quot;</p>
          </div>
        )}

        {chatMessages.map((msg, i) => (
          <div
            key={i}
            className={cn(
              "flex gap-2 text-sm",
              msg.role === "user" ? "justify-end" : "justify-start"
            )}
          >
            <div
              className={cn(
                "max-w-[85%] rounded-lg px-3 py-2",
                msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-secondary-foreground"
              )}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-secondary rounded-lg px-3 py-2">
              <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
            </div>
          </div>
        )}
      </div>

      <div className="p-3 border-t border-border">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask Hendrickson..."
            className="flex-1 bg-secondary border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="p-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
