# Speaker-note content for w2d5 (one entry per content frame, in deck order).
# Each entry: (minutes, say, [emphasise...], [ask...], transition)
S = []
def c(m, say, emph, ask, trans): S.append((m, say, emph, ask, trans))

# ---------------- intro (part of 6.4 block) ----------------
c(1, "Welcome to the last day of the course. Today we close the loop from the sensor to the finished robot cell. Yesterday we met the sensors themselves: encoders, IMUs, force sensors and LiDAR. Today we ask what happens after the sensor: how a camera turns light into a robot target, how a voltage becomes a number, how we clean that number, and how all the devices in a cell exchange data on time. The final hour is a case study that uses everything, followed by a wrap-up of all ten days.",
  ["Today is about the whole chain, not single components.", "Misconception: a better sensor alone fixes a measurement problem. Sampling, filtering and timing matter as much."],
  [], "Let us look at the plan for the day.")
c(3, "Here is the plan: five one-hour sessions. Vision first, because it is the most visual and gives a strong start. Then sampling and digitisation, then filters, then networks, and finally the integration case study and the course wrap-up. Read the learning outcomes aloud with the students: each one is a verb they should be able to do by tonight, such as project a point into an image or build an error budget. Tell them that every session ends with a short check and a summary with key terms, so they can test themselves.",
  ["Outcomes are skills: explain, calculate, choose.", "Breaks are extra, about every hour."],
  ["<b>Q:</b> Which of these have you already met in another course? <b>A:</b> Often binary numbers and RC filters; use that as an anchor."],
  "Before we start, a quick look back at yesterday.")
c(4, "Yesterday we covered material handling, safety standards and the first sensor sessions. Three ideas come back today. Resolution versus accuracy: a camera pixel or an ADC step is a resolution; calibration decides accuracy. The IMU: its gyro and accelerometer each have a weakness, and today we fuse them. And the homogeneous transform from week two, day one: vision results are only useful once we transform them into the robot base frame. Ask the students to recall one sentence about each.",
  ["Resolution is not accuracy.", "Misconception: a high-resolution sensor is automatically accurate."],
  ["<b>Q:</b> What does a homogeneous transform contain? <b>A:</b> A rotation matrix and a translation vector in one 4x4 matrix."],
  "Let us start with the robot's eyes: machine vision.")
# ---------------- 6.4 vision ----------------
c(5, "Ask: what does a robot do if the part is two centimetres away from where it was taught? It misses. A taught robot is blind; it needs parts in fixtures. A camera removes that need: it tells the robot where the part is, which part it is and whether it is good. Go through the four task types: locate, inspect, read, guide. Then distinguish 2D vision, where parts lie on a known plane, from 3D vision, where we also need height. The sketch shows the most common industrial case: parts at random angles on a conveyor, a fixed camera, and a robot.",
  ["Vision replaces expensive fixtures with software.", "Misconception: vision means artificial intelligence. Most industrial vision is classic geometry and good lighting."],
  ["<b>Q:</b> Name a vision task in a car factory. <b>A:</b> Reading a VIN, checking a weld seam, locating a windscreen for gluing."],
  "To use a camera we need a model of how it forms an image.")
c(5, "Use the dark-room analogy: a small hole in a window shutter projects an upside-down image of the street onto the wall. Draw the similar triangles: image height over focal length equals object height over distance. In pixel units we write u equals f x times X over Z plus c x. Walk through the example: f x is 1000 pixels, the point is 0.1 m to the side at 0.5 m distance, so it lands 200 pixels from the centre. One pixel then covers half a millimetre. Doubling the distance halves the size in the image.",
  ["Every symbol: X, Z in metres; f, c, u in pixels.", "Misconception: focal length is in millimetres here. In the model we use pixels."],
  ["<b>Q:</b> What happens to u if Z doubles? <b>A:</b> u minus c x halves."],
  "Real cameras need a few more parameters.")
c(5, "The matrix K collects the four intrinsic numbers: two focal lengths and the image centre. They belong to the camera and lens and do not change when we move the camera. Where the camera is located is described by the extrinsics, which is a transform like the ones from W2D1. Real lenses are not perfect: straight lines bend, outwards like a barrel or inwards like a pincushion. A simple polynomial in the radius corrects this. Stress the note: every point on one ray hits the same pixel, so one camera cannot measure depth.",
  ["Intrinsics: camera itself. Extrinsics: camera pose.", "Misconception: a single camera can measure distance. It cannot without extra knowledge."],
  ["<b>Q:</b> Do intrinsics change if the robot moves the camera? <b>A:</b> No, only the extrinsics change (unless you zoom or refocus)."],
  "How do we find K and the distortion values in practice?")
c(5, "Calibration is like tuning a guitar with a reference tone: we show the camera a pattern whose geometry we know exactly. Walk through the five steps. Emphasise variety of poses: tilted, near, far, in the corners of the image, otherwise distortion is poorly estimated. The software adjusts K, the distortion values and each board pose until the projected corners match the detected corners. The remaining mismatch is the reprojection error; below about 0.3 pixel is good. Mention that OpenCV and MATLAB do this in a few lines.",
  ["Many different poses give a good calibration.", "Misconception: a low reprojection error proves the system is accurate. It only shows the model fits the calibration images."],
  ["<b>Q:</b> Why not take all images straight on? <b>A:</b> Then focal length and distance cannot be separated well, and edge distortion is not seen."],
  "With a calibrated camera we can find where an object is.")
