// mcp-ts/src/bridge.ts
import { createConnection, Socket } from "node:net";
import { homedir } from "node:os";
import { join } from "node:path";

const SOCKET_PATH = join(homedir(), ".paperchase", "mcp-bridge.sock");

export async function callPython(method: string, params: Record<string, unknown>): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const sock: Socket = createConnection(SOCKET_PATH);
    const req = JSON.stringify({ jsonrpc: "2.0", id: Date.now(), method, params });
    sock.write(req + "\n");
    let buf = "";
    sock.on("data", (chunk) => {
      buf += chunk.toString();
      const nl = buf.indexOf("\n");
      if (nl >= 0) {
        const line = buf.slice(0, nl);
        sock.end();
        try {
          const resp = JSON.parse(line);
          if (resp.error) reject(new Error(resp.error.message));
          else resolve(resp.result);
        } catch (e) {
          reject(e);
        }
      }
    });
    sock.on("error", reject);
  });
}
