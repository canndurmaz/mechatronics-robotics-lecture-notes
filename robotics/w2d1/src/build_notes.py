#!/usr/bin/env python3
"""Builds w2d1_speaker_notes.html from common/notes_template.html (style copied verbatim)."""
import os, re, html
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
tpl = open(os.path.join(ROOT, 'common', 'notes_template.html'), encoding='utf-8').read()
style = re.search(r'<style>.*?</style>', tpl, re.S).group(0)

# session: (id, title, code, minutes)
# card: (title, minutes, say, emphasise(list), ask(list of (q,a)), transition)
S = []
def sess(sid, title, code, mins): S.append({'id': sid, 'title': title, 'code': code, 'min': mins, 'cards': []})
def card(t, m, say, emph, ask, trans): S[-1]['cards'].append((t, m, say, emph, ask, trans))

# ---------------------------------------------------------------- opening
sess('s0', 'Opening and Week 1 recap', 'Agenda · recap', 10)
card('Agenda and learning outcomes', 3,
 "Welcome to the second week. Last week we built one servo axis from the inside: the motor, the gearbox, the drive and its control loops. This week we put many axes together and get a robot. Today has four blocks. First we finish the servo story with resonance, because robot joints are springy. Then we look at what robots look like and how we classify them. After that comes the mathematics of position, rotation matrices and homogeneous transforms, and finally forward kinematics, which tells us where the tool is when we know all the joint angles. Read the five outcomes aloud; they are what students should be able to do tonight.",
 ["Today is a bridge day: the last servo topic, then the first robot-mechanism topics.", "Misconception: kinematics is not 'just geometry homework'; every robot controller computes it every millisecond."],
 [("Who has seen an industrial robot in real life?", "Use the answers to collect examples you can refer back to in 4.1.")],
 "Before we start, a quick look back at Week 1.")
card('What we learned in Week 1 (1/2)', 4,
 "Let us refresh the actuator and control part of last week. A motor turns current into torque with the torque constant. A gearbox trades speed for torque, and the load inertia seen by the motor shrinks with the square of the ratio, just like a low bicycle gear makes a steep hill feel easy. Robot joints use harmonic or cycloidal gears: high ratio, little backlash, but they are not perfectly stiff, and that finite stiffness is exactly where today begins. On the control side we built models, transfer functions, PID loops, Bode plots and margins, and we added filters and digital implementation.",
 ["Keep the phrase 'finite stiffness' on the board: it is the hook for session 3.7.", "Misconception: a gearbox with no backlash is not automatically rigid."],
 [("What does the load feel like to the motor through a 100:1 gear?", "Its inertia is divided by 100 squared, i.e. 10 000.")],
 "Now the servo-drive part of the week.")
card('What we learned in Week 1 (2/2)', 3,
 "The servo drive makes the motor voltage with an inverter and PWM; field-oriented control makes torque proportional to the q-axis current; and the cascade of current, velocity and position loops is tuned from the inside out. Feedforward from the trajectory removes most of the following error. Everything last week assumed the load is rigid. Today we drop that assumption first, then we zoom out from one axis to the whole arm. The four boxes on the right are today's path: springy joint, robot types, frames and transforms, and finally joint angles to tool pose.",
 ["The rigid-load assumption is about to be broken on purpose."],
 [("Which loop is innermost and fastest?", "The current (torque) loop.")],
 "Let us start with why robot joints are springy.")

# ---------------------------------------------------------------- 3.7
sess('s1', 'Resonance, compliance and notch filters in robot joints', '3.7', 50)
card('Why robot joints are springy', 5,
 "Last week we treated motor and arm as one rigid body. In reality every element between the motor and the tool bends a little. The flexspline in a harmonic drive is a thin steel cup that deforms on purpose; belts stretch; shafts twist; long aluminium links bend. Mass plus spring plus very little damping gives a system that can ring. Use the fishing-rod analogy: move the handle slowly and the tip follows; flick it quickly and the tip whips back and forth. The servo controller is the hand on the handle, and if we turn the gains up the controller starts flicking.",
 ["Compliance is everywhere; the question is only at which frequency it bites.", "Misconception: 'stiff enough' is not a yes/no property; it depends on how fast we want to move."],
 [("Where in your own body is there compliance?", "Tendons and muscles; that is why a fast arm motion overshoots slightly.")],
 "To quantify this we need the natural frequency of a mass on a spring.")
card('Refresher: natural frequency of a mass on a spring', 4,
 "This is a refresher from W1D2. Pull a mass on a spring and let go: it oscillates at its natural frequency, square root of k over m. A swing is the same idea: push in rhythm and the motion builds up, that is resonance. For rotation, replace mass by inertia J and the spring by a torsional stiffness in newton-metres per radian. Walk through the example: one kilogram, one hundred newtons per metre, gives ten radians per second or about 1.6 hertz. Stiffer means higher frequency, heavier means lower.",
 ["Radians per second versus hertz: divide by 2π.", "Misconception: resonance is not caused by a large force but by forcing at the right frequency."],
 [("Double the mass: what happens to f_n?", "It drops by √2, about 30 %.")],
 "A real joint has two inertias, motor and load, joined by the spring.")
card('The two-mass model and its two special frequencies', 6,
 "Draw the motor inertia on the left, the load inertia on the right and a spring between them. This system has two special frequencies. At the anti-resonance the load swings while the motor stands almost still, so the motor encoder sees nothing. At the resonance motor and load swing against each other. The anti-resonance depends only on spring and load; the resonance is higher by the square root of one plus the inertia ratio. Step through the example slowly: 159 hertz for the anti-resonance, ratio five, factor 2.45, giving 390 hertz for the resonance.",
 ["Inertia ratio R = J_L/J_M is the key number.", "Misconception: students often think the motor sees the resonance at f_AR; it sees a dip there and a peak at f_R."],
 [("If R = 0 (no load), what is f_R?", "f_R = f_AR: the factor √(1+R) becomes 1; in practice the system is then rigid.")],
 "What does this look like in a time plot?")
