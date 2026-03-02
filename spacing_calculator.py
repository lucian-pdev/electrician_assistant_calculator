#!/usr/bin/env python3
"""
spacing_calculator.py

Determines the optimal grounding configuration based on:
- available area (m²)
- electrode length L (m)
- utilization factor efficiency (uv)

Evaluates multiple geometric configurations and electrode counts,
then selects the most efficient configuration that fits in the area.
"""

import math
from variables import electrode_utilization
from functions import get_utilization_factor

# ---------------------------------------------------------------------------
# Helper: check if a shape fits in the available area
# ---------------------------------------------------------------------------

def _fits_line(n, spacing, area):
    """Line: length = (n - 1) * spacing
    Fits if the line length ≤ diagonal of the available area."""
    length = (n - 1) * spacing
    max_diagonal = math.sqrt(2 * area)  # diagonal of area
    return length <= max_diagonal


def _fits_delta(spacing, area):
    """Equilateral triangle of side s.
    Area needed: (√3/4) * s²"""
    needed = (math.sqrt(3) / 4) * spacing**2
    return needed <= area


def _fits_square(spacing, area):
    """Square of side s.
    Area needed: s²"""
    needed = spacing**2
    return needed <= area


def _fits_square_center(spacing, area, L):
    """Square with center electrode (5 total: 4 corners + 1 center).
    Constraint: diagonal ≥ 2L (to keep center electrode adequately separated).
    Diagonal of square with side s: s*√2 ≥ 2L, so s ≥ 2L/√2 ≈ 1.41L.
    Area needed: s²"""
    diagonal = spacing * math.sqrt(2)
    min_diagonal = 2 * L
    area_needed = spacing**2
    return diagonal >= min_diagonal and area_needed <= area


def _fits_double_delta(spacing, area):
    """Two equilateral triangles linked together"""
    needed = ((math.sqrt(3) / 2) * spacing**2) * 2
    return needed <= area


def _fits_rectangle(n, spacing, area):
    """Pack rods in a grid: rows × cols × spacing²"""
    rows = int(math.sqrt(n))
    cols = math.ceil(n / rows)
    needed = rows * cols * spacing**2
    return needed <= area


# ---------------------------------------------------------------------------
# Efficiency ranking (lower = better)
# ---------------------------------------------------------------------------

EFFICIENCY_RANK = {
    "line": 1,
    "rectangle": 2,
    "delta": 3,
    "square": 4,
    "square_center": 5,
    "double_delta": 6,
    "polygon": 7,
}


