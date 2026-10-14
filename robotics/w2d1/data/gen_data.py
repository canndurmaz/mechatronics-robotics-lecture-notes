#!/usr/bin/env python3
"""Data for w2d1.tex (new plots). twomass/velloop/notch/lpf.dat are copied from day5/data."""
import numpy as np, os
from scipy import signal
D = os.path.dirname(os.path.abspath(__file__))
def save(name, cols, header):
    np.savetxt(os.path.join(D, name), np.column_stack(cols), header=header, comments='', fmt='%.6g')

# 1) two-mass: response of motor and load speed to a torque pulse (time domain)
JM, JL, k, zeta = 1.2e-4, 6e-4, 600.0, 0.03
c = 2*zeta*np.sqrt(k*JL)
# states: thM, wM, thL, wL ; input TM
A = np.array([[0,1,0,0],[-k/JM,-c/JM,k/JM,c/JM],[0,0,0,1],[k/JL,c/JL,-k/JL,-c/JL]])
B = np.array([[0],[1/JM],[0],[0]]); C = np.array([[0,1,0,0],[0,0,0,1]])
sys = signal.StateSpace(A,B,C,np.zeros((2,1)))
t = np.linspace(0, 0.03, 1500)
u = np.where(t < 0.005, 0.36, 0.0)   # 0.36 Nm for 5 ms
_, y, _ = signal.lsim(sys, u, t)
save('tm_time.dat', [t*1e3, y[:,0], y[:,1], u], 't wM wL u')
print('final speed', y[-1])

# 2) resonance frequency vs payload (robot joint: harmonic gear N=100)
N = 100; Jm = 1.5e-4; Jarm = 2.0; kj = 2.0e4  # Nm/rad joint stiffness at output
m = np.linspace(0, 10, 101); r = 0.8
JLo = Jarm + m*r**2               # load inertia at output
JMo = Jm*N**2                     # motor inertia reflected to output
fAR = np.sqrt(kj/JLo)/(2*np.pi)
fR = fAR*np.sqrt(1+JLo/JMo)
save('fr_payload.dat', [m, fAR, fR], 'm fAR fR')
print('fR at 0, 10 kg', fR[0], fR[-1], 'JMo', JMo)

# 3) planar 2-link: path of the tip for a joint-space straight line
l1, l2 = 0.4, 0.3
s = np.linspace(0, 1, 60)
q1 = np.radians(0 + 90*s); q2 = np.radians(90 - 60*s)
x = l1*np.cos(q1)+l2*np.cos(q1+q2); y = l1*np.sin(q1)+l2*np.sin(q1+q2)
save('tip_path.dat', [s, np.degrees(q1), np.degrees(q2), x, y], 's q1 q2 x y')
print('tip start', x[0], y[0], 'end', x[-1], y[-1])
