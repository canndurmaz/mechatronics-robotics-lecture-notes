"""Data for W1D4 session 2.9 (robot manipulator control). Run: python3 gen_data.py"""
import numpy as np
g=9.81
# 1) single-link arm: PD vs PD + gravity compensation vs PID
m,lc,J=2.0,0.25,0.2; Kp,Kd,Ki=100.0,8.0,150.0
def sim(mode,T=2.0,dt=1e-4):
    q,w,I=-0.3,0.0,0.0; qd=0.5; out=[]
    for k in range(int(T/dt)+1):
        t=k*dt; e=qd-q
        tau=Kp*e-Kd*w
        if mode=='g': tau+=m*g*lc*np.cos(q)
        if mode=='i': I+=Ki*e*dt; tau+=I
        if k%50==0: out.append((t,q))
        a=(tau-m*g*lc*np.cos(q))/J; w+=a*dt; q+=w*dt
    return np.array(out)
A=sim('p');B=sim('g');C=sim('i')
with open('grav.dat','w') as f:
    f.write('t pd pdg pid\n')
    for a,b,c in zip(A,B,C): f.write(f'{a[0]:.4f} {np.degrees(a[1]):.4f} {np.degrees(b[1]):.4f} {np.degrees(c[1]):.4f}\n')
print('PD final deg',np.degrees(A[-1,1]),'PD+g',np.degrees(B[-1,1]),'PID',np.degrees(C[-1,1]))
# 2) 2-link planar arm: joint-1 inertia vs elbow angle
m1=m2=5.0; l1=l2=0.5; c1=c2=0.25; I1=m1*l1**2/12; I2=m2*l2**2/12
with open('m11.dat','w') as f:
    f.write('q2 M11 M22\n')
    for q2 in np.linspace(-180,180,181):
        M11=I1+I2+m1*c1**2+m2*(l1**2+c2**2+2*l1*c2*np.cos(np.radians(q2)))
        f.write(f'{q2:.1f} {M11:.4f} {I2+m2*c2**2:.4f}\n')
print('M11 range',I1+I2+m1*c1**2+m2*(l1**2+c2**2-2*l1*c2),I1+I2+m1*c1**2+m2*(l1**2+c2**2+2*l1*c2))
# 3) impedance control: 1-DOF tool pushing on a wall
mt=2.0; ke=20000.0; xw=0.10; xd=0.12
def imp(K,T=1.0,dt=1e-5):
    D=2.0*np.sqrt(K*mt); x,v=0.0,0.0; out=[]
    for k in range(int(T/dt)+1):
        t=k*dt; Fe=ke*(x-xw) if x>xw else 0.0
        F=K*(xd-x)-D*v
        if k%300==0: out.append((t,x,Fe))
        v+=(F-Fe)/mt*dt; x+=v*dt
    return np.array(out)
S1=imp(500.0);S2=imp(5000.0)
with open('imp.dat','w') as f:
    f.write('t xs Fs xh Fh\n')
    for a,b in zip(S1,S2): f.write(f'{a[0]:.4f} {1000*a[1]:.3f} {a[2]:.3f} {1000*b[1]:.3f} {b[2]:.3f}\n')
print('final F soft',S1[-1,2],'stiff',S2[-1,2])
