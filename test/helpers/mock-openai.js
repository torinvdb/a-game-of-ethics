// Minimal OpenAI/OpenRouter-compatible chat-completions server for tests and demos.
// Never talks to a real provider. `respond(body, n)` returns { status, json|text, headers }.

import http from 'node:http';

export async function startMockServer(respond) {
  const requests = [];
  const server = http.createServer((req, res) => {
    let raw = '';
    req.on('data', (d) => (raw += d));
    req.on('end', async () => {
      let body = null;
      try {
        body = JSON.parse(raw);
      } catch {
        /* keep null */
      }
      requests.push({ method: req.method, url: req.url, headers: req.headers, body });
      const out = await respond(body, requests.length, req);
      if (out?.hang) return; // never answer (timeout tests)
      res.writeHead(out.status ?? 200, { 'content-type': 'application/json', ...(out.headers || {}) });
      res.end(out.text ?? JSON.stringify(out.json));
    });
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const { port } = server.address();
  return {
    url: `http://127.0.0.1:${port}/v1`,
    requests,
    close: () => new Promise((resolve) => { server.closeAllConnections?.(); server.close(resolve); })
  };
}

export const completion = (content, finishReason = 'stop') => ({
  json: { id: 'mock', model: 'mock/model', choices: [{ index: 0, finish_reason: finishReason, message: { role: 'assistant', content } }] }
});

/** Always pick option 1 with a well-formed reply. */
export const alwaysFirst = () => completion('CHOICE: 1\nI pick the first option because it minimises harm.');
