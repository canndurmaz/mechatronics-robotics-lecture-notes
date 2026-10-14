new["HEAD"] = r"""\documentclass[aspectratio=169,10pt]{beamer}
\usetheme{mekatronik}
\renewcommand{\coursetitle}{Mechatronics and Robotics Engineering (50 h)}
\setweek{1}
\setday{5}{Servo Systems II}
\title[W1D5 -- Servo Systems II]{Servo Systems II: FOC, Cascaded Loops, Tuning and Trajectories}
\subtitle{3.3 Field-oriented control \textbullet\ 3.4 Cascaded loops \textbullet\ 3.5 Loop tuning \& bandwidth \textbullet\ 3.6 Trajectories, feedforward \& disturbance compensation}
\author{Mechatronics and Robotics Engineering Programme}
\institute{Week 1 \textperiodcentered{} Day 5}
\date{2 weeks \textperiodcentered{} 10 days \textperiodcentered{} 50 hours}

% ---- local helpers -------------------------------------------------
\tikzset{
  blk/.style={draw=mkBlue,fill=mkPale,rounded corners=1.5pt,minimum height=7mm,minimum width=12mm,font=\scriptsize,align=center,line width=.6pt},
  blko/.style={blk,draw=mkOrange,fill=mkCream},
  sumn/.style={draw=mkBlue,circle,inner sep=0pt,minimum size=4mm,fill=white,line width=.6pt},
  sig/.style={-{Latex[length=2mm]},mkNavy,line width=.6pt},
  fb/.style={-{Latex[length=2mm]},mkMid,line width=.6pt},
  ff/.style={-{Latex[length=2mm]},mkOrange,line width=.7pt,dashed},
  lab/.style={font=\tiny,text=mkNavy},
}
\newcommand{\src}[1]{\par\vfill\hfill{\color{mkGray}\fontsize{6}{7}\selectfont #1}}
\newcommand{\gofurther}[1]{\par\vspace{1mm}{\scriptsize\color{mkGray}\textbf{\color{mkMid}Going further:} #1\par}}
\pgfplotsset{every axis/.append style={label style={font=\scriptsize}}}

\begin{document}

\begin{frame}[plain]\titlepage\end{frame}

% =====================================================================
\begin{frame}[t]{Agenda and learning outcomes}
\begin{columns}[T,onlytextwidth]
\column{.52\textwidth}
\footnotesize
\begin{tabularx}{\linewidth}{@{}l X r@{}}
\toprule
\textbf{Code} & \textbf{Session} & \textbf{Net time}\\
\midrule
3.3 & Field-oriented control (Clarke/Park intuition, $d$--$q$ currents) & 1.5 h\\
3.4 & Cascaded current, velocity and position loops & 1.5 h\\
3.5 & Loop tuning and bandwidth (inner $\rightarrow$ outer, inertia ratio, delays) & 1.0 h\\
3.6 & Trajectory generation, feedforward, disturbance compensation & 1.0 h\\
\midrule
 & \textbf{Total} (+ 10-min breaks about every hour) & \textbf{5.0 h}\\
\bottomrule
\end{tabularx}\\[2mm]
\begin{notebox}
\textbf{One reference joint all day}: PM servo motor $p=4$, $R=\SI{0.5}{\ohm}$, $L=\SI{3}{mH}$,
$\psi_\text{PM}=\SI{0.12}{Vs}$, $k_t=\SI{0.72}{Nm/A}$, $J_m=\SI{3e-4}{kg\,m^2}$ (load $3\times$),
$V_\text{dc}=\SI{325}{V}$, $\hat I_\text{max}=\SI{20}{A}$, PWM \SI{16}{kHz}; gear $N=100$.
\end{notebox}
\column{.45\textwidth}
\begin{keybox}[By the end of today you can \ldots]
\small
\checkitem\ explain why FOC turns AC currents into two DC numbers\\
\checkitem\ sketch the $abc\rightarrow\alpha\beta\rightarrow dq$ chain and the FOC loop\\
\checkitem\ calculate PI gains for the current and velocity loops\\
\checkitem\ explain bandwidth, inertia ratio and the phase cost of delays\\
\checkitem\ plan a trapezoidal joint move and add feedforward and gravity compensation
\end{keybox}
\end{columns}
\end{frame}

% =====================================================================
\begin{frame}[t]{What we learned so far (1/2): control tools from W1D3--W1D4}
\begin{columns}[T,onlytextwidth]
\column{.5\textwidth}
\begin{defbox}[Feedback and its limits]
\begin{itemize}\small
\item PID: P = now, I = past, D = trend of the error (2.5).
\item Bode plot and phase margin = distance from oscillation (2.4, 2.6).
\item Filters cost phase; notch removes one frequency (2.7).
\item A digital loop adds delay of about 1.5 samples (2.8).
\end{itemize}
\end{defbox}
\column{.48\textwidth}
\begin{defbox}[Robot manipulator control (2.9)]
\begin{itemize}\small
\item Independent-joint control: one servo loop per joint.
\item Gravity compensation and computed torque: \hl{predict} the torque instead of waiting for the error.
\end{itemize}
\end{defbox}
\centering
\begin{tikzpicture}[x=1cm,y=1cm]
  \node[sumn] (s) at (0,0) {};
  \node[blk] (c) at (1.3,0) {PID};
  \node[blk] (g) at (2.9,0) {joint};
  \draw[sig] (-.9,0) node[left,lab]{$\theta^*$} -- (s); \draw[sig] (s) -- (c); \draw[sig] (c) -- (g);
  \draw[sig] (g) -- (4.2,0) node[right,lab]{$\theta$};
  \draw[ff] (1.3,.9) node[above,lab]{model torque (FF)} -- (c.north);
  \draw[fb] (3.8,0) -- (3.8,-.7) -| node[pos=.75,left,lab]{encoder} (s.south);
  \node[font=\tiny,mkGray] at (-.2,-.35) {$-$};
\end{tikzpicture}
\end{columns}
\end{frame}

% ---------------------------------------------------------------------
\begin{frame}[t]{What we learned so far (2/2): the servo drive, and today's chain}
\begin{columns}[T,onlytextwidth]
\column{.5\textwidth}
\begin{defbox}[Servo architecture and power stage (3.1 and 3.2)]
\begin{itemize}\small
\item Drive modes: torque, velocity, position.
\item DC bus $\rightarrow$ three-leg inverter $\rightarrow$ PWM sets an \hl{average} voltage on each phase.
\item Limits: peak current, bus voltage; braking energy goes back to the DC bus.
\end{itemize}
\end{defbox}
\includegraphics[width=.8\linewidth,height=2.0cm,keepaspectratio]{../figures/d4_servo_drives.png}\\
\credit{Servo drives. Tero Kontkanen, CC BY-SA 3.0, via Wikimedia Commons}
\column{.48\textwidth}
\small\textbf{Today: from switch commands to a precise joint move}\\[2mm]
\centering
\begin{tikzpicture}[y=-.95cm]
  \foreach \y/\t/\c/\s in {0/{voltage $\rightarrow$ current (FOC)}/mkMid/3.3,1/{current $\rightarrow$ torque $\rightarrow$ speed $\rightarrow$ position}/mkBlue/3.4,2/{tuning the loops}/mkNavy/3.5,3/{planned moves + compensation}/mkOrange/3.6}{
    \node[draw=\c,fill=\c!15,rounded corners=2pt,minimum width=52mm,minimum height=7mm,font=\small,align=center] at (0,\y) {\t};
    \node[font=\scriptsize\bfseries,mkOrange] at (-3.1,\y) {\s};}
  \foreach \y in {0,1,2}{\draw[sig] (0,\y+.37) -- (0,\y+.63);}
\end{tikzpicture}
\end{columns}
\end{frame}

"""

