#!/usr/bin/env python3
"""Generate numerical data for the Day-3 plots (pgfplots tables).
Run from anywhere:  python3 make_data.py   -> writes *.dat next to this file and prints key numbers.
"""
import os
import numpy as np
from scipy import signal

D = os.path.dirname(os.path.abspath(__file__))


def save(name, cols, header):
    arr = np.column_stack(cols)
    np.savetxt(os.path.join(D, name), arr, fmt="%.6g", header=header, comments="")


def db(h):
    return 20 * np.log10(np.abs(h))


def ph(h):
    return np.degrees(np.unwrap(np.angle(h)))


def thin(*arrs, n=400):
    idx = np.linspace(0, len(arrs[0]) - 1, n).astype(int)
    return [a[idx] for a in arrs]


# ------------------------------------------------------------------ 1  LPF Bode (normalised w/wf)
u = np.logspace(-2, 2, 300)
s = 1j * u
h1 = 1 / (s + 1)
h2 = 1 / (s**2 + np.sqrt(2) * s + 1)
b4, a4 = signal.butter(4, 1, analog=True)
h4 = np.polyval(b4, s) / np.polyval(a4, s)
save("lpf_bode.dat", [u, db(h1), ph(h1), db(h2), ph(h2), db(h4), ph(h4)], "w m1 p1 m2 p2 m4 p4")

# ------------------------------------------------------------------ 2  phase loss at crossover vs wf/wc
r = np.logspace(0, np.log10(30), 200)
x = 1 / r
pl1 = np.degrees(np.arctan(x))
pl2 = np.degrees(np.arctan2(np.sqrt(2) * x, 1 - x**2))
h4c = np.polyval(b4, 1j * x) / np.polyval(a4, 1j * x)
pl4 = -np.degrees(np.unwrap(np.angle(h4c)))
save("phase_loss.dat", [r, pl1, pl2, pl4], "r p1 p2 p4")
print("LPF phase loss at r=10: 1st %.1f deg, 2nd %.1f deg, 4th %.1f" % (
    np.degrees(np.arctan(0.1)), np.degrees(np.arctan2(np.sqrt(2) * 0.1, 0.99)), np.interp(10, r, pl4)))

# ------------------------------------------------------------------ 3  HPF bode + step
hh = s / (s + 1)
save("hpf_bode.dat", [u, db(hh), ph(hh)], "w m p")

# ------------------------------------------------------------------ 4  notch family (normalised)
u2 = np.logspace(-1, 1, 500)
s2 = 1j * u2
cols = [u2]
for zz in (0.005, 0.05, 0.15):
    zp = 0.5
    hn = (s2**2 + 2 * zz * s2 + 1) / (s2**2 + 2 * zp * s2 + 1)
    cols += [db(hn), ph(hn)]
save("notch_bode.dat", cols, "w m1 p1 m2 p2 m3 p3")

# ------------------------------------------------------------------ 5  two-mass resonance + notch in the velocity loop
JM = JL = 1e-3
Jt = JM + JL
fr = 1000.0
wr = 2 * np.pi * fr
wa = wr / np.sqrt(2)
zr = 0.02
Td = 1.5 / 8000  # 1.5 samples at 8 kHz
fc = 100.0
wc = 2 * np.pi * fc
Kp = Jt * wc
wi = wc / 4
f = np.logspace(1, np.log10(3000), 800)
w = 2 * np.pi * f
s = 1j * w
Gr = 1 / (Jt * s)
R = (s**2 / wa**2 + 2 * zr * s / wa + 1) / (s**2 / wr**2 + 2 * zr * s / wr + 1)
G = Gr * R
C = Kp * (1 + wi / s)
Dl = np.exp(-s * Td)
wi_c = 2 * np.pi * 2000
Dl = Dl * wi_c**2 / (s**2 + 1.4 * wi_c * s + wi_c**2)  # delay x current-loop lag
zz, zp = 0.02, 0.35
N = (s**2 + 2 * zz * wr * s + wr**2) / (s**2 + 2 * zp * wr * s + wr**2)
L0 = C * G * Dl
L1 = C * G * Dl * N
save("notch_app.dat", [f, db(L0), ph(L0), db(L1), ph(L1), db(Gr * C * Dl)], "f m0 p0 m1 p1 mr")


