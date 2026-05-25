# @paperchase/mcp

TypeScript MCP companion for [PaperChase](https://paperchaselabs.com).

This package mirrors the Python MCP server, exposing PaperChase tools to JS-native consumers (Cursor, VS Code, Node-based agents) over the Model Context Protocol.

It is a thin wrapper: requests come in over stdio MCP and get forwarded to the Python core via a local Unix socket at `~/.paperchase/mcp-bridge.sock`.

## Install

```bash
npm install -g @paperchase/mcp
```

Then in your MCP client config:

```json
{
  "mcpServers": {
    "paperchase": {
      "command": "paperchase-mcp"
    }
  }
}
```

## Architecture

```
MCP client (Cursor / Claude Desktop / etc.)
        ↓ stdio
@paperchase/mcp  (this package)
        ↓ unix socket  ~/.paperchase/mcp-bridge.sock
paperchase  (Python core)
```

The Python core must be running for tool calls to succeed. Start it with `paperchase start` or via the npx shim.

## Build

```bash
npm install
npm run build
```

## License

MIT