card('What resonance looks like in time', 5,
 "Here we push the same two-mass system with a short torque pulse. A rigid body would ramp up and then stay at 2.5 radians per second, the dashed line. Instead the motor and load speeds swap energy through the spring: when the motor is fast the load is slow and vice versa, at 390 hertz. Because damping is small, the ringing decays slowly. The important practical point is in the grey box: the encoder sits on the motor, so the controller sees the blue curve, but the customer cares about the tool, which is the orange curve.",
 ["The controller measures the motor, not the tool.", "Misconception: a quiet motor encoder does not prove the tool is quiet."],
 [("Why do both curves end around 2.5 rad/s?", "Momentum: impulse 0.36 N·m × 5 ms divided by total inertia 7.2e-4 kg·m².")],
 "Now the same system in the frequency domain.")
card('Frequency response of the two-mass system', 5,
 "This is the Bode magnitude from motor torque to motor speed. At low frequency the curve sits on the rigid-body line with slope minus twenty dB per decade. Then there is a dip at the anti-resonance and a sharp peak at the resonance. Above the resonance only the motor moves, so the gain jumps up by one plus R, six times or about 15.6 dB. A large inertia ratio means a big jump and a hard tuning problem. Remind students of the dB rule in the box: plus twenty is ten times, plus six is about twice.",
 ["The peak is what the velocity loop trips over.", "Misconception: the dip is not a 'good' feature; it hides the load motion from the controller."],
 [("A peak of +20 dB means what gain factor?", "Ten times.")],
 "Let us put this plant inside the velocity loop.")
card('What the velocity loop sees', 5,
 "The velocity loop was tuned for fifty hertz bandwidth on a rigid model, the dashed curve. With the real two-mass plant, red, the resonance lifts the loop gain above zero dB at 390 hertz, where the phase is already far below minus 180 degrees. The loop therefore amplifies that frequency and the axis buzzes. The blue curve adds a notch filter centred on the resonance: the peak is pushed back below zero dB. The price is a little phase lost near the crossover, about nine degrees, which the margins can usually afford.",
 ["A second 0 dB crossing at bad phase means instability or ringing.", "Misconception: lowering all gains is not the only cure; a targeted filter keeps the bandwidth."],
 [("Why is the phase so low at 390 Hz?", "Integrator-like plant, current-loop lag, sampling delay and the resonance itself all add lag.")],
 "So what exactly is a notch filter?")
card('The notch filter: cutting out one frequency', 5,
 "A notch, or band-stop filter, removes a narrow band around its centre frequency and passes everything else at zero dB. It sits in the torque command, after the velocity controller and before the current loop. It has two settings beyond the centre: the depth, how much it cuts, and the width, how many hertz it covers. A wide notch is robust if the resonance drifts, but it costs more phase at low frequency. The biquad formula is in the going-further line; it is enough to know the drive offers centre, width and depth as parameters.",
 ["Centre on f_R, then choose width from how much f_R moves.", "Misconception: a deeper notch is not always better; width matters more for robustness."],
 [("Where is the notch placed in the cascade?", "In the torque/current reference, between velocity controller and current loop.")],
 "When should we use a notch and when a low-pass?")
card('Notch or low-pass? Setting up the filter', 5,
 "A low-pass filter is the right tool against broad high-frequency noise, such as encoder quantisation or many small modes. But look at the plot: at 390 hertz a one-kilohertz low-pass cuts almost nothing. A notch targets one narrow peak. The recipe on the right is what technicians do: measure the frequency response at low gain, read the peak, check it in several poses and payloads, set the notch, widen if needed, and only then raise the gain again. The rule of thumb: keep the notch several times above the loop bandwidth, otherwise no filter helps and the mechanics must change.",
 ["Measure first, filter second.", "Misconception: a filter cannot fix a resonance close to the loop bandwidth."],
 [("Your resonance is at 60 Hz and the bandwidth 50 Hz. What do you do?", "Stiffen the mechanics or lower the bandwidth; a notch would eat too much phase.")],
 "Robots add one more complication: the resonance moves.")
card('Robot joints: the resonance moves with pose and payload', 5,
 "Now a real robot shoulder. Through a 100-to-1 harmonic gear, the small motor inertia appears at the joint as 1.5 kilogram square metres. The arm adds two. The joint stiffness is twenty thousand newton-metres per radian. Walk through the four steps: anti-resonance 15.9 hertz, ratio 1.33, resonance 24 hertz. These are low frequencies compared with a machine tool. The plot shows that adding payload at the tool lowers both frequencies, and stretching the arm out does the same. That is why robot drives use wide notches, gain scheduling or input shaping of the trajectory.",
 ["Robot resonances are typically 5–30 Hz and pose dependent.", "Misconception: a notch tuned in one pose is not automatically right in another."],
 [("Why does the gear make the motor look so heavy?", "Reflected inertia scales with N²: 1.5e-4 × 10 000 = 1.5 kg·m².")],
 "Time for a short check.")
card('Check your understanding – 3.7', 3,
 "Give students two minutes in pairs, then collect answers. Answers: one, f_AR is proportional to one over the square root of J_L, so four times the inertia halves f_AR. Two, at 390 hertz a low-pass placed high enough to keep the 50 hertz loop healthy cuts almost nothing, and one placed low enough to cut 390 hertz would destroy the phase margin at 50 hertz; the notch cuts only the narrow band. Three, a heavy part increases the load inertia, so the joint resonance goes down.",
 ["Let students explain to each other before you give answers."],
 [("Answers", "1) f_AR halves. 2) LPF either too weak at 390 Hz or too costly at 50 Hz; notch is selective. 3) Down.")],
 "Let us summarise 3.7.")
