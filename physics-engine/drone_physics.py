"""Drone physics screening. Not a flight-safety certification."""
import math
from dataclasses import dataclass
from typing import Optional, Tuple
from ung_system_physics import Check, G, require_positive
@dataclass
class Drone:
    name:str
    n_motors:int
    motor_thrust_g:float
    motor_g:float
    motor_kv:float
    prop_diameter_mm:float
    prop_g:float
    battery_mah:float
    battery_v:float
    battery_c:float
    battery_g:float
    frame_g:float
    electronics_g:float
    payload_g:float=0.0
    material:str="PLA"
    arm_length_mm:Optional[float]=None
    arm_width_mm:Optional[float]=None
    arm_thickness_mm:Optional[float]=None
    estimated:Tuple[str,...]=()
def total_mass_g(d):
    return d.frame_g+d.electronics_g+d.payload_g+d.battery_g+d.n_motors*(d.motor_g+d.prop_g)
def check_drone(d,altitude_m=0,efficiency=0.35,loaded_rpm_factor=0.6):
    if not isinstance(d.n_motors,int) or isinstance(d.n_motors,bool) or d.n_motors<=0: raise ValueError("n_motors must be a positive integer")
    for key in ("motor_thrust_g","motor_g","motor_kv","prop_diameter_mm","prop_g","battery_mah","battery_v","battery_c","battery_g","frame_g","electronics_g","payload_g"):
        v=getattr(d,key)
        if not math.isfinite(v) or v<0: raise ValueError(key+" must be finite and nonnegative")
    require_positive(battery_mah=d.battery_mah,battery_v=d.battery_v,prop_diameter_mm=d.prop_diameter_mm,efficiency=efficiency)
    if not 0<efficiency<=1 or not 0<loaded_rpm_factor<=1: raise ValueError("invalid efficiency or RPM factor")
    if not 0<=altitude_m<=11000: raise ValueError("altitude must be 0..11000 m")
    mass=total_mass_g(d)
    require_positive(mass=mass)
    thrust=d.n_motors*d.motor_thrust_g
    ratio=thrust/mass
    out=[Check("Lift margin","FAIL" if ratio<=1 else "WARN" if ratio<2 else "OK",f"estimated thrust-to-weight {ratio:.2f}:1; real lift requires measured thrust and correct propulsion setup")]
    spare=thrust/2-(mass-d.payload_g)
    out.append(Check("Payload at 2:1","OK" if spare>=0 else "WARN",f"estimated maximum total payload {max(0,spare):.1f} g at 2:1"))
    if ratio<=1:
        out.append(Check("Hover time","FAIL","hover impossible at assumed maximum thrust; no valid flight-time estimate"))
    else:
        rho=1.225*(1-2.25577e-5*altitude_m)**4.25588
        area=d.n_motors*math.pi*(d.prop_diameter_mm/2000)**2
        power=(mass/1000*G)**1.5/math.sqrt(2*rho*area)/efficiency
        current=power/d.battery_v
        mins=0.8*d.battery_mah/1000/current*60
        out.append(Check("Idealized hover endurance","WARN",f"approximately {mins:.1f} min using modeled {current:.1f} A; not a measured runtime"))
    out.append(Check("Battery rating","WARN",f"advertised nominal current {d.battery_mah/1000*d.battery_c:.1f} A; actual current, wiring, ESC and voltage sag unverified"))
    tip=d.motor_kv*d.battery_v*loaded_rpm_factor/60*math.pi*d.prop_diameter_mm/1000
    out.append(Check("Prop tip speed","WARN" if tip/343>=0.7 else "OK",f"estimated Mach {tip/343:.2f}"))
    dims=(d.arm_length_mm,d.arm_width_mm,d.arm_thickness_mm)
    if any(x is not None for x in dims):
        if not all(x is not None and x>0 for x in dims): raise ValueError("all arm dimensions must be positive if supplied")
        stress=6*(d.motor_thrust_g/1000*G)*(d.arm_length_mm/1000)/((d.arm_width_mm/1000)*(d.arm_thickness_mm/1000)**2)/1e6
        out.append(Check("Arm bending screening","WARN",f"simple cantilever stress {stress:.2f} MPa; printed strength and dynamic loads not certified"))
    if d.estimated: out.append(Check("Unverified inputs","WARN",", ".join(d.estimated)))
    return out