def margins(L, w):
    m = np.abs(L)
    p = np.unwrap(np.angle(L))
    out = {}
    i = np.where(np.diff(np.sign(m - 1)))[0]
    out["wc"] = [w[k] / 2 / np.pi for k in i]
    out["pm"] = [180 + np.degrees(p[k]) for k in i]
    j = np.where(np.diff(np.sign(np.degrees(p) + 180 + 360 * np.round(-(np.degrees(p) + 180) / 360))))[0]
    # simpler: phase crossings of -180 mod 360
    pp = (np.degrees(p) + 180) % 360 - 180
    jj = np.where((np.abs(np.diff(pp)) < 180) & (np.diff(np.sign(pp)) != 0))[0]
    out["pc"] = [(w[k] / 2 / np.pi, 20 * np.log10(m[k])) for k in jj]
    return out


print("notch app no notch:", margins(L0, w))
print("notch app with notch:", margins(L1, w))
print("peak |L0| at resonance dB: %.1f" % db(L0).max() if False else "", "|L0| near 600 Hz:",
      db(L0)[np.argmin(np.abs(f - 600))])

# closed loop poles check (Pade for delay) to state stability honestly
def cl_stable(with_notch):
    from math import factorial as fa_
    nP = 6
    c = [fa_(2*nP-k)*fa_(nP)/(fa_(2*nP)*fa_(k)*fa_(nP-k))*Td**k for k in range(nP+1)]
    num_d = np.array([c[k]*(-1)**k for k in range(nP+1)][::-1]); den_d = np.array(c[::-1])
    # build L as polynomial ratio
    nC = np.array([Kp, Kp * wi]); dC = np.array([1, 0])
    nG = np.array([1 / wa**2, 2 * zr / wa, 1]); dG = np.polymul([Jt, 0], [1 / wr**2, 2 * zr / wr, 1])
    nL = np.polymul(np.polymul(np.polymul(nC, nG), num_d), [wi_c**2]); dL = np.polymul(np.polymul(np.polymul(dC, dG), den_d), [1, 1.4 * wi_c, wi_c**2])
    if with_notch:
        nL = np.polymul(nL, [1, 2 * zz * wr, wr**2]); dL = np.polymul(dL, [1, 2 * zp * wr, wr**2])
    p = np.roots(np.polyadd(dL, nL))
    return p.real.max()


print("max Re(pole) without notch: %.1f, with notch: %.1f" % (cl_stable(False), cl_stable(True)))

# ------------------------------------------------------------------ 6  robust stability |T| vs 1/|Delta|
Delta = R - 1
Lnom_n = C * Gr * Dl * N
T_n = Lnom_n / (1 + Lnom_n)
Lnom_0 = C * Gr * Dl
T_0 = Lnom_0 / (1 + Lnom_0)
save("robust.dat", [f, db(1 / np.abs(Delta)), db(T_0), db(T_n)], "f invW T0 Tn")
print("max |W T| no notch %.2f, with notch %.2f" % (np.max(np.abs(Delta * T_0)), np.max(np.abs(Delta * T_n))))
S_n = 1 / (1 + Lnom_n)
# performance weight 1/W1 = (s + wb*A)/(s/M + wb)
M, A, wb = 2.0, 1e-3, 2 * np.pi * 40
invW1 = (s + wb * A) / (s / M + wb)
save("sens.dat", [f, db(S_n), db(T_n), db(invW1), db(1 / np.abs(Delta))], "f S T invW1 invW3")
print("peak |S| dB %.2f, peak |T| dB %.2f" % (db(S_n).max(), db(T_n).max()))