c(5, "If we know at least four points on the object, for example the corners of a printed marker or features in a CAD model, and we see them in the image, we can compute the full pose of the object relative to the camera: three rotations and three translations. This is called Perspective-n-Point. Fiducial markers like ArUco or AprilTag are square black-and-white codes designed so that software finds them fast and knows which one it is. They are used for calibration, for AMR docking and in teaching labs.",
  ["Pose means position and orientation together.", "Misconception: PnP gives the pose in robot coordinates. It gives it in camera coordinates."],
  ["<b>Q:</b> Why are four points enough? <b>A:</b> Each image point gives two equations; six unknowns need at least three points, four make it unique and robust."],
  "What if we really need depth, for example in a bin of parts?")
c(5, "Our eyes solve depth with two views. A stereo camera does the same: the same point appears shifted between left and right images; this shift is the disparity. Distance is focal length times baseline divided by disparity. Example: 700 pixel focal length, 10 cm baseline, 35 pixel disparity gives 2 m. The plot shows the price: the depth error grows with the square of the distance. Mention the two other 3D methods briefly: structured light projects a known pattern; time of flight measures travel time, the same principle as LiDAR from yesterday.",
  ["Depth error grows with Z squared.", "Misconception: a 3D camera is equally accurate at all distances."],
  ["<b>Q:</b> How do we make a stereo camera more accurate at long range? <b>A:</b> A wider baseline or a longer focal length."],
  "Now the camera knows where the part is, but the robot does not yet.")
c(6, "The camera reports the object in its own frame. The robot needs it in the base frame. Show the chain: base to flange is known from forward kinematics, camera to object comes from vision, and the missing piece is flange to camera, which we cannot measure with a ruler accurately enough. Hand-eye calibration finds it: move the robot to many poses and look at a fixed checkerboard each time. For a fixed camera the unknown is base to camera instead. Mention the AX equals XB equation only as a name.",
  ["Transforms chain by multiplication, in order.", "Misconception: the camera's mounting drawing is accurate enough. Millimetre errors at the flange become larger errors at the part."],
  ["<b>Q:</b> Which frame do we need for a fixed camera? <b>A:</b> Base to camera."],
  "Let us do the full calculation once with numbers.")
c(5, "Go slowly through the four steps. The part is found at pixel 840, 520; the centre is 640, 480. The offset is 200 by 40 pixels. With 0.5 mm per pixel that is 100 by 20 mm in the camera frame. The camera image y-axis points along negative base y, so we flip the sign. Finally add the camera axis position, 600 mm along base x. The robot target is 700, minus 20 mm. Point out that steps three and four are exactly a homogeneous transform applied to a point.",
  ["Check signs of axes every time.", "Misconception: pixel axes match robot axes. They rarely do."],
  ["<b>Q:</b> If the part were found at the centre pixel, what is the target? <b>A:</b> (600, 0) mm."],
  "A few practical rules make vision work in a real factory.")
c(4, "Industrial vision engineers say: light first, software second. A back light gives a crisp silhouette, ideal for measuring outlines and holes. A ring light from the front shows surface detail like printing or scratches. Two time effects: motion blur during exposure, and processing time. One millisecond exposure at half a metre per second is already half a millimetre of smear. Processing takes tens of milliseconds, so the result is old when it arrives. The solution, a time stamp, returns in the case study.",
  ["Lighting is the cheapest accuracy improvement.", "Misconception: a faster computer solves the age of the vision result. Time-stamping does."],
  ["<b>Q:</b> How do you reduce blur without a faster camera? <b>A:</b> Shorter exposure with brighter or strobed light."],
  "Time to check understanding.")
c(4, "Give the students two minutes to work in pairs, then collect answers from two or three pairs before you reveal anything. The first question is a direct use of the pinhole model, so ask for the units at every step: metres divided by pixels gives metres per pixel. The second question checks whether they understood that a single camera loses depth; good answers mention that every point on one ray lands on the same pixel. The third question checks the stereo error formula; listen for the word squared. Praise reasoning, not only the number. Answers are below.",
  ["Let students explain to each other before you reveal answers."],
  ["<b>Q1:</b> Pixel size on the part: Z / f = 0.4 / 800 = 0.5 mm per pixel.",
   "<b>Q2:</b> All points on one ray land on the same pixel; without a known plane, marker size or second view, distance is unknown.",
   "<b>Q3:</b> Error grows with Z squared: twice the distance gives about four times the error, so about 20 mm."],
  "Let us summarise the vision session.")
c(3, "Run through the five bullets and ask a student to define each key term in their own words. The thread through this session is a chain of transforms: pixel to camera ray, camera to object, flange to camera, base to flange. If one link is wrong, the robot misses. The references are the standard books: Corke for robotics and vision together, Szeliski for computer vision.",
  ["Vision is geometry plus calibration plus lighting.", "Misconception: vision results can be used without hand-eye calibration."],
  [], "After the break we look at the step every sensor signal goes through: sampling.")
