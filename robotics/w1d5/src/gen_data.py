"""Generate numerical data for Day 4 plots (all values are computed from the model equations).
Run: python3 src/gen_data.py  (from day4/)"""
import numpy as np, os
from scipy import signal
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
def save(name, cols, header):
    np.savetxt(os.path.join(D, name), np.column_stack(cols), header=header, comments="", fmt="%.6g")

# ---------------- reference servo motor (SPM) -----------------
p, R, L, psi = 4, 0.5, 3e-3, 0.12
kt = 1.5 * p * psi            # 0.72 Nm/A (amplitude-invariant)
Jm = 3e-4; J = 4 * Jm        # inertia ratio 3
Vdc = 325.0
Ts = 1 / 16e3; Tsig = 1.5 * Ts
print("kt", kt, "Tsig", Tsig)

# ---------------- 1. carrier SPWM -----------------
th = np.linspace(0, 360, 1801)
mf = 15; m = 0.8
car = 2 * np.abs(((th / 360 * mf) % 1) * 2 - 1) - 1   # triangle -1..1, +1 at cycle start
va = m * np.sin(np.radians(th)); vb = m * np.sin(np.radians(th - 120))
Sa = (va > car).astype(float); Sb = (vb > car).astype(float)
vab = Sa - Sb
save("spwm.dat", [th, car, va, vb, Sa, Sb, vab], "th car va vb Sa Sb vab")

# ---------------- 2. zero-sequence injection -----------------
th = np.linspace(0, 360, 721); r = np.radians(th); m = 2 / np.sqrt(3)
a, b, c = m * np.sin(r), m * np.sin(r - 2 * np.pi / 3), m * np.sin(r + 2 * np.pi / 3)
thi = m * (np.sin(r) + np.sin(3 * r) / 6)
z = -(np.maximum(np.maximum(a, b), c) + np.minimum(np.minimum(a, b), c)) / 2
save("zeroseq.dat", [th, a, thi, a + z, z], "th sine thi svpwm zs")

# ---------------- 3. current ripple vs modulation index (SVPWM, centred) -----------------
def ripple_pp(mi, kind):
    # normalised: delta_i_pp * L * fsw / Vdc
    best = 0
    for ang in np.linspace(0, np.pi / 3, 61):
        ref = mi * np.array([np.sin(ang + np.pi/2 ), np.sin(ang + np.pi/2 - 2*np.pi/3), np.sin(ang + np.pi/2 + 2*np.pi/3)])
        if kind == "svpwm":
            ref = ref - (ref.max() + ref.min()) / 2
        d = (ref + 1) / 2  # duty 0..1
        t = np.linspace(0, 1, 4001)
        tri = np.abs(2 * t - 1)   # 1 -> 0 -> 1 , centred PWM: on when tri < d
        S = (tri[None, :] < d[:, None]).astype(float)
        vph = (2 * S[0] - S[1] - S[2]) / 3
        v = vph - vph.mean()
        i = np.cumsum(v) * (t[1] - t[0])
        best = max(best, i.max() - i.min())
    return best
ms = np.linspace(0.0, 1.15, 24)
rs = [ripple_pp(x, "svpwm") for x in ms]
rsp = [ripple_pp(x, "spwm") if x <= 1.0 else np.nan for x in ms]
save("ripple.dat", [ms, rs, rsp], "m svpwm spwm")
print("max ripple norm", max(rs))

# ---------------- 4. field-weakening envelope (SPM) -----------------
Imax, Vmax = 20.0, Vdc / np.sqrt(3)
rpm = np.linspace(0, 8000, 401); T = []; P = []; ID = []
for n in rpm:
    we = n * 2 * np.pi / 60 * p
    best = (0, 0)
    for idd in np.linspace(0, -Imax, 801):
        iq = np.sqrt(max(Imax**2 - idd**2, 0))
        # find largest iq meeting voltage limit (steady state)
        lo, hi = 0, iq
        def ok(q):
            vd = R * idd - we * L * q; vq = R * q + we * (L * idd + psi)
            return vd*vd + vq*vq <= Vmax**2
        if not ok(0): continue
        if not ok(hi):
            for _ in range(40):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if ok(mid) else (lo, mid)
            iq = lo
        if iq > best[0]: best = (iq, idd)
    T.append(kt * best[0]); P.append(kt * best[0] * n * 2 * np.pi / 60 / 1000); ID.append(best[1])
