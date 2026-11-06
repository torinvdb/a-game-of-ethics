"""PresentationML timing (p:timing) for native PowerPoint animations.

A slide's steps are lists of effects. The first step may start on slide entry;
each later step is one click.

  fade     visibility set + fade filter (Entrance/Fade, preset 10)
  wipe     visibility set + wipe(left) (Entrance/Wipe, preset 22)
  flicker  visibility toggles at 0/70/140/200/320 ms, then fade (custom, on Appear)
  path     relative motion path, repeatCount=indefinite (custom Motion Path)

Validated by python-pptx round trip and LibreOffice import. Microsoft PowerPoint
playback is untested.
"""
from lxml import etree
from pptx.oxml.ns import qn

P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
SLIDE_W = 1600.0  # scene units


def add_timeline(slide, steps, first_auto=False):
    steps = [s for s in steps if s]
    if not steps:
        return
    counter = [0]

    def nid():
        counter[0] += 1
        return str(counter[0])

    def el(parent, tag, **attrs):
        node = etree.SubElement(parent, '{%s}%s' % (P, tag))
        for k, v in attrs.items():
            node.set(k, str(v))
        return node

    def target(parent, spid):
        el(el(parent, 'tgtEl'), 'spTgt', spid=spid)

    def setvis(parent, spid, value, delay):
        s = el(parent, 'set')
        b = el(s, 'cBhvr')
        ctn = el(b, 'cTn', id=nid(), dur='1', fill='hold')
        el(el(ctn, 'stCondLst'), 'cond', delay=delay)
        target(b, spid)
        el(el(b, 'attrNameLst'), 'attrName').text = 'style.visibility'
        el(el(s, 'to'), 'strVal', val=value)

    def filt(parent, spid, filter_, dur, delay=0):
        e = el(parent, 'animEffect', transition='in', filter=filter_)
        b = el(e, 'cBhvr')
        ctn = el(b, 'cTn', id=nid(), dur=dur)
        if delay:
            el(el(ctn, 'stCondLst'), 'cond', delay=delay)
        target(b, spid)

    timing = etree.Element(qn('p:timing'))
    root = el(el(el(timing, 'tnLst'), 'par'), 'cTn', id=nid(), dur='indefinite', restart='never', nodeType='tmRoot')
    seq = el(el(root, 'childTnLst'), 'seq', concurrent='1', nextAc='seek')
    main = el(seq, 'cTn', id=nid(), dur='indefinite', nodeType='mainSeq')
    main_id = main.get('id')
    lst = el(main, 'childTnLst')
    for si, step in enumerate(steps):
        auto = first_auto and si == 0
        outer = el(el(lst, 'par'), 'cTn', id=nid(), fill='hold')
        conds = el(outer, 'stCondLst')
        el(conds, 'cond', delay='indefinite')
        if auto:
            c = el(conds, 'cond', evt='onBegin', delay='0')
            el(c, 'tn', val=main_id)
        inner = el(el(el(outer, 'childTnLst'), 'par'), 'cTn', id=nid(), fill='hold')
        el(el(inner, 'stCondLst'), 'cond', delay='0')
        effects = el(inner, 'childTnLst')
        for j, fx in enumerate(step):
            anim = fx['anim']
            node_type = ('afterEffect' if auto else 'clickEffect') if j == 0 else 'withEffect'
            preset = {'fade': ('10', 'entr', '0'), 'wipe': ('22', 'entr', '8'), 'flicker': ('1', 'entr', '0'),
                      'path': ('0', 'path', '0')}[anim]
            ctn = el(el(effects, 'par'), 'cTn', id=nid(), presetID=preset[0], presetClass=preset[1],
                     presetSubtype=preset[2], fill='hold', nodeType=node_type)
            el(el(ctn, 'stCondLst'), 'cond', delay=int(fx.get('delay', 0)))
            beh = el(ctn, 'childTnLst')
            spid = fx['id']
            if anim == 'fade':
                setvis(beh, spid, 'visible', 0)
                filt(beh, spid, 'fade', 450)
            elif anim == 'wipe':
                setvis(beh, spid, 'visible', 0)
                filt(beh, spid, 'wipe(left)', 520)
            elif anim == 'flicker':
                for d, v in ((0, 'visible'), (70, 'hidden'), (140, 'visible'), (200, 'hidden'), (320, 'visible')):
                    setvis(beh, spid, v, d)
                filt(beh, spid, 'fade', 260, delay=320)
            elif anim == 'path':
                setvis(beh, spid, 'visible', 0)
                dx = fx['dx'] / SLIDE_W
                m = el(beh, 'animMotion', origin='layout', path=f'M 0 0 L {dx:.4f} 0 E', pathEditMode='relative',
                       ptsTypes='AA')
                b = el(m, 'cBhvr')
                ctn2 = el(b, 'cTn', id=nid(), dur=int(fx.get('dur', 3000)), fill='hold', repeatCount='indefinite')
                el(el(ctn2, 'stCondLst'), 'cond', delay=300)
                target(b, spid)
                names = el(b, 'attrNameLst')
                el(names, 'attrName').text = 'ppt_x'
                el(names, 'attrName').text = 'ppt_y'
    for name, evt in (('prevCondLst', 'onPrev'), ('nextCondLst', 'onNext')):
        c = el(el(seq, name), 'cond', evt=evt, delay='0')
        el(el(c, 'tgtEl'), 'sldTgt')
    # Schema order: cSld, clrMapOvr, transition, timing, extLst
    ext = slide._element.find(qn('p:extLst'))
    if ext is not None:
        ext.addprevious(timing)
    else:
        slide._element.append(timing)
