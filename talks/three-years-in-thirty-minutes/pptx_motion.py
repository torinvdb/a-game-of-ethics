"""Native PowerPoint click-sequence entrance animations (PresentationML).

All content is editable. Each group is one presenter click; members appear
simultaneously. GIF motion is separately embedded as ordinary picture media.
"""
from lxml import etree
from pptx.oxml.ns import qn

P='http://schemas.openxmlformats.org/presentationml/2006/main'

def add_entrances(slide, groups):
    groups=[g for g in groups if g]
    if not groups:return
    seqid=0
    def nid():
        nonlocal seqid
        seqid+=1;return str(seqid)
    def el(parent,tag,**attrs):
        node=etree.SubElement(parent,'{%s}%s'%(P,tag));node.attrib.update({k:str(v) for k,v in attrs.items()});return node
    def target(parent,shape_id):
        tgt=el(parent,'tgtEl');el(tgt,'spTgt',spid=shape_id)
    timing=etree.Element(qn('p:timing'))
    tn=el(timing,'tnLst');par=el(tn,'par')
    root=el(par,'cTn',id=nid(),dur='indefinite',restart='never',nodeType='tmRoot')
    children=el(root,'childTnLst');seq=el(children,'seq',concurrent='1',nextAc='seek')
    main=el(seq,'cTn',id=nid(),dur='indefinite',nodeType='mainSeq')
    steps=el(main,'childTnLst')
    for group in groups:
        outer=el(steps,'par');outer_tn=el(outer,'cTn',id=nid(),fill='hold')
        starts=el(outer_tn,'stCondLst');el(starts,'cond',delay='indefinite')
        outer_children=el(outer_tn,'childTnLst')
        inner=el(outer_children,'par');inner_tn=el(inner,'cTn',id=nid(),fill='hold')
        starts=el(inner_tn,'stCondLst');el(starts,'cond',delay='0')
        effects=el(inner_tn,'childTnLst')
        for j,shape_id in enumerate(group):
            effect=el(effects,'par')
            effect_tn=el(effect,'cTn',id=nid(),presetID='10',presetClass='entr',presetSubtype='0',fill='hold',nodeType='clickEffect' if j==0 else 'withEffect')
            starts=el(effect_tn,'stCondLst');el(starts,'cond',delay='0')
            behaviors=el(effect_tn,'childTnLst')
            setnode=el(behaviors,'set');behavior=el(setnode,'cBhvr')
            el(behavior,'cTn',id=nid(),dur='1',fill='hold');target(behavior,shape_id)
            attrs=el(behavior,'attrNameLst');el(attrs,'attrName').text='style.visibility'
            to=el(setnode,'to');el(to,'strVal',val='visible')
            fade=el(behaviors,'animEffect',transition='in',filter='fade')
            behavior=el(fade,'cBhvr');el(behavior,'cTn',id=nid(),dur='400');target(behavior,shape_id)
    for name,event in [('prevCondLst','onPrev'),('nextCondLst','onNext')]:
        conds=el(seq,name);cond=el(conds,'cond',evt=event,delay='0');tgt=el(cond,'tgtEl');el(tgt,'sldTgt')
    # Schema order: cSld, clrMapOvr, transition, timing, extLst.
    ext=slide._element.find(qn('p:extLst'))
    if ext is not None:slide._element.insert(list(slide._element).index(ext),timing)
    else:slide._element.append(timing)