card('Summary 3.7 – Resonance and notch filters', 2,
 "Read the five take-aways. A compliant joint is motor inertia plus spring plus load inertia. The two formulas give the dip and the peak. The peak can push the loop gain above zero dB and cause ringing. Notch for one narrow peak, low-pass for broad noise. And in robots the resonance changes with pose and payload, so fix the mechanics first and filter second. Point at the key-terms box and ask students to define two of the terms in their own words.",
 ["Mechanics first, filter second."],
 [], "Now we leave the single joint and look at the whole robot.")

# ---------------------------------------------------------------- 4.1
sess('s2', 'Robot anatomy and classification', '4.1', 60)
card('Anatomy of a robot arm', 6,
 "Use the students' own arm as the model. Links are the bones, joints are the body joints, and each joint has a motor, gearbox and encoder, everything from Week 1. The base is fixed to the floor, the wrist orients the tool, and the end-effector or end-of-arm tooling is the gripper, torch or suction cup from W1D2. A serial robot is one chain: base, link, joint, link, and so on to the tool. Ask students to count the joints in their arm: shoulder three, elbow one, wrist three, roughly seven.",
 ["Every joint is a complete servo axis from Week 1.", "Misconception: the gripper is not part of the robot's DOF count; it is a separate tool."],
 [("How many joints in your arm, shoulder to wrist?", "About seven: 3 + 1 + 3.")],
 "What kinds of joints exist?")
card('Joint types: revolute and prismatic', 6,
 "There are two basic joint types. A revolute joint rotates, like a door hinge, and its variable is an angle theta in radians. A prismatic joint slides, like a drawer, and its variable is a stroke d in metres. Each has one degree of freedom. More complex joints, such as a ball joint with three, are built from revolute joints in practice. The joint variables together form the joint vector q. We name robots by their joint string from base to wrist: a SCARA starts R R P, a gantry is P P P.",
 ["Joint variable: θ for R, d for P.", "Misconception: a prismatic joint is not 'less of a joint'; it counts as one DOF just like R."],
 [("What joint type is a lift door? A laptop hinge?", "Prismatic; revolute.")],
 "How many joints does a robot need?")
card('Degrees of freedom (DOF)', 7,
 "A free body in space can move in six independent ways: three translations and three rotations, often called roll, pitch and yaw. In a plane only three. To place a tool anywhere with any orientation, a robot therefore needs six joints. Seven or more is redundant, like your arm: you can move your elbow while your hand stays on the table. Grübler's formula counts mobility for linkages; walk through the three examples: the planar two-link arm has two, a four-bar linkage has one, and a six-axis arm has six.",
 ["6 DOF for full position and orientation.", "Misconception: more joints is not always better; redundancy costs mass, cost and computation."],
 [("Can a 5-axis robot reach any pose?", "No: one orientation (or position) direction is then constrained.")],
 "Where can the tool actually reach?")
card('Workspace: where can the tool reach?', 6,
 "The workspace is the set of points the tool can reach. For the planar two-link arm with full rotation, it is a ring: outer radius the sum of the link lengths, inner radius their difference. With 0.4 and 0.3 metres that is 0.1 to 0.7 metres, so a part at 0.75 metres is simply out of reach. The dexterous workspace, where any orientation is possible, is smaller. Real joint limits caused by cables and self-collision shrink it further. Data sheets show the workspace as a side-view drawing.",
 ["Reach = ℓ1 + ℓ2; the hole = |ℓ1 − ℓ2|.", "Misconception: equal links do not leave a hole; the inner radius is zero."],
 [("When does the ring have no hole?", "When ℓ1 = ℓ2.")],
 "Now let us meet the main robot families.")
card('Articulated arms and SCARA robots', 6,
 "On the left the articulated arm, six revolute joints, the classic industrial robot that looks like a human arm. It has a large, roughly spherical workspace and is used for welding, painting, machine tending and palletising. On the right the SCARA: two revolute joints with vertical axes, a vertical slide and a tool rotation. It is stiff vertically but slightly compliant sideways, which helps insert a pin into a hole. SCARAs are very fast for small pick-and-place and assembly on a table.",
 ["SCARA = Selective Compliance Assembly Robot Arm.", "Misconception: SCARA's compliance is deliberate and small, not a weakness."],
 [("Which robot would you use to screw parts on a PCB?", "A SCARA.")],
 "Two more families: Cartesian and parallel robots.")
card('Cartesian / gantry and delta (parallel) robots', 6,
 "The Cartesian or gantry robot has three linear axes, so its workspace is a box and its kinematics is trivial: each axis is one coordinate. It scales easily from a 3D printer to a palletising gantry spanning a hall, as in the photo. The delta robot is a parallel robot: three arms work together on one light platform. All motors stay on the fixed base, so the moving mass is tiny and it can pick hundreds of items per minute from a conveyor, typical in food and pharmaceutical packaging.",
 ["Gantry: simple maths, big box. Delta: tiny moving mass, very fast.", "Misconception: a gantry is still a robot, even if it looks like a crane."],
 [("Why can a delta robot accelerate so hard?", "The motors don't move; only light carbon rods and the platform do.")],
 "Let us compare serial and parallel structures directly.")
card('Serial vs. parallel kinematic chains', 6,
 "A serial chain is open: one path from base to tool, and each joint must carry all the motors after it. Errors and compliance add up along the chain, but the workspace is large. A parallel chain has closed loops: several legs share the load, so it is stiff and light, but the workspace is small. A nice twist for later: for serial robots forward kinematics is easy and inverse is hard; for parallel robots it is the other way round. Read the table row by row.",
 ["Serial: big and flexible; parallel: stiff and fast.", "Misconception: parallel robots are not just 'several serial robots'; the closed loops change the maths."],
 [("Which is stiffer for the same mass?", "Parallel.")],
 "Two newer families work closer to people.")
