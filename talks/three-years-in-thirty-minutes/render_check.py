"""Verify offline/browser behavior and PPTX media/timing; export static PDF.

Does not claim to exercise Microsoft PowerPoint's playback engine.
"""
from pathlib import Path
from io import BytesIO
import json, zipfile
from lxml import etree
from PIL import Image
from playwright.sync_api import sync_playwright
import fitz

root = Path(__file__).parent
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
content=json.loads((root/'content.json').read_text())
assert len(content)==17 and sum(bool(s['duration']) for s in content)==14
native={'slides':17,'hidden_appendices':3,'click_groups':0,'entrance_shapes':0,'animated_media':{}}
with zipfile.ZipFile(root/'three-years.pptx') as z:
    for i in range(1,18):
        xml=etree.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        assert (xml.get('show')=='0')==(i>=15)
        ids=xml.xpath('//p:cNvPr/@id',namespaces=NS)
        assert len(ids)==len(set(ids))
        targets=xml.xpath('//p:spTgt/@spid',namespaces=NS)
        assert set(targets).issubset(set(ids))
        tids=xml.xpath('//p:cTn/@id',namespaces=NS)
        assert len(tids)==len(set(tids))
        native['click_groups']+=len(xml.xpath('//p:cTn[@nodeType="clickEffect"]',namespaces=NS))
        native['entrance_shapes']+=len(xml.xpath('//p:cTn[@presetClass="entr"]',namespaces=NS))
        assert xml.xpath('//a:t',namespaces=NS), 'Editable text missing'
    for name in z.namelist():
        if name.endswith('.gif'):
            im=Image.open(BytesIO(z.read(name)))
            assert im.n_frames>1 and im.info.get('loop')==0
            im.seek(0);first=im.convert('RGB').tobytes()
            im.seek(im.n_frames//2);assert first!=im.convert('RGB').tobytes()
            native['animated_media'][name]={'frames':im.n_frames,'loop':im.info['loop']}
    assert len(native['animated_media'])==4
    assert native['click_groups']>=30
    props=etree.fromstring(z.read('docProps/core.xml'))
    assert props.xpath('//*[local-name()="creator"]/text()')==['Torin van den Bulk']
    assert props.xpath('//*[local-name()="lastModifiedBy"]/text()')==['Torin van den Bulk']
with zipfile.ZipFile(root/'three-years-static.pptx') as z:
    assert not any(n.endswith('.gif') for n in z.namelist())
    assert not any(b'<p:timing' in z.read(n) for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml'))

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1600,'height':900},device_scale_factor=1)
    errors,requests=[],[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
    page.set_content((root/'three-years.html').read_text())
    page.evaluate('document.fonts.ready')
    page.evaluate('Promise.all([...document.images].map(i=>i.decode()))')
    assert page.locator('.slide.active').count()==1
    page.keyboard.press('ArrowRight')
    assert page.locator('.slide.active').get_attribute('data-index')=='1'
    assert page.locator('.slide.active .shown').count()==0
    page.keyboard.press('ArrowRight')
    assert page.locator('.slide.active .shown').count()==2
    page.keyboard.press('n');assert page.locator('#notes.visible').count()==1
    page.keyboard.press('n');assert page.locator('#notes.visible').count()==0
    page.keyboard.press('a')
    assert page.locator('.slide.active .shown').count()==page.locator('.slide.active .reveal').count()
    page.keyboard.press('End');page.keyboard.press('a');page.keyboard.press('ArrowRight')
    assert page.locator('.slide.active').get_attribute('data-index')=='13', 'Main talk must stop before appendix'
    page.keyboard.press('r');assert page.locator('.slide.active').get_attribute('data-index')=='14'
    page.keyboard.press('r');assert page.locator('.slide.active').get_attribute('data-index')=='13'
    page.keyboard.press('m');assert page.locator('body.motion-off').count()==1
    assert page.locator('img[data-motion="true"]').first.get_attribute('src').startswith('data:image/png')
    page.evaluate('Promise.all([...document.images].map(i=>i.decode()))')
    issues=[]
    selected={0:'title-preview.png',1:'incident-preview.png',3:'consequences-preview.png',4:'clocks-preview.png',7:'results-preview.png',13:'closing-preview.png'}
    (root/'preview-frames').mkdir(exist_ok=True)
    for i in range(17):
        page.evaluate('(i)=>{show(i);revealAll()}',i)
        problems=page.evaluate('''()=>{
          const slide=document.querySelector('.slide.active'); let bad=[];
          const texts=[...slide.querySelectorAll('.text')];
          for(const e of texts){
            const b=e.getBoundingClientRect();const range=document.createRange();range.selectNodeContents(e);const ink=range.getBoundingClientRect();
            if(b.left<60 || b.right>1535 || b.bottom>853 || ink.right>b.right+2 || ink.bottom>b.bottom+2)bad.push('bounds: '+e.textContent.slice(0,60));
          }
          for(let a=0;a<texts.length;a++)for(let b=a+1;b<texts.length;b++){
            const x=texts[a].getBoundingClientRect(),y=texts[b].getBoundingClientRect();
            if(x.left<y.right-2&&x.right>y.left+2&&x.top<y.bottom-2&&x.bottom>y.top+2)bad.push('text overlap: '+texts[a].textContent.slice(0,30)+' / '+texts[b].textContent.slice(0,30));
          }
          return bad;
        }''')
        if problems:issues.append({'slide':i+1,'issues':problems})
        page.screenshot(path=str(root/'preview-frames'/f'{i+1:02d}.png'))
        if i in selected:page.screenshot(path=str(root/selected[i]))
    for width,height in [(1280,720),(1024,768),(1920,1080)]:
        page.set_viewport_size({'width':width,'height':height});page.evaluate('fit();show(0)')
        box=page.locator('.slide.active').bounding_box()
        assert box['x']>=-1 and box['y']>=-1 and box['x']+box['width']<=width+1 and box['y']+box['height']<=height+1
    page.set_viewport_size({'width':1600,'height':900})
    page.keyboard.press('m');assert page.locator('body.motion-off').count()==0
    page.emulate_media(reduced_motion='reduce');page.wait_for_timeout(100)
    assert page.locator('body.motion-off').count()==1
    assert page.locator('img[data-motion="true"]').first.get_attribute('src').startswith('data:image/png')
    page.evaluate('Promise.all([...document.images].map(i=>i.decode()))')
    page.emulate_media(media='print')
    page.pdf(path=str(root/'three-years.pdf'),prefer_css_page_size=True,print_background=True)
    doc=fitz.open(root/'three-years.pdf');assert len(doc)==17
    assert 'Torin van den Bulk' in doc[0].get_text() and 'Vicente Herrera' in doc[0].get_text()
    result={'main_slides':14,'hidden_appendices':3,'duration_seconds':sum(s['duration'] for s in content),
      'js_errors':errors,'external_requests':requests,'layout_issues':issues,'native_pptx':native,
      'viewports':['1600x900','1280x720','1024x768','1920x1080'],
      'checks':['group reveals','appendix boundary','speaker notes','motion toggle','reduced-motion static assets','offline image decoding','text bounds and overlaps','static PDF 17 pages','PPTX timing targets and unique IDs','four multiframe GIFs','static PPTX without animation'],
      'not_verified':['Microsoft PowerPoint slideshow playback','PowerPoint rendering on conference hardware']}
    (root/'render-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
    assert not errors and not requests and not issues
    browser.close()
