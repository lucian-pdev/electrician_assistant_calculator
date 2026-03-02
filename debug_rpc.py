#!/usr/bin/env python3
"""
Debug script to test Rpc calculation with manual reference values.
Expected: Rpc = 1.74 ohm
Parameters: 10 electrodes, 3m long, 3" diameter, 1m deep, 60mm strip, 50m² area, 100 ohm*m soil resistivity
"""

import math
from functions import (
    h_formula, rv, ro, Rv, Ro, Rpc,
    get_exterior_diameter
)
from spacing_calculator import spacing_calc

# Input parameters
n = 10
l = 3  # electrode length in meters
d_inch = "3"  # diameter 3 inches
q = 1  # pit depth in meters
b_mm = 60  # strip width in mm
area = 50  # available surface area in m²
rho_measured = 100  # measured soil resistivity in ohm*m

# For measured resistivity, use directly (no K coefficient)
rho_calc = rho_measured

print("=" * 70)
print("RPC CALCULATION DEBUG")
print("=" * 70)
print(f"\nInput Parameters:")
print(f"  n (electrodes): {n}")
print(f"  l (electrode length): {l} m")
print(f"  d (diameter): {d_inch}\"")
print(f"  q (pit depth): {q} m")
print(f"  b (strip width): {b_mm} mm")
print(f"  area: {area} m²")
print(f"  rho (soil resistivity): {rho_measured} ohm·m")
print(f"  Expected Rpc: 1.74 Ω")

# Get exterior diameter
d = get_exterior_diameter(d_inch, l)
print(f"\n  d (exterior diameter): {d} m")

# Calculate h
h = h_formula(q, l)
print(f"\nCalculated h = q + l/2 = {q} + {l}/2 = {h} m")

# Calculate rv (single electrode)
rv_value = rv(rho_calc, l, d, h)
print(f"\nrv (single vertical electrode):")
print(f"  rv = 0.366 × (ρ/l) × [ln(2l/d) + 0.5×ln((4h+l)/(4h-l))]")
print(f"  rv = 0.366 × ({rho_calc}/{l}) × [ln({2*l}/{d}) + 0.5×ln(({4*h+l})/({4*h-l}))]")
print(f"  rv = {rv_value:.4f} Ω")

# Convert strip width to meters
b = b_mm / 1000  # Convert mm to m

# Calculate ro (strip)
ro_value = ro(rho_calc, l, b, q)
print(f"\nro (horizontal strip):")
print(f"  ro = 0.366 × (ρ/l) × ln(2l²/(b×q))")
print(f"  ro = 0.366 × ({rho_calc}/{l}) × ln(2×{l}²/({b}×{q}))")
print(f"  ro = {ro_value:.4f} Ω")

# Get optimal configuration
# Pass n explicitly (not as maximum, but as the specific count to use)
config = spacing_calc(area, l, n=n)
print(f"\nOptimal Configuration:")
print(f"  Shape: {config['config']}")
print(f"  Electrodes: {config['n']}")
print(f"  Spacing: {config['spacing']}")
print(f"  Openess: {config['openess']}")
print(f"  uv (vertical utilization): {config['uv']}")
print(f"  uo (horizontal utilization): {config['uo']}")

# Calculate Rv and Ro
uv = config['uv']
uo = config['uo']
n_opt = config['n']

Rv_value = Rv(rv_value, n_opt, uv)
Ro_value = Ro(ro_value, n_opt, uo)

print(f"\nTotal Resistances:")
print(f"  Rv = rv / (n × uv) = {rv_value:.4f} / ({n_opt} × {uv}) = {Rv_value:.4f} Ω")
print(f"  Ro = ro / (n × uo) = {ro_value:.4f} / ({n_opt} × {uo}) = {Ro_value:.4f} Ω")

# Calculate Rpc
Rpc_value = Rpc(Rv_value, Ro_value)

print(f"\n" + "=" * 70)
print(f"RPC CALCULATION:")
print(f"  Rpc = (Rv × Ro) / (Rv + Ro)")
print(f"  Rpc = ({Rv_value:.4f} × {Ro_value:.4f}) / ({Rv_value:.4f} + {Ro_value:.4f})")
print(f"  Rpc = {Rpc_value:.4f} Ω")
print(f"\nEXPECTED: 1.74 Ω")
print(f"RATIO (Calculated / Expected): {Rpc_value / 1.74:.2f}x")
print("=" * 70)

# Try alternative: Maybe the issue is with utilization factors?
print(f"\n\nDEBUG: What if we ignore utilization factors?")
Rv_alt = rv_value / n_opt
Ro_alt = ro_value / n_opt
Rpc_alt = (Rv_alt * Ro_alt) / (Rv_alt + Ro_alt)
print(f"  Rv (no uv) = {rv_value:.4f} / {n_opt} = {Rv_alt:.4f} Ω")
print(f"  Ro (no uo) = {ro_value:.4f} / {n_opt} = {Ro_alt:.4f} Ω")
print(f"  Rpc = {Rpc_alt:.4f} Ω")
print(f"  Ratio to expected: {Rpc_alt / 1.74:.2f}x")

# Try another alternative: Maybe rv and ro should NOT be divided by utilization factors?
print(f"\nDEBUG: What if rv and ro ARE the total, not single?")
Rv_alt2 = rv_value / (n_opt * uv)
Ro_alt2 = ro_value / (n_opt * uo)
Rpc_alt2 = (Rv_alt2 * Ro_alt2) / (Rv_alt2 + Ro_alt2)
print(f"  Already calculated as: Rv={Rv_alt2:.4f}, Ro={Ro_alt2:.4f}, Rpc={Rpc_alt2:.4f}")

# Check what 1.74 back-calculates to
print(f"\n\nDEBUG: Back-calculate from expected Rpc = 1.74")
target_rpc = 1.74
# If Rpc = (Rv × Ro) / (Rv + Ro), and we know Rv_value and ro_value...
# What should the divisors be?
print(f"  Current Rv × Ro = {Rv_value:.4f} × {Ro_value:.4f} = {Rv_value * Ro_value:.4f}")
print(f"  Current sum = {Rv_value + Ro_value:.4f}")
print(f"  To get 1.74, we'd need: (Rv × Ro) = 1.74 × (Rv + Ro)")
print(f"  From our calculation: {Rpc_value:.4f} × {Rv_value + Ro_value:.4f} = {Rpc_value * (Rv_value + Ro_value):.4f}")