card('Collaborative and mobile robots', 6,
 "Cobots are light arms, six or seven axes, designed to share the workspace with people. They sense joint torques, limit speed and force, and stop on contact; the rules come from ISO/TS 15066, which we cover on W2D4. The photo shows a cobot with its teach pendant. Mobile robots replace the fixed base with wheels: AGVs follow fixed paths, AMRs navigate freely with lidar. Put an arm on an AMR and you get a mobile manipulator, whose workspace travels around the factory.",
 ["Cobot = arm designed for contact with people, not a weaker industrial robot.", "Misconception: a cobot is not automatically safe; the application must be risk-assessed."],
 [("Difference AGV vs AMR?", "AGV follows fixed guides; AMR plans its own path.")],
 "Let us put all families in one table.")
card('Classification at a glance', 5,
 "This table is the one to photograph. For each type we list the joint string, DOF, workspace shape and typical use. Ask students to cover the last column and guess the application from the workspace. Then read the box: robot choice starts from the task, not the catalogue. Reach and workspace shape, payload, speed and cycle time, accuracy, and whether people share the space. We will return to this choice in the work-cell design session on W2D3.",
 ["Choose from the task: reach, payload, speed, accuracy, people.", "Misconception: the biggest, most flexible robot is rarely the best choice."],
 [("A pallet of 20 kg boxes, 4 per minute: which robot?", "Articulated palletiser or gantry.")],
 "Quick check.")
card('Check your understanding – 4.1', 3,
 "Two minutes in pairs. Answers: one, six joints for any position and orientation in space. Two, with equal links of 0.5 metres the workspace is a full disc of radius one metre, no hole, assuming full joint range. Three, the delta robot is faster because its motors stay on the base and only a very light platform and rods move, so the moving inertia is tiny and the closed chains are stiff. If many students get the second question wrong, redraw the ring on the board with equal links and show that the hole shrinks to a point.",
 [], [("Answers", "1) Six. 2) Disc of radius 1 m, inner radius 0. 3) Motors fixed on the base, very low moving mass, stiff parallel structure.")],
 "Summary of 4.1.")
card('Summary 4.1 – Robot anatomy and classification', 3,
 "Read the take-aways: links and joints, six DOF for full pose, workspace from link lengths and limits, serial versus parallel, and selection by the task. Point at the key terms. Ask one student to explain SCARA and another to explain AMR in one sentence each. This vocabulary appears in every session of the rest of the week. If time allows, show one short video of each family and let the class shout the type. Remind students that tomorrow's kinematics applies mainly to serial arms.",
 ["Vocabulary used all week."], [], "To describe where a robot's tool is, we need coordinate frames.")

# ---------------------------------------------------------------- 4.2
sess('s3', 'Spatial descriptions: positions, rotations, homogeneous transforms', '4.2', 90)
card('Why we need coordinate frames', 6,
 "Every object in a robot cell gets its own frame: an origin and three perpendicular axes. The robot base, the tool, the part, the camera. A camera reports the part in the camera frame, but the robot must move in its base frame, so we need to convert between frames. Use the analogy in the box: 'two metres left of the door' only means something if you know where the door is and which way you are facing. That is exactly the information a frame carries: position and orientation.",
 ["A coordinate is meaningless without its frame.", "Misconception: there is no single 'true' coordinate system in a robot cell."],
 [("Name three frames a welding robot needs.", "Base, tool (torch tip), workpiece/user frame.")],
 "We need a little matrix arithmetic, so here is a refresher.")
card('Refresher: vectors and matrix–vector multiplication', 7,
 "Matrix times vector: each output row is the matching row of the matrix multiplied element by element with the vector and summed. Work the example on the board: the matrix with zero, minus one, one, zero applied to two, one gives minus one, two. Draw both vectors: the second is the first turned by ninety degrees. That is our first rotation matrix. Also introduce the notation: a superscript before p says in which frame the vector is measured.",
 ["Leading superscript = the frame we measure in.", "Misconception: row times column, not column times column."],
 [("Apply the same matrix to (1,0).", "(0,1): the x-axis turns into the y-axis.")],
 "Let us build the general rotation in the plane.")
card('Rotation in the plane', 8,
 "Frame B is turned by theta relative to frame A. Where does B's x-axis point, seen from A? Cos theta along x, sin theta along y. B's y-axis points to minus sin, cos. Put these two unit vectors side by side as columns and you have the rotation matrix. Multiplying a point known in B by this matrix gives the same point in A. Example: thirty degrees, the point one-zero in B is 0.866, 0.5 in A. Check it in the drawing.",
 ["Columns = axes of B written in A.", "Misconception: the matrix does not move the point; it re-expresses the same point in another frame (both views are valid but be consistent)."],
 [("Theta = 90°: what is R?", "[[0,−1],[1,0]], the matrix from the refresher.")],
 "Rotation matrices have special properties that make life easy.")
card('Properties of rotation matrices', 7,
 "Go through the properties with the worked check. Each column has length one and the columns are perpendicular, so the matrix is orthonormal. That gives the most useful property: the inverse is just the transpose. Turning back by minus theta flips the sign of the sine, which is exactly transposing. The determinant is plus one, so a right-handed frame stays right-handed. In 3D there are nine numbers but only three are free, matching three rotational degrees of freedom.",
 ["R⁻¹ = Rᵀ: no matrix inversion needed.", "Misconception: any 3×3 matrix is not a rotation; it must be orthonormal with det +1."],
 [("Determinant of a mirror matrix?", "−1, so a mirror is not a rotation.")],
 "Now the same idea in three dimensions.")