# ---------------------------------------------------------------------------
# Main function: spacing_calc()
# ---------------------------------------------------------------------------
def spacing_calc(area, L, n=None, n_max=20, force_config=None):
    """
    Determine optimal grounding configuration.
    
    Objective (depends on parameters):
    - If force_config is specified: Find that SPECIFIC shape (with best spacing)
    - Else if n is specified: Find BEST SHAPE for that electrode count
    - Else: Find MINIMUM electrodes that fit, then optimize shape
    
    Parameters:
        area (float): available surface area in m²
        L (float): electrode length in meters
        n (int or None): specific electrode count to optimize FOR, or None to minimize
        n_max (int): maximum electrode count to search (only used if n is None)
        force_config (str or None): force a specific configuration shape
                                   Options: 'line', 'delta', 'square', 'square_center', 'double_delta', 'rectangle'
                                   If specified, ignores optimization and returns that shape if possible

    Returns:
        dict with:
            - config: shape name
            - n: number of electrodes
            - spacing: spacing between electrodes ('L' or '2L')
            - openess: 'open' or 'closed' perimeter
            - uv: utilization factor (vertical)
            - uo: utilization factor (horizontal)
            - efficiency: uv * uo (for this configuration)
            
    Raises:
        ValueError: if force_config is specified but cannot fit in the area
    """

    spacing_options = ["L", "2L"]
    
    # FORCED CONFIG MODE: Look specifically for the requested configuration
    if force_config is not None:
        for num_electrodes in range(2, n_max + 1):
            for spacing_ratio_idx, spacing_ratio in enumerate(spacing_options):
                spacing_ratio_val = spacing_ratio_idx + 1
                spacing = spacing_ratio

                # Check which shape matches the forced config
                valid = False
                target_n = None

                if force_config == "line":
                    if _fits_line(num_electrodes, spacing_ratio_val, area):
                        valid = True
                        target_n = num_electrodes

                elif force_config == "delta":
                    if num_electrodes == 3 and _fits_delta(spacing_ratio_val, area):
                        valid = True
                        target_n = 3

                elif force_config == "square":
                    if num_electrodes == 4 and _fits_square(spacing_ratio_val, area):
                        valid = True
                        target_n = 4

                elif force_config == "square_center":
                    if num_electrodes == 5 and _fits_square_center(spacing_ratio_val, area, L):
                        valid = True
                        target_n = 5

                elif force_config == "double_delta":
                    if num_electrodes == 6 and _fits_double_delta(spacing_ratio_val, area):
                        valid = True
                        target_n = 6

                elif force_config == "rectangle":
                    if num_electrodes > 2 and _fits_rectangle(num_electrodes, spacing_ratio_val, area):
                        valid = True
                        target_n = num_electrodes
                else:
                    raise ValueError(f"Unknown force_config: '{force_config}'. Must be one of: line, delta, square, square_center, double_delta, rectangle")

                # If valid, get utilization factors and return
                if valid and target_n is not None:
                    openess = "open perimeter" if force_config == "line" else "closed perimeter"

                    try:
                        uv = get_utilization_factor(openess, "vertical", spacing, target_n)
                        uo = get_utilization_factor(openess, "horizontal", spacing, target_n)
                        if not uv or not uo:
                            continue
                    except Exception:
                        continue

                    efficiency = uv * uo

                    return {
                        "config": force_config,
                        "n": target_n,
                        "spacing": spacing,
                        "openess": openess,
                        "uv": uv,
                        "uo": uo,
                        "efficiency": efficiency,
                    }

        # If we get here, forced config doesn't fit
        raise ValueError(f"Forced configuration '{force_config}' cannot fit in available area of {area} m²")

    # NORMAL OPTIMIZATION MODE (no forced config)
    # If n is specified, optimize FOR that n; otherwise search for minimum
    if n is not None:
        # MODE 1: Use specified electrode count, find best shape
        electrodes_to_search = [n]
    else:
        # MODE 2: Find minimum n that fits
        electrodes_to_search = range(2, n_max + 1)

    # Iterate through electrode counts
    for num_electrodes in electrodes_to_search:
        best_for_this_n = None

        # For this electrode count, try all spacing ratios
        for spacing_ratio_idx, spacing_ratio in enumerate(spacing_options):
            spacing_ratio_val = spacing_ratio_idx + 1
            spacing = spacing_ratio  # "L" or "2L"

            # --- Evaluate each shape for this n and spacing ---
            shapes = []

            # LINE (any n)
            if _fits_line(num_electrodes, spacing_ratio_val, area):
                shapes.append(("line", True, num_electrodes))

            # DELTA (only n == 3)
            if num_electrodes == 3 and _fits_delta(spacing_ratio_val, area):
                shapes.append(("delta", False, 3))

            # SQUARE (n == 4)
            if num_electrodes == 4 and _fits_square(spacing_ratio_val, area):
                shapes.append(("square", False, 4))

            # SQUARE + CENTER (n == 5)
            if num_electrodes == 5 and _fits_square_center(spacing_ratio_val, area, L):
                shapes.append(("square_center", False, 5))

            # DOUBLE DELTA (n == 6)
            if num_electrodes == 6 and _fits_double_delta(spacing_ratio_val, area):
                shapes.append(("double_delta", False, 6))

            # RECTANGLE (any n higher than 2)
            if num_electrodes > 2 and _fits_rectangle(num_electrodes, spacing_ratio_val, area):
                shapes.append(("rectangle", False, num_electrodes))

            # If nothing fits and we're in minimize mode, continue to next n
            if not shapes and n is None:
                continue
            
            # --- For each valid shape, evaluate efficiency ---
            for shape_name, is_open, en in shapes:
                openess = "open perimeter" if is_open else "closed perimeter"

                try:
                    uv = get_utilization_factor(openess, "vertical", spacing, en)
                    uo = get_utilization_factor(openess, "horizontal", spacing, en)
                    if not uv or not uo:
                        raise Exception
                except Exception:
                    continue  # skip invalid combinations

                # Efficiency for this configuration
                efficiency = uv * uo  # type: ignore

                candidate = {
                    "config": shape_name,
                    "n": en,
                    "spacing": spacing,
                    "openess": openess,
                    "uv": uv,
                    "uo": uo,
                    "efficiency": efficiency,
                }

                # Keep the best configuration for this electrode count
                if best_for_this_n is None:
                    best_for_this_n = candidate
                else:
                    # Prioritize: higher efficiency, then better shape rank
                    if (candidate["efficiency"] > best_for_this_n["efficiency"] or
                        (candidate["efficiency"] == best_for_this_n["efficiency"] and
                         EFFICIENCY_RANK[candidate["config"]] < EFFICIENCY_RANK[best_for_this_n["config"]])):
                        best_for_this_n = candidate

        # If we found a valid configuration for this n, return it
        if best_for_this_n is not None:
            return best_for_this_n

    # If no configuration fits
    raise ValueError("No possible electrode configuration found within the available area.")
