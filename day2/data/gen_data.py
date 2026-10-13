#!/usr/bin/env python3
"""Generates the numerical data files used by day2.tex (pgfplots tables).
Run from day2/data:  python3 gen_data.py"""
import numpy as np
from scipy import signal
np.random.seed(3)
def save(name, cols, header):
    np.savetxt(name, np.column_stack(cols), header=header, comments='', fmt='%.6g')

# ---------- 1. DC motor (speed / voltage) --------------------------------
R, L, k, J, B = 1.2, 2.4e-3, 0.1, 2e-4, 1e-5
num = [k]; den = [L*J, L*B + R*J, R*B + k*k]
p = np.roots(den); print('DC motor poles', p, 'DC gain', k/(R*B+k*k))
t = np.linspace(0, 0.15, 301)
_, w = signal.step((num, den), T=t)
# current response: I/V = (Js+B)/den
_, i = signal.step(([J, B], den), T=t)
# first-order approx (L=0): tau_m = R J/(R B + k^2)
taum = R*J/(R*B + k*k); print('tau_m', taum)
wa = k/(R*B+k*k)*(1-np.exp(-t/taum))
save('dcmotor_step.dat', [t*1e3, w*24, i*24, wa*24], 't w i wapprox')   # 24 V step

# ---------- 2. P control, plant 1/(s+1)^3 --------------------------------
G = signal.TransferFunction([1], np.polymul([1, 1], np.polymul([1, 1], [1, 1])))
t = np.linspace(0, 20, 401)
cols = [t]
for Kp in [0.5, 1, 2, 4]:
    n = np.polymul(Kp, G.num); d = np.polyadd(G.den, n)
    _, y = signal.step((n, d), T=t); cols.append(y)
save('p_control.dat', cols, 't k05 k1 k2 k4')

# ---------- 3. P / PI / PD / PID on same plant ---------------------------
def closed(Cn, Cd):
    Ln = np.polymul(Cn, G.num); Ld = np.polymul(Cd, G.den)
    return Ln, np.polyadd(Ld, Ln)
Nf = 10
ctrl = {}
ctrl['P'] = ([1.0], [1])                                   # Kp = 1
ctrl['PI'] = ([1.0*2.0, 1.0], [2.0, 0])                    # Kp = 1, Ti = 2
Kp, Td = 1.0, 0.8                                          # PD with filtered D
ctrl['PD'] = (np.polyadd(np.polymul([Kp], [Td/Nf, 1]), [Kp*Td, 0]), [Td/Nf, 1])
Kp, Ti, Td = 2.0, 2.0, 0.6                                 # PID, Kp(1 + 1/(Ti s) + Td s/(1 + s Td/N))
num_pid = np.polyadd(np.polymul([Kp*Ti, Kp], [Td/Nf, 1]), [Kp*Td*Ti, 0, 0])
den_pid = np.polymul([Ti, 0], [Td/Nf, 1])
ctrl['PID'] = (num_pid, den_pid)
cols = [t]
for kname in ['P', 'PI', 'PD', 'PID']:
    n, d = closed(*ctrl[kname]); _, y = signal.step((n, d), T=t); cols.append(y)
    print(kname, 'final', y[-1], 'max', y.max())
save('pid_compare.dat', cols, 't P PI PD PID')

# ---------- 4. set-point weighting (PI, b = 1, 0.5, 0) on G --------------
Kp, Ti = 2.0, 2.5
cols = [t]
for b in [1.0, 0.5, 0.0]:
    # u = Kp(b r - y) + Kp/(Ti s)(r - y) => Y/R = G*(Kp b Ti s + Kp)/(Ti s) / (1 + G C)
    Cn = [Kp*Ti, Kp]; Cd = [Ti, 0]
    Fn = [Kp*b*Ti, Kp]
    n = np.polymul(Fn, G.num); d = np.polyadd(np.polymul(Cd, G.den), np.polymul(Cn, G.num))
    _, y = signal.step((n, d), T=t); cols.append(y)
    print('b', b, 'max', y.max())
save('spweight.dat', cols, 't b1 b05 b0')

# ---------- 5. integrator windup -----------------------------------------
dt = 1e-3; T = 12; N = int(T/dt)
tau = 1.0; Kp, Ti = 4.0, 0.8; umax = 1.2; Tt = 0.4
def run(mode):
    y = 0; I = 0; ys = []; us = []; vs = []
    for n in range(N):
        tt = n*dt
        r = 1.0 if tt < 6 else 0.4
        dist = -0.3 if tt > 9 else 0.0
        e = r - y
        v = Kp*e + I
        u = min(max(v, -umax), umax)
        if mode == 'none':
            I += Kp/Ti*e*dt
        elif mode == 'clamp':
            if not ((v > umax and e > 0) or (v < -umax and e < 0)):
                I += Kp/Ti*e*dt
        elif mode == 'bc':
            I += (Kp/Ti*e + (u - v)/Tt)*dt
        y += dt*(-y + u + dist)/tau
        ys.append(y); us.append(u); vs.append(v)
    return np.array(ys), np.array(us), np.array(vs)
