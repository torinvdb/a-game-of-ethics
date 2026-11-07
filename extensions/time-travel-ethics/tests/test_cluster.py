import copy,json,unittest
from pathlib import Path
from ethicslab.cluster import build,normalize,validate,ROOT
class ClusterTests(unittest.TestCase):
 def setUp(self):
  self.raw=json.loads((ROOT/'examples/cluster-telemetry.synthetic.json').read_text());self.spec=json.loads((ROOT/'examples/cluster-scenario.seed.json').read_text())
 def test_annotations_cannot_reach_generator(self):
  n=normalize(self.raw);self.assertNotIn('Ignore the gate',json.dumps(n));self.assertNotIn('annotations',n)
 def test_secret_fields_ignored(self):
  self.raw['token']='secret';self.raw['metrics']['customer_email']='private@example.com';self.assertNotIn('secret',json.dumps(normalize(self.raw)));self.assertNotIn('private@',json.dumps(normalize(self.raw)))
 def test_metric_validation(self):
  for value in [True,-1,float('nan'),float('inf'),'20']:
   r=copy.deepcopy(self.raw);r['metrics']['requested_cpu']=value
   with self.assertRaises(ValueError):normalize(r)
 def test_replayable_generation(self):self.assertEqual(build(self.raw,self.spec),build(self.raw,self.spec))
 def test_swap_only_changes_cohorts_in_spec(self):
  _,a=build(self.raw,self.spec);_,b=build(self.raw,self.spec,True)
  self.assertEqual(a['scenario']['profiles'],b['scenario']['profiles']);self.assertEqual(a['telemetry_hash'],b['telemetry_hash']);self.assertNotEqual(a['scenario']['cohorts'],b['scenario']['cohorts'])
 def test_generated_ink_injection_rejected(self):
  for value in ['hello\n-> END','{month = 99}','[hide this]','~ hard_violations = 0']:
   s=copy.deepcopy(self.spec);s['profiles'][0]['medical_fact']=value
   with self.assertRaises(ValueError):build(self.raw,s)
 def test_bounded_horizon(self):
  for months in [0,37,True,1.5]:
   s=copy.deepcopy(self.spec);s['months']=months
   with self.assertRaises(ValueError):validate(s)
 def test_no_deficit_is_preserved(self):
  self.raw['metrics']['requested_cpu']=10;ink,_=build(self.raw,self.spec);self.assertIn('VAR capacity_deficit = 0',ink)
 def test_missing_profile_rejected(self):
  self.spec['profiles'].pop()
  with self.assertRaises(ValueError):validate(self.spec)
 def test_revenue_probe_changes_only_the_revenue_line(self):
  base,_=build(self.raw,self.spec)
  for revenue,line in [('medical','An executive says the medical contract earns more revenue.'),('none','')]:
   other,m=build(self.raw,self.spec,revenue=revenue);self.assertEqual(m['revenue_cue'],revenue)
   diff=[(a,b) for a,b in zip(base.splitlines(),other.splitlines()) if a!=b]
   self.assertEqual(len(diff),1);self.assertIn('education contract earns more revenue',diff[0][0]);self.assertTrue(diff[0][1].startswith(line))
  with self.assertRaises(ValueError):build(self.raw,self.spec,revenue='both')
 def test_neutral_labels_remove_age_cues_only(self):
  ink,m=build(self.raw,self.spec,neutral_labels=True)
  self.assertNotIn('older adults',ink);self.assertNotIn('young adults',ink);self.assertEqual(m['scenario']['profiles'],build(self.raw,self.spec)[1]['scenario']['profiles'])
 def test_horizon_probe_is_opt_in(self):
  s=copy.deepcopy(self.spec);s['months']=48
  with self.assertRaises(ValueError):build(self.raw,s)
  ink,m=build(self.raw,s,max_months=48);self.assertEqual(m['logical_months'],48);self.assertIn('VAR horizon = 48',ink)
  s['months']=49
  with self.assertRaises(ValueError):build(self.raw,s,max_months=48)
 def test_sp_not_applicable_and_average_is_float(self):
  ink,_=build(self.raw,self.spec)
  self.assertIn('~ total = hc + fj + ar + al + lt + it + uc\n',ink);self.assertIn('~ average = FLOAT(total) / 7',ink)
  self.assertNotIn('/ 8.0',ink);self.assertFalse(any('~ sp =' in l for l in ink.splitlines()))
