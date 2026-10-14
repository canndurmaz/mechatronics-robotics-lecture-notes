#!/usr/bin/env python3
"""New data for w1d3.tex (robot joint examples). Other *.dat files are copied from day2/data
(generated there by day2/data/gen_data.py). Run from w1d3/data: python3 gen_data.py"""
import numpy as np
def save(name, cols, header):
    np.savetxt(name, np.column_stack(cols), header=header, comments='', fmt='%.6g')

# Robot joint: J = 0.5 kg m^2 (link + reflected motor inertia), B = 0.1 Nm s/rad
J, B = 0.5, 0.1
dt = 1e-4
def sim(Kp, Kd, Ki, tau_g, ff=False, T=3.0, r=0.5, delay=0.0, umax=None):
    n = int(T/dt); th = 0.0; w = 0.0; I = 0.0
    nd = int(round(delay/dt)); buf = [0.0]*(nd+1)
    out = []
    for k in range(n):
        e = r - th
        I += Ki*e*dt
        u = Kp*e - Kd*w + I + (tau_g if ff else 0.0)
        if umax is not None: u = max(-umax, min(umax, u))
        buf.append(u); ud = buf.pop(0)
        acc = (ud - B*w - tau_g)/J
        w += acc*dt; th += w*dt
        out.append(th)
    return np.arange(n)*dt, np.array(out)

# 1. P only vs PD on joint (no gravity), step 0.5 rad
t, yP = sim(50, 0, 0, 0)
_, yPD = sim(50, 7, 0, 0)
_, yPD2 = sim(50, 3, 0, 0)
idx = slice(0, None, 50)
save('joint_pd.dat', [t[idx], yP[idx], yPD2[idx], yPD[idx]], 't P PDlow PD')
print('PD max', yPD.max())

# 2. gravity load 4.9 Nm: PD offset, PID, PD + gravity feedforward
tg = 4.9
t, a = sim(50, 7, 0, tg)
_, b = sim(50, 7, 100, tg)
_, c = sim(50, 7, 0, tg, ff=True)
save('joint_gravity.dat', [t[idx], a[idx], b[idx], c[idx]], 't PD PID PDFF')
print('PD final', a[-1], 'PID final', b[-1], 'PID max', b.max())

# 3. delay: loop L = K/(s(tau s+1)) with K=100, tau=0.01 as unity feedback, delays 0, 2, 6 ms
dt2 = 1e-5
def simL(delay, T=0.15):
    n = int(T/dt2); y = 0.0; x = 0.0; nd = int(round(delay/dt2)); buf=[0.0]*(nd+1); out=[]
    for k in range(n):
        e = 1.0 - y; u = 100*e
        buf.append(u); ud = buf.pop(0)
        # 1/(s(0.01s+1)): x' = (ud - x)/0.01 ; y' = x
        x += (ud - x)/0.01*dt2; y += x*dt2; out.append(y)
    return np.arange(n)*dt2, np.array(out)
cols = []
for d in [0, 0.002, 0.006]:
    t, y = simL(d); cols.append(y[::100]); print('delay', d, 'max', y.max())
save('delay_step.dat', [t[::100]*1e3] + cols, 't d0 d2 d6')
