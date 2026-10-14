#!/usr/bin/env python3
"""Build w1d4_speaker_notes.html from the compiled PDF (page numbers) + card texts below."""
import re, subprocess, html, pathlib
HERE = pathlib.Path(__file__).resolve().parent
TPL = (HERE / '../../common/notes_template.html').resolve().read_text()
STYLE = re.search(r'<style>.*?</style>', TPL, re.S).group(0)

def page_titles():
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', str(HERE/'w1d4.pdf')], capture_output=True, text=True).stdout).group(1))
    out = {}
    for p in range(1, n+1):
        t = subprocess.run(['pdftotext', '-f', str(p), '-l', str(p), '-layout', str(HERE/'w1d4.pdf'), '-'], capture_output=True, text=True).stdout
        out[p] = re.sub(r'\s+', ' ', t).replace('\u2014','---').replace('\u2013','--')
    return out

# (session id, frame-title key (start of the slide title), minutes, say, [emphasise], [(Q, A)], transition)
S = {}
S['s0'] = ('Opening', 'Agenda and recap', 5)
S['s1'] = ('2.7 Filters and compensation', '2.7', 55)
S['s2'] = ('2.8 Digital control', '2.8', 60)
S['s3'] = ('2.9 Control of robot manipulators', '2.9', 60)
S['s4'] = ('3.1 Servo architecture and control modes', '3.1', 60)
S['s5'] = ('3.2 Power electronics for drives', '3.2', 60)

