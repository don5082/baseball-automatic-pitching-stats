
# Global variables for average ball movement ranges
# Averages based on 2024-2025 Statcast induced movement data (inches)
# Vertical: + is 'rise/carry', - is 'sink/drop'
# Horizontal: + is typically arm-side run, - is glove-side sweep
# Disclaimer: these averages were sourced from GenAI, but are based on Baseball Savant


class FF:
    avg_vb = (1.08, 1.67)  # Typical 'ride' fastballs
    avg_hb = (0.38, 0.95)

class SI:
    avg_vb = (0.42, 1.0)
    avg_hb = (1.05, 1.54)

class FC:
    avg_vb = (0.34, 0.92)
    avg_hb = (-0.37, 0.28)

class SL:
    avg_vb = (-0.33, 0.42)
    avg_hb = (-0.79, -0.21)

class ST:
    avg_vb = (-0.33, 0.33)
    avg_hb = (-1.67, -0.83) # Sweepers have high variance

class CU:
    avg_vb = (-1.17, -0.5)
    avg_hb = (-1.13, -0.46)

class KC:
    avg_vb = (-1.42, -0.67)
    avg_hb = (-0.95, -0.38)

class SV:
    avg_vb = (-0.83, -0.17)
    avg_hb = (-0.95, -0.46)

class CH:
    avg_vb = (0.25, 0.92)
    avg_hb = (1.05, 1.63)

class FS:
    avg_vb = (0.0, 0.58)
    avg_hb = (0.55, 1.12)

class KN:
    avg_vb = (-0.58, 0.58) # High uncertainty
    avg_hb = (-0.58, 0.58)

class FO:
    avg_vb = (-0.08, 0.5)
    avg_hb = (0.38, 0.95)

class SC:
    avg_vb = (0.0, 0.67)
    avg_hb = (0.88, 1.45)

class EP:
    avg_vb = (-1.83, -0.67)
    avg_hb = (-0.54, 0.54)