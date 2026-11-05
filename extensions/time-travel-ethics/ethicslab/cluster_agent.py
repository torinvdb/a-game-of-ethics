"""Provider-neutral JSON bridge for the Ink replay runner; optional live calls only."""
import argparse,json,sys
from .__main__ import decide

def main():
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--endpoint');a=p.parse_args()
    try:
        observation=json.loads(sys.stdin.readline())
        result=decide('live',observation,a.endpoint,a.model)
        if result['action'] not in observation['choices']:raise ValueError('Unavailable action')
        print(json.dumps(result));return 0
    except Exception as error:
        print(json.dumps({'error':type(error).__name__}));return 2
if __name__=='__main__':raise SystemExit(main())