C = [
('s0','Agenda and learning outcomes',2,
 "Welcome back. Today has two halves. In the morning we finish the control block: filters and compensators, then digital control, which is how every real controller runs, and then we look at what changes when the plant is a whole robot arm instead of one motor. After lunch we open the box that runs these loops, the servo drive: its architecture and control modes, and the power electronics inside it. Read the five outcomes aloud; they are verbs: calculate, choose, explain, sketch, calculate. Tell students that the two worked formulas of the day, the phase cost of a delay and the average PWM voltage, will come back tomorrow.",
 ["Five one-hour sessions; breaks are extra.","Misconception: 'control' and 'drives' are separate subjects. Today shows the drive is where the control runs."],
 [],"Let us quickly recall where we stopped yesterday."),
('s0','What we learned so far',3,
 "Yesterday we built the feedback loop: measure, compare, correct. PID gave us three ways to react to the error, and anti-windup protected the integrator. With the Bode plot we found the crossover frequency, roughly the loop bandwidth, and the phase margin, our distance from instability. Today's thread is phase. Think of phase margin as money in a wallet. Filters, sampling delays and mechanical resonances spend it; lead compensators and faster sampling earn it back. Whenever you see a new block today, ask: does it cost phase near crossover or not?",
 ["Phase margin as a budget is the key mental model of the morning.","Misconception: a stable loop is automatically a good loop. Little margin means ringing."],
 [("What is crossover?","The frequency where the loop gain magnitude equals 1 (0 dB).")],"First, filters."),
('s1','Refresher: what does a filter do',5,
 "A filter is like the equaliser on a music player: it turns some frequencies down and leaves others. A low-pass keeps the bass, slow signals, and removes the treble, fast noise. A high-pass does the opposite and removes constant offsets. A notch removes one single tone, like a hum. The simplest low-pass is a resistor and a capacitor; its cut-off is one over two pi R C. With one kilo-ohm and one microfarad we get 159 hertz, and ten times higher only ten percent passes. The important side effect: every filter that weakens a signal also delays it.",
 ["Name every symbol with units: f_f in hertz.","Misconception: filters only change the amplitude. They also shift the phase, which matters inside loops."],
 [("At 10 f_f, how much passes a 1st-order low-pass?","About 0.1, i.e. -20 dB.")],"Why would we want filters in a robot joint at all?"),
('s1','Why filters in a robot joint loop',5,
 "Look at the four orange boxes: positions where a filter can sit. On the reference, on the error, on the torque command, or on the feedback. We filter against encoder quantisation noise, resonances in gearboxes and belts, jerky set-points from the robot program, and offsets. The rule on the slide is the main message: anything inside the red dotted loop becomes part of L of s, so its phase lag reduces the phase margin. A filter on the reference, outside the loop, only changes how the motion looks; it can never make the loop unstable.",
 ["Inside the loop costs margin; outside is free.","Misconception: more filtering is always safer. Inside the loop it can destabilise."],
 [],"Let us quantify how much phase a low-pass costs."),
('s1','Low-pass filter: cut-off',5,
 "Here is the first-order low-pass, omega f over s plus omega f. The cut-off is where the gain is down 3 dB. Higher order means a steeper slope: minus 20 dB per decade per order, so the 4th-order curve kills noise much faster. But look at the phase plot: at the cut-off a first-order filter already lags 45 degrees, the fourth-order 180 degrees. A second-order filter with low damping even has a peak, amplifying near its cut-off. So higher order means a cleaner signal but far more lag, which is bad news inside a loop.",
 ["-20n dB/decade and -45 degrees per order at the cut-off.","Misconception: phase lag only appears above the cut-off. It starts a decade below."],
 [("Phase of a 2nd-order LPF at its cut-off?","About -90 degrees.")],"So where should we put the cut-off?"),
('s1','The price of filtering',6,
 "The plot shows how many degrees we lose at crossover versus the ratio of filter cut-off to crossover. The first-order formula is simply arctan of omega c over omega f. Walk through the example: a joint velocity loop at 150 hertz, and we allow ten degrees. Tan of ten degrees is 0.176, so the filter must sit at 150 divided by 0.176, about 850 hertz. Checking: arctan of 150 over 850 is ten degrees. Rule of thumb: put an in-loop low-pass five to ten times above crossover. Lower is quieter but less stable.",
 ["omega_f around 5-10 omega_c.","Misconception: a filter at twice the crossover is 'far enough'. For 4th order it costs about 90 degrees."],
 [("Filter at 5 f_c, first order: loss?","arctan(0.2) = 11 degrees.")],"Sometimes the problem is not broadband noise but one single frequency."),
('s1','Notch filter: cutting out one',5,
 "Think of a playground swing: it has one natural frequency, and pushing at exactly that rhythm makes it swing wildly. A robot joint with a springy gearbox is the same. A notch filter removes the controller's push at that one frequency. The formula has the same polynomial on top and bottom except for the damping: zeta z over zeta p sets the depth, 0.1 gives minus 20 dB. Zeta p sets the width. A wide notch tolerates the resonance drifting, say with payload, but costs more phase at lower frequencies. Show the three curves.",
 ["Centre on the resonance; depth from zeta_z/zeta_p; width from zeta_p.","Misconception: a notch costs no phase. It costs a little below its centre."],
 [],"Let us see a notch save a real loop."),
('s1','Notch in practice',5,
 "This axis has a motor, a stiff coupling and a load, with a resonance at one kilohertz. The velocity loop crosses at 100 hertz with a nice 65 degrees margin. But the resonance peak pushes the gain above zero dB again near one kilohertz, where the phase is already beyond minus 180: three crossings, and the loop is unstable even though the margin at 100 hertz looks good. With a minus 25 dB notch the peak drops below 0 dB; only one crossing remains and we lose just four degrees at 100 hertz. Robot joint resonances come back in W2D1.",
 ["Check all 0 dB crossings, not just the first.","Misconception: a good phase margin at the main crossover guarantees stability."],
 [("Why can a resonance destabilise a loop with 65 degrees PM?","The resonance creates extra 0 dB crossings where the phase is past -180 degrees.")],"Filters spend phase. How do we earn it back?"),
('s1','Phase-lead compensator',5,
 "The lead compensator has a zero before its pole, so between them the phase goes up. Its maximum lead sits at omega m, one over T root alpha, and we place it right at crossover. The amount of lead depends only on alpha: three gives about 30 degrees, 7.5 gives 50, twenty gives 65. The price is that high-frequency gain rises by alpha, so more noise reaches the motor. A useful picture: riding a bicycle, you steer by looking where you are going, not where you are. Lead reacts to the trend, much like a filtered D-term.",
 ["Place maximum lead at crossover.","Misconception: more alpha is free phase. It amplifies noise by alpha."],
 [],"Let us design one."),
('s1','Lead design',6,
 "A pure inertia, one over J s squared, has minus 180 degrees phase at all frequencies, so a plain gain gives zero margin: it would oscillate forever. Goal: 50 hertz crossover and 50 degrees margin. Step one, 50 degrees of lead needs alpha 7.55. Step two, centre it: T equals one over omega c root alpha, 1.16 milliseconds. Step three, choose K so the loop gain is one at crossover: J omega c squared over root alpha, 7.2 newton metres per radian. The computed Bode plot confirms 50 degrees, and the step overshoots 28 percent, removable by a reference filter.",
 ["Three steps: alpha from the needed lead, T to centre, K for |L|=1.","Misconception: overshoot means low margin. Here part of it comes from the lead zero."],
 [],"The opposite tool is the lag compensator."),
('s1','Phase-lag compensator',5,
 "The lag compensator boosts gain only at low frequency, by the factor beta, so the steady-state error shrinks and the joint becomes stiffer against a constant load like gravity. High frequencies are untouched, so no extra noise. Put its zero a decade below crossover and it costs only about five degrees. Lead and lag combine: lead buys phase margin, lag buys stiffness. And PID is really a lead-lag in disguise: the PI part behaves like a lag, the filtered D like a lead. The grey line mentions high-pass filters for offsets; never in the position feedback.",
 ["Lag adds low-frequency gain; keep its zero a decade below crossover.","Misconception: lag improves stability. It slightly reduces margin."],
 [],"Time to check understanding."),
('s1','Session 2.7 --- Check',4,
 "Give students two minutes in pairs. Answers: First, a fourth-order low-pass at twice the crossover costs roughly 90 degrees of phase, so a typical 60-degree margin disappears and the loop goes unstable. Second, the reference filter is outside the loop, so it is not part of L of s; it only changes the command. The feedback filter is inside L of s and its lag reduces the margin. Third, an 800 hertz whistle is a resonance; use a notch filter centred at 800 hertz, then check how much phase it costs at crossover.",
 ["Collect one answer per question from different pairs."],
 [("Q1","PM drops by about 90 degrees: unstable."),("Q2","F_r outside L(s); F_y inside."),("Q3","Notch at 800 Hz.")],"Let us summarise."),
('s1','Session 2.7 --- Summary',4,
 "Four messages. In-loop filters are part of the loop gain: budget their phase and keep them five to ten times above crossover. A notch removes a single resonance for a few degrees. Lead adds phase at crossover; lag adds low-frequency stiffness. Reference filters are free. Go through the key terms quickly, asking students to say each definition before you reveal it.",
 ["Key terms: cut-off, order, notch, resonance, lead, lag.","Misconception check: filters inside versus outside the loop."],
 [],"Real controllers run on computers. Next: digital control."),
('s2','Refresher: sampling a signal',7,
 "A film is 24 photographs per second, and our eyes see motion. A digital controller is the same: it looks at the signal only at instants k times T, where T is the sample period and f s is one over T. Between samples it holds its output constant: the zero-order hold, which makes the orange staircase. Look at the dashed curve: on average the staircase is the original signal shifted by half a sample. So simply holding costs a delay of T over two. Example: 8 kilohertz sampling gives 125 microseconds, 80 samples per period of a 100 hertz sine.",
 ["ZOH = staircase = T/2 average delay.","Misconception: a fast computer has no delay. The hold itself delays."],
 [],"Where do these samplers sit in a joint controller?"),
('s2','Anatomy of a digital joint controller',7,
 "Trace the loop. The error is computed in the discrete world, inside the dashed box, by a CPU or FPGA. Its output is held by the ZOH, which in a drive means the PWM update. The real world, inverter, motor and link, is continuous. The sampler, an ADC for current or an encoder for position, brings the measurement back. Three facts: the computer sees only samples; the output is held; and computing takes time, so the result is usually applied one sample later. The table shows typical rates: inner loops sample fastest; the robot path planner runs at about 1 kilohertz.",
 ["Inner loops: faster sampling.","Misconception: the robot controller closes the current loop. The drive does, at kHz rates."],
 [],"How much does all this delay cost?"),
('s2','Delay budget',8,
 "Think of a shower with a long pipe: you turn the tap, wait, nothing happens, you turn more, and then it is scalding. Delay makes us overcorrect. Total delay is about one and a half samples: half from the hold, one for computing. Its phase cost at crossover is 360 degrees times f c times T d. Example: 4 kilohertz sampling, 200 hertz crossover. T is 250 microseconds, T d is 375, and the loss is 27 degrees: half a typical margin. At 8 kilohertz it halves to 13.5. The plot shows the lines for other rates.",
 ["Delta phi = 360 f_c T_d; double f_s, halve the loss.","Misconception: a delay only shifts the response in time. In a loop it destroys margin."],
 [("Loss at f_s = 16 kHz, f_c = 200 Hz?","360 x 200 x 93.75e-6 = 6.75 degrees.")],"How do we judge stability of a discrete system?"),
('s2','From the',7,
 "In discrete time a pole is just a number that multiplies the signal each sample: x next equals z times x. If the magnitude of z is below one, every sample is smaller and the signal decays: stable. If it is above one it grows. The map z equals e to the s T sends the left half of the s-plane into the unit circle. Poles near plus one are slow; near minus one they ring at half the sample rate. Example: a pole at minus 70 plus or minus j 71 with one millisecond sampling lands at about 0.93, inside: stable.",
 ["Stable if |z|<1.","Misconception: negative z means stable as in the s-plane. Only the magnitude matters."],
 [],"How does a PID look in code?"),
('s2','Discrete PID',8,
 "Every sample the controller runs only a few lines. The integral is a bucket collecting error: add K i T e each sample. The derivative is the slope between two snapshots of the measurement, filtered, and acting on y instead of e so a set-point step does not cause a kick. Then the output is limited to the maximum current. When it is limited, the anti-windup lines remove the excess from the integrator so it stops growing. Finally the new value goes to the PWM, taking effect in the next period. The grey note mentions Tustin and other discretisation methods.",
 ["Saturation + anti-windup always together.","Misconception: the derivative should act on the error. On y avoids derivative kick."],
 [],"Sampling has another trap: aliasing."),
('s2','Aliasing',7,
 "In films a fast wheel can seem to turn slowly or backwards: the camera samples too slowly. The figure shows a red fast sine and a blue slow sine that give exactly the same samples. Anything above half the sample rate folds back below it: the alias frequency is f minus the nearest multiple of f s. Example: a 4.6 kilohertz vibration sampled at 4 kilohertz looks like 600 hertz, and the controller will happily try to fight a vibration that does not exist. The cure is an analogue filter before the sampler. We return to this in W2D5.",
 ["Filter before sampling, not after.","Misconception: a digital filter can remove aliasing. After sampling it is too late."],
 [("10.5 kHz sampled at 10 kHz?","Looks like 500 Hz.")],"So how fast should we sample?"),
('s2','Choosing the sample rate',7,
 "Here is the same velocity PI with 100 hertz crossover; only the sample rate changes. At 20 and 4 kilohertz the responses are nearly the same, 14 and 16 percent overshoot. At 1 kilohertz the delay is 1.5 milliseconds, the phase loss 54 degrees, and the overshoot 95 percent: almost unstable. Rules of thumb: sample at least 20 to 40 times the loop bandwidth, check 360 f c T d against the margin budget, and sample inner loops faster than outer ones.",
 ["f_s at least 20-40x bandwidth.","Misconception: Nyquist (2x) is enough for control. That is for reconstructing signals, not for loop phase."],
 [],"Check your understanding."),
('s2','Session 2.8 --- Check',5,
 "Two minutes in pairs. Answers: First, T is 62.5 microseconds, T d is 93.75 microseconds, and the loss is 360 times 2000 times 93.75 microseconds, 67.5 degrees: a big part of the margin, which is why current loops need high sampling. Second, z equals 1.05 means each sample is five percent bigger than the last: the signal grows without bound, unstable. Third, at the current limit the motor cannot respond more, the error stays, and the integrator keeps adding it up; when the error finally reverses, the oversized integral causes a big overshoot.",
 ["Use Q1 to rehearse the delay formula."],
 [("Q1","67.5 degrees."),("Q2","Grows 5 % per sample: unstable."),("Q3","Error persists in saturation, integral accumulates.")],"Summary."),
('s2','Session 2.8 --- Summary',4,
 "Five take-aways: sampling plus hold plus computing gives about 1.5 samples of delay; it costs 360 f c T d degrees; discrete poles must be inside the unit circle; a discrete PID needs saturation and anti-windup; and we must filter before sampling to avoid aliasing. Run through the key terms.",
 ["Key terms: sample rate, ZOH, z-plane, anti-windup, aliasing."],
 [],"Now we leave the single motor and look at a whole robot arm."),
('s3','Why a robot arm is harder',7,
 "Draw attention to the two-link arm. Each joint has its own motor and servo loop, just like before. But gravity pulls with a torque that depends on the pose. The inertia that joint one feels changes when joint two folds or stretches. Accelerating one joint pushes on the other: coupling. And the payload changes all of it. The equation on the slide collects this: mass matrix times acceleration, plus Coriolis and centrifugal terms, plus gravity, equals the motor torques. Do not derive it; it returns in W2D2. Today we only use its structure.",
 ["Three effects: pose-dependent gravity, pose-dependent inertia, coupling.","Misconception: a robot is just six independent motors."],
 [],"Despite this, most industrial robots use a simple approach."),
('s3','Independent-joint control',7,
 "Independent-joint control treats every joint as its own single-input single-output servo, using everything from W1D3. The effects of the other joints and gravity are lumped into a disturbance that the PID rejects. Why does this work? The gearbox. Reflected load inertia is divided by N squared. Example: motor inertia 3 times ten to the minus 4, link inertia varying from 0.8 to 3.3, gear ratio 100. Divided by ten thousand the link adds only 0.8 to 3.3 times ten to the minus four, so the total varies by a factor 1.7 instead of 4. High gear ratios hide the coupling.",
 ["J_eff = J_m + J_link/N^2.","Misconception: direct-drive robots are simpler to control. They feel all the coupling."],
 [],"Where does that inertia variation come from?"),
('s3','The inertia a joint feels',6,
 "The plot shows the shoulder inertia of our two-link arm versus elbow angle, computed for 5 kilogram, half-metre links. Stretched out it is 3.3 kilogram square metres, folded only 0.8: four times less. Ask a student to imagine spinning on an office chair with arms out, then pulling them in: same mass, but you spin faster. The elbow, in orange, always sees the same value. With fixed PID gains the shoulder would be sluggish when stretched and nervous when folded. Remedies: a high gear ratio, gain scheduling with the elbow angle, or model-based control.",
 ["Same mass, different inertia: the pose matters.","Misconception: inertia is a constant property of a robot."],
 [],"The second pose-dependent effect is gravity."),
('s3','Gravity torque on a joint',6,
 "Hold a broom horizontally by one end: hard. Hold it upright: easy. Gravity acts at the centre of mass, and its lever arm is l c times cos q. So the torque is m g l c cos q. With 2 kilograms at 0.25 metres: horizontal 4.9 newton metres, at 60 degrees half of it, 2.45, and vertical zero. Ask students where a robot needs the most holding torque: arm horizontal and stretched. This torque is constant in time for a held pose, so it acts like a constant disturbance on the joint loop.",
 ["tau_g = m g l_c cos q, with q from horizontal.","Misconception: gravity torque is constant. It depends on the angle."],
 [("Torque at 30 degrees?","4.9 x 0.866 = 4.2 N m.")],"What does this constant torque do to a PD controller?"),
('s3','Gravity compensation',8,
 "With plain PD the arm sags until the proportional torque balances gravity: error equals tau g over K p, about 4.4 over 100, 0.044 radians or 2.5 degrees, as the red curve shows. PID removes the sag, but the dashed curve needs well over a second and overshoots. Gravity compensation simply adds the modelled gravity torque to the PD output; the blue curve reaches the target with no sag at all. Picture a desk lamp with a spring: the spring carries the weight, your hand only positions it. Almost every industrial robot controller does this.",
 ["Use the model for what you know; feedback for what you do not.","Misconception: integral action is the only way to remove steady error."],
 [],"Taking this idea all the way gives computed torque."),
('s3','Computed-torque control',6,
 "Computed torque takes the gravity idea to its end. The outer PD, plus the planned acceleration as feedforward, produces a desired acceleration a. The robot model then computes the torque needed for that acceleration in the current pose, including inertia, coupling and gravity. Together, model plus robot behave like a simple double integrator for every joint, so one fixed PD works in every pose. The catch: it is only as good as the model. A wrong payload mass leaves an error that feedback must clean up. It requires drives in torque mode.",
 ["Model cancels the nonlinearity; PD handles the rest.","Misconception: with a perfect model, no feedback is needed. Models are never perfect."],
 [],"So far the robot moved in free space. What happens at contact?"),
('s3','When the robot touches things',6,
 "Position control is stiff: if the robot is commanded one millimetre into a steel part, it pushes with huge force. For contact tasks we have two families. Force control regulates the contact force directly, as in polishing or insertion. Impedance control, introduced by Hogan, makes the tool behave like a chosen spring and damper attached to the set-point. Think of a handshake: you do not dictate the exact position of the hand, you stay springy. Example: set-point 20 millimetres behind the surface, stiffness 500 newtons per metre: about 10 newtons of contact force.",
 ["Impedance: we choose K and D; the force follows.","Misconception: force control and impedance control are the same."],
 [],"Let us compare a soft and a stiff impedance."),
('s3','Impedance control: soft',6,
 "Both simulations push a 2 kilogram tool towards a surface at 100 millimetres, with the set-point 20 millimetres behind it. The soft setting, 500 newtons per metre, arrives slowly and settles at about 10 newtons of force. The stiff setting, 5000, hits fast and settles near 80 newtons. The force is set by our chosen stiffness, not by knowing the exact surface position, which is why impedance control tolerates position errors. Collaborative robots like the one in the photo use low stiffness near people; the limits come from ISO TS 15066, covered in W2D4.",
 ["Contact force about K times the set-point offset (for a stiff surface).","Misconception: stiffer control is always more accurate and therefore better."],
 [],"Check your understanding."),
('s3','Session 2.9 --- Check',4,
 "Two minutes. Answers: First, the sag equals gravity torque over K p, and gravity torque is m g l c cos q: maximal when horizontal, zero when pointing straight up, so no sag there. Second, with 100 to 1 gearboxes the link inertia and coupling are divided by ten thousand, so each joint looks almost like a constant motor inertia; a direct drive feels the full variation and coupling, so model-based control is needed. Third, wiping needs a gentle, roughly constant contact force despite an uneven table: impedance control, with low stiffness.",
 ["Link answer 2 back to reflected inertia from W1D2."],
 [("Q1","Gravity torque proportional to cos q."),("Q2","N^2 hides variation."),("Q3","Impedance control.")],"Summary of 2.9."),
('s3','Session 2.9 --- Summary',4,
 "Five take-aways: joints are coupled and inertia and gravity depend on the pose; independent-joint PID with high gear ratios is the industrial standard; gravity compensation removes sag immediately; computed torque cancels the dynamics with a model; impedance control makes contact safe. Point out that the last two need the drive to deliver torque on command, which leads straight into the servo system after the break.",
 ["Key terms: independent-joint, coupling, gravity compensation, computed torque, impedance, force control."],
 [],"After the break: what is inside a servo system?"),
('s4','What is a servo system',7,
 "Servo comes from the Latin servus, servant: a motor system that obeys a command using feedback. Three parts: the servo motor, usually a permanent-magnet synchronous motor with encoder and brake; the servo drive with power electronics, control loops and protection; and the motion controller that plans the moves of all axes. The taxi analogy: the passenger says where to go, the driver handles pedals and steering, the engine does the work. The photo shows an industrial drive and motor pair.",
 ["Controller plans, drive executes, motor converts.","Misconception: a hobby RC servo and an industrial servo are the same thing. The principle is, the scale and performance are not."],
 [],"Let us follow the energy and the signals."),
('s4','Servo system architecture',8,
 "Follow the thick arrows for energy: mains, power supply giving DC, the drive with its DC bus and inverter, the three motor phases U V W, motor, gearbox, link and payload. Then the thin arrows for information: the robot controller sends targets over a fieldbus like EtherCAT every quarter to four milliseconds; the drive closes the fast loops up to tens of kilohertz; the encoder feeds back to the drive. The photo shows compact drives side by side, sharing a DC bus. Ask: where does each loop of this morning live? The fast ones in the drive.",
 ["Two flows: energy (thick) and information (thin).","Misconception: the fieldbus carries the current-loop signals. It carries set-points only."],
 [],"In a robot, this whole chain sits inside each joint."),
('s4','Inside a robot joint',8,
 "A typical robot joint, sketched here, contains the encoder, a holding brake, the PMSM motor, a harmonic gearbox and the output flange driving the next link; cobots often integrate the drive in the same housing, with power and EtherCAT cables running through the arm. A six-axis robot is therefore six complete servo axes, coordinated by one controller. The brake keeps the arm from falling when power is off. Gear ratios of 50 to 160 are common, which is why independent-joint control works so well. The photos show an industrial arm and a strain-wave gear set.",
 ["One joint = one servo axis.","Misconception: the brake is used to stop motion. It is a holding brake for power-off."],
 [],"Which loops does the drive close? That is the control mode."),
('s4','Torque, velocity and position',8,
 "Three modes. In torque mode the controller sends a torque and the drive closes only the current loop, kilohertz bandwidth. That is what computed-torque and impedance control need, and what cobots use. In velocity mode the drive adds a velocity loop: AMR wheels, conveyor tracking. In position mode it closes all three loops: classic industrial joints and gantries. Analogy: tell a driver to press the pedal this much, to drive at 50, or to stop at that line. Selection rule: close each loop where its sensor is and where it can be updated fast enough.",
 ["Mode = which loops the drive closes.","Misconception: position mode is always best. Model-based robot control needs torque mode."],
 [],"Inside the drive these loops are nested."),
('s4','Cascade control structure',10,
 "Read the diagram from the left: position error into a P gain, giving a velocity command; velocity error into a PI, giving a current command; current error into another PI, giving a voltage via the PWM inverter. Then the motor: winding, k t, inertia, integrator. Three feedback paths, nested like Russian dolls. Each inner loop turns its part into something simple for the next: the current loop makes the motor an ideal torque source. Inner loops are three to ten times faster. Tune from the inside out. The orange dashed paths are feedforward, including gravity torque from session 2.9.",
 ["Inner loops faster; tune inside-out.","Misconception: one big PID could do the same. Cascades handle limits and disturbances far better."],
 [],"Let us see the speeds side by side."),
('s4','The bandwidth hierarchy',8,
 "The plot shows the closed-loop responses: current loop around 2 kilohertz, velocity about 250 hertz, position about 40 hertz, each defined at the minus 3 dB line. What limits each? The current loop is limited by PWM and sampling delay, the velocity loop by inertia, resonances and encoder noise, the position loop by the velocity loop beneath it. The separation of three to ten times lets each outer loop see the inner one as practically instant. W1D5 tunes these loops step by step.",
 ["Bandwidth = -3 dB point of the closed loop.","Misconception: the position loop can be tuned faster than the velocity loop."],
 [],"Check."),
('s4','Session 3.1 --- Check',6,
 "Two minutes. Answers: First, the controller computes torques, so the joints must run in torque mode, with the drive closing only the current loop. Second, if the position loop is faster than the velocity loop it asks for corrections the inner loop cannot deliver; the inner loop is no longer 'instant', its lag enters the outer loop and the axis oscillates or goes unstable. Third, the current loop is the innermost; the outer loops' design assumes it works, so it must be tuned first, from the inside out.",
 [],[("Q1","Torque mode."),("Q2","Inner loop too slow: oscillation."),("Q3","Inside-out.")],"Summary."),
('s4','Session 3.1 --- Summary',5,
 "Summarise: a servo is supply, drive, motor, gearbox, load, encoder and controller. A robot joint is one complete servo axis. The mode is which loops the drive closes. And in the cascade, current is much faster than velocity, which is much faster than position. Ask a student to sketch the cascade from memory on the board in thirty seconds.",
 ["Key terms: servo drive, motion controller, control mode, cascade, feedforward, bandwidth."],
 [],"Last session: how does the drive actually make the motor voltage?"),
('s5','Refresher: diode, capacitor',5,
 "Three components. The diode is a one-way valve: current only from anode to cathode, which lets us turn AC into DC. The capacitor is an energy tank, half C V squared, smoothing voltage and buffering current. The transistor is a tap opened by a small gate signal, and in drives it is used only fully on or fully off. Why? Power loss is V times I in the switch. At 10 amps: on, 1.5 volts, 15 watts; off, no current, zero. Half-way, 280 volts across it: 2.8 kilowatts. It would melt.",
 ["Switches are used only on or off.","Misconception: transistors in drives work like a dimmer resistor."],
 [],"Let us put these parts together."),
('s5','Power stage of a servo drive',5,
 "This is the whole power stage. From the left: the three mains phases into a six-diode rectifier. A pre-charge resistor, bypassed after start-up, limits the inrush current. The big capacitor holds the DC bus voltage. Then the brake chopper: a transistor and resistor that burn surplus energy. Finally the three-phase inverter: six transistors with freewheeling diodes, making the motor voltages U V W. The story is AC to DC to AC: we first make a stiff DC bus, then chop it into any amplitude and frequency we want.",
 ["AC -> DC -> AC.","Misconception: the motor is connected to the mains through the drive. It is fed from the DC bus."],
 [],"First stage: the rectifier."),
('s5','Rectifier and DC bus',6,
 "The diodes always connect the highest of the six line-to-line voltages, giving the bumpy orange curve. Its average is 1.35 times the line voltage: 540 volts on a 400 volt mains. With the capacitor, the bus charges to the peak, root 2 times 400, about 566 volts. The capacitor smooths the bumps; the pre-charge resistor protects it at power-on; and importantly, diodes cannot send energy back to the mains. Small robots and AMRs skip all this: their 24 to 48 volt battery is the DC bus.",
 ["V_dc about 1.35 V_LL; peak root 2 V_LL.","Misconception: the DC bus is 400 volts on a 400 volt mains."],
 [("DC bus on 230 V line-to-line?","About 310-325 V.")],"Now: how do switches make a variable voltage?"),
('s5','PWM: duty cycle',6,
 "Flick a light switch on and off very fast, and the room looks evenly dimmed. PWM, pulse-width modulation, switches fully on and off at a fixed rate and varies the on-time. The duty cycle D is on-time over period, between 0 and 1, and the average voltage is D times V d c. The motor inductance smooths the current like a flywheel. Example for a 48 volt robot joint at 20 kilohertz: period 50 microseconds, on for 15, D is 0.3, average 14.4 volts. Changing D slowly gives a slowly changing average: for example a sine.",
 ["v_bar = D V_dc.","Misconception: the motor sees 48 V pulses as harmful. Inductance averages them."],
 [("D for 12 V from 48 V?","0.25.")],"Three legs give three phases."),
('s5','Three-phase inverter',7,
 "Each leg has two switches that must never be on together. We compare a reference sine for each phase with a fast triangle. Where the sine is above the triangle, the upper switch is on. So the duty cycle follows the sine, and the filtered line-to-line voltage, orange in the bottom plot, is a clean sine. The peak phase voltage is the modulation index m times V d c over two. With m between 0 and 1 the drive sets amplitude; with the sine's frequency it sets motor speed. Tomorrow's FOC decides which sine to make.",
 ["Sine vs triangle comparison.","Misconception: the inverter output is a true sine. It is pulses whose average is a sine."],
 [],"The inverter has limits, and they shape the motor's capability."),
('s5','Voltage and current limits',6,
 "Two limits shape the torque-speed envelope. The current limit, from switch and winding heating, caps the torque: 14.4 newton metres here, the flat part. The voltage limit: back-EMF grows with speed, and the inverter can give at most about V d c over root 3 per phase. Example: 325 volt bus gives 188 volts; with a flux of 0.12 weber, electrical speed is at most about 1560 radians per second, with 4 pole pairs about 3730 rpm at no load. Under load the resistance and inductance drops lower the base speed to about 3240 rpm.",
 ["Current limit = torque; voltage limit = speed.","Misconception: more current gives more speed. Speed is limited by voltage."],
 [],"What happens when the motor brakes?"),
('s5','Regeneration and the brake chopper',7,
 "When a robot lowers a heavy part or brakes hard, the motor becomes a generator and pushes energy into the DC bus. Worked example: 0.05 kilogram square metres from 3000 rpm to zero in half a second. Kinetic energy: 2.47 kilojoules. The capacitor, going from 565 to 780 volts, only absorbs 145 joules. Peak power 9.9 kilowatts. So a brake resistor must take it: at most 780 squared over 9870, 62 ohms; choose 56. The plot shows the chopper switching on at 780 volts and off at 760, holding the bus.",
 ["Diode rectifier cannot return energy: the resistor must burn it.","Misconception: the capacitor can store braking energy. Only a few percent."],
 [],"Last hardware slide: the switches themselves."),
('s5','Power switches and dead time',6,
 "Three technologies. Silicon IGBTs for 400 volt drives, switching at 4 to 16 kilohertz. Silicon MOSFETs for low-voltage drives up to about 250 volts, like cobots and AMRs, very fast. Silicon-carbide MOSFETs: high voltage and fast, in compact modern drives. The photo shows an opened IGBT module with chips and bond wires. Because both switches in a leg must never conduct together, a short dead time with both off is inserted at each change, avoiding shoot-through. Its price is a small voltage error: one microsecond at 16 kilohertz and 325 volts gives 5.2 volts.",
 ["Dead time prevents shoot-through, costs a small voltage error.","Misconception: faster switching is always better. It raises losses and EMI."],
 [],"Check your understanding."),
('s5','Session 3.2 --- Check',4,
 "Two minutes. Answers: First, a half-on transistor has both voltage across it and current through it, so it dissipates kilowatts and would overheat; on or off, one of the two is nearly zero. Second, D equals 12 over 48, 0.25. Third, during lowering the motor regenerates energy into the bus; with a diode rectifier it cannot go back to the mains, so the brake chopper or brake resistor is missing, too small, or faulty.",
 [],[("Q1","Loss V x I huge in the linear region."),("Q2","D = 0.25."),("Q3","Brake chopper / resistor.")],"Summary."),
('s5','Session 3.2 --- Summary',4,
 "Five take-aways: rectifier, DC bus, brake chopper, inverter, motor; V d c is about 1.35 times the line voltage; PWM average is D times V d c and the inverter makes sines from it; the current limit sets torque and the voltage limit sets speed; braking energy goes into the resistor. Run through key terms.",
 ["Key terms: DC bus, inverter, PWM, duty cycle, regeneration, brake chopper, shoot-through."],
 [],"Let us wrap up the day."),
('s5','Day summary',2,
 "Recap both halves. Control: filters cost phase, notches remove resonances, lead buys phase back, sampling delay costs 360 f c T d, and robot arms need gravity compensation and, for demanding tasks, model-based or impedance control. Hardware: one servo axis per joint, three control modes, cascaded loops, and the power stage from rectifier to inverter. Read the one-sentence summary aloud.",
 ["The one-sentence summary ties the day together."],[],"Tomorrow we go deeper into the drive."),
('s5','Preview of W1D5',2,
 "Tomorrow: field-oriented control, the way the drive makes a PMSM behave like a DC motor using d and q currents; then the cascaded loops in detail, their tuning, and trajectory generation with feedforward. Ask students to bring three things: the delay formula, the cascade picture and the PWM average-voltage formula.",
 [],[],"Thank you; figure credits and references follow."),
]

