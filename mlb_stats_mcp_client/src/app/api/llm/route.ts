import { NextRequest, NextResponse } from "next/server";
import OpenAI from "openai";
import Anthropic from "@anthropic-ai/sdk";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

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

interface LLMRequestPayload {
  prompt: string;
  systemPrompt: string;
  availableTools: MCPTool[];
  modelConfig: {
    model: string;
    maxTokens: number;
  };
}

// Initialize clients
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Helper function to determine if model is OpenAI or Anthropic
function getModelProvider(model: string): "openai" | "anthropic" | Error {
  const openaiModels = [
    "gpt-4",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "gpt-4o",
    "gpt-4o-mini",
  ];
  const anthropicModels = [
    "claude-3-opus",
    "claude-3-sonnet",
    "claude-3-haiku",
    "claude-3-5-sonnet",
    "claude-sonnet-4",
  ];

  if (openaiModels.some((m) => model.includes(m))) {
    return "openai";
  }
  if (anthropicModels.some((m) => model.includes(m))) {
    return "anthropic";
  }
  throw Error("Incorrect model");
}

// Convert tools to OpenAI format
function convertToOpenAITools(tools: MCPTool[]) {
  return tools.map((tool) => ({
    type: "function" as const,
    function: {
      name: tool.name,
      description: tool.description || `Execute ${tool.name}`,
      parameters: tool.inputSchema || {},
    },
  }));
}

// Convert tools to Anthropic format
function convertToAnthropicTools(tools: MCPTool[]) {
  return tools.map((tool) => ({
    name: tool.name,
    description: tool.description || `Execute ${tool.name}`,
    input_schema: {
      type: "object" as const,
      properties: tool.inputSchema.properties || {},
      required: tool.inputSchema.required || [],
    },
  }));
}

// Extract HTML from response
function extractHTML(content: string): string {
  // Look for HTML in various formats
  const htmlPatterns = [
    /```html\n([\s\S]*?)\n```/i,
    /```\n(<!DOCTYPE html[\s\S]*?<\/html>)\n```/i,
    /(<html[\s\S]*?<\/html>)/i,
    /(<!DOCTYPE html[\s\S]*?<\/html>)/i,
  ];

  for (const pattern of htmlPatterns) {
    const match = content.match(pattern);
    if (match) {
      return match[1].trim();
    }
  }

  // If no HTML blocks found, check if the entire response is HTML
  if (content.includes("<html") || content.includes("<!DOCTYPE")) {
    return content.trim();
  }

  // Return empty if no HTML found
  return "";
}

// Global MCP client instance for reuse across API calls
let globalMCPClient: Client | null = null;
let clientInitializationPromise: Promise<Client> | null = null;

// Initialize MCP client with connection reuse
async function getMCPClient(): Promise<Client> {
  // If client already exists and is connected, return it
  if (globalMCPClient) {
    return globalMCPClient;
  }

  // If initialization is already in progress, wait for it
  if (clientInitializationPromise) {
    return clientInitializationPromise;
  }

  // Start new initialization
  clientInitializationPromise = (async () => {
    const url = process.env.NEXT_PUBLIC_MLB_STATS_MCP_URL;
    if (!url) {
      throw new Error(
        "NEXT_PUBLIC_MLB_STATS_MCP_URL environment variable is not set"
      );
    }

    const client = new Client({
      name: "ai-baseball-analyst-backend",
      version: "1.0.0",
    });

    const transport = new StreamableHTTPClientTransport(new URL(url));
    await client.connect(transport);

    globalMCPClient = client;
    return client;
  })();

  try {
    return await clientInitializationPromise;
  } catch (error) {
    // Reset on error so we can retry
    clientInitializationPromise = null;
    globalMCPClient = null;
    throw error;
  }
}

// Enhanced executeToolCall function with better error handling
async function executeToolCall(
  toolName: string,
  parameters: Record<string, unknown>,
  mcpClient: Client
): Promise<string> {
  try {
    console.log(`Executing tool: ${toolName} with parameters:`, parameters);

    const result = await mcpClient.callTool({
      name: toolName,
      arguments: parameters,
    });

    const resultString = JSON.stringify(result.content, null, 2);
    console.log(`Tool ${toolName} executed successfully`);
    return resultString;
  } catch (error) {
    console.error(`Error executing tool ${toolName}:`, error);

    // Create a more informative error message but don't lose the original error
    const errorMessage = `Tool execution failed for ${toolName}: ${
      error instanceof Error ? error.message : "Unknown error"
    }`;

    // Re-throw to be handled by the calling function
    throw new Error(errorMessage);
  }
}

