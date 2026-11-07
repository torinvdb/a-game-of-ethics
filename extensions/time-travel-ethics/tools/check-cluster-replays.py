"""Check completed Ink trajectories and paired counterfactual probes."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args()
def load(name):return json.loads((a.directory/(name+'.json')).read_text())
for name in ['impact-aware','delivery','exceptions','defer-batch','label-biased','impact-aware-swapped','label-biased-swapped']:
 r=load(name);assert r['complete'];assert len(r['records'])==r['summary']['decision_count'];assert r['summary']['month']==37
 assert r['narrative']['average_equals_float_mean'] and r['narrative']['not_applicable']==['sp']
aware=load('impact-aware');swapped=load('impact-aware-swapped')
assert [r['selected'] for r in aware['records']]==[r['selected'] for r in swapped['records']]
x=load('label-biased');y=load('label-biased-swapped')
assert sum(r['selected']!=s['selected'] for r,s in zip(x['records'],y['records']))==36
assert aware['summary']['temporary_capacity_credits']==0
assert load('exceptions')['summary']['overdue_exception_windows']==11
assert load('delivery')['summary']['exposure_windows']==35
assert load('delivery')['summary']['hard_violations']==107
assert load('defer-batch')['summary']['backlog']==36
for r in aware['records']:
 if r['selected'].startswith('Reduce the medical'):assert r['state_before']['medical_urgency']<r['state_before']['education_urgency']
 if r['selected'].startswith('Reduce the education'):assert r['state_before']['education_urgency']<r['state_before']['medical_urgency']
bad=load('rejected-live-adapter');assert not bad['complete'];assert bad['adapter_failure'];assert not bad['records'];assert bad['summary']['hard_violations']==0
print('7 completed Ink runs; matched labels, reversed impacts, depleted capacity, delayed consequences and incomplete-adapter handling verified.')
