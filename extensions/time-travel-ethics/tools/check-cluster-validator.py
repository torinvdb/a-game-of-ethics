"""Integration checks for the original Ink validator's persistent-choice support."""
import os,subprocess,tempfile
from pathlib import Path
repo=Path(__file__).resolve().parents[3]
headers='\n'.join('VAR '+k+' = 0' for k in ['hc','fj','ar','al','lt','it','sp','uc','total','average','counter_a','counter_b','counter_c'])+'\nVAR returnPath = ""\n-> start\n=== start ===\n'
end='\n=== debrief ===\n~ total = hc + fj + ar + al + lt + it + sp + uc\nVERDICT: REVIEW REQUIRED\n-> END\n'
cases={
 'persistent':('+ [Advance]\n ~ hc = hc + 1 // care\n ~ fj = fj + 1 // fairness\n ~ it = it + 1 // truth\n -> debrief\n',0),
 'bookkeeping-only':('+ [Advance]\n ~ counter_a = counter_a + 1 // counter\n ~ counter_b = counter_b + 1 // counter\n ~ counter_c = counter_c + 1 // counter\n -> debrief\n',1),
 'no-choices':('This story has no choice.\n-> debrief\n',1)}
with tempfile.TemporaryDirectory(prefix='ethics-validator-') as tmp:
 for name,(body,expected) in cases.items():
  f=Path(tmp)/(name+'.ink');f.write_text(headers+body+end)
  r=subprocess.run(['node',str(repo/'src/debug.js'),'--auto-validate',str(f)],capture_output=True,text=True,timeout=30)
  assert r.returncode==expected,(name,r.returncode,r.stdout,r.stderr)
  print(name+': expected exit '+str(expected)+' confirmed')
