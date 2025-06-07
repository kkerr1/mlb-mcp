"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

export interface Prompt {
  name: string;
  description?: string;
  arguments?: Array<{
    name: string;
    description?: string;
    required?: boolean;
  }>;
}

interface MCPTool {
  name: string;
  description?: string;
  inputSchema: {
    type: "object";
    properties?: Record<string, unknown>;
    required?: string[];
  };
  outputSchema?: Record<string, unknown>;
  annotations?: Record<string, unknown>;
}

interface MCPContextType {
  client: Client | null;
  prompts: Prompt[];
  tools: MCPTool[];
  loading: boolean;
  error: string | null;
  reconnect: () => Promise<void>;
}

const MCPContext = createContext<MCPContextType | undefined>(undefined);

export function useMCP() {
  const context = useContext(MCPContext);
  if (context === undefined) {
    throw new Error("useMCP must be used within a MCPProvider");
  }
  return context;
}

interface MCPProviderProps {
  children: ReactNode;
}

export function MCPProvider({ children }: MCPProviderProps) {
  const [client, setClient] = useState<Client | null>(null);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [tools, setTools] = useState<MCPTool[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const initializeClient = async () => {
    try {
      setLoading(true);
      setError(null);

      const url = process.env.NEXT_PUBLIC_MLB_STATS_MCP_URL;
      if (!url) {
        throw new Error("NEXT_PUBLIC_MLB_STATS_MCP_URL environment variable is not set");
      }

      const newClient = new Client({
        name: "ai-baseball-analyst",
        version: "1.0.0",
      });

      const transport = new StreamableHTTPClientTransport(new URL(url));
      await newClient.connect(transport);

      console.log("MCP client connected successfully");
      setClient(newClient);

      // List all available prompts and tools
      const [promptList, toolsList] = await Promise.all([
        newClient.listPrompts(),
        newClient.listTools(),
      ]);

      setPrompts(promptList.prompts || []);
      setTools((toolsList.tools || []) as MCPTool[]);
    } catch (err) {
      console.error("Failed to initialize MCP client:", err);
      setError(
        `Failed to connect to MCP server: ${
          err instanceof Error ? err.message : "Unknown error"
        }`
      );
      setClient(null);
      setPrompts([]);
      setTools([]);
    } finally {
      setLoading(false);
    }
  };

  const reconnect = async () => {
    await initializeClient();
  };

  useEffect(() => {
    initializeClient();
  }, []);

  const value: MCPContextType = {
    client,
    prompts,
    tools,
    loading,
    error,
    reconnect,
  };

  return <MCPContext.Provider value={value}>{children}</MCPContext.Provider>;
}
