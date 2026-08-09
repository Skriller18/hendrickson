import { create } from "zustand";

interface TestCase {
  test_id: string;
  context_id: string;
  title: string;
  category: string;
  sub_category: string;
  target_framework: string;
  script_path: string;
  code_body: string;
  status: string;
  prd_reference?: string;
  jira_reference?: string;
}

interface TestRun {
  run_id: string;
  context_id: string;
  status: string;
  total_tests: number;
  passed: number;
  failed: number;
  errors: number;
  duration_ms: number;
  results?: Array<{
    test_id: string;
    title: string;
    status: string;
    duration_ms: number;
    error_message?: string;
    stdout?: string;
    stderr?: string;
  }>;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  description: string;
  context_window: number;
  max_output_tokens: number;
  supports_vision: boolean;
  supports_tools: boolean;
  cost_level: string;
}

interface AppState {
  activeContextId: string | null;
  setActiveContextId: (id: string | null) => void;

  chatMessages: ChatMessage[];
  addChatMessage: (msg: ChatMessage) => void;
  clearChat: () => void;

  testCases: TestCase[];
  setTestCases: (tests: TestCase[]) => void;
  selectedTestId: string | null;
  setSelectedTestId: (id: string | null) => void;

  testRuns: TestRun[];
  setTestRuns: (runs: TestRun[]) => void;
  activeRunId: string | null;
  setActiveRunId: (id: string | null) => void;

  runLogs: string[];
  addRunLog: (log: string) => void;
  clearRunLogs: () => void;

  isRunning: boolean;
  setIsRunning: (v: boolean) => void;

  prdContent: string | null;
  setPrdContent: (content: string | null) => void;

  requirements: Array<Record<string, unknown>>;
  setRequirements: (reqs: Array<Record<string, unknown>>) => void;

  selectedModel: string;
  setSelectedModel: (model: string) => void;
  availableModels: ModelInfo[];
  setAvailableModels: (models: ModelInfo[]) => void;
  modelProviders: Record<string, { name: string; models: ModelInfo[] }>;
  setModelProviders: (providers: Record<string, { name: string; models: ModelInfo[] }>) => void;
}

export const useStore = create<AppState>((set) => ({
  activeContextId: null,
  setActiveContextId: (id) => set({ activeContextId: id }),

  chatMessages: [],
  addChatMessage: (msg) =>
    set((state) => ({ chatMessages: [...state.chatMessages, msg] })),
  clearChat: () => set({ chatMessages: [] }),

  testCases: [],
  setTestCases: (tests) => set({ testCases: tests }),
  selectedTestId: null,
  setSelectedTestId: (id) => set({ selectedTestId: id }),

  testRuns: [],
  setTestRuns: (runs) => set({ testRuns: runs }),
  activeRunId: null,
  setActiveRunId: (id) => set({ activeRunId: id }),

  runLogs: [],
  addRunLog: (log) =>
    set((state) => ({ runLogs: [...state.runLogs, log] })),
  clearRunLogs: () => set({ runLogs: [] }),

  isRunning: false,
  setIsRunning: (v) => set({ isRunning: v }),

  prdContent: null,
  setPrdContent: (content) => set({ prdContent: content }),

  requirements: [],
  setRequirements: (reqs) => set({ requirements: reqs }),

  selectedModel: "gpt-5.6-terra",
  setSelectedModel: (model) => set({ selectedModel: model }),
  availableModels: [],
  setAvailableModels: (models) => set({ availableModels: models }),
  modelProviders: {},
  setModelProviders: (providers) => set({ modelProviders: providers }),
}));
