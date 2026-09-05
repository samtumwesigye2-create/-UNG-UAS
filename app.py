from fastapi import FastAPI,Header,HTTPException
from pydantic import BaseModel
from domain import register_aircraft,list_aircraft
from integration import dependencies
SYSTEM_ID="UNG-HORUS"; LEGACY_ID="UNG-UAS"; VERSION="0.2.0"
app=FastAPI(title=SYSTEM_ID,version=VERSION,description="UNG Uncrewed Aircraft and Aerial Operations System")
class AircraftIn(BaseModel): callsign:str; model:str
def auth(p,h):
 s={x.strip() for x in (h or "").split(",") if x.strip()}
 if p not in s and "ung.admin" not in s: raise HTTPException(403,"UNG-JANUS permission required")
@app.get("/")
def root(): return {"system":SYSTEM_ID,"legacy_id":LEGACY_ID,"status":"online","version":VERSION}
@app.get("/health")
def health(): return {"status":"ok","service":SYSTEM_ID,"version":VERSION}
@app.get("/ready")
def ready(): return {"status":"ready","service":SYSTEM_ID,"dependencies":dependencies()}
@app.get("/v1/system")
def system(): return {"system_id":SYSTEM_ID,"legacy_id":LEGACY_ID,"domain":"uas-aerial-operations","dependencies":dependencies()}
@app.get("/v1/aircraft")
def aircraft(x_ung_permissions:str|None=Header(None)): auth("horus.aircraft.read",x_ung_permissions); return list_aircraft()
@app.post("/v1/aircraft",status_code=201)
def register(body:AircraftIn,x_ung_permissions:str|None=Header(None)): auth("horus.aircraft.register",x_ung_permissions); return register_aircraft(body.callsign,body.model)
