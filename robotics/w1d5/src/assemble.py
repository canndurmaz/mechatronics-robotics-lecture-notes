"""Assemble w1d5.tex: reuses (adapted) frames from ../../../day4/day4.tex plus new robotics frames."""
import re, os
H = os.path.dirname(os.path.abspath(__file__))
old = open(os.path.join(H, "../../../day4/day4.tex")).read()
frames = {}
for m in re.finditer(r"\\begin\{frame\}(\[[^\]]*\])?\{(.*?)\}\n(.*?)\\end\{frame\}", old, re.S):
    frames[m.group(2)] = m.group(0)

def F(title, *subs):
    s = frames[title]
    for a, b in subs:
        assert a in s, (title, a)
        s = s.replace(a, b)
    return s + "\n\n"

new = {}
exec(open(os.path.join(H, "new_frames.py")).read(), {"new": new})

out = [new["HEAD"]]
out.append("\\section{3.3 Field-Oriented Control (FOC)}\n\n")
out.append(F("Why field-oriented control? The DC-motor analogy",
  ("\\begin{tikzpicture}[scale=.95]", "\\begin{tikzpicture}[scale=.72]"),
  ("\\includegraphics[width=.8\\linewidth,height=2.3cm,keepaspectratio]{../figures/d4_servo_drives.png}\\\\\n\\credit{Servo drives. Tero Kontkanen, CC BY-SA 3.0, via Wikimedia Commons}",
   "\\includegraphics[width=.62\\linewidth,height=1.5cm,keepaspectratio]{../figures/d1_bldc.jpg}\\\\\n\\credit{Opened brushless PM motor. Sebastian Koppehel, CC BY 3.0, via Wikimedia Commons}\\\\\n\\small Almost every robot joint uses a PMSM driven by FOC."),
  ("\\src{[Blaschke, 1972]; [Leonhard, 2001]; [Krishnan, 2010]}", "\\src{[Blaschke, 1972]; [Leonhard, 2001]; [Krishnan, 2010]}")))
out.append(F("Refresher: three-phase sinusoids, $120^\\circ$ apart"))
out.append(F("Refresher: rotating vectors and rotation matrices",
  ("\\small\\hl{Take-away:} $R(-\\theta)$", "\\small You will meet $R(\\theta)$ again in W2D1 (robot frames).\\\\ \\hl{Take-away:} $R(-\\theta)$")))
out.append(F("Clarke transform: three phases $\\to$ two axes ($\\alpha\\beta$)",
  ("\\begin{defbox}[Clarke: $abc\\to\\alpha\\beta$ (fixed to the stator)]", "\\begin{defbox}[Clarke transform (axes fixed to the stator)]")))
out.append(F("Park transform: looking at the rotor from a rotating camera"))
out.append(F("The same current seen in the three frames",
  ("A PI controller (Day 2)", "A PI controller (W1D3)")))
out.append(F("Electrical vs.\\ mechanical angle: $\\theta_e = p\\,\\theta_m$"))
out.append(F("The motor seen by the rotating camera: two $R$--$L$ circuits",
  ("Each axis = the Day-1 winding", "Each axis = the W1D1 winding")))
out.append(F("Torque comes from $i_q$"))
out.append(F("Worked example: operating point at \\SI{3000}{rpm}"))
out.append(F("FOC: the basic structure"))
out.append(F("Rotor angle alignment and offset errors"))
out.append(new["FOC_JOINT"])
out.append(F("Check your understanding -- 3.3"))
out.append(F("Summary 3.3 -- Field-oriented control"))

out.append("\\section{3.4 Cascaded Current, Velocity and Position Loops}\n\n")
out.append(F("The nested (cascade) control structure"))
out.append(new["CASCADE_JOINT"])
out.append(F("Current-loop PI: a step-by-step recipe"))
out.append(F("Current loop: computed frequency and step response"))
out.append(F("Velocity-loop PI: a step-by-step recipe"))
out.append(F("Velocity loop: computed Bode plot and step responses"))
out.append(new["POSLOOP"])
out.append(F("Torque and speed limits; integrator windup"))
out.append(new["CHECK34"])
out.append(new["SUM34"])

out.append("\\section{3.5 Loop Tuning and Bandwidth}\n\n")
out.append(F("Refresher: what does ``bandwidth'' mean?"))
out.append(F("The bandwidth hierarchy of a servo drive"))
out.append(F("Tuning procedure: from the inside out"))
out.append(F("Bandwidth separation: rule of thumb 3--10$\\times$"))
out.append(F("Effect of the load inertia ratio",
  ("\\item Analogy: bicycle gears -- the gear (or screw) ratio changes how heavy the load feels at the motor.",
   "\\item Robot arm: the inertia seen by joint 1 changes with the \\hl{pose} (arm stretched vs.\\ folded), divided by $N^2$ through the gear (W1D2)."),
  ("\\item Rule: retune with $\\hat J$; aim for $J_L/J_m\\le3\\ldots10$.", "\\item Rule: tune for the worst pose, or schedule gains with pose; aim for $J_L/J_m\\le3\\ldots10$."),
  ("\\includegraphics[width=.85\\linewidth,height=1.3cm,keepaspectratio]{../figures/d4_ballscrew.jpg}\\\\\n\\credit{Ball screws. Graibeard, CC BY-SA 3.0, via Wikimedia Commons}\n", "")))
out.append(F("Delays and their phase cost at crossover"))
out.append(F("Measuring frequency responses (FRFs)"))
out.append(F("A measured-style FRF: resonance and notch filter",
  ("More on Day 5.", "More in W2D1, session 3.7.")))
out.append(F("Check your understanding -- 3.5"))
out.append(F("Summary 3.5 -- Tuning and bandwidth"))

out.append("\\section{3.6 Trajectory Generation, Feedforward and Disturbance Compensation}\n\n")
out.append(F("Trajectory generation: trapezoidal vs.\\ S-curve profiles"))
out.append(new["TRAPEX"])
out.append(F("Following error and how feedforward removes it"))
out.append(F("Feedforward: velocity, acceleration/torque and friction"))
out.append(F("Disturbances: load torque and friction",
  ("\\item Also: cogging, dead time, sensor noise.", "\\item Robots: also \\hl{gravity} on every link (next slide).")))
out.append(new["GRAVITY"])
out.append(F("Disturbance observer (DOB): estimate the unknown push",
  ("\\item Bonus: $\\hat T_L$ can detect collisions.", "\\item Bonus: $\\hat T_L$ detects \\hl{collisions} -- used in cobots to stop on contact.")))
out.append(F("Cogging and torque ripple compensation"))
out.append(new["CHECK36"])
out.append(new["SUM36"])
out.append(new["TAIL"])
tex = "".join(out).replace("{../figures/", "{../../figures/")
open(os.path.join(H, "../w1d5.tex"), "w").write(tex)
print("frames", tex.count("\\begin{frame}"))