# ---------------- 6.5 sampling ----------------
c(8, "Start with the wagon-wheel effect from old films: the wheel seems to turn backwards. The camera takes 24 pictures a second; between two pictures each spoke moves almost to the next spoke position, so the eye matches it to the wrong spoke. A computer reading a sensor does the same: it only sees samples. Nyquist says the signal frequency must stay below half the sampling frequency. Faster content does not disappear; it is disguised as a slower signal. This is aliasing.",
  ["Sampling is like a strobe light.", "Misconception: frequencies above f_s/2 are simply lost. They come back as false low frequencies."],
  ["<b>Q:</b> Who has seen helicopter blades standing still in a video? <b>A:</b> Same effect: rotation rate matches the frame rate."],
  "Here is the whole path from sensor to processor.")
c(7, "Walk along the chain: a strain gauge gives millivolts, an amplifier makes volts, an analogue filter removes fast content, the sample-and-hold freezes the voltage, the ADC converts it, and the processor filters and controls. The left part is continuous, the right part is numbers at instants k T s. Refresh binary numbers: N bits give 2 to the N values; work out 1011 binary equals 11. Two errors appear: between samples in time and between steps in amplitude. This session handles both.",
  ["Two kinds of loss: time and amplitude.", "Misconception: digital means exact. Every number is rounded and sampled."],
  ["<b>Q:</b> How many levels has a 10-bit ADC? <b>A:</b> 1024."],
  "Let us see aliasing in a real-looking signal.")
c(7, "The plot shows a 900 Hz signal sampled at 1 kHz. The samples, the blue dots, fit perfectly onto a 100 Hz sine. The calculation: half the sampling rate is 500 Hz, 900 is above it, so it appears at 1000 minus 900, 100 Hz. Stress the final bullet: once sampled, the fake 100 Hz looks exactly like a real 100 Hz vibration. No digital filter can tell them apart. In a robot this could be motor vibration aliasing into the force-sensor data.",
  ["Alias frequency: distance to the nearest multiple of f_s.", "Misconception: a digital low-pass after the ADC removes aliasing."],
  ["<b>Q:</b> 1.2 kHz sampled at 1 kHz? <b>A:</b> Appears at 200 Hz."],
  "So the protection must sit before the ADC.")
c(7, "The spectrum sketch shows the useful signal band and some noise above half the sampling rate. Without protection, that noise folds into the useful band. Only an analogue filter in front of the ADC can stop it. A practical trick is oversampling: sample much faster than needed, so a simple RC filter is enough, then do the sharp filtering digitally. Warn that the analogue filter also adds delay; keep its corner five to ten times above the loop bandwidth.",
  ["Anti-alias filter: analogue, before the ADC.", "Misconception: the anti-alias filter can be designed after the system is built, in software."],
  ["<b>Q:</b> Why oversample? <b>A:</b> It relaxes the analogue filter, which is expensive and drifts; digital filters are cheap and exact."],
  "Now the amplitude side: quantisation.")
c(8, "An N-bit ADC divides its range into 2 to the N steps. Each sample is rounded to the nearest step, so the error is at most half a step. The plot shows a 3-bit converter: the staircase and the error below it. For a full-scale sine the signal-to-noise ratio is about 6 dB per bit. Example: a joint torque sensor with a 200 Nm range and 12 bits has steps of 0.049 Nm and an SNR of about 74 dB. Each extra bit doubles the number of steps.",
  ["Step size q = range / 2^N.", "Misconception: more bits always means more accuracy. Noise and offset errors may be larger than one step."],
  ["<b>Q:</b> Step size of 16 bits on the same sensor? <b>A:</b> 200/65536 = about 3 mNm."],
  "There are two main ADC families.")
c(7, "The successive-approximation ADC plays the game of guess the number: is the voltage above half range? Then above three quarters? One bit per guess. It is fast and has little delay, so it is used for motor currents. The sigma-delta converter runs a very fast one-bit converter and averages; it gives very high resolution but with more delay, ideal for load cells and force sensors. The sample-and-hold freezes the input while the SAR guesses.",
  ["SAR: fast. Sigma-delta: precise but slower.", "Misconception: the higher-resolution ADC is always better for control. Its delay may hurt the loop."],
  ["<b>Q:</b> Which ADC for a 6-axis F/T sensor? <b>A:</b> Usually sigma-delta: high resolution, moderate bandwidth."],
  "Timing of the sample matters too.")
c(7, "In a motor drive the PWM makes the current ripple. If we sample at a random moment we see ripple and aliasing. Sampling exactly at the peak or valley of the PWM carrier gives the average current. More generally, every delay costs phase: 360 degrees times frequency times delay. The example: 94 microseconds of delay costs 34 degrees at 1 kHz. Link back to W1D3 and W1D4: phase margin is our safety distance, and delays eat it.",
  ["Delay costs phase linearly with frequency.", "Misconception: a small delay does not matter. At the loop bandwidth it can eat most of the phase margin."],
  ["<b>Q:</b> Phase cost of 1 ms at 50 Hz? <b>A:</b> 18 degrees."],
  "Let us check understanding.")
