# Revision brief: adapt the deck to 2nd-year (sophomore) engineering students

The existing decks (dayN/dayN.tex) were written for practising engineers. The real audience is
**2nd-year undergraduate engineering students who are new to these concepts**. Revise the deck
and its speaker notes so they can follow it. Keep the theme, the curriculum topics/timing, the
academic tone and the visual style (dark blue + orange). Speed matters: edit the existing file,
don't restart from scratch, and reuse existing drawings wherever they still fit.

## What students can be assumed to know
Calculus (derivatives, integrals), first exposure to ODEs, complex numbers, vectors, Newton's laws
incl. basic rotation (torque, moment of inertia), basic circuits (Ohm, KVL/KCL, R, L, C, RC charging),
sin/cos and phasor basics, simple matrix arithmetic.
**Not** assumed: Laplace transform, transfer functions, Bode plots, feedback control, state space,
Fourier analysis, power electronics, electrical machines, sampling theory, communication protocols.

## How to revise
1. **Intuition before maths.** For each new concept: everyday analogy / physical picture →
   drawing → the simplest equation (every symbol named with units) → one small numeric example →
   one-line take-away. Example analogies: cruise control for feedback, shower temperature for delay,
   bicycle gears for gear ratio/reflected inertia, car suspension for mass–spring–damper, a
   playground swing for resonance, a strobe light / wagon-wheel effect for aliasing.
2. **Add short "Refresher" frames** where a prerequisite is missing (use a `defbox[Refresher: …]`):
   e.g. Laplace transform as a "tool that turns ODEs into algebra", complex numbers / e^{jωt},
   phasors, what a sinusoidal frequency response means, matrices for state space, what a
   transistor switch does, binary numbers for encoders/ADCs. Day 3–5 also start with a 1–2 frame
   "What we learned so far" recap linking to the previous day.
3. **Trim depth, don't drop topics.** Every curriculum sub-topic must still appear, but advanced
   items become *conceptual* (one picture + one sentence, flagged "Going further" in small text):
   e.g. Routh tables, Nyquist details, H∞, Lyapunov/MRAC maths, Ackermann formula,
   SVPWM dwell-time algebra, MTPA/field weakening, RDC loop maths, CiA 402 state machine detail.
   Remove dense multi-line derivations; keep at most 1 key boxed equation per frame (`eqbox`).
4. **Explain jargon on first use** (`\term{}`), and add a small **glossary / key terms** frame at the end of each
   session (can be merged with that session's summary frame).
5. **Active learning:** add 1 "Check your understanding" frame per session (2–3 short conceptual
   questions, answers in the speaker notes, not on the slide), using `keybox[Check your understanding]`.
6. **Worked examples:** keep them, but make them step-by-step (numbered steps, round numbers,
   units at every step). Drop any example that needs more than ~4 steps or split it across 2 frames.
7. **Less text per slide:** max ~5 bullets, short phrases, larger figures. Body text not smaller
   than \small where possible (\scriptsize only for credits/footnotes).
8. **Learning objectives** on the agenda frame rewritten as student-level outcomes
   ("By the end of today you can explain…, sketch…, calculate…").
9. Frame count stays **~50–58** (the PDF frame counter); new refresher/check frames replace
   trimmed advanced frames rather than inflating the deck.

## Speaker notes (dayN/dayN_speaker_notes.html)
Update to match the revised deck exactly (one card per content frame, page numbers re-checked
against the compiled PDF, session minutes still summing to the session durations, total 300 min).
Write for an instructor teaching sophomores: plain language, the analogy to use, a common
misconception to watch for (add it to the "Emphasise" box), and the answers to the
"Check your understanding" questions. ~100–160 words of `.say` per card. Keep the template's
HTML/CSS structure.

## Build / verify
`cd /home/ukssb/Workspaces/tunaakan && ./compile.sh N` must print `dayN: OK`. Render the pages you
changed (`pdftoppm -r 40 -png dayN/dayN.pdf <your scratch dir>/p`) and visually inspect a sample
(paste several into a grid image to save time) to make sure nothing overflows. Do not touch
other days' files or common/ files. Put scratch files in your own scratch subfolder.
Report briefly: frame count, what was added (refreshers, checks), what was demoted to
"Going further", compile status.
