import re, html, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from notes_content import S1, S2, S3, S4, S5
tpl = open(os.path.join(os.path.dirname(__file__), "../../common/notes_template.html")).read()
style = re.search(r"<style>.*?</style>", tpl, re.S).group(0)
E = html.escape
sessions = [
 ("s1", "3.2 (cont.) Motor driving: PWM, voltage and current limits", "3.2", 30, S1),
 ("s2", "3.3 Field-oriented control", "3.3", 90, S2),
 ("s3", "3.4 Current, velocity and position loops", "3.4", 90, S3),
 ("s4", "3.5 Loop tuning and bandwidth", "3.5", 60, S4),
 ("s5", "3.6 Disturbances and compensation + day wrap-up", "3.6", 30, S5),
]
for sid, t, c, m, cards in sessions:
    assert sum(x[2] for x in cards) == m, (sid, sum(x[2] for x in cards))
def card(p, title, mins, say, emph, asks, trans):
    out = [f'    <div class="slide">', f'      <h3><span class="num">Slide {p}</span>{E(title)}<span class="time">~{mins} min</span></h3>',
           f'      <p class="say">{E(say)}</p>',
           '      <div class="key"><span class="label">Emphasise</span><ul>' + "".join(f"<li>{E(e)}</li>" for e in emph) + "</ul></div>"]
    if asks:
        out.append('      <div class="ask"><span class="label">Ask the audience / likely questions</span><ul>' +
                   "".join(f"<li><b>Q:</b> {E(q)} <b>A:</b> {E(a)}</li>" for q, a in asks) + "</ul></div>")
    out.append(f'      <p class="trans">Transition: {E(trans)}</p>')
    out.append("    </div>")
    return "\n".join(out)
plan = [
 ("1", "3.2 (cont.) PWM, SVPWM, dead time, limits", "2–11", "30 min"),
 ("2", "3.3 FOC part A: transforms, angle, dq model, circuits", "12–19", "35 min"),
 ("", "<i>Break</i>", "", "10 min"),
 ("3", "3.3 FOC part B: torque, MTPA, field weakening, FOC structure, decoupling, alignment", "20–27", "55 min"),
 ("", "<i>Break</i>", "", "10 min"),
 ("4", "3.4 Loops part A: cascade, signals, current-loop design and verification", "28–33", "38 min"),
 ("5", "3.4 Loops part B: velocity SO, position loop, anti-windup, trajectories, feedforward", "34–40", "52 min"),
 ("", "<i>Break</i>", "", "10 min"),
 ("6", "3.5 Loop tuning and bandwidth", "41–50", "60 min"),
 ("", "<i>Break</i>", "", "10 min"),
 ("7", "3.6 Disturbances and compensation; day summary, preview, credits, references", "51–62", "30 min"),
 ("", "<b>Total net teaching time</b>", "", "<b>300 min (5 h)</b> + 40 min breaks"),
]
body = []
body.append('<header><div class="wrap">\n  <div class="day">DAY 4 / 5 · SPEAKER NOTES</div>\n  <h1>Servo Systems: Drives, FOC, Control Loops, Tuning and Compensation</h1>\n  <p>Mechatronics: Electrical Machines, Control, Servo Systems and Sensing · 5 h net teaching time</p>\n</div></header>')
body.append('<nav class="toc"><a href="#plan">Plan</a>' + "".join(f'<a href="#{sid}">{c} · {E(t.split(" ",1)[1].split(":")[0])}</a>' for sid, t, c, m, _ in sessions) + "</nav>")
body.append("<main>")
body.append('  <section id="plan">\n    <h2 class="session">Day plan &amp; timing</h2>\n    <table class="plan"><tr><th>Block</th><th>Topic</th><th>Slides (PDF pages)</th><th>Duration</th></tr>')
for b, t, s, d in plan:
    body.append(f"      <tr><td>{b}</td><td>{t}</td><td>{s}</td><td>{d}</td></tr>")
body.append("    </table>\n    <p>Slide numbers refer to PDF page numbers of <code>day4.pdf</code> (section-divider pages 3, 12, 28, 41, 51, 58 have no card). The reference motor (p=4, R=0.5&nbsp;Ω, L=3&nbsp;mH, ψ<sub>PM</sub>=0.12&nbsp;Vs, k<sub>t</sub>=0.72&nbsp;Nm/A, J<sub>m</sub>=3·10<sup>-4</sup>&nbsp;kg&nbsp;m², V<sub>dc</sub>=325&nbsp;V, 16&nbsp;kHz) is used for every computed plot; the data are produced by <code>day4/src/gen_data.py</code>.</p>\n  </section>")
for sid, t, c, m, cards in sessions:
    body.append(f'\n  <section id="{sid}">\n    <h2 class="session">Session {c} · {E(t.split(" ",1)[1])} <small>Curriculum code {c} · {m} min</small></h2>')
    for x in cards: body.append(card(*x))
    body.append("  </section>")
body.append("</main>\n<footer>Figures and references are listed on the final slides of the deck.</footer>")
doc = f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>Day 4 Speaker Notes</title>\n{style}\n</head>\n<body>\n' + "\n".join(body) + "\n</body>\n</html>\n"
open(os.path.join(os.path.dirname(__file__), "../day4_speaker_notes.html"), "w").write(doc)
n = sum(len(x[4]) for x in sessions)
wc = [len(x[3].split()) for s in sessions for x in s[4]]
print("cards", n, "words min/avg/max", min(wc), sum(wc)//len(wc), max(wc))
