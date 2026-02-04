import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from numba import njit

# HIGH-PERFORMANCE NUMERICAL METHODS (NUMBA)

@njit
def euler_step_numba(x1, x2, t, T, R, L, C, U0, w):
    dx1 = x2
    dx2 = -(R/L)*x2 - (1/(L*C))*x1 + (U0/L)*np.sin(w*t)
    return x1 + T*dx1, x2 + T*dx2

@njit
def rk4_step_numba(x1, x2, t, T, R, L, C, U0, w):

    def f(x1, x2, t):
        return np.array([
            x2,
            -(R/L)*x2 - (1/(L*C))*x1 + (U0/L)*np.sin(w*t)
        ])

    k1 = f(x1, x2, t)
    k2 = f(x1 + T*k1[0]/2, x2 + T*k1[1]/2, t + T/2)
    k3 = f(x1 + T*k2[0]/2, x2 + T*k2[1]/2, t + T/2)
    k4 = f(x1 + T*k3[0], x2 + T*k3[1], t + T)

    out = np.array([x1, x2]) + (T/6)*(k1 + 2*k2 + 2*k3 + k4)
    return out[0], out[1]

# FAST SIMULATE FUNCTION

def simulate(R, L, C, U0, w, method='rk4', periods=8):
    wn = 1 / np.sqrt(L * C)
    Tn = 2*np.pi / wn
    T_desired = 0.1 * (2*np.pi / w)
    T_cap = Tn / 100
    T = min(T_desired, T_cap)
    period = 2*np.pi / w
    tmax = periods * period
    N = int(tmax / T) + 1
    t = np.linspace(0, tmax, N)
    x1, x2 = 0.0, 0.0
    y_out = np.zeros(N)
    y_in = U0 * np.sin(w * t)

    if method == "euler":
        for i in range(N):
            y_out[i] = x1
            x1, x2 = euler_step_numba(x1, x2, t[i], T, R, L, C, U0, w)
    else:
        for i in range(N):
            y_out[i] = x1
            x1, x2 = rk4_step_numba(x1, x2, t[i], T, R, L, C, U0, w)
    return t, y_in, y_out

# ANALYSIS FUNCTIONS

def estimate_amplitude(t, y, w, discard=4):
    period = 2*np.pi / w
    start = discard * period
    idx = np.where(t >= start)[0]
    if len(idx) == 0: return 0
    y_ss = y[idx]
    return (np.max(y_ss) - np.min(y_ss)) / 2

def find_zero_crossings(t, y):
    signs = np.sign(y)
    ds = np.diff(signs)
    idx = np.where(ds > 0)[0]
    times = []
    for i in idx:
        t1, t2 = t[i], t[i+1]
        y1, y2 = y[i], y[i+1]
        tc = t1 - y1*(t2 - t1)/(y2 - y1)
        times.append(tc)
    return np.array(times)

def estimate_phase(t, y_in, y_out, w, discard=4):
    period = 2*np.pi / w
    start = discard * period
    zin = find_zero_crossings(t, y_in)
    zout = find_zero_crossings(t, y_out)
    zin = zin[zin >= start]
    zout = zout[zout >= start]
    if len(zin) == 0 or len(zout) == 0:
        return np.nan
    n = min(len(zin), len(zout))
    dt = np.mean(zout[:n] - zin[:n])
    phi = w * dt
    return (phi + np.pi) % (2*np.pi) - np.pi

def estimate_output_frequency(t, y, w, discard=4):
    period = 2*np.pi / w
    start = discard * period
    z = find_zero_crossings(t, y)
    z = z[z >= start]
    if len(z) < 2:
        return np.nan
    T_est = np.mean(np.diff(z))
    return 2*np.pi / T_est

# ANALYTIC BODE FUNCTION

def analytic_bode(R, L, C, w):
    num = 1/(L*C)
    den_real = (1/(L*C) - w*w)
    den_imag = w * R / L
    mag = num / np.sqrt(den_real*den_real + den_imag*den_imag)
    phase = -np.arctan2(den_imag, den_real)
    return mag, phase

# GUI

def run_gui():
    root = tk.Tk()
    root.title("RLC Circuit Simulator (Optimized)")

    tk.Label(root, text="R (ohms):").grid(row=0, column=0, sticky="e")
    entry_R = tk.Entry(root); entry_R.insert(0, "0.2"); entry_R.grid(row=0, column=1)

    tk.Label(root, text="L (henries):").grid(row=1, column=0, sticky="e")
    entry_L = tk.Entry(root); entry_L.insert(0, "1"); entry_L.grid(row=1, column=1)

    tk.Label(root, text="C (farads):").grid(row=2, column=0, sticky="e")
    entry_C = tk.Entry(root); entry_C.insert(0, "10"); entry_C.grid(row=2, column=1)

    tk.Label(root, text="U0 (volts):").grid(row=3, column=0, sticky="e")
    entry_U0 = tk.Entry(root); entry_U0.insert(0, "1"); entry_U0.grid(row=3, column=1)

    tk.Label(root, text="ω (rad/sec):").grid(row=4, column=0, sticky="e")
    entry_w = tk.Entry(root); entry_w.insert(0, "0.2"); entry_w.grid(row=4, column=1)

    method_var = tk.StringVar(value="rk4")
    tk.Label(root, text="Method:").grid(row=5, column=0, sticky="e")
    ttk.Combobox(root, textvariable=method_var, values=["rk4", "euler"]).grid(row=5, column=1)

    def run_sim():
        try:
            R = float(entry_R.get())
            L = float(entry_L.get())
            C = float(entry_C.get())
            U0 = float(entry_U0.get())
            w = float(entry_w.get())
            method = method_var.get()
        except ValueError:
            messagebox.showerror("Input Error", "Enter valid numeric values!")
            return

        t, y_in, y_out = simulate(R, L, C, U0, w, method)
        amp = estimate_amplitude(t, y_out, w)
        phi = estimate_phase(t, y_in, y_out, w)
        w_out = estimate_output_frequency(t, y_out, w)

        print("\n--- RESULTS ---")
        print("Amplitude:", amp)
        print("Phase (rad):", phi)
        print("Output freq w':", w_out)

        # Time-domain plot
        plt.figure()
        plt.plot(t, y_in, label="Input")
        plt.plot(t, y_out, label="Output")
        plt.title("Time-domain Response")
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (V)")
        plt.legend()
        plt.grid()
        plt.show()

        # Analytic Bode
        freqs = np.logspace(-2, 1, 200)
        mags, phases = [], []
        for w0 in freqs:
            m, p = analytic_bode(R, L, C, w0)
            mags.append(m)
            phases.append(p)

        f_mark = np.array([0.01, 0.1, 1, 10])
        mags_mark, phases_mark = [], []
        for w0 in f_mark:
            m, p = analytic_bode(R, L, C, w0)
            mags_mark.append(m)
            phases_mark.append(p)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
        ax1.semilogx(freqs, mags)
        ax1.semilogx(f_mark, mags_mark, 'o')
        ax1.set_title("Bode Diagram (Analytic)")
        ax1.set_ylabel("Magnitude")
        ax1.grid(True, which='both')

        ax2.semilogx(freqs, phases)
        ax2.semilogx(f_mark, phases_mark, 'o')
        ax2.set_xlabel("Frequency (rad/sec)")
        ax2.set_ylabel("Phase (rad)")
        ax2.grid(True, which='both')
        plt.tight_layout()
        plt.show()

    tk.Button(root, text="Run Simulation", command=run_sim).grid(row=6, column=0, columnspan=2, pady=10)

    root.mainloop()

# MAIN

if __name__ == "__main__":
    run_gui()