save("fw.dat", [rpm, T, P, ID], "rpm T P id")
Ta = np.array(T); print("base speed ~", rpm[np.argmax(Ta < 0.999 * Ta[0])], "max speed", rpm[np.nonzero(Ta > 0.05)[0][-1]])

# ---------------- 5. current loop: Bode and step -----------------
Kp_i = L / (2 * Tsig); Ti_i = L / R
print("Kp_i", Kp_i, "Ki", Kp_i / Ti_i)
f = np.logspace(1, np.log10(2e4), 400); w = 2 * np.pi * f; s = 1j * w
Lol = Kp_i * (1 + 1 / (Ti_i * s)) / (R + L * s)
Ld = Lol * np.exp(-s * Tsig)
Lpade = Lol / (1 + s * Tsig)
mag = lambda x: 20 * np.log10(np.abs(x))
ph = lambda x: np.degrees(np.unwrap(np.angle(x)))
Tcl = Ld / (1 + Ld)
save("cur_bode.dat", [f, mag(Lol), ph(Lol), mag(Ld), ph(Ld), mag(Tcl)], "f m0 p0 md pd mcl")
ic = np.argmin(np.abs(np.abs(Ld) - 1)); print("cur fc", f[ic], "PM", 180 + ph(Ld)[ic])
ib = np.argmin(np.abs(mag(Tcl) + 3)); print("cur closed loop -3dB", f[ib])

def sim_current(dt=2e-7, tend=2e-3, discrete=True, decouple=None, we=0.0, iq_ref=10.0):
    n = int(tend / dt); t = np.arange(n) * dt
    idd = iq = 0.0; intd = intq = 0.0; vd_app = vq_app = 0.0; vd_next = vq_next = 0.0
    out = np.zeros((n, 2)); tk = 0.0
    for k in range(n):
        tt = t[k]
        if (not discrete) or tt >= tk - 1e-12:
            ed, eq = 0 - idd, (iq_ref if tt >= 1e-4 else 0) - iq
            Ki = Kp_i / Ti_i * (Ts if discrete else dt)
            intd += Ki * ed; intq += Ki * eq
            vd = Kp_i * ed + intd; vq = Kp_i * eq + intq
            if decouple:
                vd += -we * L * iq; vq += we * (L * idd + psi)
            if discrete:
                vd_app, vq_app = vd_next, vq_next; vd_next, vq_next = vd, vq; tk += Ts
            else:
                vd_app, vq_app = vd, vq
        did = (vd_app - R * idd + we * L * iq) / L
        diq = (vq_app - R * iq - we * L * idd - we * psi) / L
        idd += did * dt; iq += diq * dt
        out[k] = idd, iq
    return t, out
t1, o1 = sim_current(discrete=False)
t2, o2 = sim_current(discrete=True)
sl = slice(0, None, 20)
save("cur_step.dat", [t1[sl] * 1e3, o1[sl, 1], o2[sl, 1]], "t ideal disc")
print("overshoot discrete", o2[:, 1].max() / 10 - 1)
# decoupling at 3000 rpm with integrators pre-loaded at steady back-EMF? start from rest-current, speed held constant
we = 3000 * 2 * np.pi / 60 * p
def sim_dec(dec):
    # integrators start at steady state for iq=0 at speed we (vq = we*psi) so the comparison isolates the coupling
    dt = 2e-7; n = int(2e-3 / dt); t = np.arange(n) * dt
    idd = iq = 0.0; intd = 0.0; intq = 0.0 if dec else we * psi
    vdn = 0.0; vqn = we * psi; vda = 0.0; vqa = we * psi; tk = 0.0; out = np.zeros((n, 2))
    for k in range(n):
        if t[k] >= tk - 1e-12:
            ed, eq = -idd, (10 if t[k] >= 1e-4 else 0) - iq
            intd += Kp_i / Ti_i * Ts * ed; intq += Kp_i / Ti_i * Ts * eq
            vd = Kp_i * ed + intd; vq = Kp_i * eq + intq
            if dec: vd += -we * L * iq; vq += we * (L * idd + psi)
            vda, vqa = vdn, vqn; vdn, vqn = vd, vq; tk += Ts
        did = (vda - R * idd + we * L * iq) / L; diq = (vqa - R * iq - we * L * idd - we * psi) / L
        idd += did * dt; iq += diq * dt; out[k] = idd, iq
    return t, out
