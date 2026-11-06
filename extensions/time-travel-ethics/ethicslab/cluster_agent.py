"""Provider-neutral JSON bridge for the Ink replay runner; optional live calls only.

stdout carries either {"action", "reason"} (exit 0) or {"error": KIND} (exit 2).
KIND is a ProviderError kind, "invalid_action" or "bad_observation"; it is an
execution failure class, never a policy outcome. No provider payload is echoed.
"""
import argparse,json,sys
from .__main__ import decide

def main():
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--endpoint');a=p.parse_args()
    try:
        observation=json.loads(sys.stdin.readline())
        if not isinstance(observation,dict) or not isinstance(observation.get('choices'),list):raise KeyError('choices')
    except (ValueError,KeyError):
        print(json.dumps({'error':'bad_observation'}));return 2
    try:
        result=decide('live',observation,a.endpoint,a.model)
    except Exception as error:
        kind=getattr(error,'kind',None) or ('config' if isinstance(error,ValueError) else type(error).__name__)
        print(json.dumps({'error':kind}));return 2
    if result['action'] not in observation['choices']:
        print(json.dumps({'error':'invalid_action'}));return 2
    print(json.dumps(result));return 0
if __name__=='__main__':raise SystemExit(main())
