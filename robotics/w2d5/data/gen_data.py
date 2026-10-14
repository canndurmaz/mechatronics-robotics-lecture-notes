#!/usr/bin/env python3
"""New data for w2d5.tex (other .dat files copied from day5/data, made by day5/data/gen_data.py)."""
import numpy as np, os
D = os.path.dirname(os.path.abspath(__file__))
def save(name, cols, header):
    np.savetxt(os.path.join(D, name), np.column_stack(cols), header=header, comments='', fmt='%.5g')
rng = np.random.default_rng(3)
# ---- sensor fusion: tilt angle from gyro + accelerometer (complementary filter) ----
fs = 100.0; Ts = 1/fs; t = np.arange(0, 20, Ts)
theta = np.where(t < 4, 0, np.where(t < 6, 15*(t-4), 30))           # deg
theta = theta - np.where(t > 12, np.minimum(30, 30*(t-12)/2), 0)
rate = np.gradient(theta, Ts)
gyro = rate + 1.5 + rng.normal(0, 0.5, t.size)                       # deg/s, bias 1.5 deg/s
acc = theta + rng.normal(0, 3.0, t.size)                            # deg, noisy (vibration)
gint = np.cumsum(gyro)*Ts
alpha = 0.98; cf = np.zeros_like(t)
for k in range(1, t.size):
    cf[k] = alpha*(cf[k-1] + gyro[k]*Ts) + (1-alpha)*acc[k]
sel = slice(None, None, 5)
save('fusion.dat', [t[sel], theta[sel], acc[sel], gint[sel], cf[sel]], 't th acc gy cf')