async function callOpenAI(payload: LLMRequestPayload): Promise<string> {
  let mcpClient: Client | null = null;

  try {
    const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
      { role: "system", content: payload.systemPrompt },
      { role: "user", content: payload.prompt },
    ];

    const requestOptions: OpenAI.Chat.Completions.ChatCompletionCreateParams = {
      model: payload.modelConfig.model,
      messages,
      max_tokens: payload.modelConfig.maxTokens,
    };

    if (payload.availableTools.length > 0) {
      requestOptions.tools = convertToOpenAITools(payload.availableTools);
      requestOptions.tool_choice = "auto";
    }

    // Initialize MCP client for tool execution
    if (payload.availableTools.length > 0) {
      try {
        mcpClient = await getMCPClient();
      } catch (mcpError) {
        console.error("Failed to get MCP client:", mcpError);
        throw new Error(
          `MCP client error: ${
            mcpError instanceof Error ? mcpError.message : "Unknown error"
          }`
        );
      }
    }

    // Initial API call
    console.log("Making initial OpenAI API call...");
    const response = await openai.chat.completions.create({
      ...requestOptions,
      messages,
    });

    const message = response.choices[0]?.message;
    if (!message) {
      throw new Error("No response from OpenAI API");
    }

    // Add assistant message to conversation
    messages.push(message);

    let finalContent = message.content || "";

    // If there are tool calls, execute them and get final response
    if (message.tool_calls && message.tool_calls.length > 0 && mcpClient) {
      console.log(`Processing ${message.tool_calls.length} tool calls...`);

      for (const toolCall of message.tool_calls) {
        try {
          const result = await executeToolCall(
            toolCall.function.name,
            JSON.parse(toolCall.function.arguments),
            mcpClient
          );

          // Add tool result to conversation
          messages.push({
            role: "tool",
            content: result,
            tool_call_id: toolCall.id,
          });
        } catch (toolError) {
          console.error(
            `Tool execution failed for ${toolCall.function.name}:`,
            toolError
          );
          // Add error result to conversation so the LLM can handle it
          messages.push({
            role: "tool",
            content: `Error executing ${toolCall.function.name}: ${
              toolError instanceof Error ? toolError.message : "Unknown error"
            }`,
            tool_call_id: toolCall.id,
          });
        }
      }

      // Get final response after tool execution
      console.log("Getting final OpenAI response after tool execution...");
      const finalResponse = await openai.chat.completions.create({
        ...requestOptions,
        messages,
      });

      finalContent = finalResponse.choices[0]?.message.content || "";
    }

    console.log("OpenAI call completed successfully");
    return finalContent;
  } catch (error) {
    console.error("Error in callOpenAI:", error);

    // Re-throw the error to be handled by the main error handler
    // Don't wrap it in a new Error - preserve the original error structure
    throw error;
  } finally {
    // Note: We intentionally don't disconnect the MCP client here
    // to allow reuse across multiple API calls
  }
}