new["FOC_JOINT"] = r"""\begin{frame}[t]{FOC in a robot joint: from joint torque to $i_q$}
\begin{columns}[T,onlytextwidth]
\column{.50\textwidth}
\centering
\begin{tikzpicture}[scale=.95]
  \draw[fill=mkPale,draw=mkBlue,line width=.6pt] (0,0) rectangle (1.4,1.1); \node[font=\scriptsize,align=center] at (.7,.55) {PMSM\\+ FOC};
  \draw[fill=mkCream,draw=mkOrange,line width=.6pt] (1.6,.1) rectangle (2.6,1.0); \node[font=\scriptsize,align=center] at (2.1,.55) {gear\\$N$};
  \draw[mkNavy,line width=1.2pt] (1.4,.55) -- (1.6,.55);
  \fill[mkBlue] (2.95,.55) circle (.17);
  \draw[mkNavy,line width=1.2pt] (2.6,.55) -- (2.8,.55);
  \draw[fill=mkSky!60,draw=mkBlue,rotate around={25:(2.95,.55)}] (2.95,.4) rectangle (5.6,.7);
  \fill[mkRed!70] ($(2.95,.55)+(25:2.0)$) circle (.12) node[above left=1pt,font=\tiny,mkNavy]{payload};
  \draw[-{Latex[length=2mm]},mkOrange,line width=1pt] (2.95,.55) ++(-60:.45) arc (-60:60:.45);
  \node[font=\scriptsize,mkOrange] at (3.55,-.05) {$T_\text{joint}$};
  \node[font=\tiny,mkGray] at (.7,-.25) {$T_m=k_t i_q$};
\end{tikzpicture}\\[1mm]
\includegraphics[width=.62\linewidth,height=2.3cm,keepaspectratio]{../figures/d1_harmonic_drive.jpg}\\
\credit{Strain-wave (harmonic) gear set. Pieceofmetalwork, CC BY-SA 4.0, via Wikimedia Commons}
\column{.48\textwidth}
\begin{eqbox}\centering
$i_q^*=\dfrac{T_\text{joint}}{N\,\eta\,k_t}$
\end{eqbox}
\begin{defbox}[Worked example (reference joint)]
\small
\begin{enumerate}
\item Joint needs $T_\text{joint}=\SI{120}{Nm}$; gear $N=100$, efficiency $\eta=0.8$.
\item Motor torque: $120/(100\cdot0.8)=\SI{1.5}{Nm}$.
\item Current: $i_q^*=1.5/0.72=\SI{2.08}{A}$, $i_d^*=0$.
\item Joint at \SI{3}{rad/s} $\Rightarrow$ motor at \SI{300}{rad/s} $\approx\SI{2865}{rpm}$ -- near the \SI{3000}{rpm} example.
\end{enumerate}
\end{defbox}
\small\hl{Take-away:} the robot controller thinks in joint torque; FOC turns it into $i_q$.
\end{columns}
\end{frame}

"""

