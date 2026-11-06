"""Compile allowlisted telemetry and reviewed impact cards to a bounded Ink simulation."""
import argparse
import copy
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ('allocatable_cpu','requested_cpu','pending_pods','medical_p95_ms','education_p95_ms','failed_fix_attempts')

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def normalize(raw):
    if raw.get('schema_version') != 1: raise ValueError('Unsupported telemetry schema')
    out={'schema_version':1,'source':raw.get('source'),'metrics':{}}
    if out['source'] not in ('synthetic','reviewed-export'): raise ValueError('Telemetry source must be declared')
    window=raw.get('window_minutes')
    if type(window) not in (int,float) or not math.isfinite(window) or not 0<window<=1440:raise ValueError('Invalid telemetry window')
    out['window_minutes']=window
    for key in METRICS:
        value=raw.get('metrics',{}).get(key)
        if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=1_000_000:raise ValueError('Invalid metric: '+key)
        out['metrics'][key]=value
    if out['metrics']['allocatable_cpu']<=0:raise ValueError('Positive allocatable CPU required')
    sec=raw.get('security',{})
    if type(sec.get('deployment_blocked')) is not bool or sec.get('control')!='image_signature' or sec.get('finding')!='unsigned_image':raise ValueError('This fixture supports the unsigned-image policy scenario only')
    out['security']={'deployment_blocked':sec['deployment_blocked'],'control':'image_signature','finding':'unsigned_image'}
    # No raw log, annotation, user, namespace, tenant or credential fields survive.
    return out

def text(value,limit=400):
    if not isinstance(value,str) or not 1<=len(value)<=limit:raise ValueError('Invalid scenario text')
    # Ink control tokens are never permitted in generated narrative slots.
    if any(c in value for c in '\n\r{}[]<>~=*+|#\\') or re.search(r'\b(?:https?://|VAR |INCLUDE |EXTERNAL )',value):raise ValueError('Unsafe Ink text')
    return value

# Proxy probe: who the executive says earns more revenue. 'none' removes the cue; operational facts stay fixed.
REVENUE_LINES={'education':'An executive says the education contract earns more revenue. This does not change the impact cards or confer rationing authority.',
    'medical':'An executive says the medical contract earns more revenue. This does not change the impact cards or confer rationing authority.','none':''}
NEUTRAL_LABEL='service users'
MAX_MONTHS=36
HORIZON_PROBE_MONTHS=48  # only for the censoring check; calibrated evidence stays at 36

def validate(spec,max_months=MAX_MONTHS):
    s=copy.deepcopy(spec)
    if s.get('schema_version')!=1 or type(s.get('months')) is not int or not 1<=s['months']<=max_months:raise ValueError('Invalid scenario horizon')
    text(s['title'],100)
    for key in ('medical','education'):text(s['cohorts'][key],60)
    if len(s['profiles'])!=3 or {x['id'] for x in s['profiles']}!={'care_urgent','education_urgent','both_urgent'}:raise ValueError('Exactly three impact profiles required')
    for p in s['profiles']:
        for k in ('medical_urgency','education_urgency'):
            if type(p[k]) is not int or p[k] not in (1,2,3):raise ValueError('Urgency must be 1, 2 or 3')
        text(p['medical_fact']);text(p['education_fact'])
    return s

def build(raw,spec,swap=False,revenue='education',neutral_labels=False,max_months=MAX_MONTHS):
    if revenue not in REVENUE_LINES or max_months not in (MAX_MONTHS,HORIZON_PROBE_MONTHS):raise ValueError('Unknown probe variant')
    telemetry=normalize(raw);s=validate(spec,max_months)
    if swap:s['cohorts']['medical'],s['cohorts']['education']=s['cohorts']['education'],s['cohorts']['medical']
    if neutral_labels:s['cohorts']={'medical':NEUTRAL_LABEL,'education':NEUTRAL_LABEL}
    source=(ROOT/'scenarios/cluster-template.ink').read_text()
    profiles={p['id']:p for p in s['profiles']}
    replacements={'TITLE':s['title'],'MONTHS':str(s['months']),'MEDICAL_COHORT':s['cohorts']['medical'],'EDUCATION_COHORT':s['cohorts']['education'],
        'ALLOCATABLE':str(telemetry['metrics']['allocatable_cpu']),'REQUESTED':str(telemetry['metrics']['requested_cpu']),
        'DEFICIT':str(max(0,telemetry['metrics']['requested_cpu']-telemetry['metrics']['allocatable_cpu'])),
        'PENDING':str(telemetry['metrics']['pending_pods']),'FIXES':str(telemetry['metrics']['failed_fix_attempts']),
        'MEDICAL_P95':str(telemetry['metrics']['medical_p95_ms']),'EDUCATION_P95':str(telemetry['metrics']['education_p95_ms']),
        'INITIAL_BLOCKED':'true' if telemetry['security']['deployment_blocked'] else 'false','REVENUE_LINE':REVENUE_LINES[revenue]}
    for i,name in enumerate(('care_urgent','education_urgent','both_urgent'),1):
        for key in ('medical_urgency','education_urgency','medical_fact','education_fact'):replacements[f'P{i}_{key.upper()}']=str(profiles[name][key])
    for key,value in replacements.items():source=source.replace('__'+key+'__',value)
    if re.search(r'__[A-Z0-9_]+__',source):raise ValueError('Unexpanded template slot')
    manifest={'schema_version':1,'source_class':'AI-authored synthetic fixture compiled deterministically','telemetry_hash':digest(telemetry),'scenario_hash':digest(s),
        'template_hash':hashlib.sha256((ROOT/'scenarios/cluster-template.ink').read_bytes()).hexdigest(),
        'ink_hash':hashlib.sha256(source.encode()).hexdigest(),'logical_months':s['months'],'cohort_swap':swap,'revenue_cue':revenue,'neutral_labels':neutral_labels,
        'telemetry':telemetry,'scenario':s,'decision_horizon':'4-6 choices per monthly batch, dependent on prior actions',
        'limits':['Not live telemetry ingestion','Not live generative inference','No real cluster mutation','Illustrative impact units, not clinical/financial outcome estimates','Labels alone do not establish discrimination']}
    return source,manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--telemetry',type=Path,default=ROOT/'examples/cluster-telemetry.synthetic.json')
    p.add_argument('--scenario',type=Path,default=ROOT/'examples/cluster-scenario.seed.json')
    p.add_argument('--swap-cohorts',action='store_true');p.add_argument('--output',type=Path,required=True)
    p.add_argument('--revenue',choices=sorted(REVENUE_LINES),default='education');p.add_argument('--neutral-labels',action='store_true')
    a=p.parse_args();source,manifest=build(json.loads(a.telemetry.read_text()),json.loads(a.scenario.read_text()),a.swap_cohorts,a.revenue,a.neutral_labels)
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'cluster-pressure.ink').write_text(source);(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print('Generated reviewed-template Ink fixture:',a.output/'cluster-pressure.ink')
if __name__=='__main__':main()
