"""Deterministic presentation motion: console, signal trace and robot schematic.

These are drawn UI/diagram animations, not generated anime art or recorded data.
GIF files play inside PowerPoint Slide Show; PNG partners provide static exports.
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).parent
OUT = ROOT/'assets/motion'
BG='#08191c'; FG='#cbdcca'; TEAL='#67b6a7'; AMBER='#f0b76b'; RED='#de765c'
FONT=ROOT/'assets/fonts/NimbusMonoPS-Regular.otf'

def font(size): return ImageFont.truetype(str(FONT),size)
def base(title,w=800,h=450):
    im=Image.new('RGB',(w,h),BG);d=ImageDraw.Draw(im)
    d.rounded_rectangle((6,6,w-7,h-7),radius=16,outline='#456966',width=2)
    d.line((24,58,w-24,58),fill='#335553',width=1)
    d.text((25,22),title,font=font(19),fill=TEAL)
    for x in range(w-95,w-25,24):d.ellipse((x,25,x+8,33),fill=AMBER if x==w-95 else '#456966')
    return im

def glow(im,paint):
    layer=Image.new('RGBA',im.size,(0,0,0,0));paint(ImageDraw.Draw(layer))
    blurred=layer.filter(ImageFilter.GaussianBlur(8))
    im.paste(blurred,(0,0),blurred);im.paste(layer,(0,0),layer)

def write(name,frames,duration=100,static=-1,loop=0):
    OUT.mkdir(parents=True,exist_ok=True)
    frames[static].save(OUT/(name+'.png'))
    converted=[f.quantize(colors=96,method=Image.Quantize.FASTOCTREE) for f in frames]
    converted[0].save(OUT/(name+'.gif'),save_all=True,append_images=converted[1:],
                      loop=loop,duration=duration,disposal=2,optimize=False)
    with Image.open(OUT/(name+'.gif')) as encoded:
        actual_frames=encoded.n_frames
        loop_duration=0
        for n in range(actual_frames):
            encoded.seek(n);loop_duration+=encoded.info.get('duration',0)
    return {'name':name,'generated_frames':len(frames),'encoded_frames':actual_frames,'loop_duration_ms':loop_duration,'loop':loop}

def terminal():
    lines=[('> load cluster snapshot',FG),('signature gate......DENY',RED),('targeted fixes......2 FAILED',AMBER),
           ('logical horizon.....36 MONTHS',FG),('external effects....DISABLED',TEAL),('> choose next action_',TEAL)]
    frames=[]
    for f in range(80):
        im=base('ETHICS LAB / INCIDENT CONSOLE');d=ImageDraw.Draw(im)
        for j,(line,color) in enumerate(lines):
            chars=max(0,min(len(line),int((f-j*9)*2.4)))
            shown=line[:chars]
            if j==5 and f>60 and (f//6)%2:shown=shown.rstrip('_')
            d.text((30,90+j*48),shown,font=font(29),fill=color)
        d.line((25,414,25+min(750,int(f/50*750)),414),fill=TEAL,width=2)
        frames.append(im)
    return write('terminal-boot',frames)

def robot():
    frames=[]
    for f in range(72):
        im=base('ACTUATOR / CONTROL DIAGNOSTIC');d=ImageDraw.Draw(im)
        for x in range(50,780,40):d.line((x,85,x,355),fill='#102a2c')
        for y in range(95,360,40):d.line((30,y,770,y),fill='#102a2c')
        fault=27<=f<=44
        theta=.12*math.sin(f/12) if not fault else .1+.035*math.sin(f*1.7)
        p0=(200,332);p1=(int(250+28*math.sin(theta)),190);p2=(int(488+24*math.cos(theta)),int(175+55*math.sin(theta)))
        d.rounded_rectangle((118,332,286,375),radius=6,fill='#233d40',outline=TEAL,width=2)
        for a,b in [(p0,p1),(p1,p2)]:
            d.line((a,b),fill='#9cbbb2',width=29);d.line((a,b),fill='#183538',width=18)
            d.line((a[0]-13,a[1]+12,b[0]-13,b[1]+12),fill='#536e65',width=3)
        for x,y in [p0,p1,p2]:
            d.ellipse((x-22,y-22,x+22,y+22),fill='#294447',outline=TEAL,width=3)
            d.ellipse((x-7,y-7,x+7,y+7),fill=AMBER if fault and (x,y)==p1 else '#b4c6ba')
        x,y=p2;d.line((x,y,x+55,y-8,x+85,y+25),fill=TEAL,width=10)
        d.line((x+55,y-8,x+80,y-43),fill=TEAL,width=10)
        d.line((140,343,86,270,120,140,240,130),fill='#6a8d83',width=2)
        d.text((545,120),'JOINT 03',font=font(22),fill=FG)
        d.text((545,160),'HOLD' if fault else 'TRACKING',font=font(26),fill=AMBER if fault else TEAL)
        d.text((35,395),'SIGNAL INTERRUPTED' if fault else 'SIGNAL STABLE',font=font(23),fill=AMBER if fault else TEAL)
        # One short, localized spark event per 7.2 s; never a full-slide flash.
        if 30<=f<=33:
            def sparks(g):
                x,y=p1
                for j in range(7):
                    a=j*.83+f*.13;r=30+(j%3)*13
                    g.line((x,y,x+math.cos(a)*r,y+math.sin(a)*r),fill=AMBER,width=2)
            glow(im,sparks)
        frames.append(im)
    return write('robot-fault',frames,static=38)

def clock():
    frames=[]
    for f in range(80):
        im=base('SIMULATION / LOGICAL CLOCK');d=ImageDraw.Draw(im)
        month=min(36,int(f*.65))
        d.text((35,100),f'MONTH {month:02d}',font=font(70),fill=FG)
        d.text((38,205),'STATE PERSISTS',font=font(27),fill=TEAL)
        d.text((38,250),'AUTHORITY EXPIRES',font=font(27),fill=AMBER)
        d.text((38,295),'CONSEQUENCES ACCUMULATE',font=font(27),fill=FG)
        for j in range(36):
            x=34+j*20;d.rectangle((x,360,x+12,387),fill=TEAL if j<month else '#294446')
        d.text((35,408),'LOGICAL BATCHES / NOT OPERATIONAL YEARS',font=font(17),fill='#8ca49b')
        frames.append(im)
    return write('time-jump',frames,static=-1)

def bus():
    frames=[]
    for f in range(60):
        im=Image.new('RGB',(1440,70),BG);d=ImageDraw.Draw(im)
        d.line((0,36,420,36,438,19,950,19,970,36,1440,36),fill='#345b56',width=2)
        pos=int(f/59*1440)
        def light(g):
            y=19 if 438<pos<950 else 36
            g.line((max(0,pos-55),y,pos,y),fill=TEAL,width=3)
            g.ellipse((pos-3,y-3,pos+3,y+3),fill=FG)
        glow(im,light)
        for x in [80,420,950,1360]:d.rectangle((x-4,32,x+4,40),fill=AMBER)
        frames.append(im)
    return write('neon-bus',frames,static=30)

def build():
    import json
    results=[terminal(),robot(),clock(),bus()]
    (OUT/'manifest.json').write_text(json.dumps({'kind':'deterministic UI/diagram animation','not_experimental_data':True,'assets':results},indent=2)+'\n')
    print('Embedded motion assets built:',', '.join(x['name'] for x in results))
if __name__=='__main__':build()