new["CASCADE_JOINT"] = r"""\begin{frame}[t]{Cascaded loops in a robot joint: who closes what?}
\centering
\begin{tikzpicture}[x=1cm,y=1cm]
  \node[blko,minimum width=22mm,minimum height=16mm] (rc) at (0,0) {robot controller\\trajectory +\\kinematics/model};
  \draw[mkGray,dashed,rounded corners=3pt] (2.0,-1.15) rectangle (7.7,1.15); \node[font=\tiny,mkGray,anchor=north west] at (2.05,1.12) {servo drive (one per joint)};
  \node[blk] (pp) at (2.9,0) {position\\P};
  \node[blk] (vv) at (4.6,0) {velocity\\PI};
  \node[blk] (ii) at (6.4,0) {current\\PI + FOC};
  \node[blk] (mm) at (8.6,0) {PMSM};
  \node[blko] (gg) at (10.1,0) {gear\\$N$};
  \node[blk] (ll) at (11.6,0) {link +\\payload};
  \draw[sig] (rc) -- node[above,lab,pos=.45]{$\theta^*$} (pp); \draw[sig] (pp) -- (vv); \draw[sig] (vv) -- (ii); \draw[sig] (ii) -- (mm);
  \draw[mkNavy,line width=1.2pt] (mm) -- (gg); \draw[mkNavy,line width=1.2pt] (gg) -- (ll);
  \node[blk,minimum width=9mm] (enc) at (8.6,-1.55) {encoder};
  \draw[mkNavy] (mm) -- (enc);
  \draw[fb] (enc.west) -| (4.6,-.37); \draw[fb] (enc.west) -| (2.9,-.37);
  \draw[fb] (8.0,.0) ++(0,.35) |- (6.4,.75) -- (ii.north);
  \node[lab] at (7.3,.95) {$i_a, i_b$};
  \draw[ff] (rc.north) |- (4.6,1.55) node[pos=.7,above,lab]{$\dot\theta^*$, torque FF $\tau^*$ (every 1--4\,ms)} -- (vv.north);
  \node[blk,minimum width=9mm,dashed] (enc2) at (11.6,-1.55) {joint encoder\\(optional)};
  \draw[mkGray,dashed] (ll) -- (enc2);
\end{tikzpicture}\\[2mm]
\begin{columns}[T,onlytextwidth]
\column{.5\textwidth}
\begin{itemize}\small
\item Most industrial arms: the drive closes all three loops; the robot controller sends set-points over a fieldbus (EtherCAT, W2D5).
\item Computed-torque / force control (2.9): the controller sends \hl{torque}; the drive runs only the current loop.
\end{itemize}
\column{.48\textwidth}
\begin{itemize}\small
\item Encoder on the motor sees motor angle; the link angle differs by gear \term{backlash} and \term{compliance} (W1D2).
\item Cobots often add a joint-side encoder or torque sensor.
\end{itemize}
\end{columns}
\end{frame}

"""

