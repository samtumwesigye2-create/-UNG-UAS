from dataclasses import dataclass, asdict
from uuid import uuid4
@dataclass
class Aircraft:
    id:str; callsign:str; model:str; status:str="grounded"
_aircraft={}
def register_aircraft(callsign:str, model:str):
    a=Aircraft(str(uuid4()),callsign,model); _aircraft[a.id]=a; return asdict(a)
def list_aircraft(): return [asdict(x) for x in _aircraft.values()]
