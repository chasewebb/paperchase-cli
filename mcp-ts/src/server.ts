// mcp-ts/src/server.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

import { callPython } from "./bridge.js";

const server = new Server(
  { name: "paperchase-ts", version: "0.1.0" },
  { capabilities: { tools: {} } },
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  const result = (await callPython("tools/list", {})) as { tools: unknown[] };
  return { tools: result.tools };
});

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const result = (await callPython("tools/call", req.params)) as { content: unknown[] };
  return { content: result.content };
});

const transport = new StdioServerTransport();
await server.connect(transport);