ta, oa = sim_dec(False); tb, ob = sim_dec(True)
save("decoup.dat", [ta[sl] * 1e3, oa[sl, 0], oa[sl, 1], ob[sl, 0], ob[sl, 1]], "t id_n iq_n id_d iq_d")
print("id excursion no-dec", oa[:, 0].min(), oa[:, 0].max(), "dec", ob[:, 0].min(), ob[:, 0].max())

# ---------------- 6. velocity loop (symmetric optimum) -----------------
Tf = 0.3125e-3; Teq = 2 * Tsig + Tf   # 0.5 ms
print("Teq", Teq)
def vel_design(a, Jd=J):
    return Jd / (a * kt * Teq), a * a * Teq
f = np.logspace(0, np.log10(5e3), 400); w = 2 * np.pi * f; s = 1j * w
rows = [f]
for a in (2, 3):
    Kp, Ti = vel_design(a)
    Lv = Kp * (1 + 1 / (Ti * s)) * kt / (J * s) / (1 + 2 * Tsig * s) / (1 + Tf * s)
    rows += [mag(Lv), ph(Lv)]
    ic = np.argmin(np.abs(np.abs(Lv) - 1)); print("vel a", a, "Kp", Kp, "Ti", Ti, "fc", f[ic], "PM", 180 + ph(Lv)[ic])
save("vel_bode.dat", rows, "f m2 p2 m3 p3")
# step responses (rational, via scipy)
def tf_mul(*tfs):
    n, d = np.array([1.0]), np.array([1.0])
    for (a, b) in tfs: n = np.polymul(n, a); d = np.polymul(d, b)
    return n, d
def closed(n, d):  # unity feedback
    return n, np.polyadd(d, n)
tt = np.linspace(0, 0.02, 2001); rows = [tt * 1e3]
for a in (2, 3):
    Kp, Ti = vel_design(a)
    nL, dL = tf_mul(([Kp * Ti, Kp], [Ti, 0]), ([kt], [J, 0]), ([1], [2 * Tsig, 1]), ([1], [Tf, 1]))
    nc, dc = closed(nL, dL)
    rows.append(signal.step((nc, dc), T=tt)[1])
    ncp, dcp = tf_mul((nc, dc), ([1], [Ti, 1]))
    rows.append(signal.step((ncp, dcp), T=tt)[1])
save("vel_step.dat", rows, "t a2 a2pf a3 a3pf")
print("vel overshoot a2", rows[1].max(), "a2pf", rows[2].max(), "a3", rows[3].max(), "a3pf", rows[4].max())

# inertia ratio effect (gains designed for ratio 3, a=2)
Kp, Ti = vel_design(2)
rows_b = [f]; rows_s = [tt * 1e3]
for ratio in (0, 3, 10, 30):
    Jx = Jm * (1 + ratio)
    Lv = Kp * (1 + 1 / (Ti * s)) * kt / (Jx * s) / (1 + 2 * Tsig * s) / (1 + Tf * s)
    rows_b += [mag(Lv)]
    ic = np.argmin(np.abs(np.abs(Lv) - 1)); print("ratio", ratio, "fc", f[ic], "PM", 180 + ph(Lv)[ic])
    nL, dL = tf_mul(([Kp * Ti, Kp], [Ti, 0]), ([kt], [Jx, 0]), ([1], [2 * Tsig, 1]), ([1], [Tf, 1]))
    nc, dc = closed(nL, dL); ncp, dcp = tf_mul((nc, dc), ([1], [Ti, 1]))
    rows_s.append(signal.step((ncp, dcp), T=tt)[1])
save("inertia_bode.dat", rows_b, "f r0 r3 r10 r30")
save("inertia_step.dat", rows_s, "t r0 r3 r10 r30")