new["POSLOOP"] = r"""\begin{frame}[t]{Position loop: a P controller and the following error}
\begin{columns}[T,onlytextwidth]
\column{.52\textwidth}
\begin{itemize}\small
\item With a good velocity loop, speed $\approx$ command; position is the integral of speed.
\item So a simple \hl{P controller} reaches any fixed target with zero error. Gain $k_v$ (1/s).
\item Following a ramp (constant speed $\omega$) leaves a constant lag: the \term{following error}.
\end{itemize}
\begin{eqbox}\centering
$e_\text{ss}=\dfrac{\omega}{k_v}$\qquad (P loop, no feedforward)
\end{eqbox}
\begin{tikzpicture}
\begin{axis}[mkplot,width=7.4cm,height=3.3cm,xmin=0,xmax=0.3,ymin=0,ymax=0.32,xlabel={time (s)},ylabel={joint angle (rad)},legend pos=north west,legend style={font=\tiny},
  yticklabel style={/pgf/number format/fixed},xticklabel style={/pgf/number format/fixed}]
\addplot[mkGray,thick,dashed,domain=0:0.3] {x};
\addplot[mkBlue,thick,domain=0:0.3,samples=80] {x-0.02*(1-exp(-50*x))};
\draw[mkOrange,{Latex[length=1.5mm]}-{Latex[length=1.5mm]}] (axis cs:0.24,0.22) -- node[right,font=\tiny]{$e_\text{ss}$} (axis cs:0.24,0.24);
\legend{command $\theta^*$,actual $\theta$}
\end{axis}
\end{tikzpicture}
\column{.46\textwidth}
\begin{defbox}[Worked example: robot joint]
\small
\begin{enumerate}
\item Joint loop $k_v=\SI{50}{s^{-1}}$, joint speed $\omega=\SI{1}{rad/s}$.
\item $e_\text{ss}=1/50=\SI{0.02}{rad}=1.15^\circ$.
\item At \SI{1}{m} reach the tool lags $0.02\cdot1=\SI{20}{mm}$ (!)
\item Doubling $k_v$ halves it -- but stability limits $k_v$.
\end{enumerate}
\end{defbox}
\small Analogy: a dog on a leash -- the faster the walk, the longer the leash.\\[1mm]
\begin{notebox}
Six joints with \hl{different} lags bend a straight tool path -- feedforward (3.6) fixes this.
\end{notebox}
\end{columns}
\end{frame}

"""

new["CHECK34"] = r"""\begin{frame}[t]{Check your understanding -- 3.4}
\vspace{4mm}
\begin{keybox}[Check your understanding]
\large
\begin{enumerate}
\item $L=\SI{6}{mH}$, $T_\sigma=\SI{100}{\micro s}$. What current-loop gain $K_p$ does the recipe give?\\[3mm]
\item A robot joint turns at \SI{0.5}{rad/s} with $k_v=\SI{25}{s^{-1}}$ and no feedforward. Following error in degrees?\\[3mm]
\item Why must the loops be tuned from the inside out?
\end{enumerate}
\end{keybox}
\vfill
\centering\small\color{mkGray} Discuss with your neighbour for 2 minutes.
\end{frame}

"""