card('Rotations in 3D: the three elementary rotations', 8,
 "In 3D we rotate about an axis. The rotation about z is our 2D matrix with z unchanged. Rotations about x and y follow the same pattern. Teach the right-hand rule: thumb along the axis, fingers curl in the positive direction. Point out the sign swap in R_y: the minus sign is on the lower left because of the cyclic order x, y, z. Students do not need to memorise these; they need to be able to read them and recognise which axis stays fixed: the row and column with a one.",
 ["The fixed axis has a 1 in its row and column.", "Misconception: the sign position in R_y is not a typo."],
 [("Which elementary rotation leaves the z coordinate unchanged?", "R_z.")],
 "What happens when we combine two rotations?")
card('Order matters: composing rotations', 8,
 "Rotations combine by multiplying their matrices, and matrix multiplication is not commutative. Do the book experiment live: rotate a book ninety degrees about the vertical, then ninety about the front axis; reset and do it in the other order. The book ends in different poses. The worked example shows it with the unit vector x: one order sends it to y, the other to z. For a robot wrist this means the order in which axes are listed in a data sheet is essential. Mention roll-pitch-yaw, Euler angles and quaternions only as going-further.",
 ["R1 R2 ≠ R2 R1.", "Misconception: 'three angles' do not define an orientation unless the order and axes are stated."],
 [("Do two rotations about the same axis commute?", "Yes: the angles simply add.")],
 "Rotation is only half the pose; we also need translation.")
card('Rotation + translation: the full pose of a frame', 6,
 "The full pose of frame B in frame A has two parts: its orientation, the rotation matrix, and the position of its origin, a vector. A point known in B is first rotated into A's orientation and then shifted by B's origin. This formula works, but for a six-axis robot we would rotate, add, rotate, add six times in a row, which gets messy and error-prone. The next slide shows a trick that packs both operations into one matrix multiplication.",
 ["Pose = orientation + position.", "Misconception: the order is rotate first, then add the offset."],
 [("If R is identity, what does the formula reduce to?", "Pure translation: p_A = p_B + offset.")],
 "Here is the trick: the homogeneous transform.")
card('The homogeneous transform', 8,
 "Add a one as the fourth component to every point. Then rotation and translation fit into one four-by-four matrix: the rotation in the upper left, the translation in the last column, and a row zero-zero-zero-one at the bottom. Now chains are simple products. In the plane we use three-by-three matrices. Industrial controllers store every frame, tool, user and base, as such a matrix, or as six numbers x, y, z and three angles that are converted to it internally.",
 ["T = [R p; 0 1]; chains multiply.", "Misconception: the extra 1 is not a physical coordinate; it just switches the translation on."],
 [("What would a 0 instead of 1 in the last component mean?", "A direction (free vector): it rotates but is not translated.")],
 "Let us use it on a number example.")
card('Worked example: a point on the tool, seen from the base', 9,
 "The tool frame sits at 0.5, 0.2 metres in the base frame and is turned ninety degrees. A point P lies 0.1 metres along the tool's x-axis. Step one writes the three-by-three transform and the point with its extra one. Steps two and three are the row calculations; do them on the board with the class. The result is 0.5, 0.3 metres. Check it in the picture: the tool's x-axis points straight up, so 0.1 along x_T is 0.1 upward from 0.5, 0.2. Correct.",
 ["Always sanity-check with a drawing.", "Misconception: students often add the offset in the tool frame instead of the base frame."],
 [("Point 0.1 m along y_T instead?", "R·(0,0.1) = (−0.1, 0) + (0.5,0.2) = (0.4, 0.2) m.")],
 "Real cells have chains of frames.")
card('Chaining frames: base, tool, camera, part', 8,
 "This transform graph is the map of a vision-guided pick. Base to flange comes from forward kinematics, flange to tool from the tool data, base to camera from calibration, and camera to part from the vision system. We want the part relative to the tool. Rule: following an arrow means multiplying, going against an arrow means using the inverse. So we go back from tool to base and then forward through camera to part. This graph returns in W2D5 with hand–eye calibration.",
 ["Arrows multiply; reversed arrows invert.", "Misconception: the order of multiplication follows the path, it cannot be rearranged."],
 [("Which transform changes when the robot moves?", "Base-to-flange (forward kinematics); and camera-to-part if the part moves.")],
 "We just used an inverse; how do we compute it cheaply?")
card('Inverting a homogeneous transform', 7,
 "Because the inverse of a rotation is its transpose, the inverse of a homogeneous transform is easy: transpose the rotation and replace the translation with minus R-transpose times p. Work through the example with the tool from before. R transpose is zero-one, minus one-zero; minus R transpose p gives minus 0.2, 0.5. Interpret it: seen from the tool, the base origin is 0.2 metres behind along x_T and 0.5 metres along y_T. Check against the drawing.",
 ["T⁻¹ = [Rᵀ, −Rᵀp; 0 1].", "Misconception: the inverse translation is not simply −p."],
 [("Why not just −p?", "Because −p is expressed in the base frame; we need it in the tool frame, so it must be rotated by Rᵀ.")],
 "Time to check understanding.")
card('Check your understanding – 4.2', 4,
 "Two minutes in pairs. Answers: one, the columns are the unit axes of frame B written in frame A's coordinates. Two, the extra one lets rotation and translation be done in a single matrix multiplication, so chains of frames become simple products. Three, no, they are different: one sends x to y, the other to z. For a wrist this means the order of the axes defines where the tool points; swapping them in a program would point the tool somewhere else.",
 [], [("Answers", "1) Axes of B expressed in A. 2) Combine rotation + translation in one product. 3) Not equal; axis order changes the tool orientation.")],
 "Summary of 4.2.")
