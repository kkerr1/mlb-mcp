import { NextRequest, NextResponse } from "next/server";
import OpenAI from "openai";
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

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Model configuration with rate limits (tokens per minute)
const OPENAI_MODELS = {
  "gpt-4.1-mini": 200_000,
  "gpt-4.1-nano": 200_000,
  "gpt-4o-mini": 200_000,
} as const;

type OpenAIModel = keyof typeof OPENAI_MODELS;

// Rate limiting state
interface RateLimitState {
  tokensUsed: number;
  windowStart: number;
  requestCount: number;
}

// In-memory rate limit tracking (in production, use Redis or similar)
const rateLimitState = new Map<OpenAIModel, RateLimitState>();

// Initialize rate limit state for all models
Object.keys(OPENAI_MODELS).forEach((model) => {
  rateLimitState.set(model as OpenAIModel, {
    tokensUsed: 0,
    windowStart: Date.now(),
    requestCount: 0,
  });
});

// Helper function to validate OpenAI model
function validateOpenAIModel(model: string): model is OpenAIModel {
  return model in OPENAI_MODELS;
}

// Estimate token count (rough approximation)
function estimateTokenCount(text: string): number {
  // Rough estimate: 1 token ≈ 4 characters for English text
  return Math.ceil(text.length / 4);
}

// Check and update rate limit
function checkRateLimit(
  model: OpenAIModel,
  estimatedTokens: number
): { allowed: boolean; remaining: number } {
  const state = rateLimitState.get(model)!;
  const now = Date.now();
  const windowDuration = 60 * 1000; // 1 minute
  const maxTokens = OPENAI_MODELS[model];

  // Reset window if it's been more than a minute
  if (now - state.windowStart >= windowDuration) {
    state.tokensUsed = 0;
    state.windowStart = now;
    state.requestCount = 0;
  }

  const wouldExceed = state.tokensUsed + estimatedTokens > maxTokens;
  const remaining = maxTokens - state.tokensUsed;

  if (!wouldExceed) {
    state.tokensUsed += estimatedTokens;
    state.requestCount++;
  }

  return { allowed: !wouldExceed, remaining };
}