new["SUM34"] = r"""\begin{frame}{Summary 3.4 -- Cascaded loops}
\begin{columns}[T,onlytextwidth]
\column{.56\textwidth}
\begin{keybox}[Key take-aways]
\small
\begin{itemize}
\item Cascade: position (P) $\rightarrow$ velocity (PI) $\rightarrow$ current (PI); inner loops are faster.
\item Current PI: $T_i=L/R$, $K_p=L/(2T_\sigma)$ $\Rightarrow$ about \SI{850}{Hz}.
\item Velocity PI: $K_p=J\omega_c/k_t$ with $\omega_c=1/(aT_\text{eq})$.
\item P position loop: following error $\omega/k_v$.
\item Limits need anti-windup; in robots the drive or the controller may close the outer loops.
\end{itemize}
\end{keybox}
\column{.42\textwidth}
\begin{defbox}[Key terms]
\small
\textbf{Cascade} -- loops nested inside each other.\\
\textbf{Crossover $\omega_c$} -- where loop gain is 1.\\
\textbf{$k_v$} -- position-loop gain (1/s).\\
\textbf{Following error} -- lag behind a moving target.\\
\textbf{Windup} -- integrator overfills during a limit.\\
\textbf{Technical / symmetric optimum} -- PI recipes.
\end{defbox}
\end{columns}
\end{frame}

"""

new["TRAPEX"] = r"""\begin{frame}[t]{Worked example: planning a trapezoidal joint move}
\begin{columns}[T,onlytextwidth]
\column{.50\textwidth}
\begin{tikzpicture}
\begin{groupplot}[group style={group size=1 by 2,vertical sep=3mm,xticklabels at=edge bottom},
  mkplot,width=7.6cm,xmin=0,xmax=1.1,xticklabel style={/pgf/number format/fixed}]
\nextgroupplot[height=3.3cm,ylabel={$\theta$ (rad)},ymin=0,ymax=1.65]
\addplot[mkBlue,thick,domain=0:0.25,samples=30] {4*x^2};
\addplot[mkBlue,thick,domain=0.25:0.75,samples=2] {0.25+2*(x-0.25)};
\addplot[mkBlue,thick,domain=0.75:1,samples=30] {1.5-4*(1-x)^2};
\addplot[mkBlue,thick,domain=1:1.1,samples=2] {1.5};
\nextgroupplot[height=3.3cm,ylabel={$\omega$ (rad/s)},xlabel={time (s)},ymin=0,ymax=2.4]
\addplot[mkOrange,thick] coordinates {(0,0) (0.25,2) (0.75,2) (1,0) (1.1,0)};
\draw[mkGray,densely dotted] (axis cs:0.25,0) -- (axis cs:0.25,2.4); \draw[mkGray,densely dotted] (axis cs:0.75,0) -- (axis cs:0.75,2.4);
\node[font=\tiny,mkNavy] at (axis cs:0.125,0.4) {$t_a$}; \node[font=\tiny,mkNavy] at (axis cs:0.5,1.6) {$t_c$}; \node[font=\tiny,mkNavy] at (axis cs:0.875,0.4) {$t_a$};
\end{groupplot}
\end{tikzpicture}
\column{.48\textwidth}
\small Move a joint by $\Delta\theta=\SI{1.5}{rad}$ ($86^\circ$) with $\omega_\text{max}=\SI{2}{rad/s}$, $\alpha_\text{max}=\SI{8}{rad/s^2}$.
\begin{defbox}[Step by step]
\small
\begin{enumerate}
\item Ramp time $t_a=\omega_\text{max}/\alpha_\text{max}=\SI{0.25}{s}$.
\item Angle per ramp $\tfrac12\alpha t_a^2=\SI{0.25}{rad}$; both ramps \SI{0.5}{rad}.
\item Cruise: $1.0\,\text{rad}/\SI{2}{rad/s}=\SI{0.5}{s}$.
\item Total $T=2t_a+t_c=\SI{1.0}{s}$.
\end{enumerate}
\end{defbox}
\begin{eqbox}\centering
cruise exists only if $\Delta\theta\ge\omega_\text{max}^2/\alpha_\text{max}$ (here \SI{0.5}{rad})
\end{eqbox}
\small Otherwise the profile is a \term{triangle}. Robot controllers plan all joints to finish \hl{together} (synchronised PTP, W2D2).
\end{columns}
\end{frame}

"""

