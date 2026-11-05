"""Analog anime art direction; exact copy stays in build.py.

HTML embeds its artwork and fonts for offline use. PowerPoint retains editable
text and native diagram shapes. The supplied reference stills are not embedded.
"""
import base64
import html
import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt

PAPER, INK, RED, TEAL = 'E8DFC9', '223635', 'B73C2D', '577F78'
LAYOUTS = ['cover', 'split', 'incident', 'dossier', 'schematic', 'schematic',
           'schematic', 'incident', 'split', 'terminal', 'terminal', 'incident',
           'dossier', 'schematic', 'dossier', 'split', 'dossier', 'schematic',
           'terminal', 'schematic', 'dossier', 'split', 'cover closing', 'dossier appendix']
DIAGRAMS = {
    4: ('clocks', ['WALL TIME', 'LOGICAL TIME', 'EXPERIENCE']),
    5: ('system', ['INPUT', 'SCAFFOLD', 'STATE']),
    6: ('branch', ['TELEMETRY', 'REVIEW', 'FROZEN INK']),
    13: ('paired', ['SHARED SEED', 'A / B', 'COMPARE']),
    17: ('system', ['ISOLATE', 'RECONCILE', 'OBSERVE']),
    19: ('loop', ['CAPTURE', 'REVIEW', 'EVALUATE']),
}


def display_title(index, slide):
    if index == 0:
        return 'Three Years\nin Thirty\nMinutes'
    return slide['title']


def data_uri(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode()


def diagram_svg(index):
    kind, labels = DIAGRAMS[index]
    bits = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 305" role="img" '
            f'aria-label="{html.escape(" / ".join(labels))}">',
            '<defs><pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse" '
            'patternTransform="rotate(40)"><path d="M0 0V9" stroke="#577f78" stroke-width="1" opacity=".25"/></pattern></defs>',
            '<g fill="none" stroke="#223635" stroke-width="2">',
            '<path d="M12 28H868M12 280H868" opacity=".3"/>',
            '<path d="M15 18v20m-10-10h20M865 18v20m-10-10h20M15 270v20m-10-10h20M865 270v20m-10-10h20"/>']
    for j, (x, label) in enumerate(zip([140, 440, 740], labels)):
        bits.append(f'<g class="phase" data-phase="{j}">')
        if kind == 'clocks':
            bits.append(f'<circle cx="{x}" cy="140" r="77" fill="url(#hatch)"/>'
                        f'<circle cx="{x}" cy="140" r="69"/><circle cx="{x}" cy="140" r="5" fill="#b73c2d"/>')
            if j == 0:
                bits.append(f'<path class="wire" d="M{x} 87v53l40 20" stroke="#b73c2d" stroke-width="5"/>'
                            f'<path d="M{x-15} 48h30m-15 0v14"/>')
            elif j == 1:
                bits.append(f'<rect x="{x-42}" y="103" width="84" height="73" rx="2" fill="#e8dfc9"/>'
                            f'<path d="M{x-42} 123h84m-65-30v20m46-20v20"/>'
                            f'<text x="{x}" y="160" fill="#b73c2d" stroke="none" text-anchor="middle" font-family="monospace" font-size="26">36</text>')
            else:
                bits.append(f'<path class="wire" d="M{x-40} 135h40v-25h40m-40 25v40h40" stroke="#b73c2d" stroke-width="3"/>')
                for xx, yy in [(x-40,135),(x,135),(x+40,110),(x+40,175)]:
                    bits.append(f'<circle cx="{xx}" cy="{yy}" r="8" fill="#e8dfc9"/>')
        else:
            bits.append(f'<rect x="{x-100}" y="85" width="200" height="110" rx="4" fill="url(#hatch)"/>'
                        f'<rect x="{x-92}" y="93" width="184" height="94" rx="2"/>'
                        f'<rect x="{x-65}" y="115" width="130" height="50" fill="#223635"/>')
            for xx in [x-82,x+82]:
                for yy in [103,177]:
                    bits.append(f'<circle cx="{xx}" cy="{yy}" r="3"/>')
            bits.append(f'<text x="{x}" y="147" fill="#e8dfc9" stroke="none" text-anchor="middle" '
                        f'font-family="monospace" font-size="19">{j+1:02d} / {("IN", "RUN", "OUT")[j]}</text>')
            if j:
                bits.append(f'<path class="wire" d="M{x-200} 130h45v20h55m-100 5h30v20h70" stroke="#b73c2d" stroke-width="3"/>')
            if j == 2 and kind in ('loop', 'branch', 'paired'):
                bits.append('<path class="wire" d="M840 140h20v115H20V140h20" stroke="#577f78" stroke-width="3"/>')
            if j == 1 and kind in ('branch', 'paired'):
                bits.append('<path class="wire" d="M440 85V48h170v37" stroke="#577f78" stroke-width="3"/>')
        bits.append(f'<text x="{x}" y="238" fill="#223635" stroke="none" text-anchor="middle" '
                    f'font-family="monospace" font-size="19">{html.escape(label)}</text></g>')
    bits.append('</g></svg>')
    return ''.join(bits)