// Truncate prompt to fit within rate limits
function truncatePromptForRateLimit(
  prompt: string,
  maxTokens: number
): { prompt: string; truncated: boolean } {
  const estimatedTokens = estimateTokenCount(prompt);

  if (estimatedTokens <= maxTokens) {
    return { prompt, truncated: false };
  }

  // Reserve some tokens for the truncation message
  const reservedTokens = 50;
  const availableTokens = maxTokens - reservedTokens;
  const truncatedLength = Math.floor(availableTokens * 4); // Convert back to characters

  const truncatedPrompt =
    prompt.substring(0, truncatedLength) +
    "\n\n[PROMPT TRUNCATED DUE TO RATE LIMITS - This is your final prompt, please provide your best response based on the available information.]";

  return { prompt: truncatedPrompt, truncated: true };
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

// MCP client instance
let globalMCPClient: Client | null = null;
let clientInitializationPromise: Promise<Client> | null = null;

// Initialize MCP client with connection
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

// Execute an MCP Tool Call
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

    // Validate that we actually got data back
    if (!result || !result.content) {
      console.warn(`Tool ${toolName} returned empty or null result`);
      return JSON.stringify({ error: "Tool returned no data" }, null, 2);
    }

    // Check for successful data retrieval
    const hasValidContent = Array.isArray(result.content)
      ? result.content.length > 0
      : result.content && typeof result.content === 'object';

    if (!hasValidContent) {
      console.warn(`Tool ${toolName} returned empty content array or invalid data structure`);
    }

    // Check for and log image_base64 fields
    const contentStr = JSON.stringify(result.content);
    if (contentStr.includes('image_base64')) {
      console.log(`Tool ${toolName} returned response containing image data`);

      // Count how many images were returned
      const imageMatches = contentStr.match(/"image_base64":/g);
      const imageCount = imageMatches ? imageMatches.length : 0;
      console.log(`Found ${imageCount} image(s) in response from ${toolName}`);

      // Log first 100 chars of each image for verification (without full base64 spam)
      try {
        const parsedContent = Array.isArray(result.content) ? result.content : [result.content];
        parsedContent.forEach((item: any, index: number) => {
          if (item && typeof item === 'object' && item.image_base64) {
            const imagePreview = item.image_base64.substring(0, 100);
            console.log(`Image ${index + 1} base64 preview: ${imagePreview}...`);
          }
        });
      } catch (parseError) {
        console.warn('Could not parse content for image logging:', parseError);
      }
    }

    const resultString = JSON.stringify(result.content, null, 2);
    console.log(`Tool ${toolName} executed successfully with ${hasValidContent ? 'valid' : 'empty'} content`);
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
    // Validate model
    if (!validateOpenAIModel(payload.modelConfig.model)) {
      throw new Error(`Unsupported model: ${payload.modelConfig.model}`);
    }

    const model = payload.modelConfig.model as OpenAIModel;

    // Estimate total token usage for the initial request
    const estimatedTokens = estimateTokenCount(
      payload.systemPrompt + payload.prompt
    );

    // Check rate limit
    const rateLimitCheck = checkRateLimit(model, estimatedTokens);
    let currentPrompt = payload.prompt;
    let isRateLimited = false;

    if (!rateLimitCheck.allowed) {
      console.warn(
        `Rate limit would be exceeded. Remaining tokens: ${rateLimitCheck.remaining}`
      );
      const truncateResult = truncatePromptForRateLimit(
        payload.prompt,
        rateLimitCheck.remaining
      );
      currentPrompt = truncateResult.prompt;
      isRateLimited = truncateResult.truncated;
    }

    const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
      { role: "system", content: payload.systemPrompt },
      { role: "user", content: currentPrompt },
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

    // Conversational loop - continue until no more tool calls
    const maxIterations = 10; // Prevent infinite loops
    let iteration = 0;

    while (iteration < maxIterations) {
      console.log(`Chat iteration: ${iteration}`);
      iteration++;

      // Check if this is the final iteration due to rate limits or max iterations
      const isFinalIteration = isRateLimited || iteration >= maxIterations;

      if (isFinalIteration && messages.length > 2) {
        // Add a final instruction for the last iteration
        messages.push({
          role: "user",
          content:
            "This is the final response due to rate limits or iteration limits. Please provide your best final answer based on all the information gathered so far.",
        });
      }

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

      // Check if there are tool calls to execute (but not on final iteration)
      if (
        message.tool_calls &&
        message.tool_calls.length > 0 &&
        mcpClient &&
        !isFinalIteration
      ) {
        console.log(
          `Processing ${message.tool_calls.length} tool calls in iteration ${iteration}...`
        );

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

        // Continue the loop to get the next response
        continue;
      } else {
        // No tool calls or final iteration, we have the final response
        console.log(
          `OpenAI conversation completed after ${iteration} iterations`
        );
        return message.content || "";
      }
    }

    // If we've hit the max iterations, return the last message content
    console.warn(
      `OpenAI conversation hit max iterations (${maxIterations}). Returning last response.`
    );
    const lastMessage = messages[messages.length - 1];
    if (
      lastMessage &&
      lastMessage.role === "assistant" &&
      "content" in lastMessage
    ) {
      return typeof lastMessage.content === "string" ? lastMessage.content : "";
    }

    throw new Error("Max iterations reached without final response");
  } catch (error) {
    console.error("Error in callOpenAI:", error);
    throw error;
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

    // Validate that it's a supported OpenAI model
    if (!validateOpenAIModel(payload.modelConfig.model)) {
      return NextResponse.json(
        {
          error: `Unsupported model: ${
            payload.modelConfig.model
          }. Supported models: ${Object.keys(OPENAI_MODELS).join(", ")}`,
        },
        { status: 400 }
      );
    }

    if (!process.env.OPENAI_API_KEY) {
      return NextResponse.json(
        { error: "OpenAI API key not configured" },
        { status: 500 }
      );
    }

    const llmResponse = await callOpenAI(payload);

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
