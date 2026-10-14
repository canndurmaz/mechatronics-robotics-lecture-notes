import re, html, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from notes_content import S1, S2, S3, S4
tpl = open(os.path.join(os.path.dirname(__file__), "../../../common/notes_template.html")).read()
style = re.search(r"<style>.*?</style>", tpl, re.S).group(0)
E = html.escape
sessions = [
 ("s1", "3.3 Field-oriented control (with agenda and recap)", "3.3", 90, S1),
 ("s2", "3.4 Cascaded current, velocity and position loops", "3.4", 90, S2),
 ("s3", "3.5 Loop tuning and bandwidth", "3.5", 60, S3),
 ("s4", "3.6 Trajectory generation, feedforward and disturbance compensation + wrap-up", "3.6", 60, S4),
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
 ("1", "Agenda, recap of W1D3–W1D4; 3.3 FOC part A: three-phase, rotation, Clarke, Park, frames", "2–11", "46 min"),
 ("", "<i>Break</i>", "", "10 min"),
 ("2", "3.3 FOC part B: θ_e, dq circuits, torque, worked example, FOC loop, alignment, robot joint, check, summary", "12–20", "44 min"),
 ("", "<i>Break</i>", "", "10 min"),
 ("3", "3.4 Cascade, robot-joint loops, current loop, velocity-loop recipe", "22–26", "51 min"),
 ("4", "3.4 Velocity plots, position loop, windup, check, summary", "27–31", "39 min"),
 ("", "<i>Break</i>", "", "10 min"),
 ("5", "3.5 Loop tuning and bandwidth", "33–42", "60 min"),
 ("", "<i>Break</i>", "", "10 min"),
 ("6", "3.6 Trajectories, feedforward, gravity compensation, DOB; day summary, preview, credits, references", "44–57", "60 min"),
 ("", "<b>Total net teaching time</b>", "", "<b>300 min (5 h)</b> + 40 min breaks"),
]
body = []
body.append('<header><div class="wrap">\n  <div class="day">WEEK 1 · DAY 5 / 5 · SPEAKER NOTES</div>\n  <h1>Servo Systems II: FOC, Cascaded Loops, Tuning and Trajectories</h1>\n  <p>Mechatronics and Robotics Engineering (50 h) · Week 1 · Day 5 · 5 h net teaching time</p>\n</div></header>')
body.append('<nav class="toc"><a href="#plan">Plan</a>' + "".join(f'<a href="#{sid}">{c} · {E(t.split(" ",1)[1].split(":")[0])}</a>' for sid, t, c, m, _ in sessions) + "</nav>")
body.append("<main>")
body.append('  <section id="plan">\n    <h2 class="session">Day plan &amp; timing</h2>\n    <table class="plan"><tr><th>Block</th><th>Topic</th><th>Slides (PDF pages)</th><th>Duration</th></tr>')
for b, t, s, d in plan:
    body.append(f"      <tr><td>{b}</td><td>{t}</td><td>{s}</td><td>{d}</td></tr>")
body.append("    </table>\n    <p>Slide numbers refer to PDF page numbers of <code>w1d5.pdf</code> (title page 1 and section-divider pages 5, 21, 32, 43 have no card). The reference motor (p=4, R=0.5&nbsp;Ω, L=3&nbsp;mH, ψ<sub>PM</sub>=0.12&nbsp;Vs, k<sub>t</sub>=0.72&nbsp;Nm/A, J<sub>m</sub>=3·10<sup>-4</sup>&nbsp;kg&nbsp;m², V<sub>dc</sub>=325&nbsp;V, 16&nbsp;kHz) is used for every computed plot; plus a harmonic gear N = 100 for the robot-joint examples; the data are produced by <code>w1d5/src/gen_data.py</code>.</p>\n  </section>")
for sid, t, c, m, cards in sessions:
    body.append(f'\n  <section id="{sid}">\n    <h2 class="session">Session {c} · {E(t.split(" ",1)[1])} <small>Curriculum code {c} · {m} min</small></h2>')
    for x in cards: body.append(card(*x))
    body.append("  </section>")
body.append("</main>\n<footer>Figures and references are listed on the final slides of the deck.</footer>")
doc = f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>W1D5 Speaker Notes</title>\n{style}\n</head>\n<body>\n' + "\n".join(body) + "\n</body>\n</html>\n"
open(os.path.join(os.path.dirname(__file__), "../w1d5_speaker_notes.html"), "w").write(doc)
n = sum(len(x[4]) for x in sessions)
wc = [len(x[3].split()) for s in sessions for x in s[4]]
print("cards", n, "words min/avg/max", min(wc), sum(wc)//len(wc), max(wc))
