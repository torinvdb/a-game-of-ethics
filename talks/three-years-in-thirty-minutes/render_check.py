"""Render the deck, check presentation interactions/layout, and export PDF."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

root = Path(__file__).parent
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    page = browser.new_page(viewport={'width':1600, 'height':900}, device_scale_factor=1)
    errors, requests = [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('request', lambda request: requests.append(request.url) if request.url.startswith(('http:', 'https:')) else None)
    page.set_content((root/'three-years.html').read_text())
    page.evaluate('document.fonts.ready')
    page.wait_for_timeout(400)
    assert page.locator('.slide.active').count() == 1
    assert page.evaluate("[...document.querySelectorAll('.slide')].filter(s=>getComputedStyle(s).display!=='none').length") == 1
    page.keyboard.press('ArrowRight')
    assert page.locator('.slide.active').get_attribute('data-index') == '1'
    page.keyboard.press('ArrowRight')
    assert page.locator('.slide.active .card.shown').count() == 1
    page.keyboard.press('n')
    assert 'visible' in page.locator('#notes').get_attribute('class')
    page.keyboard.press('n')
    page.evaluate('show(4)')
    assert page.locator('.slide.active .phase.shown').count() == 0
    page.keyboard.press('ArrowRight')
    assert page.locator('.slide.active .phase.shown').count() == 1
    page.keyboard.press('a')
    assert page.locator('.slide.active .phase.shown').count() == 3
    page.keyboard.press('m')
    assert 'motion-off' in page.locator('body').get_attribute('class')
    issues = []
    selected = {0:'title-preview.png',4:'slide-05-preview.png',7:'slide-08-preview.png',
                10:'slide-11-preview.png',11:'slide-12-preview.png',19:'slide-20-preview.png',22:'closing-preview.png'}
    for i in range(page.locator('.slide').count()):
        page.evaluate('(i)=>{show(i);revealAll()}', i)
        page.wait_for_timeout(10)
        problems = page.evaluate('''()=>{
            const s=document.querySelector('.slide.active'), r=s.getBoundingClientRect();
            const h=s.querySelector('h1').getBoundingClientRect(), l=s.querySelector('.lead').getBoundingClientRect();
            const footer=s.querySelector('.folio').getBoundingClientRect();
            let bad=[];
            for(const e of s.querySelectorAll('h1,.lead,.card h2,.card p,.event,.diagram-caption')){
                let b=e.getBoundingClientRect();
                if(b.bottom>footer.top-8 || b.right>r.right-55 || b.left<r.left+30)bad.push('bounds: '+e.className+' '+e.textContent.slice(0,35));
            }
            if(h.bottom>l.top-5)bad.push('title/lead overlap');
            const cards=[...s.querySelectorAll('.card')];
            if(cards.length && l.bottom>cards[0].getBoundingClientRect().top-8)bad.push('lead/annotations overlap');
            return bad;
        }''')
        if problems: issues.append({'slide':i+1,'issues':problems})
        if i in selected: page.screenshot(path=str(root/selected[i]))
    for width,height in [(1280,720),(1024,768),(1920,1080)]:
        page.set_viewport_size({'width':width,'height':height})
        page.evaluate('fit();show(0)')
        box=page.locator('.slide.active').bounding_box()
        assert box['x']>=-1 and box['y']>=-1 and box['x']+box['width']<=width+1 and box['y']+box['height']<=height+1
    page.set_viewport_size({'width':1600,'height':900})
    page.emulate_media(reduced_motion='reduce')
    page.evaluate('document.body.classList.remove("motion-off");show(4);revealAll()')
    assert page.locator('.slide.active .wire').first.evaluate('(e)=>getComputedStyle(e).animationName') == 'none'
    assert not errors and not requests and not issues, {'js_errors':errors,'external_requests':requests,'layout_issues':issues}
    page.emulate_media(media='print')
    page.pdf(path=str(root/'three-years.pdf'), prefer_css_page_size=True, print_background=True)
    result={'slides':page.locator('.slide').count(),'js_errors':errors,'external_requests':requests,
            'layout_issues':issues,'viewports':['1600x900','1280x720','1024x768','1920x1080'],
            'checks':['navigation','annotation and diagram reveals','notes','motion toggle','reduced motion','offline assets']}
    (root/'render-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result,flush=True)
    browser.close()
