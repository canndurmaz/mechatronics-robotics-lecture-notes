# Brief for each day's deck (shared by all 5 writers)

Project root: /home/ukssb/Workspaces/tunaakan
Audience: engineers in an industrial mechatronics / servo-drive context (25 h purely theoretical
training, 5 days x 5 h net, no lab or software exercises). Language: **English**.
Level: academic, rigorous, university-graduate depth, but practically oriented to servo/motion systems.

## Deliverables for day N
1. `dayN/dayN.tex` — Beamer deck, **~50 frames** (48–56 counted by the PDF frame counter, excluding
   automatic section-divider pages is NOT required; just aim for ~50 content frames).
2. `dayN/dayN.pdf` — compiled, with **zero LaTeX errors** and no overfull content running off slides.
3. `dayN/dayN_speaker_notes.html` — speaker notes, one card per content slide, built from
   `common/notes_template.html` (copy its `<style>` and structure verbatim; replace placeholders).
4. Figures you download go to `figures/` with the prefix `dN_` (e.g. `figures/d1_pmsm_rotor.jpg`).

## LaTeX conventions (mandatory)
```latex
\documentclass[aspectratio=169,10pt]{beamer}
\usetheme{mekatronik}          % common/beamerthememekatronik.sty
\setday{N}{<short day title>}
\title[<short>]{<Day title>}
\subtitle{<sessions summary>}
\author{Mechatronics Training Programme}
\institute{Theoretical Course Series}
\date{Day N of 5}
\begin{document}
\begin{frame}[plain]\titlepage\end{frame}
...
```
Compile from inside `dayN/` with:
`TEXINPUTS=../common//: pdflatex -interaction=nonstopmode dayN.tex` (run twice).
Figures are included as `\includegraphics[...]{../figures/dN_xxx.jpg}`.

Theme provides: palette colors `mkNavy mkBlue mkMid mkSky mkPale mkOrange mkAmber mkCream mkGray mkLight mkGreen mkRed`;
boxes `keybox[title]`, `defbox[title]`, `eqbox` (for key equations), `notebox`; macros `\hl{}` (orange bold),
`\term{}` (blue bold), `\credit{}` (tiny gray figure credit); pgfplots style `mkplot`
(`\begin{axis}[mkplot,...]`). Libraries loaded: tikz (arrows.meta, positioning, calc, shapes, patterns,
decorations, 3d, angles, quotes, fit, backgrounds, matrix), circuitikz, pgfplots (+groupplots, fillbetween),
siunitx, booktabs, tabularx, amsmath, bm, tcolorbox. Only use colors from the palette.

## Structure of every deck
- Title page (plain), then an "Agenda / learning objectives" frame with the timed schedule of sessions.
- `\section{...}` per curriculum session (theme auto-inserts a dark divider page).
- Content frames: mix of (a) derivations and key equations, (b) **your own TikZ / circuitikz / pgfplots
  drawings** (computed plots of real equations: step responses, Bode plots, torque–speed curves,
  phasor/vector diagrams, block diagrams, circuit schematics, cross-sections...), (c) **real photographs /
  figures downloaded from Wikimedia Commons**, (d) comparison tables (booktabs), (e) worked numerical
  examples with realistic servo values, (f) practical design rules / pitfalls.
- Target at least **20 own drawings/plots** and **6–10 downloaded figures** per deck.
- Each session ends with a short "Summary / key take-aways" frame. The deck ends with:
  "Day summary", "Preview of next day" (except Day 5 → "Course wrap-up"), a "Figure credits" frame
  (from `figures/CREDITS.tsv` lines with prefix dN_), and a "References" frame (classical textbooks
  and standards — e.g. Krishnan; Mohan; Fitzgerald & Kingsley; Ogata; Franklin–Powell–Emami-Naeini;
  Åström & Hägglund; Åström & Murray "Feedback Systems"; Ellis "Control System Design Guide"; Leonhard;
  Vas; Slotine & Li; Ioannou & Sun; Zhou & Doyle; Oppenheim & Schafer; Franklin–Powell–Workman;
  manufacturer application notes (TI, Infineon, Microchip, ST, Analog Devices, Renesas); IEC 61800,
  IEC 61158/EtherCAT ETG, ISO 11898). Only cite works you are confident exist; cite them in-slide where used
  as `[Author, Year]` style footers or small text.
- Every downloaded figure gets an in-slide `\credit{Author, License, via Wikimedia Commons}` line.
- Keep frames uncluttered: max ~7 bullets, fonts never below \scriptsize for body text.
  Use `[t]` or `\vspace` sensibly; use `columns` for figure + text. Never let content overflow the
  frame — render pages to PNG (`pdftoppm -r 45 -png dayN.pdf /tmp/...`) in your scratch area and inspect a
  good sample of them (all pages with figures/plots) visually with the Read tool, and fix problems.

## Downloading figures
Use the helper (licence-checked, appends to figures/CREDITS.tsv):
```
python3 common/fetch_commons.py search "<query> filetype:bitmap" 10
python3 common/fetch_commons.py search "<query> filetype:drawing" 10    # SVG diagrams → PNG
python3 common/fetch_commons.py get "File:Exact title.jpg" dN_shortname
```
Prefer clear photographs of real hardware (motors, encoders, resolvers, inverters, IGBT modules,
ball screws, gearboxes, servo drives, sensors, oscilloscope traces) and well-drawn diagrams. Check each
downloaded image visually (Read tool) before using it. Do not use non-free images.
You may also use WebSearch/WebFetch for research (technical facts, typical parameter values,
standards), but only Wikimedia Commons images get embedded.

## Speaker notes (HTML)
- Copy `common/notes_template.html` structure and `<style>` exactly (keep dark-mode tokens).
- Header: "DAY N / 5 · SPEAKER NOTES", day title.
- "Day plan & timing" table covering 5 h (sessions with curriculum codes, slide ranges, minutes;
  include suggested 10-min breaks roughly every hour — breaks are extra, the 5 h is net).
- One `.slide` card for **every content frame**, numbered with the PDF page number, title, time estimate
  (sum of times per session must match the session duration). Each card: 120–250 words of
  speakable explanation (`.say`, full prose the instructor can read), an "Emphasise" box, an
  "Ask the audience / likely questions" box with Q&A where useful, and a transition sentence.
- Add the sticky nav links to each session anchor.

## Quality bar
Technically correct equations (state sign conventions and units), consistent notation across the
deck (e.g. motor: R, L, k_e, k_t, J, B, T_L; dq frame: i_d, i_q, ψ_PM, p pole pairs; control: G(s), C(s),
L(s)=C(s)G(s), ω_c, PM, GM). Worked examples must compute correctly. When done, report: frame count,
number of own drawings, list of downloaded figures, compile status, and any issues.