# bandwidth separation: velocity PI designed for wc=1000 rad/s assuming ideal inner loop
wc = 1000.0; Kp = J * wc / kt; Ti = 4 / wc; rows = [tt * 1e3]
for rr in (1.5, 3, 5, 10):
    wi = rr * wc
    nL, dL = tf_mul(([Kp * Ti, Kp], [Ti, 0]), ([kt], [J, 0]), ([1], [1 / wi, 1]))
    nc, dc = closed(nL, dL); ncp, dcp = tf_mul((nc, dc), ([1], [Ti, 1]))
    rows.append(signal.step((ncp, dcp), T=tt)[1])
save("bwsep_step.dat", rows, "t r1p5 r3 r5 r10")

# ---------------- 7. anti-windup -----------------
def sim_windup(aw, dt=2e-6, tend=0.08):
    Kp, Ti = vel_design(3); imax = 20.0
    n = int(tend / dt); w_ = 0.0; I = 0.0; out = []
    iact = 0.0
    for k in range(n):
        ref = 300.0
        e = ref - w_
        u = Kp * e + I
        us = np.clip(u, -imax, imax)
        if aw == "none": I += Kp / Ti * e * dt
        elif aw == "clamp":
            if not ((u > imax and e > 0) or (u < -imax and e < 0)): I += Kp / Ti * e * dt
        iact += (us - iact) / (2 * Tsig) * dt
        w_ += kt * iact / J * dt
        if k % 25 == 0: out.append((k * dt * 1e3, w_, us))
    return np.array(out)
a1 = sim_windup("none"); a2 = sim_windup("clamp")
save("windup.dat", [a1[:, 0], a1[:, 1], a1[:, 2], a2[:, 1], a2[:, 2]], "t w_n i_n w_c i_c")
print("windup overshoot", a1[:, 1].max(), a2[:, 1].max())

# ---------------- 8. trajectories -----------------
def trap(dist, vmax, amax, dt):
    ta = vmax / amax; tc = (dist - vmax * ta) / vmax; T = 2 * ta + tc
    t = np.arange(0, T + 0.05, dt); a = np.where(t < ta, amax, np.where(t < ta + tc, 0, np.where(t < T, -amax, 0)))
    return t, a
def scurve(dist, vmax, amax, jmax, dt):
    tj = amax / jmax; tca = vmax / amax - tj; Tacc = 2 * tj + tca
    dacc = vmax * Tacc / 2; tc = (dist - 2 * dacc) / vmax; T = 2 * Tacc + tc
    t = np.arange(0, T + 0.05, dt)
    def acc_phase(x):
        return np.where(x < tj, jmax * x, np.where(x < tj + tca, amax, np.where(x < Tacc, amax - jmax * (x - tj - tca), 0)))
    a = np.where(t < Tacc, acc_phase(t), np.where(t < Tacc + tc, 0, np.where(t < T, -acc_phase(t - Tacc - tc), 0)))
    return t, a
dt = 1e-5
dist, vmax, amax, jmax = 20 * np.pi, 300.0, 3000.0, 1.5e5
def integ(t, a):
    v = np.concatenate([[0], np.cumsum((a[1:] + a[:-1]) / 2 * dt)])
    x = np.concatenate([[0], np.cumsum((v[1:] + v[:-1]) / 2 * dt)])
    j = np.gradient(a, dt)
    return v, x, j
tT, aT = trap(dist, vmax, amax, dt); vT, xT, jT = integ(tT, aT)
tS, aS = scurve(dist, vmax, amax, jmax, dt); vS, xS, jS = integ(tS, aS)
print("trap T", tT[-1] - 0.05, "x", xT[-1], "scurve T", tS[-1] - 0.05, "x", xS[-1])
n = min(len(tT), len(tS)); stp = 50
L_ = max(len(tT), len(tS))
def pad(x, L_): return np.concatenate([x, np.full(L_ - len(x), x[-1])])
tt_ = np.arange(L_) * dt
save("traj.dat", [tt_[::stp] * 1e3, pad(xT, L_)[::stp], pad(vT, L_)[::stp], pad(aT, L_)[::stp] / 1000,
                  pad(xS, L_)[::stp], pad(vS, L_)[::stp], pad(aS, L_)[::stp] / 1000, np.clip(pad(np.gradient(aS, dt), L_)[::stp], -2e5, 2e5) / 1e5],
     "t xT vT aT xS vS aS jS")

