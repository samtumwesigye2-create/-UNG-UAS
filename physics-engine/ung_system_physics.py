"""UNG shared physics checks. SI units unless indicated. Standard library only."""
import math
from dataclasses import dataclass
G=9.80665
C=299792458.0
GM=6.674e-11*5.972e24
R=6371000.0
WALL={"drywall":3,"glass":3,"wood":4,"brick":8,"concrete":12,"metal":20}
MU={"dry":0.7,"wet":0.4,"gravel":0.35,"mud":0.2}
@dataclass
class Check:
    name:str
    status:str
    message:str
def report(title,checks):
    checks=list(checks)
    return "\n".join([title,"-"*len(title)]+[f"[{c.status}] {c.name}: {c.message}" for c in checks]+["Overall: "+max((c.status for c in checks),key=lambda s:{"OK":0,"WARN":1,"FAIL":2}[s],default="OK")])
def require_positive(**values):
    for k,v in values.items():
        if not math.isfinite(v) or v<=0: raise ValueError(f"{k} must be positive and finite")
@dataclass
class Link:
    name:str
    tx_dbm:float
    rx_sensitivity_dbm:float
    freq_hz:float
    distance_m:float
    walls:tuple=()
    gains_db:float=0.0
    margin_needed_db:float=10.0
def check_link(l):
    require_positive(freq_hz=l.freq_hz,distance_m=l.distance_m)
    if l.margin_needed_db<0: raise ValueError("margin must not be negative")
    loss=sum(WALL[w] for w in l.walls)
    fspl=20*math.log10(4*math.pi*l.distance_m*l.freq_hz/C)
    rx=l.tx_dbm+l.gains_db-fspl-loss
    margin=rx-l.rx_sensitivity_dbm
    reach=C/(4*math.pi*l.freq_hz)*10**((l.tx_dbm+l.gains_db-loss-l.rx_sensitivity_dbm-l.margin_needed_db)/20)
    status="FAIL" if margin<0 else "WARN" if margin<l.margin_needed_db else "OK"
    return [Check("Signal strength",status,f"estimated receive {rx:.1f} dBm; margin {margin:.1f} dB; wall loss {loss} dB"),Check("Modeled range","OK" if reach>=l.distance_m else "WARN",f"idealized range with margin: {reach:.0f} m; not a reliability guarantee"),Check("Wavelength","OK",f"{C/l.freq_hz*100:.2f} cm")]
@dataclass
class Satellite:
    name:str
    altitude_km:float
    claimed_period_min:float=0.0
def check_orbit(s):
    if s.altitude_km<0: raise ValueError("altitude must be nonnegative")
    r=R+s.altitude_km*1000
    speed=math.sqrt(GM/r)/1000
    period=2*math.pi*math.sqrt(r**3/GM)/60
    out=[Check("Circular orbit","OK",f"ideal circular speed {speed:.2f} km/s; period {period:.1f} min")]
    if s.claimed_period_min:
        require_positive(claimed_period_min=s.claimed_period_min)
        off=abs(period-s.claimed_period_min)/period
        out.append(Check("Period matches","OK" if off<0.02 else "FAIL",f"claimed {s.claimed_period_min:.1f} vs calculated {period:.1f} min"))
    return out
@dataclass
class Vehicle:
    name:str
    empty_kg:float
    max_payload_kg:float
    load_kg:float
    speed_kmh:float
    road:str="dry"
    clear_distance_m:float=50.0
    trip_km:float=0.0
def check_vehicle(v):
    if min(v.empty_kg,v.max_payload_kg,v.load_kg,v.speed_kmh,v.clear_distance_m,v.trip_km)<0: raise ValueError("negative vehicle input")
    mu=MU[v.road]
    speed=v.speed_kmh/3.6
    braking=speed**2/(2*mu*G)
    reaction=1.5*speed
    stopping=braking+reaction
    load_status="FAIL" if v.load_kg>v.max_payload_kg else "WARN" if v.load_kg>0.9*v.max_payload_kg else "OK"
    stop_status="FAIL" if stopping>v.clear_distance_m else "WARN" if stopping>0.7*v.clear_distance_m else "OK"
    out=[Check("Load",load_status,f"{v.load_kg:.0f}/{v.max_payload_kg:.0f} kg"),Check("Stopping estimate",stop_status,f"{stopping:.1f} m including 1.5 s reaction, {braking:.1f} m braking; idealized friction")]
    if v.trip_km:
        out.append(Check("Ideal travel time","WARN" if speed==0 else "OK","undefined at zero speed" if speed==0 else f"{60*v.trip_km/v.speed_kmh:.0f} min excluding delays"))
    return out
@dataclass
class Shelf:
    name:str
    shelf_rating_kg:float
    stock_kg:float
    floor_rating_kg_m2:float=0.0
    footprint_m2:float=0.0
    stack_height_m:float=0.0
    base_width_m:float=0.0
def check_shelf(s):
    if min(s.shelf_rating_kg,s.stock_kg,s.floor_rating_kg_m2,s.footprint_m2,s.stack_height_m,s.base_width_m)<0: raise ValueError("negative shelf input")
    out=[Check("Shelf load","FAIL" if s.stock_kg>s.shelf_rating_kg else "WARN" if s.stock_kg>0.9*s.shelf_rating_kg else "OK",f"{s.stock_kg:.0f}/{s.shelf_rating_kg:.0f} kg; verify rack rating and load distribution")]
    if s.floor_rating_kg_m2 and s.footprint_m2:
        p=s.stock_kg/s.footprint_m2
        out.append(Check("Average floor load","FAIL" if p>s.floor_rating_kg_m2 else "WARN",f"{p:.0f} vs {s.floor_rating_kg_m2:.0f} kg/m²; concentrated leg loads not assessed"))
    if s.stack_height_m and s.base_width_m:
        ratio=s.stack_height_m/s.base_width_m
        out.append(Check("Tip-over screening","WARN",f"height/base {ratio:.2f}; anchoring and center of gravity not assessed"))
    return out
