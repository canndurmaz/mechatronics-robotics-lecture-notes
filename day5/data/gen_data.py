#!/usr/bin/env python3
"""Generates the numerical data plotted in day5.tex (pgfplots tables)."""
import numpy as np
from scipy import signal
import os
D = os.path.dirname(os.path.abspath(__file__))
def save(name, cols, header):
    np.savetxt(os.path.join(D, name), np.column_stack(cols), header=header, comments='', fmt='%.6g')

# ---------------- two-mass system ---------------------------------------
JM, k = 1.2e-4, 600.0           # motor inertia kg m^2, shaft stiffness Nm/rad
f = np.logspace(1, np.log10(3000), 800)
w = 2*np.pi*f; s = 1j*w
def twomass(JL, zeta=0.03):
    c = 2*zeta*np.sqrt(k*JL)
    return (JL*s**2 + c*s + k)/(s*(JM*JL*s**2 + c*(JM+JL)*s + k*(JM+JL)))
cols=[f]
for R in (1, 5, 10):
    JL = R*JM
    G = twomass(JL)
    rigid = 1/((JM+JL)*s)
    cols += [20*np.log10(abs(G)), 20*np.log10(abs(rigid))]
save('twomass.dat', cols, 'f G1 r1 G5 r5 G10 r10')

# ---------------- velocity loop with/without notch ------------------------
JL = 5*JM; G = twomass(JL)
Jt = JM+JL
fc = 50.0; Kp = Jt*2*np.pi*fc; wi = 2*np.pi*fc/5
C = Kp*(1+wi/s)
Gi = 1/(1+s/(2*np.pi*2000))                     # closed current loop approx.
Td = 125e-6; Dly = np.exp(-s*Td)                # sampling/computation delay
fn = np.sqrt(k*(JM+JL)/(JM*JL))/(2*np.pi)
wn = 2*np.pi*fn
def notch(wn, zz, zp): return (s**2+2*zz*wn*s+wn**2)/(s**2+2*zp*wn*s+wn**2)
N = notch(wn, 0.02, 0.6)
L0 = C*Gi*Dly*G; L1 = L0*N; Lr = C*Gi*Dly/(Jt*s)
ph = lambda x: np.unwrap(np.angle(x))*180/np.pi
save('velloop.dat', [f, 20*np.log10(abs(Lr)), 20*np.log10(abs(L0)), 20*np.log10(abs(L1)),
                      ph(Lr), ph(L0), ph(L1)], 'f Lr L0 L1 pr p0 p1')
print('two-mass fn (R=5): %.1f Hz, fAR: %.1f Hz' % (fn, np.sqrt(k/JL)/(2*np.pi)))
i = np.argmin(abs(f-fn)); print('|L0| at fn: %.1f dB, |L1| %.1f dB' % (20*np.log10(abs(L0[i])), 20*np.log10(abs(L1[i]))))

# ---------------- notch variations ---------------------------------------
f2 = np.logspace(np.log10(50), np.log10(3000), 800); s2 = 1j*2*np.pi*f2
wn2 = 2*np.pi*400
def notch2(zz, zp): return (s2**2+2*zz*wn2*s2+wn2**2)/(s2**2+2*zp*wn2*s2+wn2**2)
cols=[f2]
for zz, zp in ((0.0, 0.3), (0.03, 0.3), (0.0, 0.1), (0.1, 0.3)):
    H = notch2(zz, zp)
    cols += [20*np.log10(np.maximum(abs(H), 1e-4)), np.angle(H)*180/np.pi]
save('notch.dat', cols, 'f m1 p1 m2 p2 m3 p3 m4 p4')

# ---------------- low-pass torque filters ----------------------------------
f3 = np.logspace(1, np.log10(5000), 600); s3 = 1j*2*np.pi*f3; wf = 2*np.pi*1000
H1 = 1/(1+s3/wf); H2 = wf**2/(s3**2+2*0.707*wf*s3+wf**2)
save('lpf.dat', [f3, 20*np.log10(abs(H1)), 20*np.log10(abs(H2)), np.angle(H1)*180/np.pi,
                 np.unwrap(np.angle(H2))*180/np.pi], 'f m1 m2 p1 p2')

# ---------------- temperature sensors ------------------------------------
T = np.linspace(-40, 200, 121)
A, B = 3.9083e-3, -5.775e-7
pt1000 = 1000*(1+A*T+B*T**2)
ntc = 10e3*np.exp(3950*(1/(T+273.15)-1/298.15))
save('temp.dat', [T, pt1000, ntc], 'T pt ntc')