# ------------------------------------------------------------------ 7  lead design worked example
J = 2e-4
wcl = 2 * np.pi * 50
phi = np.radians(50)
alpha = (1 + np.sin(phi)) / (1 - np.sin(phi))
T = 1 / (wcl * np.sqrt(alpha))
K = J * wcl**2 / np.sqrt(alpha)
print("lead: alpha=%.3f T=%.4e aT=%.4e zero=%.1f pole=%.1f K=%.3f" % (alpha, T, alpha * T, 1 / (alpha * T), 1 / T, K))
fl = np.logspace(0, 4, 400)
wl = 2 * np.pi * fl
sl = 1j * wl
Cl = K * (1 + alpha * T * sl) / (1 + T * sl)
Ll = Cl / (J * sl**2)
save("lead_bode.dat", [fl, db(Ll), ph(Ll), db(1 / (J * sl**2) * K), db((1 + alpha * T * sl) / (1 + T * sl)),
                       ph((1 + alpha * T * sl) / (1 + T * sl))], "f mL pL mP mC pC")
mm = margins(Ll, wl)
print("lead loop margins:", mm)
num = np.polymul([K * alpha * T, K], [1])
den = np.polymul([T, 1], [J, 0, 0])
cl = signal.TransferFunction(num, np.polyadd(den, num))
tt = np.linspace(0, 0.03, 600)
tt, yy = signal.step(cl, T=tt)
print("lead step overshoot %.1f %%" % ((yy.max() - 1) * 100))
save("lead_step.dat", [tt * 1e3, yy], "t y")
# normalised lead C(s) for plotting family: w/wm
un = np.logspace(-2, 2, 300)
cols = [un]
for al in (3, 7.55, 20):
    Tn = 1 / np.sqrt(al)
    hc = (1 + al * Tn * 1j * un) / (1 + Tn * 1j * un)
    cols += [db(hc), ph(hc)]
save("lead_family.dat", cols, "w m3 p3 m7 p7 m20 p20")
# lag family
cols = [un]
for be in (10,):
    Tg = 1.0  # zero at 1
    hg = (1 + Tg * 1j * un) / (1 + be * Tg * 1j * un)
    cols += [db(be * hg), ph(hg)]
save("lag_bode.dat", cols, "w m p")

# ------------------------------------------------------------------ 8  state feedback / integral action sims
J1, B1 = 1e-3, 2e-3
a, b = B1 / J1, 1 / J1
k1, k2 = 10.0, 0.138
kk1, kk2, kI = 17.0, 0.188, 500.0
dt = 1e-5
t = np.arange(0, 0.3, dt)
TL = np.where(t >= 0.15, 0.5, 0.0)
x = np.zeros(2); xi = np.zeros(3)
y1 = np.zeros_like(t); y2 = np.zeros_like(t)
for n, tn in enumerate(t):
    u1 = -k1 * x[0] - k2 * x[1] + k1 * 1.0
    x = x + dt * np.array([x[1], -a * x[1] + b * (u1 - TL[n])])
    u2 = -kk1 * xi[0] - kk2 * xi[1] + kI * xi[2]
    xi = xi + dt * np.array([xi[1], -a * xi[1] + b * (u2 - TL[n]), 1.0 - xi[0]])
    y1[n] = x[0]; y2[n] = xi[0]
tt, y1s, y2s = thin(t, y1, y2, n=500)
save("sf_step.dat", [tt * 1e3, y1s, y2s], "t y1 y2")
print("SF error under load: %.4f rad ; with integral: %.5f" % (1 - y1[-1], 1 - y2[-1]))

