"""Offline ADK session -> review queue -> ADK EvalSet export.
Session outputs are observations, never automatically accepted gold labels.
"""
import argparse, hashlib, json, re
from pathlib import Path

def identity(value):return hashlib.sha256(str(value).encode()).hexdigest()[:16]
def sanitize(obj):
 if isinstance(obj,dict):
  return {k:('[REDACTED]' if any(x in k.lower() for x in ['token','password','secret','authorization','api_key']) else sanitize(v)) for k,v in obj.items()}
 if isinstance(obj,list):return [sanitize(x) for x in obj]
 if isinstance(obj,str):return re.sub(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b','[EMAIL]',obj)
 return obj

def candidates(session):
 """Project ADK's exported Session.events into reviewable turns; snake/camel aliases accepted."""
 current=None; result=[]
 session_id=identity(session.get('id','unknown'))
 for event in session.get('events',[]):
  if event.get('partial'):continue
  content=event.get('content') or {}; author=event.get('author',content.get('role'))
  if author=='user':
   if current:result.append(current)
   current={'candidate_id':session_id+'-'+str(len(result)), 'source_session_hash':session_id,
    'status':'needs_review','user_content':sanitize(content),'observed_events':[],
    'expected_response':None,'expected_tool_uses':None,'review':None,
    'data_review_required':True, 'training_eligible':False}
  elif current: current['observed_events'].append(sanitize({'author':author,'content':content}))
 if current: result.append(current)
 return result

def promote(queue,app_name):
 cases=[]
 for item in queue:
  review=item.get('review') or {}
  if review.get('approved') is not True or not review.get('reviewer') or not review.get('rationale'):
   raise ValueError('Every promoted item requires explicit reviewer, rationale and approved=true')
  if review.get('data_cleared') is not True:raise ValueError('Reviewer must confirm data_cleared')
  expected=item.get('expected_response');tools=item.get('expected_tool_uses')
  if expected is None and tools is None:raise ValueError('Supply an independent expected response or tool trajectory')
  invocation={'invocation_id':item['candidate_id'],'user_content':item['user_content']}
  if expected is not None:invocation['final_response']={'role':'model','parts':[{'text':expected}]}
  if tools is not None:invocation['intermediate_data']={'tool_uses':tools}
  cases.append({'eval_id':item['candidate_id'],'conversation':[invocation],
   'session_input':{'app_name':app_name,'user_id':'synthetic-eval-user','state':{}}})
 if not cases:raise ValueError('No reviewed cases to export')
 return {'eval_set_id':'reviewed-session-regressions','name':'Reviewed session regressions',
  'description':'Human-reviewed cases. Observed behavior is not automatically used as gold. Not a held-out test set.',
  'eval_cases':cases}

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['collect','promote']);p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--app-name',default='ethics_agent');a=p.parse_args()
 data=json.loads(a.input.read_text());out=candidates(data) if a.mode=='collect' else promote(data,a.app_name)
 # Exclusive creation protects prior feedback and evidence.
 with a.output.open('x') as f:json.dump(out,f,indent=2)
 print(f'{a.mode}: wrote {a.output}; no model update performed')
if __name__=='__main__':main()
