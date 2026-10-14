# Brief: "Mechatronics and Robotics Engineering" — 50 h, 2 weeks × 5 days × 5 h

Project root: /home/ukssb/Workspaces/tunaakan. This is a **brand-new course**, separate from the
existing 5-day decks in day1..day5/. You MAY reuse/adapt frames, TikZ drawings, pgfplots data and
figures from those decks (day*/day*.tex, day*/data/, figures/), but the result must be a new,
coherent deck written for this course's day plan below (new titles, new flow, robotics focus).

Audience: **2nd-year (sophomore) engineering students, new to these concepts.** Language: English.
Academic tone, intuition-first. Follow common/BRIEF_SOPHOMORE.md for the teaching style
(assumed prior knowledge, analogy → picture → one equation → small numbered worked example →
take-away; Refresher frames; "Going further" small grey text for advanced items; one
"Check your understanding" frame per session with answers only in the notes; key-terms box in each
session summary; ≤5 bullets per slide; body text ≥ \small where possible).
Also read common/BRIEF.md for the theme conventions, boxes, macros, figure helper and the
notes HTML template (common/notes_template.html). Ignore its "engineer" audience/notes-length lines.

## Course topics and hours (from the official curriculum)
1. Electrical Machines and Actuators in Robotic Systems — 8 h
2. Control in Robotic and Mechatronic Systems — 10 h
3. Servo Systems and Electric Drive Control — 8 h
4. Robot Mechanisms and Motion Systems — 8 h
5. Robotic Manufacturing and Flexible Automation Systems — 8 h
6. Sensors, Measurement and System Integration — 8 h

## Day plan (session code — title — hours)
**W1D1 Electrical Machines & Actuators in Robots I**
1.1 Electromechanical energy conversion & the actuator landscape in robots (electric vs pneumatic vs hydraulic; torque, speed, power) — 1
1.2 DC, BLDC and PMSM motors: structure and commutation — 1.5
1.3 Electrical and mechanical motor models (R, L, back-EMF, k_t, J, friction; time constants) — 1.5
1.4 Stepper and induction motors in automation — 1
**W1D2 Actuators II + Introduction to Control**
1.5 Robot joint actuators: gearboxes (planetary, harmonic, cycloidal), reflected inertia, backlash, stiffness, direct drive, series-elastic actuators — 1
1.6 Linear actuators and end-effectors: ball screw, belt, linear motor, grippers (electric, pneumatic, vacuum), solenoids — 1
1.7 Motor sizing and selection for a robot joint (torque–speed, RMS torque, duty cycle, thermal; worked example) — 1
2.1 Modelling dynamic systems (mass–spring–damper, rotational, electromechanical; linearisation) — 1
2.2 Laplace transform and transfer functions (poles, 1st/2nd-order responses) — 1
**W1D3 Control in Robotic & Mechatronic Systems**
2.3 Block diagrams, feedback and state-space basics — 1
2.4 Frequency response and Bode plots — 1
2.5 PID control (P/I/D effects, tuning, windup & anti-windup, feedforward) — 1.5
2.6 Stability and performance (specs, steady-state error, gain/phase margins, bandwidth) — 1.5
**W1D4 Control (cont.) + Servo Systems I**
2.7 Filters and compensation (LPF, notch, lead/lag) — 1
2.8 Digital control (sampling, ZOH, discrete PID, delay) — 1
2.9 Control of robot manipulators (independent-joint control, gravity compensation, computed torque, impedance/force control — conceptual) — 1
3.1 Servo system architecture and control modes (torque / velocity / position) — 1
3.2 Power electronics for drives (DC bus, inverter, PWM, current/voltage limits, regeneration) — 1
**W1D5 Servo Systems II**
3.3 Field-oriented control (Clarke/Park intuition, d–q currents) — 1.5
3.4 Cascaded current, velocity and position loops — 1.5
3.5 Loop tuning and bandwidth (inner→outer, inertia ratio, delays) — 1
3.6 Trajectory generation, feedforward and disturbance compensation — 1
**W2D1 Servo III + Robot Mechanisms I**
3.7 Resonance, compliance and notch filters in robot joints — 1
4.1 Robot anatomy and classification (joints, DOF, workspace; articulated, SCARA, Cartesian/gantry, delta/parallel, cobots, mobile robots) — 1
4.2 Spatial descriptions: positions, rotation matrices, homogeneous transforms — 1.5
4.3 Forward kinematics (DH convention; planar 2-link, SCARA examples) — 1.5
**W2D2 Robot Mechanisms II + Robotic Manufacturing I**
4.4 Inverse kinematics (2-link geometric solution, multiple solutions, reachability) — 1
4.5 Velocity kinematics: the Jacobian, singularities, statics (τ = Jᵀ F) — 1
4.6 Introduction to robot dynamics (2-link Lagrange intuition, gravity/inertia, payload effects) — 1
4.7 Motion systems & trajectory planning (PTP / linear / circular moves, joint vs Cartesian space, linear axes & gantries, differential-drive AMR kinematics) — 1
5.1 Introduction to robotic manufacturing and flexible automation (fixed / programmable / flexible automation, FMS, Industry 4.0) — 1
**W2D3 Robotic Manufacturing & Flexible Automation**
5.2 Industrial robot applications (welding, painting, palletising, machine tending, assembly, pick-and-place) — 1
5.3 Robotic work-cell design (layout, reach, cycle time, tooling, fixtures, end-of-arm tooling) — 1
5.4 PLCs and automation control (scan cycle, I/O, ladder logic, IEC 61131-3, sequential control) — 1.5
5.5 Robot programming (teach pendant, frames: base/tool/user, offline programming, simulation & digital twin) — 1.5
**W2D4 Manufacturing (cont.) + Sensors I**
5.6 Material handling and flexible systems (conveyors, AGV/AMR, FMS cells, collaborative robots & HRC) — 1
5.7 Safety and standards (ISO 12100 risk assessment, ISO 10218, ISO/TS 15066, ISO 13849 PL, light curtains, safety PLC) — 1
6.1 Sensors and measurement principles (accuracy, precision, resolution, range, linearity) — 1
6.2 Position and motion sensors (encoders, resolvers, IMU/gyro/accelerometer) — 1
6.3 Force/torque, tactile, proximity and range sensors (strain gauge, 6-axis F/T, inductive, capacitive, photoelectric, ultrasonic, LiDAR) — 1
**W2D5 Sensors, Measurement & System Integration**
6.4 Machine vision in robotics (camera model intuition, calibration, pose estimation, hand–eye) — 1
6.5 Sampling and digitisation (ADC, quantisation, aliasing, latency) — 1
6.6 Signal processing and filters (LPF, moving average, FIR/IIR, notch, filtered derivative, sensor fusion / Kalman — conceptual) — 1
6.7 Communication and integration (CAN, EtherCAT, PROFINET, OPC UA, ROS overview, synchronisation & latency) — 1
6.8 System-integration case study and course wrap-up — 1