# ------------------------------------------------------------------ 9  observer vs finite difference
Ts = 1 / 4000
q = 2 * np.pi / 65536
l1, l2 = 698.0, 248604.0
dt = 1e-6
t = np.arange(0, 0.3, dt)
x = np.array([0.0, 0.5])
xh = np.zeros(2)
nsub = int(round(Ts / dt))
rec_t, rec_w, rec_fd, rec_wh = [], [], [], []
th_prev = 0.0
uu = 0.0
for n, tn in enumerate(t):
    if n % nsub == 0:
        thm = np.round(x[0] / q) * q
        fd = (thm - th_prev) / Ts
        th_prev = thm
        uu = 0.1 * np.sin(2 * np.pi * 5 * tn)
        # observer update (forward Euler at Ts)
        e = thm - xh[0]
        xh = xh + Ts * np.array([xh[1] + l1 * e, -a * xh[1] + b * uu + l2 * e])
        rec_t.append(tn); rec_w.append(x[1]); rec_fd.append(fd); rec_wh.append(xh[1])
    x = x + dt * np.array([x[1], -a * x[1] + b * uu])
rec_t = np.array(rec_t); sel = slice(0, len(rec_t), 2)
save("observer.dat", [rec_t[sel] * 1e3, np.array(rec_w)[sel], np.array(rec_fd)[sel], np.array(rec_wh)[sel]], "t w fd wh")

# ------------------------------------------------------------------ 10  parameter (inertia) variation, fixed PI
Jn = 2e-3
wc = 2 * np.pi * 100
Kp = Jn * wc
Ki = Kp * wc / 4
Td = 187.5e-6
dt = 1e-6
t = np.arange(0, 0.06, dt)
nd = int(round(Td / dt))
res = [t]
for Jx in (Jn, 5 * Jn, 0.2 * Jn):
    wv = 0.0; I = 0.0; buf = np.zeros(nd)
    out = np.zeros_like(t)
    for n in range(len(t)):
        e = 1.0 - wv
        I += Ki * e * dt
        uc = Kp * e + I
        ud = buf[n % nd]; buf[n % nd] = uc
        wv += dt * ud / Jx
        out[n] = wv
    res.append(out)
res = thin(*res, n=500)
save("jvar.dat", [res[0] * 1e3] + res[1:], "t y1 y5 y02")
print("Jvar overshoots:", [round((r.max() - 1) * 100, 1) for r in res[1:]])

# ------------------------------------------------------------------ 11  MRAC MIT rule (Astrom-Wittenmark style)
dt = 1e-3
t = np.arange(0, 100, dt)
uc = np.where(np.sin(2 * np.pi * t / 20) >= 0, 1.0, -1.0)
cols = [t]
k, k0 = 1.0, 2.0
yplot = None
for gam in (0.5, 1.0, 2.0):
    y = ym = 0.0; th = 0.0
    thr = np.zeros_like(t); yr = np.zeros_like(t); ymr = np.zeros_like(t)
    for n in range(len(t)):
        e = y - ym
        th += dt * (-gam * e * ym)
        u = th * uc[n]
        y += dt * (-y + k * u)
        ym += dt * (-ym + k0 * uc[n])
        thr[n] = th; yr[n] = y; ymr[n] = ym
    cols.append(thr)
    if gam == 1.0:
        yplot = (yr, ymr)
cols += list(yplot)
cols = thin(*cols, n=600)
save("mrac.dat", cols, "t th05 th1 th2 y ym")

# ------------------------------------------------------------------ 12  Lyapunov phase-plane trajectory
dt = 1e-3
t = np.arange(0, 25, dt)
xx = np.zeros((len(t), 2)); xx[0] = [2.0, 0.0]
for n in range(1, len(t)):
    p_, v_ = xx[n - 1]
    xx[n] = [p_ + dt * v_, v_ + dt * (-p_ - 0.4 * v_)]
xs = thin(xx[:, 0], xx[:, 1], n=500)
save("lyap.dat", xs, "x v")

