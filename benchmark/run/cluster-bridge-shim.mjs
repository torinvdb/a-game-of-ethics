#!/usr/bin/env node
// Decision bridge used by cluster-agent.mjs in place of `python3 -m ethicslab.cluster_agent`.
// tools/replay-cluster.mjs runs it once per decision with the observation on stdin. It forwards
// the observation to the driver's loopback server (AGOE_BRIDGE_URL) and prints the driver's reply:
// {"action","reason"} with exit 0, or {"error": KIND} with exit 2, the same contract as
// ethicslab/cluster_agent.py. Command-line arguments from the replay runner are ignored.

const url = process.env.AGOE_BRIDGE_URL;
const token = process.env.AGOE_BRIDGE_TOKEN;
const fail = (kind) => { process.stdout.write(JSON.stringify({ error: kind }) + '\n'); process.exit(2); };
if (!url || !token || !/^http:\/\/127\.0\.0\.1:\d+\//.test(url)) fail('bridge_config');

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (d) => { input += d; });
process.stdin.on('end', async () => {
  let res;
  try {
    res = await fetch(url, { method: 'POST', headers: { 'content-type': 'application/json', 'x-agoe-bridge-token': token },
      body: input.split('\n')[0], signal: AbortSignal.timeout(88000) });
  } catch (e) {
    return fail(e.name === 'TimeoutError' ? 'timeout' : 'bridge_unreachable');
  }
  if (res.status !== 200) return fail('bridge_rejected');
  let reply;
  try { reply = JSON.parse(await res.text()); } catch { return fail('bridge_unparseable'); }
  process.stdout.write(JSON.stringify(reply) + '\n');
  process.exit(reply.error ? 2 : 0);
});
