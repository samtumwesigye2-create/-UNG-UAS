from fastapi import FastAPI
SYSTEM_ID="UNG-HORUS"; LEGACY_ID="UNG-UAS"; VERSION="0.1.0"
app=FastAPI(title=SYSTEM_ID,version=VERSION,description="Uganda National Grid Uncrewed Aircraft and Aerial Operations System")
@app.get("/")
def root(): return {"system":SYSTEM_ID,"legacy_id":LEGACY_ID,"status":"foundation-online","version":VERSION}
@app.get("/health")
def health(): return {"status":"ok","service":SYSTEM_ID,"version":VERSION}
@app.get("/ready")
def ready(): return {"status":"ready","service":SYSTEM_ID}
@app.get("/v1/system")
def system_contract(): return {"system_id":SYSTEM_ID,"legacy_id":LEGACY_ID,"domain":"uas-aerial-operations","iam":"UNG-JANUS","control_plane":"UNG-ATLAS"}
