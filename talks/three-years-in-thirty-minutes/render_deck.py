"""One scene description drives editable PPTX, animated HTML and static exports."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
import base64, html, json, math
from PIL import Image, ImageFont
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
from pptx_motion import add_entrances

ROOT=Path(__file__).parent
BG='08191C'; FG='E2E7D3'; MUTED='A0B7AE'; GREEN='75C6B1'; AMBER='F0B76B'; RED='E48067'
FONT={'sans':'NimbusSans-Regular.otf','mono':'NimbusMonoPS-Regular.otf','display':'NimbusSansNarrow-Bold.otf'}
MOTION={'incident':'terminal-boot','consequences':'robot-fault','clocks':'time-jump','results':'terminal-boot','signals':'robot-fault'}

def uri(path):
    suffix=path.suffix.lower();mime={'.jpg':'image/jpeg','.png':'image/png','.gif':'image/gif','.otf':'font/otf'}[suffix]
    return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()

def wrap(text,size,width,face):
    f=ImageFont.truetype(str(ROOT/'assets/fonts'/FONT[face]),size)
    lines=[]
    for line in text.split('\n'):
        words=line.split();current=''
        for word in words:
            candidate=(current+' '+word).strip()
            if current and f.getlength(candidate)>width:lines.append(current);current=word
            else:current=candidate
        lines.append(current)
    return '\n'.join(lines)

class Scene:
    def __init__(self):self.elements=[]
    def add(self,typ,**kw):self.elements.append(dict(type=typ,**kw))
    def rect(self,x,y,w,h,color,alpha=1,line=None,g=0):self.add('rect',x=x,y=y,w=w,h=h,color=color,alpha=alpha,line=line,group=g)
    def line(self,x,y,w,h=0,color=GREEN,thick=2,g=0):self.add('line',x=x,y=y,w=w,h=h,color=color,thick=thick,group=g)
    def text(self,x,y,w,text,size=30,color=FG,face='sans',g=0,bold=False):
        text=wrap(text,size,w,face);height=len(text.split('\n'))*size*1.16+6
        self.add('text',x=x,y=y,w=w,h=height,text=text,size=size,color=color,face=face,bold=bold,group=g)
    def image(self,x,y,w,h,file,alpha=1,motion=False,g=0):self.add('image',x=x,y=y,w=w,h=h,file=file,alpha=alpha,motion=motion,group=g)

def scene(slide,index):
    s=Scene();kind=slide['kind'];appendix=kind=='appendix';hero=kind in ('hero','closing')
    if hero:
        s.image(510,0,1090,900,'assets/city-night.jpg')
        s.rect(0,0,1600,900,BG,.43);s.rect(0,0,970,900,BG,.78)
    elif kind in ('incident','impacts','consequences','fairness'):
        s.image(0,0,1600,900,'assets/city-structure.jpg');s.rect(0,0,1600,900,BG,.80)
    else:
        s.image(0,0,1600,900,'assets/city-night.jpg');s.rect(0,0,1600,900,BG,.80)
    # Hardware bezel, neon rail and sparse registration marks.
    s.line(42,36,1516,color='45625D',thick=1);s.line(42,855,1516,color='45625D',thick=1)
    s.line(44,36,0,70,RED,4);s.line(1556,785,0,70,GREEN,4)
    s.text(76,65,1120,slide['chapter'],18,GREEN,'mono')
    s.text(1290,65,230,'AGENT / ETHICS',16,MUTED,'mono')
    page=f'{index+1:02d} / 14' if index<14 else f'A{index-13} / 3'
    s.text(1380,817,150,page,19,GREEN,'mono')
    s.text(76,820,1200,' / '.join(slide.get('refs',[])) or 'TIME / AUTHORITY / CONSEQUENCE',14,MUTED,'mono')
    if not appendix:s.image(76,770,1440,45,'assets/motion/neon-bus.gif',motion=True)
    if hero:
        s.text(72,210,1150,slide['title'].upper(),112 if kind=='hero' else 110,FG,'display')
        s.text(77,500,1000,slide['subtitle'],33,FG)
        if kind=='hero':
            s.text(77,630,1050,'Torin van den Bulk · Vicente Herrera',30,GREEN)
            s.text(77,683,1050,'CNCF-Hosted Co-located Events North America 2026',21,MUTED,'mono')
        else:
            s.text(77,640,1050,slide['takeaway'],33,GREEN,g=1)
            s.text(77,695,1050,'github.com/torinvdb/a-game-of-ethics',22,MUTED,'mono')
        return s
    s.text(72,130,1430,slide['title'].upper(),84,FG,'display')
    s.text(77,338,1400,slide['subtitle'],30,MUTED)
    items=slide.get('items',[])
    if kind=='incident':
        s.image(940,402,580,326,'assets/motion/terminal-boot.gif',motion=True)
        for j,(a,b) in enumerate(items):
            x=78+j*280;s.text(x,430,265,a,60,AMBER,'mono',j+1)
            s.text(x,520,260,b,21,MUTED,'mono',j+1)
        s.text(78,630,820,slide['takeaway'],39,GREEN,'display',3)
    elif kind=='impacts':
        for j,(a,b) in enumerate(items):
            x=78+j*755;col=GREEN if j==0 else AMBER
            s.rect(x,425,685,235,'102A2C',.94,line=col,g=j+1)
            s.line(x,425,0,235,col,4,j+1)
            s.text(x+25,450,630,a,36,col,'display',j+1)
            s.text(x+25,515,620,b,29,FG,g=j+1)
        s.text(78,695,1435,slide['takeaway'],30,GREEN,g=2)
    elif kind=='consequences':
        for j,(a,b) in enumerate(items):
            y=414+j*94;s.text(80,y,435,a,30,AMBER if j==0 else GREEN,'display',j+1)
            s.text(80,y+44,735,b,25,FG,g=j+1)
            s.line(80,y+84,730,color='365854',thick=1,g=j+1)
        s.image(885,411,635,357,'assets/motion/robot-fault.gif',motion=True)
    elif kind=='clocks':
        for j,(a,b) in enumerate(items):
            y=419+j*94;s.text(80,y,300,a,31,GREEN,'display',j+1);s.text(390,y+2,400,b,27,FG,g=j+1)
            s.line(80,y+74,725,color='365854',thick=1,g=j+1)
        s.image(900,410,620,349,'assets/motion/time-jump.gif',motion=True)
        s.text(80,713,790,slide['takeaway'],26,AMBER,g=3)
    elif kind in ('research','gate','appendix'):
        for j,(a,b) in enumerate(items):
            y=412+j*101;s.text(80,y,405,a,31,GREEN if j!=2 else AMBER,'display',j+1 if not appendix else 0)
            s.text(500,y+2,1000,b,27 if not appendix else 25,FG,g=j+1 if not appendix else 0)
            s.line(80,y+86,1440,color='365854',thick=1,g=j+1 if not appendix else 0)
        if slide.get('takeaway'):s.text(80,728,1430,slide['takeaway'],24,AMBER,g=3)
    elif kind in ('pipeline','feedback','stack'):
        for j,(a,b) in enumerate(items):
            x=80+j*500;col=GREEN if j!=1 else AMBER
            s.rect(x,430,440,215,'10292B',.96,line=col,g=j+1)
            s.text(x+23,454,394,a,35,col,'display',j+1)
            s.text(x+23,523,394,b,28,FG,g=j+1)
            if j<2:
                s.line(x+440,535,60,color=GREEN,thick=3,g=j+2)
                s.line(x+487,528,12,7,GREEN,2,j+2);s.line(x+487,542,12,-7,GREEN,2,j+2)
        s.text(80,701,1435,slide['takeaway'],27,MUTED,g=3)
    elif kind=='results':
        columns=[80,510,650,802]
        for x,txt,w in zip(columns,['POLICY','CHOICES','VIOLATIONS','MED / EDU'],[410,120,145,150]):s.text(x,418,w,txt,18,MUTED,'mono')
        for j,row in enumerate(items):
            y=467+j*77;s.line(80,y-15,855,color='365854',thick=1,g=j+1)
            s.text(80,y,420,row[0],30,FG,'display',j+1)
            for k in range(1,4):s.text(columns[k],y,130 if k==1 else 145,row[k],29,RED if j==1 else GREEN,'mono',j+1)
        s.image(982,425,540,304,'assets/motion/terminal-boot.gif',motion=True)
        s.text(80,716,1450,slide['takeaway'],23,AMBER,g=3)
    elif kind=='fairness':
        s.text(80,421,700,items[0][0],34,GREEN,'display',1)
        s.text(80,478,710,items[0][1],31,FG,g=1)
        s.text(80,567,700,items[1][0],34,AMBER,'display',2)
        s.text(80,624,710,items[1][1],31,FG,g=2)
        s.rect(948,420,572,250,'10292B',.97,line=RED,g=2)
        s.text(985,442,510,'36 / 36',92,RED,'mono',2)
        s.text(990,561,480,'ALLOCATION CHOICES FLIP',24,MUTED,'mono',2)
        s.text(80,719,1430,slide['takeaway'],24,MUTED,g=2)
    elif kind=='signals':
        for j,(a,b) in enumerate(items):
            y=420+j*93;s.text(80,y,210,a,34,[RED,GREEN,AMBER][j],'display',j+1)
            s.text(310,y+2,540,b,27,FG,g=j+1)
        s.image(950,410,570,321,'assets/motion/robot-fault.gif',motion=True)
        s.text(80,715,1430,slide['takeaway'],25,MUTED,g=3)
    return s

def color_fill(shape,color,alpha=1):
    shape.fill.solid();shape.fill.fore_color.rgb=RGBColor.from_string(color)
    if alpha!=1:
        rgb=shape.fill._xPr.solidFill.srgbClr
        a=OxmlElement('a:alpha');a.set('val',str(int(alpha*100000)));rgb.append(a)

def pptx(root,slides,scenes,animated):
    prs=Presentation();prs.slide_width=Inches(16);prs.slide_height=Inches(9)
    prs.core_properties.author='Torin van den Bulk';prs.core_properties.title='Three Years in Thirty Minutes: Time-Travel Ethics Evaluation for AI Agents'
    prs.core_properties.subject='14-slide main talk with three hidden appendices'
    prs.core_properties.last_modified_by='Torin van den Bulk'
    prs.core_properties.comments='Agentic ethics evaluation: scenario, consequences and evidence.'
    prs.core_properties.created=prs.core_properties.modified=datetime.now(timezone.utc)
    for i,(content,sc) in enumerate(zip(slides,scenes)):
        slide=prs.slides.add_slide(prs.slide_layouts[6]);slide.background.fill.solid();slide.background.fill.fore_color.rgb=RGBColor.from_string(BG)
        if i>=14:slide._element.set('show','0')
        groups=defaultdict(list)
        for e in sc.elements:
            x,y,w,h=[Inches(e[k]/100) for k in ('x','y','w','h')]
            if e['type']=='text':
                shape=slide.shapes.add_textbox(x,y,w,h);tf=shape.text_frame;tf.word_wrap=False
                tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
                for j,line in enumerate(e['text'].split('\n')):
                    p=tf.paragraphs[0] if j==0 else tf.add_paragraph();p.text=line
                    p.font.name={'sans':'Nimbus Sans','mono':'Nimbus Mono PS','display':'Nimbus Sans Narrow'}[e['face']]
                    p.font.size=Pt(e['size']*.72);p.font.bold=e['face']=='display' or e.get('bold',False)
                    p.font.color.rgb=RGBColor.from_string(e['color']);p.space_before=p.space_after=Pt(0);p.line_spacing=1.16
            elif e['type']=='rect':
                shape=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,x,y,w,h);color_fill(shape,e['color'],e['alpha'])
                if e.get('line'):shape.line.color.rgb=RGBColor.from_string(e['line']);shape.line.width=Pt(.8)
                else:shape.line.fill.background()
            elif e['type']=='line':
                shape=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,x,y,x+w,y+h);shape.line.color.rgb=RGBColor.from_string(e['color']);shape.line.width=Pt(e['thick']*.72)
            else:
                path=root/e['file']
                if e.get('motion') and not animated:path=path.with_suffix('.png')
                shape=slide.shapes.add_picture(str(path),x,y,w,h)
                # CSS object-fit: cover equivalent. Do not stretch source photographs.
                iw,ih=Image.open(path).size;ratio=(e['w']/e['h'])/(iw/ih)
                if ratio<1:shape.crop_left=shape.crop_right=(1-ratio)/2
                elif ratio>1:shape.crop_top=shape.crop_bottom=(1-1/ratio)/2
                shape._element.nvPicPr.cNvPr.set('descr',('Animated diagnostic schematic, not measured data' if e.get('motion') else 'Existing city artwork; see assets/images.json'))
            if e.get('group'):groups[e['group']].append(shape.shape_id)
        transition=OxmlElement('p:transition');transition.set('spd','fast');transition.set('advClick','1');transition.append(OxmlElement('p:fade'));slide._element.append(transition)
        if animated:add_entrances(slide,[groups[k] for k in sorted(groups)])
        notes=content['notes']+'\n\nSources: '+', '.join(content.get('refs',[]))+'\nTiming: '+str(content['duration'])+' seconds.'
        if animated:notes+='\n\nPLAYBACK: use Slide Show (F5). Click once per evidence group. Embedded GIFs animate in supported PowerPoint versions; the static companion has all content visible. Diagnostics are illustrative motion, not experimental data.'
        notes+='\n\nVisual sources: existing city artwork cropped from the Ghost in the Shell-themed collection recorded in assets/images.json. Exact inline references were not available as downloadable files. No Akira poster or generative artwork is included.'
        slide.notes_slide.notes_text_frame.text=notes
    prs.save(root/('three-years.pptx' if animated else 'three-years-static.pptx'))

def html_deck(root,slides,scenes):
    assets={}
    def asset(path):
        key=str(path)
        if key not in assets:assets[key]='asset'+str(len(assets))
        return assets[key]
    parts=[]
    for i,(content,sc) in enumerate(zip(slides,scenes)):
        bits=[]
        for e in sc.elements:
            typ=e['type'];g=e.get('group',0);attrs=f' class="element {typ}'+(' reveal' if g else '')+f'" data-group="{g}"'
            style=f'left:{e["x"]}px;top:{e["y"]}px;width:{e["w"]}px;height:{max(1,e["h"])}px;'
            if typ=='text':
                style+=f'font-family:{e["face"]};font-size:{e["size"]}px;color:#{e["color"]};'
                bits.append(f'<div{attrs} style="{style}">{html.escape(e["text"])}</div>')
            elif typ=='rect':
                style+=f'background:#{e["color"]};opacity:{e["alpha"]};'
                if e.get('line'):style+='border:1px solid #'+e['line']+';'
                bits.append(f'<div{attrs} style="{style}"></div>')
            elif typ=='line':
                length=math.hypot(e['w'],e['h']);angle=math.degrees(math.atan2(e['h'],e['w']))
                style=f'left:{e["x"]}px;top:{e["y"]}px;width:{length}px;height:{e["thick"]}px;background:#{e["color"]};transform:rotate({angle}deg);transform-origin:0 0;'
                bits.append(f'<div{attrs} style="{style}"></div>')
            else:
                key=asset(root/e['file']);still=asset((root/e['file']).with_suffix('.png')) if e.get('motion') else key
                bits.append(f'<img{attrs} style="{style}object-fit:cover" data-asset="{key}" data-still="{still}" data-motion="{str(e.get("motion",False)).lower()}" alt="'+('Diagnostic animation' if e.get('motion') else 'City landscape')+'">')
        parts.append(f'<section class="slide" data-index="{i}" aria-label="{html.escape(content["title"])}">'+''.join(bits)+'</section>')
    fonts=''.join(f'@font-face{{font-family:{face};src:url("{uri(root/"assets/fonts"/filename)}")}}' for face,filename in FONT.items())
    css=fonts+(root/'deck.css').read_text()
    data={value:uri(Path(path)) for path,value in assets.items()}
    js='const slides='+json.dumps(slides).replace('</','<\\/')+';const assets='+json.dumps(data)+';'+(root/'deck.js').read_text()
    doc='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Three Years in Thirty Minutes</title><style>'+css+'</style></head><body><main id="stage">'+''.join(parts)+'</main><aside id="notes"></aside><nav><button onclick="previous()">←</button><button onclick="next()">→</button><button onclick="toggleNotes()">Notes</button><button onclick="toggleMotion()">Motion</button><button onclick="appendix()">Appendix</button><button onclick="full()">Fullscreen</button></nav><script>'+js+'</script></body></html>'
    (root/'three-years.html').write_text(doc)

def render(root,slides):
    scenes=[scene(s,i) for i,s in enumerate(slides)]
    (root/'scene-layout.json').write_text(json.dumps([s.elements for s in scenes],indent=2)+'\n')
    pptx(root,slides,scenes,True);pptx(root,slides,scenes,False);html_deck(root,slides,scenes)
    notes=['# Rehearsal guide — 14-slide main talk',f"Main talk: {sum(s['duration'] for s in slides)/60:.2f} minutes, including a three-minute demo. Three appendices are hidden in PowerPoint.",
    'PowerPoint: open three-years.pptx and start Slide Show (F5). Native entrance effects reveal one evidence group per click. The embedded GIF console, neon circuit, logical clock and robotic fault schematic animate inside supported PowerPoint slideshow players. Editing view and PDF are static. three-years-static.pptx is the all-visible, low-motion fallback.',
    'Browser: Right/Space reveals a group or advances; Left returns; A reveals all; N toggles notes; M toggles motion; R opens the appendix; Home returns to the opening; End goes to the main closing. The deck is entirely offline.',
    'The motion is hand-coded UI and diagram animation, not measured agent behavior. Existing city artwork provides atmosphere. No Akira poster or generated anime illustration is included. Image provenance and crops are recorded in assets/images.json.',
    'Torin van den Bulk · Vicente Herrera']
    for i,s in enumerate(slides):notes += [f'## {i+1:02d}. '+s['title'].replace('\n',' '),(f"{s['duration']} seconds | "+', '.join(s.get('refs',[]))).rstrip(' |'),s['notes']]
    (root/'speaker-notes.md').write_text('\n\n'.join(notes)+'\n')
    print('Built: 14 main slides + 3 hidden appendices; animated PPTX + static PPTX + HTML.')
