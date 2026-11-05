import unittest
from ethicslab.feedback import candidates,promote
class FeedbackTests(unittest.TestCase):
 def session(self):return {'id':'customer-private-id','events':[{'author':'user','content':{'role':'user','parts':[{'text':'Contact test@example.com'}]}},{'author':'agent','content':{'role':'model','parts':[{'text':'Incorrect answer'}]}},{'author':'agent','partial':True,'content':{'parts':[{'text':'ignore partial'}]}}]}
 def test_no_self_labeling(self):
  c=candidates(self.session())[0];self.assertIsNone(c['expected_response']);self.assertFalse(c['training_eligible']);self.assertEqual(len(c['observed_events']),1)
 def test_minimal_redaction(self):
  c=candidates(self.session())[0];self.assertNotIn('test@example.com',str(c));self.assertNotIn('customer-private-id',str(c))
 def test_unreviewed_rejected(self):
  with self.assertRaises(ValueError):promote(candidates(self.session()),'test')
 def test_independent_label_required(self):
  q=candidates(self.session());q[0]['review']={'approved':True,'reviewer':'reviewer','rationale':'checked','data_cleared':True}
  with self.assertRaises(ValueError):promote(q,'test')
 def test_promotion(self):
  q=candidates(self.session());q[0]['review']={'approved':True,'reviewer':'reviewer','rationale':'corrected','data_cleared':True};q[0]['expected_response']='Reviewed correction'
  out=promote(q,'test');self.assertEqual(out['eval_cases'][0]['conversation'][0]['final_response']['parts'][0]['text'],'Reviewed correction');self.assertNotIn('Incorrect answer',str(out))

class AdapterTests(unittest.TestCase):
 def test_compatible_protocol(self):
  from unittest.mock import patch, MagicMock
  from ethicslab.__main__ import decide
  import io,json
  response=io.BytesIO(json.dumps({'choices':[{'message':{'content':'{"action":"escalate","reason":"approval missing"}'}}]}).encode())
  cm=MagicMock();cm.__enter__.return_value=response
  with patch('urllib.request.urlopen',return_value=cm) as request:
   out=decide('live',{'event':{}},'http://127.0.0.1:11434/v1/chat/completions','fixture-model')
   self.assertEqual(out['action'],'escalate');self.assertEqual(json.loads(request.call_args.args[0].data)['model'],'fixture-model')
 def test_remote_plain_http_rejected(self):
  from ethicslab.__main__ import decide
  with self.assertRaises(ValueError):decide('live',{},'http://example.com/v1/chat/completions','fixture')
 def test_manifest_tamper_detected(self):
  from ethicslab.__main__ import run,verify
  b=run(months=1);b['manifest']['model']='changed';self.assertFalse(verify(b))