new["GRAVITY"] = r"""\begin{frame}[t]{Gravity compensation for a robot joint}
\begin{columns}[T,onlytextwidth]
\column{.50\textwidth}
\begin{tikzpicture}
\begin{axis}[mkplot,width=7.4cm,height=4.3cm,xmin=-90,xmax=90,xtick={-90,-45,0,45,90},ymin=0,ymax=45,
  xlabel={link angle from horizontal $\theta$ (deg)},ylabel={gravity torque (Nm)},legend style={font=\tiny,at={(0.5,0.03)},anchor=south}]
\addplot[mkBlue,thick,domain=-90:90,samples=91] {39.2*cos(x)};
\addplot[mkOrange,thick,dashed,domain=-90:90,samples=91] {0.392*cos(x)/0.72*100/2.5};
\legend{joint torque $mgl\cos\theta$,motor $i_q$ (A) $\times40$}
\end{axis}
\end{tikzpicture}\\
\includegraphics[width=.75\linewidth,height=2.2cm,keepaspectratio]{../figures/r15_robot_cell.jpg}\\
\credit{Robots in a car-body welding line. Mixabest, CC BY-SA 3.0, via Wikimedia Commons}
\column{.48\textwidth}
\begin{itemize}\small
\item Gravity pulls every link down: a load torque that \hl{changes with pose}.
\item Pure PI: the integrator must ``discover'' it -- sag and overshoot after each move.
\item Better: compute it from the model and add it as feedforward (2.9).
\end{itemize}
\begin{eqbox}\centering
$\tau_g=m\,g\,l\cos\theta,\qquad i_{q,\text{g}}=\dfrac{\tau_g}{N\,k_t}$
\end{eqbox}
\begin{defbox}[Example]
\small $m=\SI{8}{kg}$, $l=\SI{0.5}{m}$: $\tau_g=8\cdot9.81\cdot0.5=\SI{39.2}{Nm}$ (horizontal).
With $N=100$: motor \SI{0.392}{Nm}, $i_q=\SI{0.54}{A}$ just to hold still.
\end{defbox}
\gofurther{for several links the gravity vector $\bm g(\bm\theta)$ comes from the robot's dynamic model (W2D2, 4.6).}
\end{columns}
\end{frame}

"""

new["CHECK36"] = r"""\begin{frame}[t]{Check your understanding -- 3.6}
\vspace{4mm}
\begin{keybox}[Check your understanding]
\large
\begin{enumerate}
\item A joint must move \SI{0.3}{rad} with $\omega_\text{max}=\SI{2}{rad/s}$ and $\alpha_\text{max}=\SI{8}{rad/s^2}$. Trapezoid or triangle?\\[3mm]
\item A robot arm holds a load horizontally. Which compensation would you add, and why does it depend on the pose?\\[3mm]
\item Explain in one sentence how a disturbance observer ``sees'' a collision.
\end{enumerate}
\end{keybox}
\vfill
\centering\small\color{mkGray} Discuss with your neighbour for 2 minutes.
\end{frame}

"""

new["SUM36"] = r"""\begin{frame}{Summary 3.6 -- Trajectories, feedforward, disturbances}
\begin{columns}[T,onlytextwidth]
\column{.56\textwidth}
\begin{keybox}[Key take-aways]
\small
\begin{itemize}
\item Trajectory generator gives $\theta^*$, $\dot\theta^*$, $\ddot\theta^*$; S-curves limit jerk.
\item Feedforward sends the \emph{known} speed and torque directly: following error almost vanishes.
\item Gravity, friction and load push against the joint; model what you can.
\item A DOB estimates the \emph{unknown} push from $k_ti_q-\hat J\dot\omega$.
\item Cogging repeats with angle: table compensation.
\end{itemize}
\end{keybox}
\column{.42\textwidth}
\begin{defbox}[Key terms]
\small
\textbf{Trapezoidal profile} -- ramp, cruise, ramp.\\
\textbf{Jerk} -- rate of change of acceleration.\\
\textbf{Feedforward} -- act on the known command.\\
\textbf{Gravity compensation} -- $mgl\cos\theta$ added to $i_q^*$.\\
\textbf{DOB} -- disturbance observer.\\
\textbf{Cogging} -- magnet--slot torque at zero current.
\end{defbox}
\end{columns}
\end{frame}

"""

