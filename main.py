import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Asset, Location, Assignment, Audit

app = FastAPI(title="Fixed Asset Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IDModel(BaseModel):
    id: str


def to_str_id(doc: dict):
    if not doc:
        return doc
    doc["id"] = str(doc.get("_id"))
    doc.pop("_id", None)
    return doc


@app.get("/")
def read_root():
    return {"message": "Fixed Asset Management Backend Running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


# Assets
@app.post("/api/assets")
def create_asset(asset: Asset):
    try:
        inserted_id = create_document("asset", asset)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/assets")
def list_assets(q: Optional[str] = None, status: Optional[str] = None):
    try:
        filter_dict = {}
        if q:
            filter_dict["$or"] = [
                {"name": {"$regex": q, "$options": "i"}},
                {"tag": {"$regex": q, "$options": "i"}},
                {"serial_number": {"$regex": q, "$options": "i"}},
            ]
        if status:
            filter_dict["status"] = status
        docs = get_documents("asset", filter_dict, limit=100)
        return [to_str_id(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Locations
@app.post("/api/locations")
def create_location(location: Location):
    try:
        inserted_id = create_document("location", location)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/locations")
def list_locations():
    try:
        docs = get_documents("location", {}, limit=200)
        return [to_str_id(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Assignments
@app.post("/api/assignments")
def create_assignment(assignment: Assignment):
    try:
        inserted_id = create_document("assignment", assignment)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/assignments")
def list_assignments(asset_id: Optional[str] = None):
    try:
        filter_dict = {"asset_id": asset_id} if asset_id else {}
        docs = get_documents("assignment", filter_dict, limit=200)
        return [to_str_id(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Audits
@app.post("/api/audits")
def create_audit(audit: Audit):
    try:
        inserted_id = create_document("audit", audit)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/audits")
def list_audits(asset_id: Optional[str] = None):
    try:
        filter_dict = {"asset_id": asset_id} if asset_id else {}
        docs = get_documents("audit", filter_dict, limit=200)
        return [to_str_id(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
