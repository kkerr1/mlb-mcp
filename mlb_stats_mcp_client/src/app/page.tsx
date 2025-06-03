"use client";

import { useState, useEffect } from "react";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

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
  const [argumentValues, setArgumentValues] = useState<Record<string, string>>(
    {}
  );
  const [completePromptText, setCompletePromptText] = useState<string>("");
  const [mcpClient, setMcpClient] = useState<Client | null>(null);

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
        setMcpClient(client);

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

  const handlePromptChange = (value: string) => {
    setSelectedPrompt(value);
    setArgumentValues({});
    setCompletePromptText("");
  };

  const handleArgumentChange = (argName: string, value: string) => {
    const newArgValues = { ...argumentValues, [argName]: value };
    setArgumentValues(newArgValues);

    // Update complete prompt text when arguments change
    if (selectedPromptData && selectedPrompt !== "custom") {
      updateCompletePromptText(selectedPromptData, newArgValues);
    }
  };

  const updateCompletePromptText = async (
    promptData: Prompt,
    argValues: Record<string, string>
  ) => {
    if (!mcpClient) return;

    try {
      // Check if all required arguments are filled
      const allRequiredFilled = (promptData.arguments || []).every(
        (arg) =>
          !arg.required ||
          (argValues[arg.name] && argValues[arg.name].trim() !== "")
      );

      if (!allRequiredFilled) {
        setCompletePromptText("");
        return;
      }

      // Use MCP client to get the completed prompt
      const result = await mcpClient.getPrompt({
        name: promptData.name,
        arguments: argValues,
      });

      console.log("Prompt completion result:", result);

      // Extract the prompt text from the result
      if (result && result.messages && result.messages.length > 0) {
        const promptText = result.messages
          .map((msg) => msg.content?.text || JSON.stringify(msg.content))
          .join("\n");
        setCompletePromptText(promptText);
      } else {
        // Fallback if the response format is different
        setCompletePromptText(JSON.stringify(result, null, 2));
      }
    } catch (error) {
      console.error("Error completing prompt:", error);
      setCompletePromptText(
        `Error completing prompt: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
    }
  };

  const selectedPromptData =
    selectedPrompt === "custom"
      ? null
      : prompts.find((p) => p.name === selectedPrompt);

  // Check if all required arguments are filled
  const allRequiredArgsFilled = selectedPromptData
    ? (selectedPromptData.arguments || []).every(
        (arg) =>
          !arg.required ||
          (argumentValues[arg.name] && argumentValues[arg.name].trim() !== "")
      )
    : false;

  const showPromptTextCard =
    selectedPrompt === "custom" ||
    (selectedPromptData &&
      allRequiredArgsFilled &&
      completePromptText.trim() !== "");

  const handleSubmit = () => {
    console.log("Submitting prompt:", completePromptText);
    // Add your submit logic here
  };

  return (
    <div className="dark min-h-screen bg-background text-foreground py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">
            AI Baseball Scout ⚾️
          </h1>
          <p className="text-muted-foreground">
            Connect to your MCP baseball statistics server
          </p>
        </div>

        {/* Content */}
        <Card>
          <CardHeader>
            <CardTitle>MCP Connection Status</CardTitle>
            <CardDescription>
              {loading
                ? "Establishing connection to MCP server..."
                : error
                ? "Connection failed"
                : `Connected successfully - ${prompts.length} prompts available`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex flex-col items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-primary mb-3" />
                <p className="text-muted-foreground">
                  Connecting to MCP server...
                </p>
              </div>
            ) : error ? (
              <div className="text-center py-8">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-destructive/20 mb-4">
                  <span className="text-destructive text-xl">⚠️</span>
                </div>
                <h3 className="text-lg font-semibold text-destructive mb-2">
                  Connection Error
                </h3>
                <p className="text-sm text-muted-foreground max-w-md mx-auto">
                  {error}
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">
                    Select a Prompt
                  </label>
                  <Select
                    value={selectedPrompt}
                    onValueChange={handlePromptChange}
                  >
                    <SelectTrigger className="h-auto min-h-10 py-3">
                      <SelectValue placeholder="Choose a prompt..." />
                    </SelectTrigger>
                    <SelectContent className="max-h-80">
                      <SelectItem value="custom">
                        <div className="flex flex-col items-start py-1">
                          <span className="font-medium">Custom Prompt</span>
                          <span className="text-xs text-muted-foreground mt-1">
                            Create your own custom prompt
                          </span>
                        </div>
                      </SelectItem>
                      {prompts.map((prompt, index) => (
                        <SelectItem key={index} value={prompt.name}>
                          <div className="flex flex-col items-start py-1">
                            <span className="font-medium">{prompt.name}</span>
                            {prompt.description && (
                              <span className="text-xs text-muted-foreground mt-1 max-w-xs truncate">
                                {prompt.description}
                              </span>
                            )}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {prompts.length === 0 && (
                  <div className="text-center py-4">
                    <p className="text-sm text-muted-foreground">
                      No prompts available from the MCP server.
                    </p>
                  </div>
                )}

                {selectedPromptData && (
                  <Card>
                    <CardHeader className="pb-3">
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-primary text-lg">
                          {selectedPromptData.name}
                        </CardTitle>
                        <Badge variant="secondary">Selected</Badge>
                      </div>
                      {selectedPromptData.description && (
                        <CardDescription>
                          {selectedPromptData.description}
                        </CardDescription>
                      )}
                    </CardHeader>
                    {selectedPromptData.arguments &&
                      selectedPromptData.arguments.length > 0 && (
                        <CardContent className="pt-0">
                          <div className="space-y-4">
                            <h4 className="text-sm font-medium text-foreground">
                              Arguments:
                            </h4>
                            <div className="space-y-4">
                              {selectedPromptData.arguments.map(
                                (arg, index) => (
                                  <div key={index} className="space-y-2">
                                    <div className="flex items-center gap-2">
                                      <Badge
                                        variant={
                                          arg.required
                                            ? "destructive"
                                            : "outline"
                                        }
                                        className="text-xs"
                                      >
                                        {arg.name}
                                      </Badge>
                                      {arg.required && (
                                        <span className="text-xs text-destructive">
                                          required
                                        </span>
                                      )}
                                    </div>
                                    {arg.description && (
                                      <p className="text-xs text-muted-foreground">
                                        {arg.description}
                                      </p>
                                    )}
                                    <Input
                                      placeholder={`Enter ${arg.name}...`}
                                      value={argumentValues[arg.name] || ""}
                                      onChange={(e) =>
                                        handleArgumentChange(
                                          arg.name,
                                          e.target.value
                                        )
                                      }
                                    />
                                  </div>
                                )
                              )}
                            </div>
                          </div>
                        </CardContent>
                      )}
                  </Card>
                )}

                {showPromptTextCard && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-primary">
                        Complete Prompt
                      </CardTitle>
                      <CardDescription>
                        Review and edit your complete prompt before submitting
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <Textarea
                        placeholder="Enter your custom prompt here..."
                        value={completePromptText}
                        onChange={(e) => setCompletePromptText(e.target.value)}
                        className="min-h-32 resize-none"
                      />
                      <Button
                        onClick={handleSubmit}
                        className="w-full bg-destructive hover:bg-destructive/90 text-destructive-foreground"
                        disabled={!completePromptText.trim()}
                      >
                        Submit
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
