#!/usr/bin/env python3
import logging, time, math
from variables import *
from functools import wraps

DEBUG_MODE = False
logging.basicConfig(level=logging.ERROR, format="%(message)s")

# decorators
def value_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except Exception as e:
            if DEBUG_MODE:
                logging.error(f"\n {func.__name__} failed:")
                logging.error(f"   Error: {e}")
                logging.error(f"   Args: {args}")
                logging.error(f"   Kwargs: {kwargs}")
                logging.exception("   Traceback:")
            else:
                pass

            # Re-raise the exception instead of returning None
            raise

    return wrapper


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args,**kwargs)
        logging.info(f"{func.__name__} took {time.time() - start:.4f}s")
        return result
    return wrapper

def decorator(func):    # the sequence-control decorator
    decorators = [
        value_handler,
        # timeit
    ]

    for dec in reversed(decorators):
        func = dec(func)
        # this becomes dec_A(dec_B(dec_C(dec_D....dec_n(func))))
    return func
    
# functions
@decorator
def ohm_law(I=None, U=None, R=None):
    """Ohm's law (I = U/R) to identify Voltage, Amperage or Resistance when one is unknown."""
    
    # guardrails
    count_unknowns = 0
    values = [I, U, R]
    unknowns = []
    
    for v in values:
        if v is None:
            count_unknowns += 1
            unknowns.append(v)

    if count_unknowns != 1:
        raise ValueError(f"Too many unknowns, can only process one, received: {unknowns}")
    
    # function
    if I is None:
        return U / R # type: ignore
    if U is None:
        return I * R 
    if R is None:
        return U / I

@decorator
def prompter(message):
    """Prompts the user with a Yes/No question."""
    try:
        raw = input(f"{message} [Y/N, default is No]:").upper()

        if raw == "":
            return False
        elif raw != "Y":
            return False
        elif raw == "Y":
            return True
        
    except ValueError:
        print("Please answer only with 'Y', 'N' or hit the Enter/Return key.")
        return None
  
@decorator
def get_resistivity(soil_type, mode="median"):
    """Return soil resistivity based on type.
       mode = 'min', 'max', or 'median'."""
    if soil_type not in soil_resistivity:
        raise ValueError(f"Unknown soil type: {soil_type}")

    low, high = soil_resistivity[soil_type]["rho_ohm_m"]

    if mode == "min":
        return low
    elif mode == "max":
        return high
    elif mode == "median":
        return (low + high) / 2
    else:
        raise ValueError("Mode must be 'min', 'max', or 'median'")

@decorator
def get_exterior_diameter(d_inch, L):
    d_str = str(d_inch).replace(".5", " 1/2")
    for row in surface_contact_table:
        if row["diameter"] == d_str and row["length"] == L:
            return row["exterior_diam"]
    raise ValueError(f"No match for diameter={d_inch} inch, length={L} m")


@decorator
def input_values():
    message = """Input, for these 6, in order:
    * the number of electrodes, 
    * the length of electrodes (all will be considered identical),
    * the diameter of the electrode (A, B, 1, 1.5, 2, 2.5, 3),
    * the depth of the pit dug out (recommended to be more than the freezing depth: 0.9 m) in m,
    * the width of the strip used to connect the electrodes and the grounding separation piece in mm,
    * the available surface space for the pit in m2.
    
    The numbers must separated by a space and provided in the specific order and measurement units.
    """
    # raw input handling part 1
    raw = input(message).split()
    
    # Get resistance refference
    measured = prompter("Did you measure the resistivity of the soil?")
    to_calc_rho = False
    rho_measured = 200  # arbitrary default value (dry clay) 
    
    if measured:
        rho_measured = float(input("Enter the measured resistivity (ohm*m): "))
    
    # make a new list of soil names to simplify the later code
    else:
        to_calc_rho = True
        # Get a measure for humidity
        error_msg = "Please answer with a number from 1 to 3."
        while True:
            try:
                mode = int(input("\n\nHow humid is your soil all-year?\n1) dry\n2) medium\n3) wet\n\n"))
                humidity_map = {1: "min", 2: "median", 3: "max"}
                humidity = humidity_map[mode]
                break
            except ValueError:
                print(error_msg)  
                
        soil_list = list(soil_resistivity.items())

        for idx, (key, data) in enumerate(soil_list, start=1):
            print(f"{idx}) {data['name']}")
            
        print(f"Which type of soil from these do you have? [1-{len(soil_list)}]:")

        error_msg = "Please answer with a number from 1 to 9."
        while True:
            try:
                soil_index = int(input("Choose soil number: "))
                if 1 <= soil_index <= len(soil_list):
                    rho_measured = get_resistivity(soil_list[soil_index - 1][0], humidity)
                    break
                else:
                    print(error_msg)
            except ValueError:
                print(error_msg)
    
    # raw input handling part 2
    raw.append(rho_measured)    # type: ignore
    expected = [ "number of electrodes", 
               "electrode length (m)", 
               "diameter (inches)", 
               "pit depth (m)", 
               "strip width (mm)",  
               "available surface (m2)", 
               "soil resistivity (ohm*m)"]
    
    
    if len(raw) != len(expected): 
       raise ValueError( f"Expected {len(expected)} values but received {len(raw)}." )
    
    values = {}
    
    for idx, (value, name) in enumerate(zip(raw, expected)):
        if name != "diameter (inches)":
            try:
                values[name] = float(value)
            except ValueError:
                raise ValueError(
                f"Invalid value at position {idx+1}: '{value}' " f"(expected {name}, numeric)"
            )
        else:
            values[name] = value

    # find the exterior diameter
    d_inch = values["diameter (inches)"]
    L = int(values["electrode length (m)"])
    d = get_exterior_diameter(d_inch, L)

    # map to the keys 
    return { 
            "n": values["number of electrodes"], 
            "l": values["electrode length (m)"], 
            "d": d,
            "q": values["pit depth (m)"], 
            "b": values["strip width (mm)"] / 100, 
            "space": values["available surface (m2)"],
            "rho_mas": 
                rho_calculator(values["soil resistivity (ohm*m)"], humidity, values["pit depth (m)"]) 
                               if to_calc_rho else values["soil resistivity (ohm*m)"],
            }

