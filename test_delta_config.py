#!/usr/bin/env python3
"""
Test case: Delta (triangular) configuration grounding system
Parameters:
- 3 electrodes in delta/triangle formation
- 3 meters long
- 3 inch diameter
- 1 meter deep ditch
- 40 mm connective strip
- 500 m² available area
- 66 ohm*m measured soil resistivity
"""

from functions import (
    h_formula, rv, ro, Rv, Ro, Rpc,
    get_exterior_diameter
)
from spacing_calculator import spacing_calc

# Test parameters
n = 3
l = 3  # electrode length in meters
d_inch = "3"  # diameter 3 inches
q = 1  # pit depth in meters
b_mm = 40  # strip width in mm
area = 500  # available surface area in m²
rho_measured = 66  # measured soil resistivity in ohm*m

# For measured resistivity, use directly
rho_calc = rho_measured

print("=" * 70)
print("TEST CASE: DELTA CONFIGURATION GROUNDING")
print("=" * 70)
print(f"\nTest Parameters:")
print(f"  Number of electrodes (n): {n}")
print(f"  Electrode length (l): {l} m")
print(f"  Electrode diameter: {d_inch}\"")
print(f"  Pit depth (q): {q} m")
print(f"  Strip width (b): {b_mm} mm")
print(f"  Available area: {area} m²")
print(f"  Soil resistivity (ρ): {rho_measured} ohm·m")
print(f"  Expected configuration: DELTA (triangle)")

# Get exterior diameter
d = get_exterior_diameter(d_inch, l)
print(f"\nDerived Parameters:")
print(f"  Exterior diameter (d): {d} m")

# Calculate h
h = h_formula(q, l)
print(f"  Effective depth (h): h = q + l/2 = {q} + {l}/2 = {h} m")

# Calculate rv (single electrode)
rv_value = rv(rho_calc, l, d, h)
print(f"\nSingle Electrode Resistance (rv):")
print(f"  Formula: rv = 0.366 × (ρ/l) × [ln(2l/d) + 0.5×ln((4h+l)/(4h-l))]")
print(f"  rv = 0.366 × ({rho_calc}/{l}) × [ln({2*l}/{d}) + 0.5×ln(({4*h+l})/({4*h-l}))]")
print(f"  rv = {rv_value:.4f} Ω")

# Convert strip width to meters
b = b_mm / 1000  # Convert mm to m

# Calculate ro (strip)
ro_value = ro(rho_calc, l, b, q)
print(f"\nHorizontal Strip Resistance (ro):")
print(f"  Formula: ro = 0.366 × (ρ/l) × ln(2l²/(b×q))")
print(f"  ro = 0.366 × ({rho_calc}/{l}) × ln(2×{l}²/({b}×{q}))")
print(f"  ro = {ro_value:.4f} Ω")

# Get optimal configuration
config = spacing_calc(area, l, n=n)

print(f"\nOptimal Configuration Found:")
print(f"  Shape: {config['config']}")
print(f"  Electrodes: {config['n']}")
print(f"  Spacing: {config['spacing']}")
print(f"  Perimeter type: {config['openess']}")
print(f"  Vertical utilization factor (uv): {config['uv']}")
print(f"  Horizontal utilization factor (uo): {config['uo']}")
print(f"  Configuration efficiency (uv × uo): {config['efficiency']:.4f}")

# Verify it's actually delta
if config['config'] != 'delta':
    print(f"\n⚠ Note: Optimizer selected '{config['config']}' instead of 'delta'")
    print(f"  (This is the most efficient configuration for the given parameters)")
else:
    print(f"\n✓ Confirmed: DELTA configuration selected")

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
print(f"RESULT (OPTIMIZED):")
print(f"  Rpc = (Rv × Ro) / (Rv + Ro)")
print(f"  Rpc = ({Rv_value:.4f} × {Ro_value:.4f}) / ({Rv_value:.4f} + {Ro_value:.4f})")
print(f"  Rpc = {Rpc_value:.4f} Ω")
print("=" * 70)

print(f"\nCompliance Check (Optimized):")
if Rpc_value <= 1:
    print(f"  ✓ Meets COMBINED lightning + residential (≤ 1 Ω)")
elif Rpc_value <= 4:
    print(f"  ✓ Meets RESIDENTIAL (≤ 4 Ω)")
elif Rpc_value <= 10:
    print(f"  ✓ Meets LIGHTNING ROD (≤ 10 Ω)")
else:
    print(f"  ✗ Does NOT meet requirements (> 10 Ω)")

# Now force DELTA configuration
print(f"\n" + "=" * 70)
print(f"FORCED CONFIGURATION: DELTA")
print("=" * 70)

try:
    config_delta = spacing_calc(area, l, n=n, force_config='delta')
    
    print(f"\nForced Configuration:")
    print(f"  Shape: {config_delta['config']}")
    print(f"  Electrodes: {config_delta['n']}")
    print(f"  Spacing: {config_delta['spacing']}")
    print(f"  Perimeter type: {config_delta['openess']}")
    print(f"  Vertical utilization factor (uv): {config_delta['uv']}")
    print(f"  Horizontal utilization factor (uo): {config_delta['uo']}")
    print(f"  Configuration efficiency (uv × uo): {config_delta['efficiency']:.4f}")
    
    uv_delta = config_delta['uv']
    uo_delta = config_delta['uo']
    n_delta = config_delta['n']
    
    Rv_delta = Rv(rv_value, n_delta, uv_delta)
    Ro_delta = Ro(ro_value, n_delta, uo_delta)
    
    print(f"\nTotal Resistances (Delta):")
    print(f"  Rv = rv / (n × uv) = {rv_value:.4f} / ({n_delta} × {uv_delta}) = {Rv_delta:.4f} Ω")
    print(f"  Ro = ro / (n × uo) = {ro_value:.4f} / ({n_delta} × {uo_delta}) = {Ro_delta:.4f} Ω")
    
    Rpc_delta = Rpc(Rv_delta, Ro_delta)
    
    print(f"\n" + "=" * 70)
    print(f"RESULT (FORCED DELTA):")
    print(f"  Rpc = (Rv × Ro) / (Rv + Ro)")
    print(f"  Rpc = ({Rv_delta:.4f} × {Ro_delta:.4f}) / ({Rv_delta:.4f} + {Ro_delta:.4f})")
    print(f"  Rpc = {Rpc_delta:.4f} Ω")
    print("=" * 70)
    
    print(f"\nCompliance Check (Forced Delta):")
    if Rpc_delta <= 1:
        print(f"  ✓ Meets COMBINED lightning + residential (≤ 1 Ω)")
    elif Rpc_delta <= 4:
        print(f"  ✓ Meets RESIDENTIAL (≤ 4 Ω)")
    elif Rpc_delta <= 10:
        print(f"  ✓ Meets LIGHTNING ROD (≤ 10 Ω)")
    else:
        print(f"  ✗ Does NOT meet requirements (> 10 Ω)")
    
    print(f"\nComparison:")
    print(f"  Optimized Rpc: {Rpc_value:.4f} Ω")
    print(f"  Delta Rpc: {Rpc_delta:.4f} Ω")
    print(f"  Difference: {Rpc_delta - Rpc_value:.4f} Ω ({(Rpc_delta / Rpc_value - 1) * 100:.1f}%)")
    
except ValueError as e:
    print(f"\n✗ Error: {e}")
print("\n" + "=" * 70)
print("TEST CASE COMPLETE")
print("=" * 70)