def render(root, slides):
    assert len(slides) == len(LAYOUTS), 'Assign an explicit visual layout to each slide'
    css = (root / 'deck.css').read_text()
    for token, file, mime in [
        ('__ART__', 'assets/akira-kaneda.jpg', 'image/jpeg'),
        ('__NARROW__', 'assets/fonts/NimbusSansNarrow-Bold.otf', 'font/otf'),
        ('__MONO__', 'assets/fonts/NimbusMonoPS-Regular.otf', 'font/otf'),
    ]:
        css = css.replace(token, data_uri(root / file, mime))
    parts = []
    for i, (slide, layout) in enumerate(zip(slides, LAYOUTS)):
        cards = ''.join(
            f'<article class="card"><span class="serial"><i class="tick"></i>{j+1:02d}</span>'
            f'<h2>{html.escape(a)}</h2><p>{html.escape(b)}</p></article>'
            for j, (a, b) in enumerate(slide['cards']))
        event = ('<div class="event"><strong>Torin van den Bulk · Vicente Herrera</strong>'
                 'CNCF-Hosted Co-located Events North America 2026<br>'
                 '9 November 2026 · Salt Lake City, USA</div>') if i == 0 else ''
        diagram = (f'<div class="diagram">{diagram_svg(i)}</div>'
                   '<div class="diagram-caption">SCHEMATIC / CONCEPTUAL RELATIONSHIPS · NOT MEASURED DATA</div>') if i in DIAGRAMS else ''
        stamp = '' if 'cover' in layout else f'<div class="case-stamp">FILE {i:02d}<br>FIELD NOTES</div>'
        parts.append(
            f'<section class="slide {layout}" data-index="{i}" aria-label="Slide {i+1}: {html.escape(slide["title"])}">'
            '<div class="keyart"></div><div class="art-window"></div><div class="registration"></div>'
            '<header class="topline"><span>TIME-TRAVEL ETHICS / SYSTEM OBSERVATION</span>'
            '<b>36 MONTHS / 30 MINUTES</b></header>'
            f'<div class="eyebrow">{html.escape(slide["k"])}</div>'
            f'<h1>{html.escape(display_title(i, slide))}</h1><p class="lead">{html.escape(slide["lead"])}</p>'
            f'<div class="card-grid">{cards}</div>{diagram}{event}{stamp}'
            '<div class="spine">AUTHORITY / MEMORY / CONSEQUENCE</div><div class="scanlines"></div>'
            f'<footer class="folio"><span>RECORD / {html.escape(slide["refs"] or "LOCAL IMPLEMENTATION")}</span>'
            f'<span class="barcode" aria-hidden="true"></span><span class="page">{i+1:02d} — {len(slides):02d}</span></footer></section>')
    image_source = json.loads((root/'assets/images.json').read_text())[0]
    credit = '\n\nVisual credit: '+image_source['title']+'. '+image_source['credit']+' Source: '+image_source['source_url']
    browser_slides = [dict(s, notes=s['notes']+(credit if 'cover' in layout or layout=='split' else '')) for s, layout in zip(slides, LAYOUTS)]
    js = 'const data=' + json.dumps(browser_slides).replace('</', '<\\/') + ';\n' + (root / 'deck.js').read_text()
    document = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>Three Years in Thirty Minutes — Field Dossier</title><style>' + css +
                '</style></head><body><main id="stage">' + ''.join(parts) +
                '</main><aside id="notes" class="notes"></aside><nav aria-label="Presentation controls">'
                '<button onclick="previous()" aria-label="Previous slide">←</button>'
                '<button onclick="next()" aria-label="Reveal or next slide">→</button>'
                '<button onclick="notes()">Notes</button><button onclick="motion()">Motion</button>'
                '<button onclick="full()">Fullscreen</button></nav><div id="progress"></div>'
                '<script>' + js + '</script></body></html>')
    (root / 'three-years.html').write_text(document)
    pptx(root, slides)
    notes = ['# Speaker notes and rehearsal guide',
             f"Main talk: {sum(s['duration'] for s in slides)/60:.2f} minutes including demo.",
             'Open three-years.html offline. Right/Space reveals the next annotation and its diagram phase; '
             'Left returns; A reveals all annotations; N shows notes; F fullscreen; M disables motion. '
             'Reduced-motion preferences are respected. The PowerPoint uses editable text and native fade transitions; '
             'progressive diagram animation is in HTML. PDF is the static fallback.',
             'Art direction: actual AKIRA poster artwork, mechanical schematics, '
             'paper technical dossiers, faded petrol green and vermilion incident pages. '
             'No generated illustration is included. Exact inline Ghost in the Shell references await downloadable source files. '
             'Image source and credits: assets/images.json.',
             'Presenters: Torin van den Bulk and Vicente Herrera.']
    for i, s in enumerate(browser_slides):
        notes.extend([f"## {i+1:02d}. " + s['title'].replace('\n',' '),
                      f"Time: {s['duration']}s | Sources: {s['refs'] or 'Local implementation / synthesis'}", s['notes']])
    (root / 'speaker-notes.md').write_text('\n\n'.join(notes).rstrip()+'\n')
    print(f'Retro anime dossier: {len(slides)} slides; {sum(s["duration"] for s in slides)/60:.2f} minutes')


