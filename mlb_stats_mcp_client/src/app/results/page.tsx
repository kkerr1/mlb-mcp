"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, ArrowLeft, RefreshCw } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

interface LLMRequestPayload {
  prompt: string;
  systemPrompt: string;
  availableTools: any[];
  modelConfig: {
    model: string;
    maxTokens: number;
  };
}

export default function ResultsPage() {
  const router = useRouter();
  const [htmlResult, setHtmlResult] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [requestPayload, setRequestPayload] =
    useState<LLMRequestPayload | null>(null);
  const [mcpClient, setMcpClient] = useState<Client | null>(null);
  const [submissionData, setSubmissionData] = useState<{
    completePromptText: string;
    mcpServerUrl: string;
  } | null>(null);

  useEffect(() => {
    // Get submission data from sessionStorage
    const storedData = sessionStorage.getItem("baseball-submission-data");
    if (!storedData) {
      router.push("/"); // Redirect to home if no data
      return;
    }

    try {
      const data = JSON.parse(storedData);
      setSubmissionData(data);
      initializeMCPAndGenerate(data);
    } catch (error) {
      console.error("Error parsing submission data:", error);
      setError("Invalid submission data");
      setLoading(false);
    }
  }, [router]);

  const initializeMCPAndGenerate = async (data: {
    completePromptText: string;
    mcpServerUrl: string;
  }) => {
    try {
      // Initialize MCP client
      const client = new Client({
        name: "ai-baseball-analyst-results",
        version: "1.0.0",
      });

      const transport = new StreamableHTTPClientTransport(
        new URL(data.mcpServerUrl)
      );
      await client.connect(transport);
      setMcpClient(client);

      // Generate the report
      await generateReport(data.completePromptText, client);
    } catch (error) {
      console.error("Error initializing MCP client:", error);
      setError(
        `Failed to connect to MCP server: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
      setLoading(false);
    }
  };

  const prepareRequestPayload = async (
    prompt: string,
    client: Client
  ): Promise<LLMRequestPayload> => {
    const toolsResponse = await client.listTools();
    const availableTools = toolsResponse.tools || [];

    const formattedTools = availableTools.map((tool) => ({
      name: tool.name,
      description: tool.description || `Execute ${tool.name}`,
      input_schema: tool.inputSchema || {
        type: "object",
        properties: {},
        required: [],
      },
    }));

    const systemPrompt = `You are an expert baseball analyst with access to comprehensive MLB data through specialized tools.

Your task is to execute the provided prompt instructions exactly as specified. The prompt contains detailed steps for:
1. Gathering data using specific MCP tools
2. Creating visualizations
3. Generating a complete HTML report

IMPORTANT INSTRUCTIONS:
- Follow ALL steps in the prompt sequentially
- Use the available tools to gather real data
- Generate a complete, self-contained HTML document as the final output
- Include proper HTML structure with embedded CSS
- Ensure all visualizations are included as base64 images
- The HTML should be ready to display in a browser

Available MCP tools: ${formattedTools.map((t) => t.name).join(", ")}

Execute the prompt instructions and return ONLY the final HTML document.`;

    return {
      prompt,
      systemPrompt,
      availableTools: formattedTools,
      modelConfig: {
        model: "claude-3-5-sonnet-20241022",
        maxTokens: 8000,
      },
    };
  };

  const generateReport = async (prompt: string, client: Client) => {
    try {
      setLoading(true);
      setError(null);

      const payload = await prepareRequestPayload(prompt, client);
      setRequestPayload(payload);

      console.log("Request payload prepared for server-side API:");
      console.log(payload);

      // TODO: Replace this with actual API call to your server-side endpoint
      // const response = await fetch('/api/generate-report', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify(payload)
      // });
      //
      // if (!response.ok) {
      //   throw new Error(`HTTP error! status: ${response.status}`);
      // }
      //
      // const result = await response.json();
      // setHtmlResult(result.html);

      await simulateApiCall(payload);
    } catch (err) {
      console.error("Error generating report:", err);
      setError(
        `Failed to generate report: ${
          err instanceof Error ? err.message : "Unknown error"
        }`
      );
    } finally {
      setLoading(false);
    }
  };

  const simulateApiCall = async (payload: LLMRequestPayload) => {
    console.log("Simulating server-side API call with payload:");
    console.log("Prompt length:", payload.prompt.length);
    console.log(
      "Available tools:",
      payload.availableTools.map((t) => t.name)
    );
    console.log("Model config:", payload.modelConfig);

    await new Promise((resolve) => setTimeout(resolve, 3000));

    const mockHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baseball Analysis Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        .container {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #003366;
        }
        .payload-info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #003366;
            margin-bottom: 30px;
        }
        .tool-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .tool-card {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #2196f3;
        }
        .tool-name {
            font-weight: bold;
            color: #1976d2;
            margin-bottom: 5px;
        }
        .tool-desc {
            font-size: 14px;
            color: #666;
        }
        .navigation {
            background: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            margin-top: 30px;
            border: 1px solid #ffc107;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚾ Baseball Analysis Report</h1>
            <p>Generated using Next.js routing and server-side API preparation</p>
        </div>

        <div class="payload-info">
            <h3>📋 Request Payload Summary</h3>
            <p><strong>Model:</strong> ${payload.modelConfig.model}</p>
            <p><strong>Max Tokens:</strong> ${payload.modelConfig.maxTokens}</p>
            <p><strong>Prompt Length:</strong> ${
              payload.prompt.length
            } characters</p>
            <p><strong>Available Tools:</strong> ${
              payload.availableTools.length
            }</p>
        </div>

        <h3>🔧 Available MCP Tools</h3>
        <div class="tool-list">
            ${payload.availableTools
              .map(
                (tool) => `
                <div class="tool-card">
                    <div class="tool-name">${tool.name}</div>
                    <div class="tool-desc">${tool.description}</div>
                </div>
            `
              )
              .join("")}
        </div>

        <div class="navigation">
            <h3>🚀 Next Steps</h3>
            <ol>
                <li>Create the server-side API endpoint at <code>/app/api/generate-report/route.ts</code></li>
                <li>Integrate with Anthropic Claude API server-side</li>
                <li>Handle MCP tool execution in the API route</li>
                <li>Return the generated HTML from Claude</li>
            </ol>
            <p><strong>This is now using proper Next.js routing with sessionStorage!</strong></p>
        </div>
    </div>
</body>
</html>`;

    setHtmlResult(mockHtml);
  };

  const handleRetry = () => {
    if (submissionData && mcpClient) {
      generateReport(submissionData.completePromptText, mcpClient);
    }
  };

  const handleBackToHome = () => {
    // Clear the submission data and navigate back
    sessionStorage.removeItem("baseball-submission-data");
    router.push("/");
  };

  return (
    <div className="dark min-h-screen bg-background text-foreground py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={handleBackToHome}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Home
            </Button>
            <div>
              <h1 className="text-4xl font-bold text-foreground">
                Custom Report 📊
              </h1>
              <p className="text-muted-foreground">
                AI-generated baseball analysis using MCP tools
              </p>
            </div>
          </div>
          {!loading && !error && htmlResult && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleRetry}
              className="flex items-center gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Regenerate
            </Button>
          )}
        </div>

        {/* Debug Info */}
        {requestPayload && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>🔍 LLM Prompt Info</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <p>
                  <strong>Prompt Length:</strong> {requestPayload.prompt.length}{" "}
                  characters
                </p>
                <p>
                  <strong>Available Tools:</strong>{" "}
                  {requestPayload.availableTools.length}
                </p>
                <p>
                  <strong>Model:</strong> {requestPayload.modelConfig.model}
                </p>
                <details className="mt-4">
                  <summary className="cursor-pointer font-medium">
                    View Full Payload JSON
                  </summary>
                  <pre className="mt-2 p-4 bg-muted rounded-lg overflow-x-auto text-xs">
                    {JSON.stringify(requestPayload, null, 2)}
                  </pre>
                </details>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Content */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Report Results
              {loading && (
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-6">
                <div className="flex flex-col items-center justify-center py-12">
                  <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    Preparing Server Request...
                  </h3>
                  <p className="text-sm text-muted-foreground text-center max-w-md">
                    Connecting to MCP server and formatting data for Claude API
                    call.
                  </p>
                </div>

                <div className="space-y-4">
                  <Skeleton className="h-8 w-3/4" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-5/6" />
                  <div className="grid grid-cols-3 gap-4 mt-6">
                    <Skeleton className="h-24" />
                    <Skeleton className="h-24" />
                    <Skeleton className="h-24" />
                  </div>
                  <Skeleton className="h-48 w-full mt-6" />
                </div>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-destructive/20 mb-4">
                  <span className="text-destructive text-2xl">⚠️</span>
                </div>
                <h3 className="text-lg font-semibold text-destructive mb-2">
                  Report Generation Failed
                </h3>
                <p className="text-sm text-muted-foreground max-w-md mx-auto mb-6">
                  {error}
                </p>
                <div className="flex gap-3 justify-center">
                  <Button variant="outline" onClick={handleBackToHome}>
                    Go Back to Home
                  </Button>
                  <Button onClick={handleRetry}>Try Again</Button>
                </div>
              </div>
            ) : htmlResult ? (
              <div className="space-y-4">
                <div className="border rounded-lg overflow-hidden">
                  <div className="bg-muted px-4 py-2 border-b">
                    <p className="text-sm text-muted-foreground">
                      Generated HTML Report
                    </p>
                  </div>
                  <div className="relative">
                    <iframe
                      srcDoc={htmlResult}
                      className="w-full h-[800px] border-0"
                      title="Generated Baseball Report"
                      sandbox="allow-scripts allow-same-origin"
                    />
                  </div>
                </div>

                <div className="flex justify-between items-center pt-4">
                  <p className="text-sm text-muted-foreground">
                    Mock response generated. Ready for server-side integration!
                  </p>
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={handleBackToHome}>
                      Create New Report
                    </Button>
                    <Button onClick={handleRetry}>Regenerate Report</Button>
                  </div>
                </div>
              </div>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