card('Summary 4.2 – Spatial descriptions', 4,
 "Read the take-aways and connect them: frames, rotation matrices with columns as axes and inverse as transpose, elementary rotations in 3D where order matters, the homogeneous transform packing rotation and translation, and chains with inverses. Ask a student to write the inverse formula on the board from memory. Everything in forward kinematics is built from these pieces. Then ask a second student to explain in words why the columns of R are the axes of the rotated frame. If both can do it, the class is ready for forward kinematics.",
 ["These are the building blocks of FK."], [], "Now we can compute where the tool of a robot is.")

# ---------------------------------------------------------------- 4.3
sess('s4', 'Forward kinematics: DH convention, planar 2-link, SCARA', '4.3', 80)
card('Forward kinematics: from joint angles to tool pose', 5,
 "Introduce the two spaces. Joint space is the list of joint values the encoders measure. Task space is where the tool is and how it is oriented. Forward kinematics goes from joint space to task space: it always has exactly one answer and is easy to compute. Inverse kinematics goes the other way, may have several answers or none, and is tomorrow's topic. Forward kinematics is pure geometry: no forces, no time. Controllers use it to display the tool position, to check limits and in simulation.",
 ["FK: unique and easy; IK: tomorrow.", "Misconception: FK does not depend on speed or load."],
 [("Why does IK have several answers?", "E.g. elbow-up and elbow-down reach the same point.")],
 "Let us start with the simplest arm, using plain geometry.")
card('The planar 2-link arm: geometry first', 6,
 "Walk along the arm from the base. The first link of length l1 points at angle theta1. The second link points at theta1 plus theta2, because theta2 is measured relative to the first link. Project both links onto x and y and add them. The orientation of the gripper is simply theta1 plus theta2. Name every symbol with units. Draw the arm big on the board and let students see the cosine and sine projections.",
 ["θ2 is relative to link 1.", "Misconception: using θ2 alone for the second link instead of θ1 + θ2."],
 [("θ1 = 0, θ2 = 0: where is the tool?", "(ℓ1 + ℓ2, 0): stretched along x.")],
 "Let us put numbers in.")
card('Worked example: 2-link forward kinematics', 6,
 "Lengths 0.4 and 0.3 metres, angles thirty and sixty degrees. Step one: the sum is ninety. Step two: x is 0.346 plus zero. Step three: y is 0.2 plus 0.3, so 0.5 metres. Step four: the gripper points straight up. Do the sanity check in the box: the distance from the base, 0.61 metres, is less than the reach of 0.7. Warn students about calculators in radian mode, the most common source of wrong answers in exams.",
 ["Check the distance against ℓ1 + ℓ2.", "Misconception: calculator in RAD mode while angles are in degrees."],
 [("θ2 = 180°: where is the tool?", "At distance |ℓ1 − ℓ2| = 0.1 m, folded back.")],
 "The same result can be written as a product of transforms.")
card('The same result as a product of transforms', 6,
 "Each joint can be written as 'rotate by theta i, then move l i along the new x-axis', one homogeneous transform. Multiply the two and simplify with the angle-sum identities: the last column is exactly the x and y from the geometry, and the upper-left block is the rotation by theta1 plus theta2. Emphasise why we bother: geometry by hand works for two joints but not for six in 3D, whereas multiplying one more matrix per joint always works.",
 ["One matrix per joint; multiply in order base to tool.", "Misconception: the order of multiplication can be swapped – it cannot."],
 [("What would a third link add?", "One more factor ¹T₂ ... ²T₃ with angle θ3 and length ℓ3.")],
 "What does FK tell us about motion?")
card('Joint space vs. task space: a straight joint move is a curve', 6,
 "Here both joints move linearly in time from the start to the end values. Forward kinematics maps each intermediate pose to the tool position, the orange curve. It is an arc, not a straight line. This is what a robot's point-to-point, or PTP, move does: simple for the joints, curved for the tool. If the tool must follow a straight line, for example when gluing, the controller must solve inverse kinematics at every step; that is the LIN move in session 4.7 tomorrow.",
 ["Linear in joint space ≠ linear in task space.", "Misconception: PTP moves do not travel on straight lines."],
 [("Why do PTP moves exist at all?", "They are fast, avoid singularities and need no IK in between.")],
 "For 3D robots we need a systematic way to place frames: DH.")
card('Why a convention? The Denavit–Hartenberg (DH) idea', 6,
 "In 3D you could place frames anywhere, but then each link needs six numbers and every engineer does it differently. Denavit and Hartenberg proposed in 1955 a standard way to place frames so that each link needs only four numbers. One of them is the joint variable, theta for revolute or d for prismatic; the other three are fixed by the link's geometry. The matrix A i is a product of four simple moves. Mention that Craig's book uses a modified convention; same idea, different bookkeeping.",
 ["4 parameters per link: θ, d, a, α.", "Misconception: there is not one DH table for a robot; it depends on the frame choices and the convention."],
 [("Why only four, not six?", "Clever placement of the axes removes two degrees of freedom of choice.")],
 "Let us see the four parameters in a picture.")
card('The four DH parameters in a picture', 6,
 "Point at the drawing. The z axis of frame i-minus-one lies along joint i's axis. The common normal is the shortest line between this axis and the next joint axis; x i lies along it. a i is its length, alpha i the twist between the two joint axes. d i is how far along the previous z axis the common normal sits, and theta i how far it is turned about that axis. For parallel joint axes, as in planar arms and SCARAs, alpha is zero and the picture becomes flat.",
 ["z along the joint axis; x along the common normal.", "Misconception: a is not always the 'visible' length of the metal link."],
 [("Two joint axes intersect. What is a?", "Zero.")],
 "Here is the procedure as a recipe.")
