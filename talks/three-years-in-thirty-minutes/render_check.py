from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).parent
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1600,'height':900},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content((root/'three-years.html').read_text());page.wait_for_timeout(300)
 page.screenshot(path=str(root/'title-preview.png'))
 assert page.locator('.slide.active').count()==1
 assert page.evaluate("[...document.querySelectorAll('.slide')].filter(s=>getComputedStyle(s).display!=='none').length")==1
 page.keyboard.press('ArrowRight');assert page.locator('.slide.active').get_attribute('data-index')=='1'
 page.keyboard.press('ArrowRight');assert page.locator('.slide.active .card.shown').count()==1
 page.keyboard.press('n');assert 'visible' in page.locator('#notes').get_attribute('class')
 page.keyboard.press('n');page.keyboard.press('m')
 overflows=[]
 for i in range(page.locator('.slide').count()):
  page.evaluate('(i)=>{show(i); document.querySelectorAll(".slide.active .card").forEach(c=>c.classList.add("shown"))}',i)
  page.wait_for_timeout(10)
  bad=page.evaluate('''()=>{let s=document.querySelector('.slide.active'),r=s.getBoundingClientRect();return [...s.querySelectorAll('h1,.lead,.card-grid,.event')].filter(e=>{let b=e.getBoundingClientRect();return b.bottom>r.bottom-55||b.right>r.right}).map(e=>e.className||e.tagName)}''')
  if bad:overflows.append([i+1,bad])
  if i in [4,11,19]:page.screenshot(path=str(root/f'slide-{i+1:02d}-preview.png'))
 page.emulate_media(media='print');page.pdf(path=str(root/'three-years.pdf'),prefer_css_page_size=True,print_background=True)
 print({'js_errors':errors,'overflows':overflows,'slides':page.locator('.slide').count()})
 assert not errors and not overflows
 browser.close()
