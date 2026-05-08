# Battery Arbitrage Optimisation (LP)

A simple Python project that uses **linear programming** to find the optimal charge/discharge schedule for a battery trading in a day‑ahead electricity market.

## What it does

Given time‑varying electricity prices and a battery with:
- fixed energy capacity (MWh)  
- power limits (MW)  
- charging/discharging efficiencies  

… the model computes the hourly charge and discharge amounts that **maximise profit** over a 24‑hour horizon, while respecting all physical constraints and a terminal energy‑neutrality condition.

## Mathematical background

The model is formulated as a linear program:

**Objective**  
Maximise:  
\[
\sum_{t=1}^{T} p_t (d_t - c_t)
\]

**Subject to**  
- Power limits: \(0 \le c_t, d_t \le P_{\max}\)  
- Energy dynamics: \(e_t = e_{t-1} + \eta_c c_t - \frac{1}{\eta_d} d_t\)  
- State‑of‑charge bounds: \(0 \le e_t \le C\)  
- Initial & terminal condition: \(e_0 = e_T = E_0\)

A full walk‑through of the maths (with a hand‑solved example) is available in the accompanying explanation (see comments in the code and the project documentation).

## Project structure
