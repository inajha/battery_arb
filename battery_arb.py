import pulp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# 1. Generate dummy price data (24 hours, typical day-ahead)
# ------------------------------------------------------------
np.random.seed(42)
hours = 24
times = range(hours)
# Base profile + randomness
base = 30 + 20 * np.sin((np.array(times) - 9) * (2 * np.pi / 24))
noise = np.random.normal(0, 5, size=hours)
price = np.maximum(base + noise, 10)  # price >= 10 €/MWh
price = np.round(price, 2)

# ------------------------------------------------------------
# 2. Battery parameters
# ------------------------------------------------------------
C = 10.0          # MWh total capacity
P_max = 3.0       # MW charge/discharge power limit
eta_c = 0.95      # charging efficiency
eta_d = 0.95      # discharging efficiency (=> round-trip ~0.9025)
E0 = 5.0          # initial energy (MWh)
E_min = 0.0
E_max = C

# ------------------------------------------------------------
# 3. Build the LP model
# ------------------------------------------------------------
model = pulp.LpProblem("Battery_Arbitrage", pulp.LpMaximize)

# Decision variables
c = pulp.LpVariable.dicts("charge", times, lowBound=0, upBound=P_max)
d = pulp.LpVariable.dicts("discharge", times, lowBound=0, upBound=P_max)
e = pulp.LpVariable.dicts("energy", range(hours+1), lowBound=E_min, upBound=E_max)

# Objective: profit = sum over t of price[t] * (d[t] - c[t])
model += pulp.lpSum([price[t] * (d[t] - c[t]) for t in times])

# Energy dynamics constraints
for t in times:
    if t == 0:
        # e[0] is initial state, e[1] after first hour
        model += e[t+1] == E0 + eta_c * c[t] - (1/eta_d) * d[t]
    else:
        model += e[t+1] == e[t] + eta_c * c[t] - (1/eta_d) * d[t]

# Fix initial energy explicitly (it's e[0])
model += e[0] == E0

# Optional: end at the same energy (energy-neutral)
model += e[hours] == E0

# ------------------------------------------------------------
# 4. Solve
# ------------------------------------------------------------
solver = pulp.PULP_CBC_CMD(msg=True)
model.solve(solver)

# Check status
print(f"Solution status: {pulp.LpStatus[model.status]}")
print(f"Optimal profit = €{pulp.value(model.objective):.2f}")

# ------------------------------------------------------------
# 5. Extract results into a DataFrame
# ------------------------------------------------------------
charge_vals = [c[t].varValue for t in times]
discharge_vals = [d[t].varValue for t in times]
energy_vals = [e[t].varValue for t in range(hours+1)]  # e0...e24

df = pd.DataFrame({
    'hour': range(1, hours+1),
    'price': price,
    'charge_MW': charge_vals,
    'discharge_MW': discharge_vals,
    'net_power_MW': np.array(discharge_vals) - np.array(charge_vals),
    'energy_start_MWh': energy_vals[:-1],   # energy at beginning of hour
    'energy_end_MWh': energy_vals[1:]
})

print("\nHourly schedule:")
print(df.to_string(index=False, float_format="%.2f"))

# ------------------------------------------------------------
# 6. Plot
# ------------------------------------------------------------
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

ax1.plot(times, price, 'ko-', label='Price (€/MWh)')
ax1.set_ylabel('Price')
ax1.legend(loc='upper left')
ax1.grid(True)

ax2.bar(times, charge_vals, width=0.4, label='Charge (MW)', color='green', alpha=0.7)
ax2.bar(times, [-v for v in discharge_vals], width=0.4, label='Discharge (MW)', color='red', alpha=0.7)
ax2.set_ylabel('Power (MW)')
ax2.legend()
ax2.grid(True)

ax3.step(range(hours+1), energy_vals, where='post', label='State of Energy (MWh)', color='blue')
ax3.set_ylabel('Energy (MWh)')
ax3.set_xlabel('Hour')
ax3.legend()
ax3.grid(True)

plt.tight_layout()
plt.show()