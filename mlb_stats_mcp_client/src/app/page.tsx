"use client";

import { useState, useEffect } from "react";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

interface Prompt {
  name: string;
  description?: string;
  arguments?: Array<{
    name: string;
    description?: string;
    required?: boolean;
  }>;
}

export default function Home() {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPrompt, setSelectedPrompt] = useState<string>("");

  useEffect(() => {
    const initializeMCPClient = async () => {
      try {
        // Get the MCP server URL from environment variable
        const url = process.env.NEXT_PUBLIC_MLB_STATS_MCP_URL;

        if (!url) {
          throw new Error(
            "NEXT_PUBLIC_MLB_STATS_MCP_URL environment variable is not set"
          );
        }

        const client = new Client({
          name: "ai-baseball-scout",
          version: "1.0.0",
        });

        const transport = new StreamableHTTPClientTransport(new URL(url));

        await client.connect(transport);
        console.log("Connected using Streamable HTTP transport");

        // List all available prompts
        const promptList = await client.listPrompts();
        console.log(promptList);
        setPrompts(promptList.prompts || []);
      } catch (err) {
        console.error("Failed to initialize MCP client:", err);
        setError(
          `Failed to connect to MCP server: ${
            err instanceof Error ? err.message : "Unknown error"
          }`
        );
      } finally {
        setLoading(false);
      }
    };

    initializeMCPClient();
  }, []);

  const handlePromptChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedPrompt(event.target.value);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AI Baseball Scout ⚾️
          </h1>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-md p-6">
          {loading ? (
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">Connecting to MCP server...</p>
            </div>
          ) : error ? (
            <div className="text-center text-red-600">
              <p className="text-lg font-semibold">Connection Error</p>
              <p className="mt-2 text-sm">{error}</p>
            </div>
          ) : (
            <div className="max-w-md mx-auto">
              <label
                htmlFor="prompt-select"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Select a Prompt:
              </label>
              <select
                id="prompt-select"
                value={selectedPrompt}
                onChange={handlePromptChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Choose a prompt...</option>
                {prompts.map((prompt, index) => (
                  <option key={index} value={prompt.name}>
                    {prompt.name}
                    {prompt.description ? ` - ${prompt.description}` : ""}
                  </option>
                ))}
              </select>

              {prompts.length === 0 && !loading && !error && (
                <p className="mt-2 text-sm text-gray-500">
                  No prompts available from the MCP server.
                </p>
              )}

              {selectedPrompt && (
                <div className="mt-4 p-3 bg-blue-50 rounded-md">
                  <p className="text-sm text-blue-800">
                    Selected: <strong>{selectedPrompt}</strong>
                  </p>
                  {prompts.find((p) => p.name === selectedPrompt)
                    ?.description && (
                    <p className="text-xs text-blue-600 mt-1">
                      {
                        prompts.find((p) => p.name === selectedPrompt)
                          ?.description
                      }
                    </p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