c(5, "Pairs, two minutes, then discuss. The first question uses the alias rule directly; ask a student to draw the frequency axis with f_s and f_s/2 on the board and fold the 9 kHz line back. The second question practises the 6 dB per bit rule; some students will compute 16/12 and say 33 percent better, which is the misconception to correct: each bit doubles the number of steps, so the gain is exponential. The third question is the key idea of the session: once aliased, a false signal is indistinguishable from a real one. Answers below.",
  ["Use the alias rule f_alias = |f - k f_s|."],
  ["<b>Q1:</b> |9 - 10| = 1 kHz: it appears at 1 kHz.",
   "<b>Q2:</b> 4 bits more, about 6 dB each: 24 dB, a factor of 16 in amplitude.",
   "<b>Q3:</b> After sampling the alias is indistinguishable from a real signal, so it must be removed before the sampler."],
  "Summary of sampling.")
c(4, "Read the five bullets and the key terms. Ask a student to explain aliasing using the wagon wheel without notes. Point out that the delay rule connects this session to every control session of the course.",
  ["Nyquist, anti-alias filter, bits and delay are the four design choices.", "Misconception: Nyquist alone is enough; in practice sample 5 to 10 times faster than the highest frequency of interest."],
  [], "After the break: what we do with the numbers, signal processing.")
# ---------------- 6.6 filters ----------------
c(6, "Four basic filter shapes. Low-pass keeps slow signals: smoothing a noisy speed or force. High-pass removes offsets and drift. Band-pass keeps one band, for example to measure one vibration. Band-stop or notch removes one band, for example a resonance. Each plot shows gain in decibels against frequency relative to the corner. The dashed curves are first order, the solid ones second order: steeper. Ask students which filter a hand-held phone camera stabiliser might use.",
  ["Name the filter by what it lets through.", "Misconception: a filter only changes the size. It also shifts the timing (phase)."],
  ["<b>Q:</b> Which filter removes a slowly drifting offset? <b>A:</b> High-pass."],
  "The simplest one is the RC low-pass, and it fits in one line of code.")
c(7, "Students know the RC circuit: the output chases the input with time constant RC. In software, at every sample we move the output a fraction alpha of the way towards the input. Work the example: a 500 Hz corner gives tau of 318 microseconds; with a 16 kHz sample rate alpha is about 0.18. The code line is y plus equals alpha times x minus y. Stress the note: the filter delays the signal by roughly tau. In a control loop, that costs phase.",
  ["First-order low-pass: y += alpha (x - y).", "Misconception: a filter with a lower corner is always better. It is smoother but slower."],
  ["<b>Q:</b> What is alpha if T_s equals tau? <b>A:</b> About 0.63 exact, the filter then follows very quickly."],
  "Another simple filter: the moving average.")
c(6, "Average the last N samples. It is easy to understand and always stable. Its special property: it cancels completely any disturbance whose period fits exactly into the window, the zeros in the plot at f_s over N and multiples. Between the zeros it damps only weakly. Delay is half the window. Example: 16 samples at 16 kHz cancel 1 kHz and its harmonics, useful when a known periodic disturbance exists, like a gear-mesh frequency at constant speed.",
  ["Moving average: zeros at multiples of f_s/N.", "Misconception: a longer moving average is free. Its delay grows with N."],
  ["<b>Q:</b> Delay of N = 16 at 16 kHz? <b>A:</b> 7.5 samples, about 0.47 ms."],
  "These are examples of two families: FIR and IIR.")
c(6, "A finite impulse response filter uses only past inputs, like the moving average. An infinite impulse response filter also feeds back past outputs, like the RC filter. Compare in the table: FIR is always stable but needs many terms and has more delay; IIR needs few terms and has little delay but must be designed carefully. Inside a fast control loop the low delay usually makes IIR the winner. Mention biquads only as a name for further study.",
  ["FIR: no feedback. IIR: feedback.", "Misconception: IIR filters are unstable. They are stable if designed correctly."],
  ["<b>Q:</b> Is the RC-type filter FIR or IIR? <b>A:</b> IIR, it uses the previous output."],
  "Now a special filter for robot joints: the notch.")
c(6, "Recall W2D1: a gearbox or a long, light arm makes a joint ring at one frequency, like a playground swing. Here at 400 Hz. A notch filter removes a narrow band around that frequency. The upper plot shows a wide and a narrow notch, the lower plot the phase. A wide notch is robust when the resonance moves with payload or arm pose, but costs more phase at lower frequency. A narrow notch costs little phase but must hit the frequency. Give the rule: stiffen mechanics first.",
  ["Notch width is a trade-off between robustness and phase.", "Misconception: a notch filter fixes a weak mechanical design. It hides it within limits."],
  ["<b>Q:</b> Why does the resonance move in a robot? <b>A:</b> Inertia seen by the joint changes with pose and payload."],
  "Differentiation is the next challenge.")