async function callAnthropic(payload: LLMRequestPayload): Promise<string> {
  let mcpClient: Client | null = null;

  try {
    const messages: Anthropic.Messages.MessageParam[] = [
      { role: "user", content: payload.prompt },
    ];

    const requestOptions: Anthropic.Messages.MessageCreateParams = {
      model: payload.modelConfig.model,
      max_tokens: payload.modelConfig.maxTokens,
      system: payload.systemPrompt,
      messages,
    };

    if (payload.availableTools.length > 0) {
      requestOptions.tools = convertToAnthropicTools(payload.availableTools);
    }

    // Get MCP client for tool execution
    if (payload.availableTools.length > 0) {
      try {
        mcpClient = await getMCPClient();
      } catch (mcpError) {
        console.error("Failed to get MCP client:", mcpError);
        throw new Error(
          `MCP client error: ${
            mcpError instanceof Error ? mcpError.message : "Unknown error"
          }`
        );
      }
    }

    // Initial API call
    console.log("Making initial Anthropic API call...");
    const response = await anthropic.messages.create({
      ...requestOptions,
      messages,
    });

    // Add assistant message to conversation
    const assistantMessageContent: Anthropic.Messages.ContentBlock[] = [];
    let textContent = "";
    let hasToolCalls = false;

    // Process response content
    for (const block of response.content) {
      assistantMessageContent.push(block);
      if (block.type === "text") {
        textContent += block.text;
      } else if (block.type === "tool_use") {
        hasToolCalls = true;
      }
    }

    messages.push({
      role: "assistant",
      content: assistantMessageContent,
    });

    // If there are tool calls, execute them and get final response
    if (hasToolCalls && mcpClient) {
      console.log("Processing Anthropic tool calls...");

      const toolResults: Anthropic.Messages.ToolResultBlockParam[] = [];

      for (const block of response.content) {
        if (block.type === "tool_use") {
          try {
            const result = await executeToolCall(
              block.name,
              block.input as Record<string, unknown>,
              mcpClient
            );

            console.log(`Tool [${block.name}] result: ${result}`);

            // Add tool result to conversation
            toolResults.push({
              type: "tool_result",
              tool_use_id: block.id,
              content: result,
            });
          } catch (toolError) {
            console.error(
              `Tool execution failed for ${block.name}:`,
              toolError
            );
            // Add error result to conversation so the LLM can handle it
            toolResults.push({
              type: "tool_result",
              tool_use_id: block.id,
              content: `Error executing ${block.name}: ${
                toolError instanceof Error ? toolError.message : "Unknown error"
              }`,
            });
          }
        }
      }

      if (toolResults.length > 0) {
        messages.push({
          role: "user",
          content: toolResults,
        });
      }

      // Get final response after tool execution
      console.log("Getting final Anthropic response after tool execution...");
      const finalResponse = await anthropic.messages.create({
        ...requestOptions,
        messages,
      });

      console.log(`Final Anthropic response received`);

      const finalText =
        finalResponse.content[0].type === "text"
          ? finalResponse.content[0].text
          : "";

      return finalText;
    }

    console.log("Anthropic call completed successfully");
    return textContent;
  } catch (error) {
    console.error("Error in callAnthropic:", error);

    // Re-throw the error to be handled by the main error handler
    // Don't wrap it in a new Error - preserve the original error structure
    throw error;
  } finally {
    // Clean up MCP client if needed
    if (mcpClient) {
      try {
        // Add any cleanup logic here if the MCP client has a disconnect method
      } catch (cleanupError) {
        console.warn("MCP client cleanup failed:", cleanupError);
      }
    }
  }
}

export async function POST(request: NextRequest) {
  try {
    const payload: LLMRequestPayload = await request.json();

    // Validate required fields
    if (!payload.prompt || !payload.modelConfig?.model) {
      return NextResponse.json(
        { error: "Missing required fields: prompt and modelConfig.model" },
        { status: 400 }
      );
    }

    const provider = getModelProvider(payload.modelConfig.model);

    let llmResponse: string;

    if (provider === "openai") {
      if (!process.env.OPENAI_API_KEY) {
        return NextResponse.json(
          { error: "OpenAI API key not configured" },
          { status: 500 }
        );
      }
      llmResponse = await callOpenAI(payload);
    } else {
      if (!process.env.ANTHROPIC_API_KEY) {
        return NextResponse.json(
          { error: "Anthropic API key not configured" },
          { status: 500 }
        );
      }
      llmResponse = await callAnthropic(payload);
    }

    console.log(llmResponse);

    // Extract HTML from the response
    const htmlResponse = extractHTML(llmResponse);

    if (!htmlResponse) {
      return NextResponse.json(
        {
          error: "No HTML content found in LLM response",
          fullResponse: llmResponse,
        },
        { status: 422 }
      );
    }

    // Return only the HTML content
    return new NextResponse(htmlResponse, {
      headers: {
        "Content-Type": "text/html",
      },
    });
  } catch (error) {
    console.error("LLM API Error:", error);

    // Handle rate limit errors and other API-specific errors
    if (error instanceof Error) {
      if (error.message.includes("429")) {
        return NextResponse.json(
          { error: `Rate limit: ${error.message}`, type: "rate_limit" },
          { status: 429 }
        );
      }
      if (error.message.includes("401")) {
        return NextResponse.json(
          { error: "Invalid API key", type: "auth_error" },
          { status: 401 }
        );
      }
    }

    return NextResponse.json(
      {
        error: "Internal server error",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
