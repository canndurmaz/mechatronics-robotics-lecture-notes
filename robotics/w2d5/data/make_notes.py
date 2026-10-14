#!/usr/bin/env python3
"""Builds w2d5_speaker_notes.html from notes_content.py, frame titles of w2d5.tex and the PDF page map."""
import re, os, subprocess, html, sys
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(D)
sys.path.insert(0, D)
from notes_content import S
MIN = {  # minute overrides (index -> minutes) so that every session sums to 60
}
tex = open(os.path.join(R, 'w2d5.tex')).read()
body = tex[tex.index(r'\begin{document}'):]
# walk sections and frames in order
items = []
for m in re.finditer(r'\\section\{([^}]*)\}|\\begin\{frame\}(?:\[[^\]]*\])?(?:\{((?:[^{}]|\{[^{}]*\})*)\})?', body):
    if m.group(1): items.append(('sec', m.group(1)))
    else: items.append(('frm', m.group(2) or 'Title page'))
# PDF page numbers: section dividers occupy one page each
page = 0; frames = []; secs = []; cur = 'intro'
for kind, t in items:
    page += 1
    if kind == 'sec': secs.append((t, page)); cur = t
    else: frames.append((page, t, cur))
assert len(frames) == len(S), (len(frames), len(S))
def clean(t):
    t = t.replace(r'\ ', ' ').replace('--', '–').replace(r'\&', '&').replace('~', ' ')
    t = re.sub(r'\$([^$]*)\$', lambda m: m.group(1).replace('_', '').replace('\\', ''), t)
    t = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', t)
    return t.replace('\\', '').replace('{', '').replace('}', '')
sessions = [('intro', 'Opening', '6.4')] + [(t, t.split(' ', 1)[1], t.split(' ', 1)[0]) for t, _ in secs]
# group
groups = {}
for (p, t, s), (m, say, em, ask, tr) in zip(frames, S):
    groups.setdefault(s, []).append((p, clean(t), m, say, em, ask, tr))
# merge intro into 6.4 block for timing
blocks = []
for i, (t, _) in enumerate(secs):
    fr = groups.get(t, [])
    if i == 0: fr = groups['intro'] + fr
    blocks.append((t, fr))
out = []
tpl = open(os.path.join(R, '..', '..', 'common', 'notes_template.html')).read()
style = tpl[tpl.index('<style>'):tpl.index('</style>') + 8]
nav = '<a href="#plan">Plan</a>' + ''.join(f'<a href="#s{i+1}">{html.escape(t)}</a>' for i, (t, _) in enumerate(blocks))
plan = ['<table class="plan"><tr><th>Block</th><th>Topic</th><th>Slides</th><th>Duration</th></tr>']
total = 0
for i, (t, fr) in enumerate(blocks):
    mins = sum(x[2] for x in fr); total += mins
    plan.append(f'<tr><td>{i+1}</td><td>{html.escape(t)}{" (incl. opening)" if i==0 else ""}</td><td>{fr[0][0]}–{fr[-1][0]}</td><td>{mins} min</td></tr>')
    if i < len(blocks) - 1: plan.append('<tr><td></td><td><i>Break (extra)</i></td><td></td><td>10 min</td></tr>')
plan.append(f'<tr><td></td><td><b>Total net teaching time</b></td><td></td><td><b>{total} min</b></td></tr></table>')
assert total == 300, total
secs_html = []
for i, (t, fr) in enumerate(blocks):
    code, name = t.split(' ', 1)
    mins = sum(x[2] for x in fr)
    h = [f'<section id="s{i+1}">', f'<h2 class="session">Session {i+1} · {html.escape(name)} <small>Curriculum code {code} · {mins} min</small></h2>']
    for (p, title, m, say, em, ask, tr) in fr:
        h.append('<div class="slide">')
        h.append(f'<h3><span class="num">Slide {p}</span>{html.escape(title)}<span class="time">~{m} min</span></h3>')
        h.append(f'<p class="say">{say}</p>')
        if em: h.append('<div class="key"><span class="label">Emphasise</span><ul>' + ''.join(f'<li>{e}</li>' for e in em) + '</ul></div>')
        if ask: h.append('<div class="ask"><span class="label">Ask the audience / answers</span><ul>' + ''.join(f'<li>{a}</li>' for a in ask) + '</ul></div>')
        h.append(f'<p class="trans">Transition: {tr}</p></div>')
    h.append('</section>')
    secs_html.append('\n'.join(h))
doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>W2D5 Speaker Notes</title>
{style}
</head>
<body>
<header><div class="wrap">
  <div class="day">WEEK 2 · DAY 5 / 5 · SPEAKER NOTES</div>
  <h1>Sensors, Measurement and System Integration</h1>
  <p>Mechatronics and Robotics Engineering (50 h) · 6.4 Machine vision · 6.5 Sampling · 6.6 Signal processing · 6.7 Communication · 6.8 Case study &amp; course wrap-up · 5 h net teaching time</p>
</div></header>
<nav class="toc">{nav}</nav>
<main>
  <section id="plan">
    <h2 class="session">Day plan &amp; timing</h2>
    {''.join(plan)}
    <p>Audience: 2nd-year engineering students. Slide numbers are PDF page numbers (section divider pages are included in the count and need no notes). Answers to every “Check your understanding” frame are in the blue boxes.</p>
  </section>
{chr(10).join(secs_html)}
</main>
<footer>Figures and references are listed on the final slides of the deck.</footer>
</body>
</html>
'''
open(os.path.join(R, 'w2d5_speaker_notes.html'), 'w').write(doc)
words = [len(re.sub('<[^>]+>', '', s[1]).split()) for s in S]
print('cards', len(S), 'pages', frames[-1][0], 'total', total, 'say words min/avg', min(words), sum(words)//len(words))