c(6, "Many controllers need speed but the sensor gives position. The simple difference of two encoder readings divided by the sample time is a difference of rounded numbers: at low speed it jumps between 0, 48 and 96 rpm. Differentiation amplifies fast changes, 20 dB per decade. The fix is a filtered derivative: differentiate and low-pass in one block. The same block is used for the D-term of a PID controller from W1D3. The orange line is smooth but about 1.5 ms late.",
  ["Never use a pure derivative on measured data.", "Misconception: higher sample rate gives a better speed estimate. With the same encoder it gives a noisier one."],
  ["<b>Q:</b> Two ways to get a better speed signal? <b>A:</b> More encoder resolution, or an observer/filter."],
  "Sometimes two different sensors together beat one: sensor fusion.")
c(7, "An IMU has a gyro and an accelerometer. The accelerometer gives tilt from gravity: right on average but very noisy when the robot vibrates. The gyro gives angular rate: smooth, but integrating a small bias makes the angle drift away, the dotted line. The complementary filter combines them: integrate the gyro, and pull gently towards the accelerometer. Alpha 0.98 at 100 Hz gives a time constant of about half a second. The orange fused line follows the true angle without noise and without drift.",
  ["Gyro: trust short-term. Accelerometer: trust long-term.", "Misconception: averaging the two angles gives the same result. It keeps half the noise and half the drift."],
  ["<b>Q:</b> What happens with alpha = 1? <b>A:</b> Pure gyro integration, the angle drifts."],
  "The Kalman filter generalises this idea.")
c(6, "Keep this conceptual. A Kalman filter repeats two steps. Predict: use a model to move the estimate forward; uncertainty grows. Update: compare with the measurement and blend; uncertainty shrinks. The weight, the Kalman gain, depends on trust: prediction variance over the sum of both variances. Work the example: both variances 4, so K is a half, the estimate lands in the middle at 11 degrees, and the variance halves to 2. The curves show the blend being narrower than both inputs.",
  ["Blend by trust: more weight to the less uncertain source.", "Misconception: the Kalman filter is magic. It is a weighted average with self-updating weights."],
  ["<b>Q:</b> If the sensor were very noisy (R large), what is K? <b>A:</b> Close to zero, we mostly trust the prediction."],
  "Check your understanding.")
c(5, "Pairs, two minutes, then discuss. The first question applies the moving-average zero rule; ask for the window length in time as well, which is 1 ms, so a 1 kHz disturbance fits exactly once. The second question checks the fusion idea: students should explain drift from integrating a small constant error, not just say the gyro is bad. The third question links back to delay and phase margin from the control week: in a loop, the filter with less delay is preferred, and that is usually IIR. Answers below.",
  ["Connect each answer to delay or trust."],
  ["<b>Q1:</b> f_s/N = 1 kHz and multiples: 1, 2, 3 kHz ...",
   "<b>Q2:</b> The gyro is smooth but its bias integrates to growing drift, so only short-term changes are reliable.",
   "<b>Q3:</b> IIR: few terms and small delay, so less phase loss in the loop."],
  "Summary of filters.")
c(5, "Go through the bullets and the which-filter table. Ask: you have a noisy force signal and a resonance at 300 Hz in the same joint, which filters? A low-pass well above the loop bandwidth and a notch at 300 Hz. Repeat that every filter costs delay.",
  ["Every filter = gain change + delay.", "Misconception: more filtering is always safer."],
  [], "After the break: how all these numbers travel between devices.")
# ---------------- 6.7 comm ----------------
c(5, "Use the letter analogy. A packet has an envelope with sender and receiver, the letter itself, and a seal that shows whether someone tampered with it. On a network the seal is a CRC check value. Define four words: bit rate, cycle time, latency and fieldbus. Latency is the age of the data when it arrives, and that is what control cares about. A fieldbus is a network designed for machines, with guaranteed timing.",
  ["Packet = header + payload + check.", "Misconception: a fast bit rate means low latency. Waiting for the cycle often dominates."],
  ["<b>Q:</b> What does the CRC not tell you? <b>A:</b> Whether the data is fresh."],
  "Where do which networks sit in a robot cell?")
c(6, "The automation pyramid: at the bottom field devices like sensors, valves and drives; above them PLCs and robot controllers; then HMI and SCADA; at the top MES, ERP and cloud. Going up, there is more data but deadlines become softer. The table gives typical cycle times, from tens of microseconds inside a drive to a second for factory IT. Define real time carefully: it means on time, every time, not simply fast.",
  ["Real time = guaranteed deadline.", "Misconception: Ethernet is always too slow for control. Industrial Ethernet variants are faster than old fieldbuses."],
  ["<b>Q:</b> Where does a camera sit? <b>A:</b> At the field/control level, but its data is large and its timing soft, so usually standard Ethernet with time stamps."],
  "We start at the bottom with CAN.")
c(6, "CAN uses two twisted wires shared by all nodes, with a 120 ohm resistor at each end. Each message has an identifier; if two nodes start together, the lower identifier wins without collision, like a polite queue by priority. A frame carries up to 8 bytes. The example shows the limit: 9 frames take about 1.1 ms, fine for a gripper or an AMR, but not for a fast 6-axis robot. CANopen adds a standard dictionary of parameters; CiA 402 is the drive profile.",
  ["Arbitration by identifier: no data lost.", "Misconception: CAN is obsolete. It is everywhere in AMRs, cobots and cars."],
  ["<b>Q:</b> Which message wins, ID 0x100 or 0x080? <b>A:</b> 0x080, the lower one."],
  "For fast multi-axis robots EtherCAT is popular.")