@decorator
def get_utilization_factor(openess, kind, spacing_ratio, n_electrodes):
    """openess: 'open' (line style grounding) or 'closed' (delta or polygon)
     kind: 'vertical' or 'horizontal' 
     spacing_ratio: 'L' or '2L'
     n_electrodes: 2, 3, 4, 5, 6, 10, 20 
     If your numbers don't match exactly, take the next worst option."""
     
    # try: 
    return electrode_utilization[openess][kind][spacing_ratio][n_electrodes]  
    
    # except KeyError: 
    #     raise ValueError(f"""No utilization factor for openess={openess}, 
    #                      kind={kind}, spacing={spacing_ratio}, n={n_electrodes}""")

# @decorator
# def prompt_Rpc_util_factor(openess, kind, spacing_ratio, n_electrodes):
#     """
#     Compute utilization factors uv and uo based on:
#     - openess: 'open' or 'closed'
#     - kind: 'vertical' or 'horizontal'
#     - spacing_ratio: 'L' or '2L'
#     - n_electrodes: integer
#     """

#     uv = get_utilization_factor(openess, kind, spacing_ratio, n_electrodes)
#     uo = get_utilization_factor(openess, kind, spacing_ratio, n_electrodes)

#     return uv, uo

@decorator
def rho_calculator(rho_measured, humidity, depth):
    """Rho_calculated = Rho_measured * K (coefficient related to humidity-at-depth)"""
    # Normalize depth to the discrete values used in K_table
    if depth <= 0.5:
        depth = 0.5
    elif depth <= 0.8:
        depth = 0.8
    else:
        depth = 0.9
        
    # Find matching K coefficient
    for row in K_table:
        if (row["moisture"] == humidity and row["depth"] == depth): 
            Koeff = row["K"]
            break
        
    if Koeff is None: 
        raise ValueError(f"No K coefficient found for humidity={humidity}, depth={depth}")
    
    return rho_measured * Koeff # this is rho_calc for everything else

@decorator     
def h_formula(q, l):
    """h = q + l/2"""
    h = q + l/2
    return h
    
@decorator
def rv(rho_calc, l, d, h):
    """rv = 0.366 * rho_calc/l * (log(2l/d) + 0.5 * log((4*h+l)/(4*h-l)))"""
    rv = 0.366 * (rho_calc/l) * (math.log(2*l/d) + 0.5 * math.log((4*h+l)/(4*h-l)))
    return rv

@decorator
def ro(rho_calc, l, b, q):
    """ro = 0.366 * rho_calc/l * log((2 * (l ** 2)) / (b * q))"""
    ro = 0.366 * (rho_calc/l) * math.log((2 * (l ** 2)) / (b * q))
    return ro

@decorator  
def Rv(rv, n, uv):
    """Rv = rv / (n * uv)"""
    Rv = rv / (n * uv)
    return Rv
    
@decorator
def Ro(ro, n, uo):
    """Ro = ro / (n * uo)"""
    Ro = ro / (n * uo)
    return Ro

@decorator
def Rpc(Rv, Ro):
    """Rpc = (Rv * Ro) / (Rv + Ro)"""
    Rpc = (Rv * Ro ) / (Rv + Ro)
    return Rpc