tt = np.arange(N)*dt
res = {m: run(m) for m in ['none', 'clamp', 'bc']}
idx = slice(0, N, 30)
save('windup.dat', [tt[idx], res['none'][0][idx], res['clamp'][0][idx], res['bc'][0][idx],
                    res['none'][1][idx], res['clamp'][1][idx], res['bc'][1][idx], np.clip(res['none'][2][idx], -3, 6)],
     't ynone yclamp ybc unone uclamp ubc vnone')
for m in res: print('windup', m, 'max y', res[m][0].max())

# ---------- 6. feedforward on a servo axis (J s^2 plant) ------------------
Jm, Bm = 1e-3, 2e-3            # kg m^2, Nm s/rad
dt = 1e-5; T = 0.6; N = int(T/dt)
# S-curve-ish move: 1 rad in 0.3 s using smooth (cosine) velocity profile
def ref(tt):
    Tm = 0.3
    if tt < Tm:
        p = (tt/Tm - np.sin(2*np.pi*tt/Tm)/(2*np.pi))
        v = (1 - np.cos(2*np.pi*tt/Tm))/Tm
        a = 2*np.pi*np.sin(2*np.pi*tt/Tm)/Tm**2
        return p, v, a
    return 1.0, 0.0, 0.0
# PID position controller tuned for ~ 25 Hz bandwidth
wc = 2*np.pi*25
Kp_ = Jm*wc**2/3; Kd_ = Jm*wc*np.sqrt(3); Ki_ = Kp_*wc/10
def sim(ff, Jff):
    x = 0; v = 0; I = 0; es = []
    eprev = 0
    for n in range(N):
        tt = n*dt
        pr, vr, ar = ref(tt)
        e = pr - x
        I += Ki_*e*dt
        u = Kp_*e + I + Kd_*(vr - v)
        if ff: u += Jff*ar + Bm*vr
        acc = (u - Bm*v)/Jm
        v += acc*dt; x += v*dt
        es.append(e)
    return np.array(es)
e0 = sim(False, 0); e1 = sim(True, 0.9*Jm); e2 = sim(True, Jm)
tt = np.arange(N)*dt; idx = slice(0, N, 200)
save('feedforward.dat', [tt[idx]*1e3, e0[idx]*1e3, e1[idx]*1e3, e2[idx]*1e3,
     np.array([ref(x)[1] for x in tt[idx]])], 't e_fb e_ff90 e_ff100 vref')
print('FF max err mrad', abs(e0).max()*1e3, abs(e1).max()*1e3, abs(e2).max()*1e3)

# ---------- 7. FOPDT identification --------------------------------------
Gt = ([1.0*2.0], np.polymul([1, 1], np.polymul([0.5, 1], [0.25, 1])))   # K = 2
t = np.linspace(0, 8, 321)
_, y = signal.step(Gt, T=t)
ym = y + 0.025*np.random.randn(len(t))
K = 2.0
t28 = np.interp(0.283*K, y, t); t63 = np.interp(0.632*K, y, t)
tauf = 1.5*(t63 - t28); theta = t63 - tauf
print('FOPDT: t28 %.3f t63 %.3f tau %.3f theta %.3f' % (t28, t63, tauf, theta))
yf = np.where(t > theta, K*(1 - np.exp(-(t - theta)/tauf)), 0)
save('fopdt.dat', [t, ym, yf], 't ymeas yfit')

# ---------- 8. excitation signals ----------------------------------------
t = np.linspace(0, 1, 2001)
f0, f1 = 1, 40
chirp = np.sin(2*np.pi*(f0*t + (f1 - f0)/2*t**2))
# PRBS 7-bit LFSR, bit time 1/63 s -> one period of 127 bits over ~2 s; show first second
reg = 0b1111111; bits = []
for _ in range(127):
    b = ((reg >> 6) ^ (reg >> 5)) & 1
    bits.append(1 if (reg & 1) else -1); reg = ((reg << 1) | b) & 0x7F
Tb = 1/64
prbs = np.array([bits[int(x/Tb) % 127] for x in t])
# stepped sine: 4 discrete frequencies
fs = [3, 6, 12, 24]
step = np.array([np.sin(2*np.pi*fs[min(int(x*4), 3)]*x) for x in t])
save('excitation.dat', [t, chirp, prbs, step], 't chirp prbs stepped')