c(6, "Use the train analogy: one Ethernet frame leaves the master and passes every drive; each drive unloads its set-point and loads its actual values while the frame passes, then the frame returns. A working counter tells the master everybody answered. Distributed clocks give all drives one common time. The example: 32 axes fit in about 35 microseconds of wire time, so a 100 microsecond cycle is possible. The photo shows a slave controller chip that does this in hardware.",
  ["Processing on the fly: no store-and-forward.", "Misconception: EtherCAT needs a special network card in the master. A standard Ethernet port is enough."],
  ["<b>Q:</b> What does the working counter detect? <b>A:</b> A device that did not read or write its data."],
  "PROFINET is the other big player; let us compare.")
c(6, "PROFINET is Ethernet for PLCs, widespread in European factories. RT skips the slow TCP/IP layers for cycles of milliseconds; IRT reserves a fixed time slot in each cycle, like a bus lane closed to other traffic, for synchronised motion. The table compares the networks in a robot cell: CAN for small devices, EtherCAT and PROFINET IRT for motion, PROFINET RT for PLC I/O, OPC UA for factory data and ROS 2 for robot software. Choose by cycle time and synchronisation, and by what the vendor supports.",
  ["Pick the network per link, not one for everything.", "Misconception: the highest bit rate wins."],
  ["<b>Q:</b> Network between PLC and safety light curtain? <b>A:</b> A safety protocol on PROFINET or EtherCAT (PROFIsafe, FSoE), or hard-wired."],
  "Higher up, the question is not speed but meaning: OPC UA.")
c(6, "Old fieldbuses send raw bytes: you need the manual to know that byte 7 is the temperature. OPC UA sends named, typed data: the robot controller offers a tree with state, cycle time, joint temperatures with units, and even methods like start and stop. Clients like the HMI, the MES or a cloud dashboard browse this tree. It supports client-server and publish-subscribe, and has security built in. It is not meant for fast control loops.",
  ["OPC UA = information model + secure transport.", "Misconception: OPC UA replaces the fieldbus. It complements it at higher levels."],
  ["<b>Q:</b> Why does a MES prefer OPC UA? <b>A:</b> Machines from different vendors describe their data in the same way."],
  "In research and mobile robots another glue is common: ROS.")
c(6, "ROS is not an operating system but middleware: libraries and tools that let programs called nodes exchange messages. A camera driver publishes images on a topic; a detector subscribes and publishes objects; a planner combines them with LiDAR scans and publishes velocity commands to the motor controller. Use the radio analogy: anyone may broadcast on a channel, anyone may listen. ROS 2 uses DDS for transport, and ros2_control connects to real hardware. Stress the note: fast loops stay in the drive.",
  ["Nodes, topics, services, actions.", "Misconception: ROS runs the current loop. It coordinates; drives do hard real-time."],
  ["<b>Q:</b> What is the advantage of publish-subscribe? <b>A:</b> Sender and receivers do not need to know each other; adding a new listener changes nothing."],
  "Now the timing of the whole chain.")
c(6, "The bar shows the delay from measurement to action over a bus: wait for the cycle, transfer, compute, transfer back, apply. Typically two to three bus cycles. Example: 625 microseconds costs 7 degrees at a 30 Hz position loop, fine, but 45 degrees at a 200 Hz velocity loop, far too much. So the fast loops are closed inside the drive and only position set-points travel over the bus. Synchronisation keeps all six axes of a robot acting at the same instant.",
  ["Close fast loops locally.", "Misconception: a faster network lets you close any loop centrally."],
  ["<b>Q:</b> Why must the axes be synchronised? <b>A:</b> Otherwise each joint uses a set-point from a slightly different time and the tool leaves the path."],
  "Finally: how do we know the data is valid?")
c(5, "Walk through the flow chart. The CRC catches damaged bits. A counter that increases every cycle catches frozen or lost data. A watchdog timer trips if nothing fresh arrives. A time stamp tells the age of a value. A plausibility check asks whether the value is physically possible, such as the three phase currents summing to zero. If any check fails, the machine stops safely and raises an alarm. Link this to the safety session yesterday.",
  ["Correct is not the same as fresh.", "Misconception: a valid CRC means the data can be used."],
  ["<b>Q:</b> Plausibility check for a gripper force? <b>A:</b> Within sensor range and consistent with the gripper state."],
  "Check your understanding.")
c(4, "Pairs, two minutes, then discuss. The first question has no single correct network, so reward good reasons: cycle time and synchronisation for the joints, named data and security for the MES. The second question reuses the phase rule from sampling: 360 times frequency times delay. Ask what phase margin the loop might have had, perhaps 50 degrees, so losing 36 would leave too little. The third question is about freshness rather than correctness; the CRC is fine, but a counter or time stamp shows that the value is old. Answers below.",
  ["Phase cost: 360 f T_d."],
  ["<b>Q1:</b> (a) EtherCAT or PROFINET IRT: microsecond cycles, synchronisation. (b) OPC UA: named, secure data; timing is soft.",
   "<b>Q2:</b> 360 x 100 x 0.001 = 36 degrees: too much, close that loop locally.",
   "<b>Q3:</b> A sequence counter or time stamp with a watchdog."],
  "Summary of communication.")