card('DH recipe: a step-by-step procedure', 5,
 "Five steps: number the joints, draw the axes, place z along each joint axis, place x along the common normals, read the four parameters per link and multiply the matrices. The tips on the right come from experience: draw large, use three colours, choose d zero where you can, and always check the zero pose by eye. At the end add a fixed tool transform for the gripper or torch. The going-further note mentions that nearly parallel axes need a modified approach during calibration.",
 ["Check the all-zero pose by eye.", "Misconception: forgetting the fixed tool transform at the end."],
 [("Where is the tool transform defined in a real robot?", "In the controller's tool data (TCP definition).")],
 "Apply it to the two-link arm.")
card('DH table of the planar 2-link arm', 5,
 "All z axes point out of the page, so every alpha is zero and every d is zero. The a values are the link lengths and the thetas are the joint variables, marked with a star. With these parameters A i reduces to the three-by-three matrix we already multiplied, written in four-by-four form with z unchanged. So the DH result is the same x, y and phi as the geometry. This is the reassurance students need: DH is not new physics, just bookkeeping.",
 ["DH reproduces the geometry result.", "Misconception: DH is a different model – it is only a systematic notation."],
 [("Add a third revolute link ℓ3: new row?", "θ3*, 0, ℓ3, 0.")],
 "Now a real industrial robot: the SCARA.")
card('The SCARA robot: structure', 5,
 "Look at the side view. Joints one, two and four rotate about vertical axes, joint three slides vertically. So the joint string is R R P R, four degrees of freedom: x, y, z and one rotation about the vertical. Because all axes are parallel, the x-y part is exactly our two-link arm. The height comes only from the prismatic joint. The name explains the property: selective compliance, stiff in z for pressing, slightly compliant in x-y to find the hole.",
 ["SCARA x–y = the 2-link arm.", "Misconception: SCARAs cannot tilt the tool; they only rotate it about the vertical."],
 [("How many DOF does a SCARA have?", "Four.")],
 "Here is its DH table.")
card('SCARA: DH table and forward kinematics', 6,
 "Read the table row by row. Link one: theta1 variable, offset h for the column height, length l1. Link two: theta2 variable, length l2, and a twist of 180 degrees, which flips z to point down. Link three: the prismatic joint, variable d3. Link four: the tool rotation theta4. Multiply and you get the same x and y as the two-link arm, z equals h minus d3, and the tool angle theta1 plus theta2 minus theta4. The minus sign comes from the flipped z axis.",
 ["z is decoupled from x, y.", "Misconception: the minus sign on θ4 is not an error; it comes from α2 = 180°."],
 [("Why flip z downwards?", "So that a positive d3 means the tool moves down, towards the table.")],
 "Numbers again.")
card('Worked example: SCARA tool position', 6,
 "Column height 0.4, links 0.35 and 0.25 metres. Joints: zero, ninety degrees, 0.1 metres down, zero. Step one: x is 0.35. Step two: y is 0.25. Step three: z is 0.4 minus 0.1, so 0.3 metres. Step four: tool angle ninety degrees. Look at the top view: the elbow is bent ninety degrees and the gripper sits at 0.35, 0.25. Ask students to change d3 to 0.2: only z changes, to 0.2 metres. Finally change θ1 to 90 degrees and let them predict the result: the whole arm swings to the y axis.",
 ["Change one joint at a time to see which coordinate it affects.", "Misconception: d3 changes x or y – it does not."],
 [("θ2 = 0 instead?", "x = 0.6 m, y = 0, z unchanged.")],
 "Six-axis robots use the same recipe.")
card('Six-axis arms: same recipe, more matrices', 5,
 "A six-axis industrial arm is six DH matrices plus the fixed tool transform. Typically the first three joints place the wrist centre, the last three intersect in one point, a spherical wrist, and orient the tool. The controller evaluates this product every cycle, often every millisecond, to display and limit the tool pose. The accuracy depends on how well the DH numbers match the real robot; manufacturers calibrate each robot. The full table is in Craig, chapter three.",
 ["Spherical wrist: position and orientation separate.", "Misconception: a robot's repeatability is not the same as its absolute accuracy; calibration matters."],
 [("Why is a spherical wrist so popular?", "It makes inverse kinematics split into two easy problems (W2D2).")],
 "A last check for today.")
card('Check your understanding – 4.3', 4,
 "Two minutes in pairs. Answers: one, x equals 0.5 times cos zero plus 0.5 times cos ninety, which is 0.5; y equals zero plus 0.5, so the tool is at 0.5, 0.5 metres, pointing up. Two, four parameters per link: theta, d, a and alpha; for a prismatic joint the variable is d. Three, the prismatic joint three sets the height, and it does not change x or y. For question one, ask a student to sketch the pose: the first link along x, the second straight up, which immediately shows the answer without a calculator.",
 [], [("Answers", "1) (0.5, 0.5) m, φ = 90°. 2) Four; d. 3) Joint 3 (d3); no.")],
 "Summary of 4.3.")
card('Summary 4.3 – Forward kinematics', 3,
 "Read the take-aways. FK goes from joint values to the tool pose, uniquely. The two-link formulas are the ones to remember. DH places frames systematically with four numbers per link, and the robot's pose is the product of all link matrices plus the tool transform. The SCARA is the two-link arm in x-y plus a vertical slide and a tool roll. Point at the key terms. Suggest that students rework the SCARA example at home with other joint values and check each result with a quick sketch of the top view.",
 ["Memorise the 2-link formulas."], [], "Let us wrap up the day.")