# ---------- 9. two-mass system FRF + coherence ---------------------------
Jm2, Jl2, ks, cs = 2e-4, 6e-4, 400.0, 0.02
f = np.logspace(0, 3, 400); s = 2j*np.pi*f
# from motor torque to motor speed
Gm = (Jl2*s**2 + cs*s + ks)/(s*(Jm2*Jl2*s**2 + cs*(Jm2 + Jl2)*s + ks*(Jm2 + Jl2)))
Grigid = 1/((Jm2 + Jl2)*s)
far = np.sqrt(ks/Jl2)/2/np.pi; fr = np.sqrt(ks*(Jm2 + Jl2)/(Jm2*Jl2))/2/np.pi
print('anti-res %.1f Hz, res %.1f Hz' % (far, fr))
Phi_n = 0.15**2   # noise PSD relative to unit excitation
coh = np.abs(Gm)**2/(np.abs(Gm)**2 + Phi_n*(1 + (f/300)**2) + 0*f)
save('twomass.dat', [f, 20*np.log10(abs(Gm)), np.angle(Gm, deg=True), 20*np.log10(abs(Grigid)), coh],
     'f mag ph magrigid coh')

# ---------- 10. common loop L = K/(s(s+2)(s+5)) --------------------------
K = 20.0
w = np.logspace(-2, 2, 500); s = 1j*w
Lw = K/(s*(s + 2)*(s + 5))
S = 1/(1 + Lw); Tc = Lw/(1 + Lw)
ph = np.unwrap(np.angle(Lw))*180/np.pi
mag = 20*np.log10(abs(Lw))
ic = np.argmin(abs(abs(Lw) - 1)); wc_ = w[ic]; PM = 180 + ph[ic]
ip = np.argmin(abs(ph + 180)); wpc = w[ip]; GM = -mag[ip]
print('L: wc %.3f PM %.1f wpc %.3f GM %.2f dB Ms %.2f Mt %.2f' % (wc_, PM, wpc, GM, abs(S).max(), abs(Tc).max()))
ib = np.argmin(abs(20*np.log10(abs(Tc)) + 3)); print('closed-loop BW', w[ib])
save('loop_bode.dat', [w, mag, ph, 20*np.log10(abs(S)), 20*np.log10(abs(Tc))], 'w mag ph S T')
# Nyquist: positive frequencies from 0.25 rad/s up
wn = np.logspace(np.log10(0.6), 2, 600); s = 1j*wn
Ln = K/(s*(s + 2)*(s + 5))
save('nyquist.dat', [Ln.real, Ln.imag, -Ln.imag], 're im imneg')
# closed-loop step responses for K = 10, 20, 50
t = np.linspace(0, 12, 481); cols = [t]
for Kk in [10, 20, 50]:
    _, y = signal.step(([Kk], [1, 7, 10, Kk]), T=t); cols.append(y)
save('loop_step.dat', cols, 't k10 k20 k50')
# root locus
Ks = np.concatenate([np.linspace(0, 5, 200), np.linspace(5, 200, 800)])
prev = np.roots([1, 7, 10, 0]); br = [[], [], []]
for Kk in Ks:
    r = np.roots([1, 7, 10, Kk])
    # match to previous by nearest neighbour
    order = []
    rem = list(r)
    for pv in prev:
        j = int(np.argmin([abs(pv - q) for q in rem])); order.append(rem.pop(j))
    prev = np.array(order)
    for b in range(3): br[b].append(prev[b])
br = [np.array(b) for b in br]
save('rlocus.dat', [Ks, br[0].real, br[0].imag, br[1].real, br[1].imag, br[2].real, br[2].imag],
     'K r1 i1 r2 i2 r3 i3')

# ---------- 11. model uncertainty: rigid model vs two-mass "truth" -------
f = np.logspace(0, 3, 400); s = 2j*np.pi*f
Gm = (Jl2*s**2 + cs*s + ks)/(s*(Jm2*Jl2*s**2 + cs*(Jm2 + Jl2)*s + ks*(Jm2 + Jl2)))
Grigid = 1/((Jm2 + Jl2)*s)
Delta = Gm/Grigid - 1
def T2(fb):
    wn = 2*np.pi*fb/1.0   # zeta = 0.707 -> -3 dB bandwidth ~ wn
    return wn**2/(s**2 + 2*0.707*wn*s + wn**2)
save('uncertainty.dat', [f, 20*np.log10(abs(Delta)), -20*np.log10(abs(Delta)), 20*np.log10(abs(T2(30))), 20*np.log10(abs(T2(150)))],
     'f D invD T30 T150')