# ------------------------------------------------------------------ 13  DOB load step
J = 2e-3
wcd = 2 * np.pi * 50
Kpd = J * wcd
tau = 1 / (2 * np.pi * 200)
dt = 1e-6
t = np.arange(0, 0.06, dt)
TLd = np.where(t >= 0.01, 0.5, 0.0)
outs = [t]
for use in (False, True):
    wv = 0.0; zu = 0.0; zw = 0.0
    o = np.zeros_like(t)
    for n in range(len(t)):
        uc_ = Kpd * (0.0 - wv)
        dh = (zu - (J / tau) * wv + (J / tau) * zw) if use else 0.0
        u_ = uc_ + dh
        wv += dt * (u_ - TLd[n]) / J
        zu += dt * (u_ - zu) / tau
        zw += dt * (wv - zw) / tau
        o[n] = wv
    outs.append(o)
outs = thin(*outs, n=500)
save("dob.dat", [outs[0] * 1e3, outs[1], outs[2]], "t w0 w1")
print("DOB: P-only steady error %.3f rad/s, with DOB %.4f" % (outs[1][-1], outs[2][-1]))

# ------------------------------------------------------------------ 14  ZOH staircase
Tz = 1 / 12
tc = np.linspace(0, 1, 400)
yc = np.sin(2 * np.pi * tc) + 0.3 * np.sin(2 * np.pi * 3 * tc)
tk = np.arange(0, 1 + 1e-9, Tz)
yk = np.sin(2 * np.pi * tk) + 0.3 * np.sin(2 * np.pi * 3 * tk)
yd = np.sin(2 * np.pi * (tc - Tz / 2)) + 0.3 * np.sin(2 * np.pi * 3 * (tc - Tz / 2))
save("zoh_cont.dat", [tc, yc, yd], "t y yd")
save("zoh_samp.dat", [tk, yk], "t y")

# ------------------------------------------------------------------ 15  z-plane constant zeta / wn contours
lines = []
for zeta in (0.0, 0.2, 0.4, 0.6, 0.8):
    wnT = np.linspace(0, np.pi / np.sqrt(1 - zeta**2), 120)
    z = np.exp((-zeta + 1j * np.sqrt(1 - zeta**2)) * wnT)
    lines.append(np.column_stack([z.real, z.imag]))
with open(os.path.join(D, "zeta.dat"), "w") as fh:
    fh.write("x y\n")
    for L in lines:
        for row in L:
            fh.write("%.5f %.5f\n" % tuple(row))
        fh.write("\n")
lines = []
for k in range(1, 6):
    wnT = k * np.pi / 5
    zeta = np.linspace(0, 1, 80)
    z = np.exp((-zeta + 1j * np.sqrt(1 - zeta**2)) * wnT)
    lines.append(np.column_stack([z.real, z.imag]))
with open(os.path.join(D, "wn.dat"), "w") as fh:
    fh.write("x y\n")
    for L in lines:
        for row in L:
            fh.write("%.5f %.5f\n" % tuple(row))
        fh.write("\n")

# ------------------------------------------------------------------ 16  Tustin warping of a notch
fs = 4000.0
Tq = 1 / fs
f0 = 800.0
w0 = 2 * np.pi * f0
zz, zp = 0.02, 0.3
fa = np.linspace(300, 1300, 800)
sa = 1j * 2 * np.pi * fa
Na = (sa**2 + 2 * zz * w0 * sa + w0**2) / (sa**2 + 2 * zp * w0 * sa + w0**2)
outs = [fa, db(Na)]
for prew in (False, True):
    wd = (2 / Tq) * np.tan(w0 * Tq / 2) if prew else w0
    num = [1, 2 * zz * wd, wd**2]; den = [1, 2 * zp * wd, wd**2]
    bz, az = signal.bilinear(num, den, fs)
    _, hz = signal.freqz(bz, az, worN=2 * np.pi * fa / fs)
    outs.append(db(hz))
    print("notch prewarp=%s: min at %.0f Hz" % (prew, fa[np.argmin(np.abs(hz))]))