# ---------------- resolver signals ---------------------------------------
t = np.linspace(0, 10e-3, 4001)
fe = 2000.0  # (illustrative carrier, real ~ 10 kHz)
theta = 2*np.pi*100*t   # 100 rev/s electrical
exc = np.sin(2*np.pi*fe*t)
save('resolver.dat', [t*1e3, exc, 0.5*np.sin(theta)*exc, 0.5*np.cos(theta)*exc,
                      0.5*np.sin(theta), 0.5*np.cos(theta)], 't e s c es ec')

# ---------------- velocity measurement errors -----------------------------
n = np.logspace(-1, np.log10(6000), 300)  # rpm
Nl = 2500; Ts = 125e-6; fclk = 100e6
dM = 60/(4*Nl*Ts)               # rpm per count (M-method)
relM = dM/n*100
relT = (4*Nl*n/60)/fclk*100     # 1/m with m = fclk*Tedge
# M/T: detection window >= Ts, relative error ~ 1/(fclk*Tdet)
relMT = np.full_like(n, 1/(fclk*Ts)*100)
save('velmeas.dat', [n, relM, relT, relMT], 'n M T MT')
print('M-method resolution: %.2f rpm' % dM)

# ---------------- quantisation -------------------------------------------
tq = np.linspace(0, 1, 801)
x = 0.95*np.sin(2*np.pi*tq)
Nb = 3; q = 2/2**Nb
xq = np.clip(np.round(x/q - 0.5)*q + q/2, -1+q/2, 1-q/2)
save('quant.dat', [tq, x, xq, (x-xq)/q], 't x xq e')

# ---------------- aliasing -----------------------------------------------
ta = np.linspace(0, 20e-3, 2001)
fs_a = 1000.0
save('alias_c.dat', [ta*1e3, np.sin(2*np.pi*900*ta), np.sin(-2*np.pi*100*ta)], 't x a')
tn = np.arange(0, 20e-3+1e-9, 1/fs_a)
save('alias_s.dat', [tn*1e3, np.sin(2*np.pi*900*tn)], 't x')

# ---------------- moving average ------------------------------------------
fr = np.linspace(1e-4, 0.5, 600)   # f/fs
cols=[fr]
for Nm in (4, 8, 16):
    wv, H = signal.freqz(np.ones(Nm)/Nm, 1, worN=2*np.pi*fr)
    cols.append(20*np.log10(np.maximum(abs(H), 1e-3)))
save('mavg.dat', cols, 'f N4 N8 N16')

# ---------------- Butterworth vs Bessel (4th order, fc=1 kHz) -------------
wc = 2*np.pi*1000
bb, ab = signal.butter(4, wc, analog=True)
bs_, as_ = signal.bessel(4, wc, analog=True, norm='mag')
fb = np.logspace(1.7, np.log10(1e4), 600); wb = 2*np.pi*fb
_, Hb = signal.freqs(bb, ab, wb); _, Hs = signal.freqs(bs_, as_, wb)
def gd(H): 
    p = np.unwrap(np.angle(H)); return -np.gradient(p, wb)*1e3  # ms
save('bwbs.dat', [fb, 20*np.log10(abs(Hb)), 20*np.log10(abs(Hs)), gd(Hb), gd(Hs)], 'f mb ms gb gs')
tt = np.linspace(0, 3e-3, 600)
_, yb = signal.step((bb, ab), T=tt); _, ys = signal.step((bs_, as_), T=tt)
save('bwbs_step.dat', [tt*1e3, yb, ys], 't b s')
print('Butterworth overshoot %.1f%%' % ((yb.max()-1)*100))

# ---------------- velocity from quantised position --------------------------
rng = np.random.default_rng(3)
Tsv = 125e-6; tv = np.arange(0, 0.05, Tsv)
wtrue = 2*np.pi*(1.0 + 0.5*np.sin(2*np.pi*20*tv))          # rad/s (~ 60 rpm)
th = np.cumsum(wtrue)*Tsv
cnt = 2*np.pi/(4*Nl)
thq = np.floor(th/cnt)*cnt
vraw = np.diff(thq, prepend=0)/Tsv; vraw[0]=vraw[1]
b, a = signal.butter(2, 2*np.pi*150, analog=True)
bz, az = signal.bilinear(b, a, 1/Tsv)
vf = signal.lfilter(bz, az, vraw, zi=signal.lfilter_zi(bz, az)*vraw[0])[0]
sel = slice(0, len(tv), 2)
save('velnoise.dat', [tv[sel]*1e3, wtrue[sel]*60/(2*np.pi), vraw[sel]*60/(2*np.pi), vf[sel]*60/(2*np.pi)], 't w r f')
print('raw velocity quantum %.2f rpm' % (cnt/Tsv*60/(2*np.pi)))
