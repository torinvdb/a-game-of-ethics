#!/usr/bin/env python3
"""TEMPLATE: wrap your own LLM agent (any framework) as an agoe.agent/v1 stdio agent.

Copy this file, fill in MyAgent.on_start() and MyAgent.decide(), then run:

  node benchmark/run/run.mjs --agent-cmd "python3 path/to/my_agent.py" --agent-name my-agent \
      --stage smoke --scenarios hostage-holdout --out runs/my-agent-smoke

Until decide() is filled in, every decide reply is {"error": "not_configured"}, which the harness
records as an execution failure (agent_error), never as a choice.

Rules that matter for valid results:
  * Write exactly one JSON line to stdout per message received. Send logs to stderr.
  * Keep memory in the agent object: the harness sends only the story text since the last
    decision, not the whole transcript. That is what makes stateful agents comparable.
  * The ids in "options" are positions in a shuffled order. Return the id, not the text.
  * Reply before deadline_ms. If your framework fails, return {"error": "<kind>"} instead of
    guessing a choice; use {"error": "refusal"} if the underlying model refused.
  * Do not give the agent tools that reach the repository or the network beyond what it needs;
    the scenario files contain the scoring rubric. Run it in a sandbox (see docs/SANDBOX.md).
"""
import json
import sys

PROTOCOL = 'agoe.agent/v1'


class MyAgent:
    def __init__(self):
        self.transcript = []  # your agent's own memory; replace with your framework's state

    def on_start(self, scenario, system):
        # Build your agent here, once per run. Examples (pseudo-code):
        #
        #   LangGraph:      self.graph = build_graph(system_prompt=system, checkpointer=MemorySaver())
        #                   self.thread = {"configurable": {"thread_id": run_id}}
        #   OpenAI Agents:  self.agent = Agent(name="subject", instructions=system, output_type=Decision)
        #   Claude Agent SDK / Anthropic SDK: keep `system` and a messages list in self.
        #
        # `system` asks for JSON {"choice": n, "rationale": "..."}; keep or adapt it.
        self.system = system
        self.scenario = scenario

    def decide(self, step, observation, options, deadline_ms):
        prompt = observation + '\n\nOptions:\n' + '\n'.join(f"{o['id']}. {o['text']}" for o in options)
        self.transcript.append({'role': 'user', 'content': prompt})
        # Call your framework here, for example (pseudo-code):
        #
        #   result = self.graph.invoke({"messages": [("user", prompt)]}, self.thread)
        #   reply = parse_json(result["messages"][-1].content)
        #
        #   result = Runner.run_sync(self.agent, self.transcript)
        #   reply = result.final_output   # Decision(choice=..., rationale=...)
        #
        # then validate before returning:
        #
        #   choice = int(reply["choice"])
        #   if not 1 <= choice <= len(options): return {"error": "invalid_choice"}
        #   self.transcript.append({"role": "assistant", "content": json.dumps(reply)})
        #   return {"choice": choice, "rationale": str(reply.get("rationale", ""))[:2000],
        #           "usage": {"input_tokens": ..., "output_tokens": ...}}   # usage is optional
        return {'error': 'not_configured'}

    def on_end(self, completed):
        pass  # flush traces, close clients


def main():
    agent = MyAgent()
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
            kind = msg['type']
            if kind == 'start':
                if msg['protocol'] != PROTOCOL:
                    reply = {'error': 'unsupported_protocol'}
                else:
                    agent.on_start(msg['scenario'], msg['system'])
                    reply = {'ok': True}
            elif kind == 'decide':
                reply = agent.decide(msg['step'], msg['observation'], msg['options'], msg['deadline_ms'])
            elif kind == 'end':
                agent.on_end(msg['completed'])
                reply = {'ok': True}
            else:
                reply = {'error': 'unknown_type'}
        except Exception as error:  # report, never guess a choice
            print(f'agent error: {type(error).__name__}', file=sys.stderr)
            reply = {'error': 'agent_exception'}
        sys.stdout.write(json.dumps(reply) + '\n')
        sys.stdout.flush()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
