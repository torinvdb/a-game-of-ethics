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