new["TAIL"] = r"""% =====================================================================
\begin{frame}[t]{Day summary}
\begin{columns}[T,onlytextwidth]
\column{.5\textwidth}
\begin{defbox}[From voltage to joint torque]
\small
\textbf{3.3} FOC: Clarke + Park (rotating camera) turn AC into DC; torque $k_ti_q$; joint torque $Nk_ti_q$.\\[1mm]
\textbf{3.4} Cascade P--PI--PI with simple recipes; following error $\omega/k_v$; anti-windup.
\end{defbox}
\column{.48\textwidth}
\begin{defbox}[From loops to accurate robot moves]
\small
\textbf{3.5} Bandwidth, inside-out tuning, 3--10$\times$ separation, pose-dependent inertia, delay cost.\\[1mm]
\textbf{3.6} Trapezoid/S-curve moves, feedforward, gravity compensation, observers.
\end{defbox}
\end{columns}
\vspace{3mm}
\centering
\begin{tikzpicture}[x=1cm]
  \foreach \x/\t/\c in {0/{FOC}/mkMid,2.9/{cascade\\loops}/mkBlue,5.8/{tuning \&\\bandwidth}/mkNavy,8.7/{trajectory +\\compensation}/mkOrange}{
    \node[draw=\c,fill=\c!15,rounded corners=2pt,minimum width=22mm,minimum height=9mm,font=\scriptsize,align=center] at (\x,0) {\t};}
  \foreach \x in {1.15,4.05,6.95}{\draw[sig] (\x,0) -- (\x+.6,0);}
\end{tikzpicture}\\[2mm]
\small Week 1 done: actuators $\rightarrow$ control $\rightarrow$ servo drives. Week 2 puts them into a robot arm.
\end{frame}

% ---------------------------------------------------------------------
\begin{frame}[t]{Preview of Week 2 Day 1: Servo III + Robot Mechanisms I}
\begin{columns}[T,onlytextwidth]
\column{.58\textwidth}
\begin{itemize}\small
\item \textbf{3.7} Resonance, compliance and notch filters in robot joints -- today's FRF peak, explained.
\item \textbf{4.1} Robot anatomy: joints, DOF, workspace; articulated, SCARA, gantry, delta, cobots, mobile robots.
\item \textbf{4.2} Spatial descriptions: rotation matrices and homogeneous transforms.
\item \textbf{4.3} Forward kinematics (DH convention; planar 2-link, SCARA).
\end{itemize}
\column{.40\textwidth}
\includegraphics[width=\linewidth,height=2.6cm,keepaspectratio]{../figures/d4_kuka_robot.jpg}\\
\credit{Industrial robot. Oleg Yunakov, CC BY-SA 4.0, via Wikimedia Commons}
\begin{notebox}
\textbf{Bring along from today}\\
-- the rotation matrix $R(\theta)$ (Park),\\
-- the two-mass FRF and the notch,\\
-- joint torque $=N\eta k_ti_q$.
\end{notebox}
\end{columns}
\end{frame}

% ---------------------------------------------------------------------
\begin{frame}[t]{Figure credits}
\scriptsize
All plots, block diagrams, vector diagrams and schematics without a credit line are original drawings computed for this course
(data generated by \texttt{w1d5/src/gen\_data.py}). Downloaded figures (Wikimedia Commons):\\[2mm]
\begin{tabularx}{\linewidth}{@{}l X l@{}}
\toprule
\textbf{File} & \textbf{Source (Wikimedia Commons) and author} & \textbf{Licence}\\
\midrule
d4\_servo\_drives.png & File:Servo motor drive.png -- Tero Kontkanen & CC BY-SA 3.0\\
d4\_bldc\_stator.jpg & File:Stator Winding of a BLDC Motor.jpg -- Medvedev & CC BY-SA 3.0\\
d1\_harmonic\_drive.jpg & File:Harmonic Drive AG strain wave gear set.jpg -- Pieceofmetalwork & CC BY-SA 4.0\\
d4\_kuka\_robot.jpg & File:KUKA industrial robotic arm performing ``The Beach'' by Roy Nachum - 02.jpg -- Oleg Yunakov & CC BY-SA 4.0\\
d4\_signal\_analyzer.jpg & File:3562A Dynamic Signal Analyzer HP.jpg -- Loxyger & CC BY 4.0\\
d4\_machining\_center.jpg & File:DeckelMaho-DMU50e-MachiningCenter.jpg -- Glenn McKechnie & CC BY-SA 2.0\\
d1\_bldc.jpg & File:Floppy drive spindle motor open.jpg -- Sebastian Koppehel & CC BY 3.0\\
r15\_robot\_cell.jpg & File:KUKA Industrial Robots IR.jpg -- Mixabest & CC BY-SA 3.0\\
\bottomrule
\end{tabularx}
\end{frame}

% ---------------------------------------------------------------------
\begin{frame}[t]{References}
\fontsize{6}{7}\selectfont\setlength{\itemsep}{0pt}
\begin{columns}[T,onlytextwidth]
\column{.5\textwidth}
\begin{itemize}
\item Krishnan, R.: \emph{Permanent Magnet Synchronous and Brushless DC Motor Drives}. CRC Press, 2010.
\item Leonhard, W.: \emph{Control of Electrical Drives}, 3rd ed. Springer, 2001.
\item Vas, P.: \emph{Sensorless Vector and Direct Torque Control}. Oxford Univ.\ Press, 1998.
\item Blaschke, F.: The principle of field orientation \ldots\ \emph{Siemens Review} 39, 1972.
\item Park, R.\,H.: Two-reaction theory of synchronous machines. \emph{AIEE Trans.} 48, 1929.
\item Clarke, E.: \emph{Circuit Analysis of A-C Power Systems}. Wiley, 1943.
\item Jahns, T.; Kliman, G.; Neumann, T.: Interior PM synchronous motors for adjustable-speed drives. \emph{IEEE Trans. Ind. Appl.} 22(4), 1986.
\item Kessler, C.: Das symmetrische Optimum. \emph{Regelungstechnik} 6, 1958.
\item Ellis, G.: \emph{Control System Design Guide}, 4th ed. Butterworth-Heinemann, 2012.
\item Åström, K.\,J.; Hägglund, T.: \emph{Advanced PID Control}. ISA, 2006.
\end{itemize}
\column{.48\textwidth}
\begin{itemize}
\item Åström, K.\,J.; Murray, R.\,M.: \emph{Feedback Systems}. Princeton Univ.\ Press, 2008.
\item Spong, M.\,W.; Hutchinson, S.; Vidyasagar, M.: \emph{Robot Modeling and Control}. Wiley, 2006.
\item Siciliano, B.; Sciavicco, L.; Villani, L.; Oriolo, G.: \emph{Robotics: Modelling, Planning and Control}. Springer, 2009.
\item Craig, J.\,J.: \emph{Introduction to Robotics: Mechanics and Control}, 3rd ed. Pearson, 2005.
\item Ohnishi, K.; Shibata, M.; Murakami, T.: Motion control for advanced mechatronics. \emph{IEEE/ASME Trans. Mechatronics} 1(1), 1996.
\item Armstrong-Hélouvry, B.; Dupont, P.; Canudas de Wit, C.: A survey of models, analysis tools and compensation methods for the control of machines with friction. \emph{Automatica} 30(7), 1994.
\item Biagiotti, L.; Melchiorri, C.: \emph{Trajectory Planning for Automatic Machines and Robots}. Springer, 2008.
\item Microchip AN1078: Sensorless field oriented control of a PMSM. \quad IEC 61800-2: Adjustable speed electrical power drive systems.
\end{itemize}
\end{columns}
\end{frame}

\end{document}
"""
