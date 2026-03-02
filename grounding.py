#!/usr/bin/env python3
import logging
from variables import *
from functions import *
from spacing_calculator import spacing_calc

"""Main script of the calculator for electrical circuits and grounding."""
#TODO: Main stuff
# 1. create variables to hold the tables of data and constants
# 2. create functions to calculate the formulas
# 3. create object hierarchy for each elemenet of the circuits
# 4. create logic to relate each element to each other and make the floor plan
# 5. devise output logic 

# Script settings
logging.basicConfig(level=logging.ERROR, format="%(message)s")

print("\n=== Grounding Resistance Calculator ===\n")

# 1. User input for geometry + soil resistivity
while True: 
    values = input_values() 
    if values is not None: 
        break 
    print("Wrong input.\n")

n = int(values["n"])
L = float(values["l"])
d = float(values["d"])
q = float(values["q"])
b = float(values["b"])
area = float(values["space"])
rho_calc = float(values["rho_mas"])

# 3. Compute rho_calc using humidity coefficient K


# 4. Compute h (depth + half electrode length)
h = h_formula(q, L)

# 5. Compute single-electrode resistances
rv_single = rv(rho_calc, L, d, h)
ro_single = ro(rho_calc, L, b, q)

# 6. Determine optimal electrode configuration
# Pass n as a named argument to use that specific electrode count
config = spacing_calc(area, L, n=int(n))

n_opt = config["n"] # type: ignore
spacing = config["spacing"] # type: ignore
openess = config["openess"] # type: ignore
uv = config["uv"] # type: ignore
uo = config["uo"] # type: ignore

print("\nOptimal configuration found:")
print(f"  Shape: {config['config']}") # type: ignore
print(f"  Electrodes: {n_opt}")
print(f"  Spacing: {L if spacing == "L" else 2*L} m")
print(f"  Open/Closed: {openess}")
print(f"  rv={rv_single}, ro={ro_single}")

# 7. Compute Rv, Ro, Rpc
Rv_total = Rv(rv_single, n_opt, uv)
Ro_total = Ro(ro_single, n_opt, uo)
Rpc_total = Rpc(Rv_total, Ro_total)

print("\n=== Results ===")
print(f"Rv = {Rv_total:.3f} Ω")
print(f"Ro = {Ro_total:.3f} Ω")
print(f"Rpc = {Rpc_total:.3f} Ω")

# 8. Compliance check
print("\n=== Compliance Check ===")

if Rpc_total <= 1:
    print("Meets requirement for COMBINED lightning + residential grounding (≤ 1 Ω).")
elif Rpc_total <= 4:
    print("Meets requirement for RESIDENTIAL grounding (≤ 4 Ω).")
elif Rpc_total <= 10:
    print("Meets requirement for LIGHTNING ROD grounding (≤ 10 Ω).")
else:
    print("Does NOT meet grounding requirements. Increase availabe electrodes, electrode length or area.")