save("warp.dat", outs, "f ma m0 m1")

# ------------------------------------------------------------------ 17  sample-rate comparison (discrete PI, 1-sample delay)
J = 2e-3
wc = 2 * np.pi * 100
Kp = J * wc
Ki = Kp * wc / 4
cols = []
for fs_ in (20000, 4000, 1000):
    T_ = 1 / fs_
    n = int(0.03 / T_) + 1
    wv = np.zeros(n); I = 0.0; up = 0.0
    for k_ in range(n - 1):
        e = 1.0 - wv[k_]
        I += Ki * T_ * e
        uk = Kp * e + I
        wv[k_ + 1] = wv[k_] + T_ * up / J  # previous command applied (1-sample delay)
        up = uk
    tk_ = np.arange(n) * T_
    cols.append((tk_ * 1e3, wv))
    print("fs=%d overshoot %.1f%%" % (fs_, (wv.max() - 1) * 100))
for (tk_, wv), fs_ in zip(cols, (20000, 4000, 1000)):
    tt_, ww_ = (thin(tk_, wv, n=400) if len(tk_) > 400 else (tk_, wv))
    save("fs_%d.dat" % fs_, [tt_, ww_], "t w")

# ------------------------------------------------------------------ 18  6-pulse rectifier
VLL = 400.0
Vp = VLL * np.sqrt(2)
t = np.linspace(0, 0.04, 800)
wg = 2 * np.pi * 50
va = Vp / np.sqrt(3) * np.sin(wg * t)
vb = Vp / np.sqrt(3) * np.sin(wg * t - 2 * np.pi / 3)
vc = Vp / np.sqrt(3) * np.sin(wg * t + 2 * np.pi / 3)
vab, vbc, vca = va - vb, vb - vc, vc - va
vdc = np.max(np.abs(np.column_stack([vab, vbc, vca])), axis=1)
save("rect.dat", [t * 1e3, vab, vbc, vca, -vab, -vbc, -vca, vdc], "t ab bc ca ba cb ac dc")
print("Vdc mean %.1f V, min %.1f, max %.1f" % (vdc.mean(), vdc.min(), vdc.max()))

# ------------------------------------------------------------------ 19  DC bus during braking with chopper
C_ = 1e-3; Rb = 56.0; Von, Voff = 780.0, 760.0
Jb = 0.05; w0b = 2 * np.pi * 3000 / 60; tdec = 0.5
dt = 1e-6
t = np.arange(0, 0.7, dt)
V = 565.0; on = False
Vr = np.zeros_like(t); Pr = np.zeros_like(t)
for n, tn in enumerate(t):
    if 0.05 <= tn < 0.05 + tdec:
        wn_ = w0b * (1 - (tn - 0.05) / tdec)
        P = Jb * (w0b / tdec) * wn_
    else:
        P = 0.0
    if V > Von: on = True
    if V < Voff: on = False
    i = P / V - (V / Rb if on else 0.0)
    V += dt * i / C_
    Vr[n] = V; Pr[n] = P
ts, Vs, Ps = thin(t, Vr, Pr, n=1400)
save("vdc_brake.dat", [ts * 1e3, Vs, Ps / 1e3], "t v p")
print("brake: peak P %.0f W, E %.0f J" % (Pr.max(), 0.5 * Jb * w0b**2))

# ------------------------------------------------------------------ 20  bandwidth hierarchy
f = np.logspace(0, 4.5, 400)
cols = [f]
for fb in (2000, 250, 40):
    wn_ = 2 * np.pi * fb / 1.0
    sx = 1j * 2 * np.pi * f
    hb = wn_**2 / (sx**2 + 2 * 0.7 * wn_ * sx + wn_**2)
    cols.append(db(hb))
save("bw.dat", cols, "f ic vc pc")
print("done")
