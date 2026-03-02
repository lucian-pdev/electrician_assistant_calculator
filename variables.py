#!/usr/bin/env pyton3

# Global Variables and tables
cc = 0.366 # conversion coefficient between international standards
           # that use natural log into log10() for practical applications
           
surface_contact_table = [
    {"diameter":"A", "exterior_diam": 0.01, "length": 1, "surface_contact": 0.0314},
    {"diameter":"A", "exterior_diam": 0.01, "length": 2, "surface_contact": 0.0628},
    {"diameter":"A", "exterior_diam": 0.01, "length": 3, "surface_contact": 0.0942},
    {"diameter":"B", "exterior_diam": 0.02, "length": 1, "surface_contact": 0.1058},
    {"diameter":"B", "exterior_diam": 0.02, "length": 2, "surface_contact": 0.1517},
    {"diameter":"B", "exterior_diam": 0.02, "length": 3, "surface_contact": 0.1884},
    {"diameter":"1", "exterior_diam": 0.0337, "length": 1, "surface_contact": 0.179},
    {"diameter":"1", "exterior_diam": 0.0337, "length": 2, "surface_contact": 0.19782},
    {"diameter":"1", "exterior_diam": 0.0337, "length": 3, "surface_contact": 0.3175},
    {"diameter":"1 1/2", "exterior_diam": 0.0483, "length": 1, "surface_contact": 0.2386},
    {"diameter":"1 1/2", "exterior_diam": 0.0483, "length": 2, "surface_contact": 0.27632},
    {"diameter":"1 1/2", "exterior_diam": 0.0483, "length": 3, "surface_contact": 0.455},
    # {"diameter":"2", "exterior_diam": 0.057, "length": 1, "surface_contact": 0.0628},
    # {"diameter":"2", "exterior_diam": 0.057, "length": 2, "surface_contact": 0.1256},
    # {"diameter":"2", "exterior_diam": 0.057, "length": 3, "surface_contact": 0.5369},
    {"diameter":"2", "exterior_diam": 0.063, "length": 1, "surface_contact": 0.2116},
    {"diameter":"2", "exterior_diam": 0.063, "length": 2, "surface_contact": 0.3033},
    {"diameter":"2", "exterior_diam": 0.063, "length": 3, "surface_contact": 0.59346},
    {"diameter":"2 1/2", "exterior_diam": 0.076, "length": 1, "surface_contact": 0.358},
    {"diameter":"2 1/2", "exterior_diam": 0.076, "length": 2, "surface_contact": 0.39564},
    {"diameter":"2 1/2", "exterior_diam": 0.076, "length": 3, "surface_contact": 0.7159},
    {"diameter":"3", "exterior_diam": 0.088, "length": 1, "surface_contact": 0.4773},
    {"diameter":"3", "exterior_diam": 0.088, "length": 2, "surface_contact": 0.55264},
    {"diameter":"3", "exterior_diam": 0.088, "length": 3, "surface_contact": 0.82896}
]

K_table = [
    {"moisture": "min", "depth": 0.5, "K": 6.5}, 
    {"moisture": "median", "depth": 0.5, "K": 5.5}, 
    {"moisture": "max", "depth": 0.5, "K": 4.5}, 
    {"moisture": "min", "depth": 0.8, "K": 3}, 
    {"moisture": "median", "depth": 0.8, "K": 2}, 
    {"moisture": "max", "depth": 0.8, "K": 1.6}, 
    {"moisture": "min", "depth": 0.9, "K": 2}, 
    {"moisture": "median", "depth": 0.9, "K": 1.5}, 
    {"moisture": "max", "depth": 0.9, "K": 1.4}
]

soil_resistivity = {
    "peat": {
        "name": "Peat soil (Pamant cu turba)",
        "rho_ohm_m": (500, 3000)
    },
    "black_soil": {
        "name": "Black soil (pământ negru)",
        "rho_ohm_m": (20, 100)
    },
    "sandy_soil": {
        "name": "Sandy soil (nisipos)",
        "rho_ohm_m": (200, 3000)
    },
    "clay_soil": {
        "name": "Clay soil (argilos)",
        "rho_ohm_m": (30, 150)
    },
    "rock": {
        "name": "Rock / stone (piatră)",
        "rho_ohm_m": (1000, 10000)
    },
    "concrete": {
        "name": "Concrete (ciment)",
        "rho_ohm_m": (30, 90)
    },
    "asphalt": {
        "name": "Asphalt (asfalt)",
        "rho_ohm_m": (2000, 30000)
    }
}

electrode_utilization = {
    "open perimeter": {
        "vertical": {
            "L": {
                2: 0.85,
                3: 0.8,
                4: 0.75,
                5: 0.7,
                6: 0.65,
                10: 0.6,
                20: 0.5,
            },
            "2L": {
                2: 0.9,
                3: 0.85,
                4: 0.82,
                5: 0.8,
                6: 0.78,
                10: 0.75,
                20: 0.7,
            },
        },
        "horizontal": {
            "L": {
                2: 0.8,
                3: 0.8,
                4: 0.77,
                5: 0.75,
                6: 0.6,
                10: 0.5,
                20: 0.2,
            },
            "2L": {
                2: 0.9,
                3: 0.9,
                4: 0.88,
                5: 0.85,
                6: 0.8,
                10: 0.75,
                20: 0.56,
            },
        }
    },
    "closed perimeter": {
        "vertical": {
            "L": {
                2: None,
                3: 0.75,
                4: 0.65,
                5: 0.62,
                6: 0.6,
                10: 0.55,
                20: 0.5,
            },
            "2L": {
                2: None,
                3: 0.8,
                4: 0.75,
                5: 0.72,
                6: 0.7,
                10: 0.66,
                20: 0.55,
            },
        },
        "horizontal": {
            "L": {
                2: None,
                3: 0.5,
                4: 0.45,
                5: 0.42,
                6: 0.4,
                10: 0.33,
                20: 0.25,
            },
            "2L": {
                2: None,
                3: 0.6,
                4: 0.55,
                5: 0.52,
                6: 0.5,
                10: 0.44,
                20: 0.3,
            },
        }
    },
}