def card(p, c):
    _, title, mins, say, emph, asks, trans = c
    e = ''.join(f'<li>{html.escape(x)}</li>' for x in emph)
    a = ''.join(f'<li><b>Q:</b> {html.escape(q)} <b>A:</b> {html.escape(ans)}</li>' for q, ans in asks)
    s = f'<div class="slide">\n  <h3><span class="num">Slide {p}</span>{html.escape(title)}<span class="time">~{mins} min</span></h3>\n  <p class="say">{html.escape(say)}</p>\n'
    if e: s += f'  <div class="key"><span class="label">Emphasise</span><ul>{e}</ul></div>\n'
    if a: s += f'  <div class="ask"><span class="label">Ask the audience / likely questions</span><ul>{a}</ul></div>\n'
    s += f'  <p class="trans">Transition: {html.escape(trans)}</p>\n</div>\n'
    return s

def main():
    pages = page_titles()
    used = set(); pg = {}
    for i, c in enumerate(C):
        key = c[1]
        hits = [p for p, t in pages.items() if key in t and p not in used and p > 1]
        if not hits: raise SystemExit(f'not found: {key}')
        p = min(hits); used.add(p); pg[i] = p
    # per-session minutes check
    tot = {}
    for c in C: tot[c[0]] = tot.get(c[0], 0) + c[2]
    for k, v in S.items():
        assert tot[k] == v[2], (k, tot[k], v[2])
    assert sum(tot.values()) == 300
    body = []
    rows = ''
    for k, (name, code, mins) in S.items():
        ps = [pg[i] for i, c in enumerate(C) if c[0] == k]
        rows += f'<tr><td>{code}</td><td>{html.escape(name)}</td><td>{min(ps)}–{max(ps)}</td><td>{mins} min</td></tr>\n'
        if k in ('s1', 's2', 's3', 's4'):
            rows += '<tr><td></td><td><i>Break (extra)</i></td><td></td><td>10 min</td></tr>\n'
        sec = f'<section id="{k}">\n<h2 class="session">{html.escape(name)} <small>{"Curriculum code " + code if k != "s0" else "Opening"} · {mins} min</small></h2>\n'
        sec += ''.join(card(pg[i], c) for i, c in enumerate(C) if c[0] == k)
        body.append(sec + '</section>\n')
    nav = '<a href="#plan">Plan</a>' + ''.join(f'<a href="#{k}">{html.escape(v[0])}</a>' for k, v in S.items())
    out = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>W1D4 Speaker Notes</title>
{STYLE}
</head>
<body>
<header><div class="wrap">
  <div class="day">WEEK 1 · DAY 4 / 5 · SPEAKER NOTES</div>
  <h1>Control (cont.) and Servo Systems I</h1>
  <p>Mechatronics and Robotics Engineering (50 h) · 5 h net teaching time</p>
</div></header>
<nav class="toc">{nav}</nav>
<main>
  <section id="plan">
    <h2 class="session">Day plan &amp; timing</h2>
    <table class="plan"><tr><th>Block</th><th>Topic</th><th>Slides</th><th>Duration</th></tr>
{rows}<tr><td></td><td><b>Net teaching time</b></td><td></td><td><b>300 min</b></td></tr>
    </table>
    <p>Slide numbers are PDF page numbers (section divider pages included). Figure credits and references (last pages) need no notes.</p>
  </section>
{''.join(body)}</main>
<footer>Figures and references are listed on the final slides of the deck.</footer>
</body>
</html>
'''
    (HERE / 'w1d4_speaker_notes.html').write_text(out)
    print('cards', len(C), 'pages', sorted(pg.values()))

main()