c(4, "Read the bullets and terms. Draw attention to the theme of the whole day: timing. A measurement is only useful if we know how old it is. This leads directly into the case study.",
  ["Every link has a cycle time and a latency.", "Misconception: one network type should be used for the whole factory."],
  [], "After the break we put everything together in a real cell.")
# ---------------- 6.8 case study + wrap-up ----------------
c(6, "Describe the cell: parts arrive at random angles on a conveyor moving at half a metre per second. A photo-eye triggers the camera, the vision PC finds each part, and a robot with a vacuum gripper picks 60 per minute. A light curtain guards the opening; a safety PLC and cell PLC coordinate; the MES collects data over OPC UA. List which day each element came from. The single question for the hour: will the gripper hit the part within plus or minus 2 mm?",
  ["Integration means all topics at once.", "Misconception: if every component meets its datasheet, the system works."],
  ["<b>Q:</b> Which sessions of the course appear in this picture? <b>A:</b> Nearly all: actuators, servo loops, kinematics, programming, safety, sensors, networks."],
  "First we map who talks to whom.")
c(7, "Follow the arrows: the photo-eye triggers the camera, images go over GigE to the vision PC, the result goes over Ethernet to the robot controller, which commands six drives over EtherCAT. The table sums the vision latency to 80 ms. In that time the part moves 40 mm, twenty times the tolerance. Ask the class for solutions. Most suggest a faster computer. The real solution is the dashed red line: the same trigger latches the conveyor encoder count, so we know exactly where the part was when the picture was taken.",
  ["Latency is fine if it is known and compensated.", "Misconception: the vision system must be faster than the conveyor."],
  ["<b>Q:</b> What would happen if processing time varied between 50 and 110 ms without time stamps? <b>A:</b> A position error of up to 30 mm varying from part to part."],
  "Let us compute the tracking with numbers.")
c(6, "The part position at any later time is the position seen in the image plus the encoder counts since the exposure times the belt travel per count. Work the four steps: a 100 mm roller has a 314 mm circumference; 1000 counts per revolution give 0.314 mm per count; the part was at 120 mm, 1900 counts have passed, so it is now at 717 mm. The robot controller treats this as a user frame on wheels, as in robot programming on W2D3.",
  ["Measure the conveyor, do not assume its speed.", "Misconception: using nominal belt speed is good enough. Speed varies with load."],
  ["<b>Q:</b> How far has the part moved after 1000 more counts? <b>A:</b> 314 mm."],
  "Is the result accurate enough? Build an error budget.")
c(7, "List each independent error source: one pixel of vision, hand-eye calibration, one encoder count, one millisecond of timing jitter, and robot repeatability. The worst case adds them: 1.86 mm. Independent errors rarely peak together, so engineers use the root of the sum of squares: 0.92 mm. Both are under the 2 mm tolerance, so the design works. To improve it, attack the biggest terms first: lens and lighting, calibration, hardware time stamps. Robot repeatability is the smallest term.",
  ["RSS for independent errors; worst case for safety-critical limits.", "Misconception: the robot is the main source of error. Here it is the smallest."],
  ["<b>Q:</b> Which single improvement helps most? <b>A:</b> Any of the three 0.5 mm terms; halving one reduces RSS to about 0.81 mm."],
  "How do we bring such a cell to life?")
c(5, "Commissioning goes inside-out, like tuning cascaded loops in W1D5: wiring and networks first, then safety, then drives and robot frames, then camera calibration, then tracking at low speed, and finally full speed with logging. Define system integration: making separately good parts work as one system. Explain FAT and SAT. Experienced integrators say most problems they meet are timing problems, so log everything with time stamps.",
  ["Inside-out, one layer at a time.", "Misconception: start at full speed to save time."],
  ["<b>Q:</b> Why safety before tuning? <b>A:</b> People work near the cell during tuning; protection must already work."],
  "Check your understanding of the case.")
c(5, "Pairs, three minutes, then discuss. For the first question let a volunteer recompute the error budget on the board: only the timing-jitter line changes, from 0.5 to 1.0 mm, because the belt moves twice as far in the same jitter time. Point out that motion blur also grows, so a shorter exposure or strobe light may be needed. The second question is the central idea of the case study: a known delay is harmless when it is measured. The third question links back to safety on W2D4. Answers below.",
  ["Recompute the budget in the open."],
  ["<b>Q1:</b> Timing jitter becomes 1.0 mm. RSS = sqrt(0.25+0.25+0.096+1.0+0.0025) = about 1.26 mm, still within 2 mm (worst case 2.36 mm exceeds it; blur also grows).",
   "<b>Q2:</b> The position at exposure is linked to an exact encoder count; the delay only changes how many counts are added, which is measured.",
   "<b>Q3:</b> People are near the machine during commissioning; risk reduction must be in place first (ISO 10218, W2D4)."],
  "Now let us step back and look at the whole course.")