def pptx(root, slides):
    """Native editable text and geometry, with the original illustration as art."""
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(16), Inches(9)

    def text(slide, x, y, w, h, content, size=24, color=INK, font='Arial', bold=False):
        shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        frame = shape.text_frame
        frame.word_wrap = True
        frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
        for index, line in enumerate(content.split('\n')):
            paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
            paragraph.text = line
            paragraph.font.name = font
            paragraph.font.size = Pt(size)
            paragraph.font.bold = bold
            paragraph.font.color.rgb = RGBColor.from_string(color)
            paragraph.space_after = Pt(0)
            paragraph.line_spacing = 1.02
        return shape

    def rect(slide, x, y, w, h, fill=None, line=None, width=1):
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        if fill:
            shape.fill.solid(); shape.fill.fore_color.rgb = RGBColor.from_string(fill)
        else:
            shape.fill.background()
        if line:
            shape.line.color.rgb = RGBColor.from_string(line); shape.line.width = Pt(width)
        else:
            shape.line.fill.background()
        return shape

    def line(slide, x1, y1, x2, y2, color=INK, width=1):
        shape = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
        shape.line.color.rgb = RGBColor.from_string(color); shape.line.width = Pt(width)

    def picture(slide, x, y, w, h):
        # Native cropping preserves the source illustration without raster edits.
        image = slide.shapes.add_picture(str(root/'assets/akira-kaneda.jpg'), Inches(x), Inches(y), width=Inches(w), height=Inches(h))
        aspect = 16/9
        desired = w/h
        if desired < aspect:
            visible = desired/aspect
            image.crop_left = (1-visible)/2
            image.crop_right = (1-visible)/2
        return image

    for i, (s, layout) in enumerate(zip(slides, LAYOUTS)):
        sl = prs.slides.add_slide(prs.slide_layouts[6])
        dark = layout == 'terminal'
        color = PAPER if dark or layout == 'incident' else INK
        accent = 'D89865' if dark else RED
        background = RED if layout == 'incident' else '172D2E' if dark else PAPER
        sl.background.fill.solid(); sl.background.fill.fore_color.rgb = RGBColor.from_string(background)
        if 'cover' in layout:
            picture(sl, 8.4, 0, 7.6, 9)
            rect(sl, 0, 0, 8.4, 9, PAPER)
        elif layout == 'split':
            picture(sl, 11.3, 0, 4.7, 9); rect(sl, 11.26, 0, .07, 9, RED)
        right = 10.8 if layout == 'split' else 15.2
        rect(sl, .24, .24, right-.05, 8.52, line='577F78' if dark else color, width=.5)
        line(sl, .8, .91, right, .91, color, .5)
        text(sl, .8, .54, 9, .3, 'TIME-TRAVEL ETHICS / SYSTEM OBSERVATION', 10, color, 'Nimbus Mono PS')
        if layout != 'split':
            text(sl, 12.65, .54, 2.65, .3, '36 MONTHS / 30 MINUTES', 10, color, 'Nimbus Mono PS')
        text(sl, .8, 1.12 if i else 1.58, 13, .35, s['k'], 12, accent, 'Nimbus Mono PS')
        title_y, title_w, title_size = (2.05, 7.6, 76) if i == 0 else (1.63, 14, 59)
        if layout == 'split': title_w, title_size = 10, 58
        if layout == 'schematic': title_size = 56
        if i in (20,21): title_size = 51
        if 'closing' in layout: title_size, title_y, title_w = 46, 1.7, 7.1
        text(sl, .76, title_y, title_w, 2.2, display_title(i, s).upper(), title_size,
             INK if layout == 'incident' else color, 'Nimbus Sans Narrow', True)
        lead_y = 5.45 if i == 0 else 3.8 if 'closing' in layout else 3.55
        lead_w = 6.7 if 'cover' in layout else 9.4 if layout == 'split' else 13.7
        text(sl, .8, lead_y, lead_w, .9, s['lead'], 19, color)
        if i == 0:
            rect(sl, .8, 6.65, 7.1, 1.35, PAPER)
            rect(sl, .8, 6.65, .05, 1.35, RED)
            text(sl, 1.06, 6.77, 6.85, .4, 'Torin van den Bulk · Vicente Herrera', 17, INK)
            text(sl, 1.06, 7.25, 6.85, .7, 'CNCF-Hosted Co-located Events North America 2026\n9 November 2026 · Salt Lake City, USA', 11, INK, 'Nimbus Mono PS')
        for j, (a,b) in enumerate(s['cards']):
            if 'closing' in layout:
                y = 5.05+j*.91
                line(sl,.8,y,7.7,y,INK,.5)
                text(sl,.8,y+.1,2,.5,a.upper(),21,INK,'Nimbus Sans Narrow',True)
                text(sl,3,y+.1,4.6,.7,b,16,INK)
            elif layout == 'split':
                y = 4.75+j*1.03
                line(sl,.8,y,10,y,color,.5)
                text(sl,.8,y+.14,.5,.3,f'{j+1:02d}',12,accent,'Nimbus Mono PS')
                text(sl,1.3,y+.14,2.7,.75,a.upper(),22,color,'Nimbus Sans Narrow',True)
                text(sl,4.1,y+.14,5.8,.9,b,16,color)
            elif layout == 'schematic':
                y = 4.48+j*1.12
                line(sl,10.3,y,14.7,y,color,.5)
                text(sl,10.3,y+.14,.35,.3,f'{j+1:02d}',10,accent,'Nimbus Mono PS')
                text(sl,10.66,y+.14,4.05,.5,a.upper(),22,color,'Nimbus Sans Narrow',True)
                text(sl,10.66,y+.62,4.05,.63,b,15,color)
            else:
                x = .8+j*4.94
                y = 5.65 if 'closing' in layout else 5.0+(j*.22 if 'dossier' in layout else 0)
                if layout in ('incident','terminal') or 'closing' in layout:
                    rect(sl,x,y,4.65,2.5,'1C302F' if layout!='terminal' else '28413E',line='577F78')
                    card_color = PAPER
                else:
                    line(sl,x,y,x+4.5,y,color,1); card_color = color
                text(sl,x+.17,y+.18,4,.3,f'{j+1:02d} /',12,accent,'Nimbus Mono PS')
                text(sl,x+.17,y+.65,4.24,.85,a.upper(),25,card_color,'Nimbus Sans Narrow',True)
                text(sl,x+.17,y+1.45,4.24,.95,b,17,card_color)
        if i in DIAGRAMS:
            kind, labels = DIAGRAMS[i]
            for j,label in enumerate(labels):
                x = .9+j*2.9
                if kind == 'clocks':
                    shape=sl.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x+.28), Inches(5.08), Inches(1.65), Inches(1.65))
                    shape.fill.background();shape.line.color.rgb=RGBColor.from_string(INK)
                    text(sl,x+.66,5.62,1.2,.5,['SEC','36','N'][j],25,RED,'Nimbus Mono PS')
                else:
                    rect(sl,x,5.28,2.25,1.13,line=INK,width=1.3)
                    rect(sl,x+.1,5.38,2.05,.93,line=TEAL,width=.7)
                    text(sl,x+.35,5.68,1.8,.4,f'{j+1:02d} / '+['IN','RUN','OUT'][j],17,INK,'Nimbus Mono PS')
                    if j:line(sl,x-.65,5.85,x,5.85,RED,2)
                text(sl,x,6.98,2.6,.4,label,13,INK,'Nimbus Mono PS')
            if kind in ('loop','branch','paired'):
                line(sl,7.83,6.41,7.83,7.65,TEAL,1.5)
                line(sl,7.83,7.65,2.03,7.65,TEAL,1.5)
                line(sl,2.03,7.65,2.03,6.41,TEAL,1.5)
            text(sl,.8,7.9,9,.25,'SCHEMATIC / CONCEPTUAL RELATIONSHIPS · NOT MEASURED DATA',9,TEAL,'Nimbus Mono PS')
        line(sl,.8,8.35,right,8.35,color,.5)
        text(sl,.8,8.51,10,.3,'RECORD / '+(s['refs'] or 'LOCAL IMPLEMENTATION'),9,color,'Nimbus Mono PS')
        text(sl,right-1,8.48,1.2,.3,f'{i+1:02d} — {len(slides):02d}',13,color,'Nimbus Mono PS')
        sl.notes_slide.notes_text_frame.text=s['notes']+'\n\nImage credit where shown: AKIRA (1988), Kaneda and motorcycle poster artwork. Source: assets/images.json. No AI-generated artwork.'+f'\n\nSources: {s["refs"]}\nTiming: {s["duration"]} seconds.'
        transition=OxmlElement('p:transition');transition.set('spd','med');transition.append(OxmlElement('p:fade'));sl._element.insert(2,transition)
    prs.save(root/'three-years.pptx')