# ---------------------------------------------------------------- wrap
sess('s5', 'Wrap-up', 'Day summary · preview · credits', 10)
card('Day summary', 4,
 "Go along the four boxes. A springy joint rings at its resonance; the notch filter removes one peak, and in robots the resonance moves with pose and payload. Robots are links and joints in a few families. Frames, rotation matrices and homogeneous transforms describe where things are. Forward kinematics turns joint values into a tool pose. Ask the class which of the four was hardest; revisit it briefly if time allows. Close by stressing that all four parts meet in a real controller: the notch runs in the drive, the transforms in the robot controller.",
 ["Today connected the servo axis to the robot arm."], [], "What comes tomorrow?")
card('Preview of W2D2', 3,
 "Tomorrow we go backwards: inverse kinematics, from a target pose to joint angles, with elbow-up and elbow-down solutions. Then the Jacobian that links joint speeds to tool speed, singularities and the force relation tau equals J transpose F. Then robot dynamics intuition, trajectory planning and the start of the manufacturing block. Ask students to bring the two-link formulas, the transform inverse and the workspace ring. Tell them that the 2-link inverse kinematics is solved with the cosine rule, so a quick look at that formula tonight will help.",
 ["Bring the 2-link FK formulas."], [], "Finally, credits and references.")
card('Figure credits', 1,
 "All photographs come from Wikimedia Commons under free licences, credited on each slide and listed here. All plots and drawings are original, computed from the course data scripts. No need to read this aloud.",
 [], [], "References.")
card('References', 2,
 "Recommend Craig or Spong for kinematics, Lynch and Park's Modern Robotics, which is freely available online with videos, and Ellis for the servo resonance part. The ISO standards define robot vocabulary and coordinate systems. Encourage students to rework today's examples from one of these books.",
 ["Lynch & Park is free online."], [], "End of day.")

# ---------------------------------------------------------------- page numbers
# title=1, then cards; a divider page precedes each session except the opening.
page = 1
for i, s in enumerate(S):
    if i > 0: page += 1           # section divider page
    s['pages'] = []
    for _ in s['cards']:
        page += 1; s['pages'].append(page)
total_pages = page
for s in S:
    assert abs(sum(c[1] for c in s['cards']) - s['min']) < 1e-6, (s['id'], sum(c[1] for c in s['cards']), s['min'])
assert sum(s['min'] for s in S) == 300

def e(x): return html.escape(x, quote=False)
out = []
out.append('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>W2D1 Speaker Notes</title>\n' + style + '\n</head>\n<body>\n')
out.append('<header><div class="wrap">\n  <div class="day">WEEK 2 · DAY 1 / 5 · SPEAKER NOTES</div>\n  <h1>Resonance in Robot Joints, Robot Anatomy and Forward Kinematics</h1>\n  <p>Mechatronics and Robotics Engineering (50 h) · 5 h net teaching time · audience: 2nd-year engineering students</p>\n</div></header>\n')
out.append('<nav class="toc"><a href="#plan">Plan</a>' + ''.join(f'<a href="#{s["id"]}">{e(s["code"].split(" ")[0])} · {e(s["title"].split(":")[0][:28])}</a>' for s in S) + '</nav>\n<main>\n')
out.append('  <section id="plan">\n    <h2 class="session">Day plan &amp; timing</h2>\n    <table class="plan"><tr><th>Block</th><th>Topic</th><th>Slides</th><th>Duration</th></tr>\n')
breaks = {1: True, 2: True, 3: True, 4: False}
for i, s in enumerate(S):
    out.append(f'      <tr><td>{e(s["code"])}</td><td>{e(s["title"])}</td><td>{s["pages"][0]}–{s["pages"][-1]}</td><td>{s["min"]} min</td></tr>\n')
    if i in (1, 2, 3):
        out.append('      <tr><td>—</td><td><i>Break (extra, not counted)</i></td><td></td><td>10 min</td></tr>\n')
out.append(f'      <tr><td></td><td><b>Total net teaching time</b></td><td>1–{total_pages}</td><td><b>300 min</b></td></tr>\n    </table>\n')
out.append('    <p class="say">Section-divider pages (dark) are not counted in the slide counter and have no card. Breaks are suggested after 3.7, after 4.1 and after 4.2; they are extra to the 5 h.</p>\n  </section>\n')
for s in S:
    out.append(f'\n  <section id="{s["id"]}">\n    <h2 class="session">{e(s["title"])} <small>Curriculum code {e(s["code"])} · {s["min"]} min</small></h2>\n')
    for p, (t, m, say, emph, ask, trans) in zip(s['pages'], s['cards']):
        out.append(f'    <div class="slide">\n      <h3><span class="num">Slide {p}</span>{e(t)}<span class="time">~{m} min</span></h3>\n      <p class="say">{e(say)}</p>\n')
        if emph:
            out.append('      <div class="key"><span class="label">Emphasise</span><ul>' + ''.join(f'<li>{e(x)}</li>' for x in emph) + '</ul></div>\n')
        if ask:
            out.append('      <div class="ask"><span class="label">Ask the audience / likely questions</span><ul>' + ''.join(f'<li><b>Q:</b> {e(q)} <b>A:</b> {e(a)}</li>' for q, a in ask) + '</ul></div>\n')
        out.append(f'      <p class="trans">Transition: {e(trans)}</p>\n    </div>\n')
    out.append('  </section>\n')
out.append('</main>\n<footer>Figures and references are listed on the final slides of the deck.</footer>\n</body>\n</html>\n')
open(os.path.join(HERE, '..', 'w2d1_speaker_notes.html'), 'w', encoding='utf-8').write(''.join(out))
print('cards', sum(len(s['cards']) for s in S), 'pages', total_pages)
for s in S:
    for p, c in zip(s['pages'], s['cards']):
        print(p, c[0], len(c[2].split()))