c(5, "Show the ten days in two columns. Week one built one good joint: actuators, models, control and servo drives. Week two made many joints do useful work: mechanisms and kinematics, manufacturing systems, then sensors and integration. Ask students which day they found hardest and which most useful; collect a few answers. This is also a good moment for feedback on the course.",
  ["Week 1: one joint. Week 2: the whole robot.", "Misconception: the topics are separate subjects. They are layers of one machine."],
  ["<b>Q:</b> Which topic links both weeks most strongly? <b>A:</b> Feedback control: it appears in servo loops, robot control and filtering."],
  "All of this meets in a single robot joint.")
c(6, "Follow the signal around the loop: the PLC program commands a move, trajectory generation and inverse kinematics give joint set-points, the position, velocity and current loops drive the motor through the gearbox, the link and payload move, sensors measure, the ADC and filters clean the signal, and networks connect it all. The orange numbers are the session codes where each block was taught. Read the one-sentence summary: the weakest link sets the performance.",
  ["Design all blocks together.", "Misconception: a better controller can compensate any weak block."],
  ["<b>Q:</b> Which block limits a joint with a soft gearbox? <b>A:</b> The mechanics: resonance limits the loop bandwidth."],
  "Ten principles to take home.")
c(6, "Read the ten principles, one per student if the group is small. Each one names the day where it came from, so students can go back to the slides. Ask each student to choose the one principle they think they will use first in their next project or lab, and say why.",
  ["Principles are easier to remember than formulas.", "Misconception: the course content is only theory; each principle is a practical rule."],
  [], "A short summary of today.")
c(3, "Summarise today session by session using the bullets, and run through the key terms quickly as a quiz: point at a term, a student defines it.",
  ["Timing and transforms were the threads of today."],
  [], "And finally, where to go from here.")
c(4, "Point to further courses and practical projects: state-space control, robot dynamics and force control, motion planning and SLAM, 3D perception and learning-based grasping, and practical work with ROS 2, PLCs and real servo drives. Thank the students. Invite questions and remind them of the challenge: next time they see a robot cell, name its actuators, sensors, loops and networks.",
  ["Learning continues in the lab.", "Misconception: robotics is mainly programming. It is mechanics, electronics, control and software together."],
  ["<b>Q:</b> Questions and discussion."], "End of the course.")
c(0, "Figure credits: show briefly; all photographs are from Wikimedia Commons under free licences, all diagrams and plots were drawn for this course.",
  ["Credit every image you reuse."], [], "References.")
c(0, "References: point students to Corke for robotics and vision, Oppenheim and Schafer for signal processing, and the standards for networks and safety.",
  ["Use textbooks and standards, not only web searches."], [], "End.")

# ---- extra sentences for shorter cards (keeps each .say near 80-110 words) ----
_EXTRA = {
13: "Before the break, ask everyone to write down one number they remember from this session, such as half a millimetre per pixel.",
22: "Then connect forward: everything after the ADC is numbers, and the next session is about what we do with those numbers. Remind them that the digital world cannot undo mistakes made before the sampler, so the analogue front end, the sample rate and the number of bits are decisions to take early in a design, not after the robot is built.",
32: "Also remind the students that a filter design always starts from the question: which frequencies carry information, and which carry noise or resonance? If they can sketch that on a frequency axis, the filter choice becomes obvious. Close by repeating the fusion idea in one sentence, because it is the most transferable idea of the session.",
43: "Ask the students to name, for each level of the automation pyramid, one network and its typical cycle time. Then remind them that the safest design closes fast loops locally and sends slow, meaningful data upwards. If time permits, ask which networks they have seen in a lab or internship; many will have met CAN in cars or ROS in student projects.",
48: "Add a short story if you have one from industry: a cell that failed at the customer because the encoder latch was wired to the wrong input, for example.",
50: "Remind the students that the course followed the same path as a real robot design: choose the actuator, make it controllable, describe the geometry, place it in a production system, and finally measure and connect it.",
52: "If the group is large, ask them to vote with raised hands on the most important principle; the discussion of why is often more valuable than the vote itself.",
53: "Ask: which session today connected most strongly to week one? Most will say signal processing, because filters and delay appeared in the control sessions. Link the threads together: vision gives a pose through a chain of transforms, sampling and filtering decide how much we can trust a number, and networks decide how old it is when it arrives.",
54: "Finally, collect written feedback if your institution requires it, and remind students where the slides, notes and references can be found for exam preparation.",
55: "If a student asks about reusing images, explain the licence types briefly: CC BY requires attribution, CC BY-SA also requires sharing derived works under the same licence, and public-domain images can be reused freely. Every image on these slides lists author and licence on the slide itself.",
56: "Recommend one book per area for students who want to go further: Corke for robotics and vision with code examples, Oppenheim and Schafer for digital filters, Thrun et al. for Kalman filters and localisation, and the Springer Handbook of Robotics as a reference. Standards are expensive but often available through the university library.",
}
for _i, _x in _EXTRA.items():
    _m, _s, _e, _a, _t = S[_i]
    S[_i] = (_m, _s + " " + _x, _e, _a, _t)
