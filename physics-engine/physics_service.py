"""UNG Physics API. Run: uvicorn physics_service:app --host 0.0.0.0 --port 8080"""
import os, math, secrets
from dataclasses import asdict, fields
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from ung_system_physics import Link, Satellite, Vehicle, Shelf, check_link, check_orbit, check_vehicle, check_shelf
from drone_physics import Drone, check_drone
app=FastAPI(title="UNG-PHYSICS",version="1.0.0")
KINDS={"drone":(Drone,check_drone),"link":(Link,check_link),"orbit":(Satellite,check_orbit),"vehicle":(Vehicle,check_vehicle),"shelf":(Shelf,check_shelf)}
@app.get("/health")
def health():
    return {"ok":True,"checks":sorted(KINDS)}
@app.post("/check/{kind}")
def check(kind:str,body:dict,x_api_key:str|None=Header(default=None)):
    wanted=os.getenv("PHYSICS_API_KEY")
    if not wanted: raise HTTPException(503,"PHYSICS_API_KEY must be configured")
    if not x_api_key or not secrets.compare_digest(x_api_key,wanted): raise HTTPException(401,"unauthorized")
    if kind not in KINDS: raise HTTPException(404,"unknown check kind")
    cls,fn=KINDS[kind]
    allowed={f.name for f in fields(cls)}
    unknown=set(body)-allowed
    if unknown: raise HTTPException(422,detail={"unknown_fields":sorted(unknown)})
    for k in ("walls","estimated"):
        if k in body:
            if not isinstance(body[k],list) or not all(isinstance(v,str) for v in body[k]): raise HTTPException(422,f"{k} must be a list of strings")
            body[k]=tuple(body[k])
    try:
        checks=fn(cls(**body))
    except (TypeError,ValueError,KeyError,ZeroDivisionError,OverflowError) as exc:
        raise HTTPException(422,str(exc))
    return {"status":max((c.status for c in checks),key=lambda s:{"OK":0,"WARN":1,"FAIL":2}[s],default="OK"),"checks":[asdict(c) for c in checks]}
