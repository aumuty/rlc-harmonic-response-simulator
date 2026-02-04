# RLC Circuit Harmonic Response Simulator

This project models and simulates the steady-state response of a second-order **RLC electrical circuit** under harmonic excitation.

The system is governed by the differential equation:

<img width="410" height="87" alt="image" src="https://github.com/user-attachments/assets/cc4956b5-5de1-4eb0-a42b-3ac644326f9a" />

It is converted into a state-space representation and solved numerically.

---

## Features

- Simulation of an RLC circuit response to harmonic input  
- Numerical solution using:
  - Euler Method  
  - 4th-Order Runge–Kutta (RK4)  
- Interactive **Tkinter GUI** for parameter input  
- High-performance computation using **Numba acceleration**  
- Time-domain voltage plots (input vs output)  
- Automatic steady-state analysis over multiple oscillation periods  
- Output signal analysis including:
  - Amplitude estimation  
  - Phase shift calculation (zero-crossing method)  
  - Output frequency estimation  
- Analytic transfer function evaluation  
- Generation of **Bode magnitude and phase diagrams**

---

## Technologies Used

- Python  
- NumPy  
- Matplotlib  
- Tkinter  
- Numba  

---

## Important Note

This project was developed as part of the **Real-Time System Design Course Laboratory Work**.

---