# ---------------- 9. following error with/without feedforward -----------------
def sim_follow(ff_v, ff_a, prof="S", Kpp=100.0):
    t, a_ref = (tS, aS) if prof == "S" else (tT, aT)
    v_ref, x_ref, _ = integ(t, a_ref)
    Kv, Ti = vel_design(2)
    x = w_ = I = i = 0.0; e_out = []
    for k in range(len(t)):
        e = x_ref[k] - x
        wref = Kpp * e + (v_ref[k] if ff_v else 0.0)
        ev = wref - w_
        I += Kv / Ti * ev * dt
        iref = Kv * ev + I + (J * a_ref[k] / kt if ff_a else 0.0)
        # current loop + velocity measurement filter approximated by first-order lag Teq
        i += (iref - i) / (2 * Tsig) * dt
        w_ += kt * i / J * dt; x += w_ * dt
        e_out.append(e)
    return t, np.array(e_out)
rows = []
for (fv, fa) in ((0, 0), (1, 0), (1, 1)):
    t, e = sim_follow(fv, fa); rows.append(pad(e, L_)[::stp] * 1e3)
    print("follow err max mrad", fv, fa, np.abs(e).max() * 1e3)
save("follow.dat", [tt_[::stp] * 1e3] + rows, "t e_p e_pv e_pva")

# ---------------- 10. two-mass FRF + notch -----------------
JL = 9e-4; wa = 2 * np.pi * 300; ks = JL * wa**2; cs = 2 * 0.03 * np.sqrt(ks * JL)
f = np.logspace(1, np.log10(3e3), 600); w = 2 * np.pi * f; s = 1j * w
G2 = (JL * s**2 + cs * s + ks) / (s * (Jm * JL * s**2 + cs * (Jm + JL) * s + ks * (Jm + JL)))
G1 = 1 / ((Jm + JL) * s)
wr = wa * np.sqrt(1 + JL / Jm); print("res f", wr / 2 / np.pi, "k", ks)
wn = wr; Nt = (s**2 + 2 * 0.05 * wn * s + wn**2) / (s**2 + 2 * 0.5 * wn * s + wn**2)
save("frf.dat", [f, mag(G2 * kt), ph(G2), mag(G1 * kt), mag(Nt), ph(Nt), mag(G2 * kt * Nt)], "f mG pG mR mN pN mGN")

# ---------------- 11. DOB vs PI only: load-torque step -----------------
def sim_dob(dob, dt=1e-6, tend=0.03, TL=2.0, tauQ=0.5e-3):
    Kp, Ti = vel_design(3)
    w_ = I = i = 0.0; z = 0.0; fq = 0.0; out = []
    for k in range(int(tend / dt)):
        t = k * dt
        TLk = TL if t >= 0.005 else 0.0
        ev = 0.0 - w_
        I += Kp / Ti * ev * dt
        iref = Kp * ev + I
        dhat = fq - J * (w_ - z) / tauQ if dob else 0.0
        iref_c = iref + dhat / kt
        i += (iref_c - i) / (2 * Tsig) * dt
        w_ += (kt * i - TLk) / J * dt
        z += (w_ - z) / tauQ * dt
        fq += (kt * i - fq) / tauQ * dt
        if k % 20 == 0: out.append((t * 1e3, w_, dhat))
    return np.array(out)
d0 = sim_dob(False); d1 = sim_dob(True)
save("dob.dat", [d0[:, 0], d0[:, 1], d1[:, 1], d1[:, 2]], "t w_pi w_dob dhat")
print("dob min speed", d0[:, 1].min(), d1[:, 1].min())

# ---------------- 12. cogging -----------------
th = np.linspace(0, 45, 901); r = np.radians(th)
Tc = 0.06 * np.sin(24 * r) + 0.025 * np.sin(48 * r + 0.7) + 0.01 * np.sin(72 * r + 1.3)
lut_th = np.arange(0, 45.001, 1.0); lut = np.interp(lut_th, th, Tc)
resid = Tc - np.interp(th, lut_th, lut) * 0.95
save("cogging.dat", [th, Tc, resid], "th Tc res")
print("cog pp", Tc.max() - Tc.min(), "resid pp", resid.max() - resid.min())