## Your deliverables for day wXdY (folder robotics/wXdY/)
- `wXdY.tex` (~50 content frames; PDF frame counter 48–58), compiled `wXdY.pdf`, and `wXdY_speaker_notes.html`.
- Preamble:
```latex
\documentclass[aspectratio=169,10pt]{beamer}
\usetheme{mekatronik}
\renewcommand{\coursetitle}{Mechatronics and Robotics Engineering (50 h)}
\setweek{X}
\setday{Y}{<short day title>}
\title[<short>]{<Day title>}
\subtitle{<sessions summary>}
\author{Mechatronics and Robotics Engineering Programme}
\institute{Week X \textperiodcentered{} Day Y}
\date{2 weeks \textperiodcentered{} 10 days \textperiodcentered{} 50 hours}
```
- Build: `cd /home/ukssb/Workspaces/tunaakan/robotics && ./compile.sh wXdY` must print `wXdY: OK`.
- Structure: title (plain) → agenda with timed sessions + student learning outcomes → (except W1D1)
  1–2 frame recap of the previous day → sections per session (code + title) → day summary →
  preview of next day (W2D5: course wrap-up) → figure credits → references.
- ≥20 own TikZ / circuitikz / pgfplots drawings (reuse from old decks is fine), 5–8 figures from
  Wikimedia Commons (reuse existing files in figures/ or fetch new ones with prefix `rXY_`, e.g. r21_;
  the helper rate-limits — retry with a sleep on HTTP 429). Credit every photo on its slide.
- Do NOT use math or "=" in tcolorbox titles (breaks compile). Use `\rightarrow` not `\to` in pgfplots legends.
- Speaker notes: common/notes_template.html structure + CSS; header "WEEK X · DAY Y / 5 · SPEAKER NOTES";
  day-plan table (minutes per session summing to 300, breaks extra); one card per content frame
  numbered by PDF page, ~80–110 words of `.say`, analogy, misconception in "Emphasise", check answers,
  transition. Generating the HTML from a small Python script is fine.
- Visual check: render only pages whose log shows Overfull > 10 pt plus a 6-page sample grid; fix overflows.
- Work fast. Do it yourself (no sub-agents). Only touch your own folder (+ new figures with your prefix).
  Report briefly: frames, own drawings, figures, compile status, issues.
