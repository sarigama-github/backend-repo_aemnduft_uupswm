import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson.objectid import ObjectId

from database import db

app = FastAPI(title="TechVista HR Document Access System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------- Utilities ---------------------

def serialize_doc(doc: dict) -> dict:
    if not doc:
        return {}
    d = {**doc}
    d["id"] = str(d.pop("_id"))
    return d


def parse_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document id")


# --------------------- Models ---------------------

class FavoriteCreate(BaseModel):
    user_id: str
    document_id: str
    note: Optional[str] = None


class BookmarkCreate(BaseModel):
    name: str
    owner: str
    document_id: str
    shared: bool = False


# --------------------- Seed Data ---------------------

def seed_if_empty():
    if db is None:
        return
    docs = db["document"].count_documents({})
    if docs > 0:
        return

    examples = [
        {
            "title": "Employee Handbook",
            "doc_type": "Policies",
            "departments": ["Operations", "HR"] if "HR" in ["Operations"] else ["Operations"],
            "last_updated": datetime(2025, 10, 2),
            "version": "v3.2",
            "latest": True,
            "size_kb": 120,
            "format": "PDF",
            "canonical_id": "employee-handbook",
            "download_url": "https://example.com/docs/employee-handbook-v3-2.pdf",
        },
        {
            "title": "PTO Request Form",
            "doc_type": "Forms",
            "departments": ["Operations"],
            "last_updated": datetime(2025, 7, 14),
            "version": "v2.1",
            "latest": True,
            "size_kb": 48,
            "format": "PDF",
            "canonical_id": "pto-request-form",
            "download_url": "https://example.com/docs/pto-request-form-v2-1.pdf",
        },
        {
            "title": "Performance Review Template",
            "doc_type": "Templates",
            "departments": ["Design", "Engineering"],
            "last_updated": datetime(2025, 3, 9),
            "version": "v1.8",
            "latest": True,
            "size_kb": 96,
            "format": "DOCX",
            "canonical_id": "performance-review-template",
            "download_url": "https://example.com/docs/performance-review-template-v1-8.docx",
        },
        {
            "title": "Remote Work Policy",
            "doc_type": "Policies",
            "departments": ["Engineering", "Design", "Marketing"],
            "last_updated": datetime(2025, 6, 1),
            "version": "v2.0",
            "latest": True,
            "size_kb": 85,
            "format": "PDF",
            "canonical_id": "remote-work-policy",
            "download_url": "https://example.com/docs/remote-work-policy-v2-0.pdf",
        },
        {
            "title": "Offer Letter Template",
            "doc_type": "Templates",
            "departments": ["Operations", "Finance"],
            "last_updated": datetime(2025, 9, 10),
            "version": "v4.0",
            "latest": True,
            "size_kb": 64,
            "format": "DOCX",
            "canonical_id": "offer-letter-template",
            "download_url": "https://example.com/docs/offer-letter-template-v4-0.docx",
        },
        {
            "title": "Exit Interview Checklist",
            "doc_type": "Checklists",
            "departments": ["Operations"],
            "last_updated": datetime(2024, 12, 5),
            "version": "v1.2",
            "latest": True,
            "size_kb": 33,
            "format": "PDF",
            "canonical_id": "exit-interview-checklist",
            "download_url": "https://example.com/docs/exit-interview-checklist-v1-2.pdf",
        },
        {
            "title": "Benefits Enrollment Guide",
            "doc_type": "Guides",
            "departments": ["Operations", "Finance"],
            "last_updated": datetime(2025, 5, 22),
            "version": "v3.0",
            "latest": True,
            "size_kb": 220,
            "format": "PDF",
            "canonical_id": "benefits-enrollment-guide",
            "download_url": "https://example.com/docs/benefits-enrollment-guide-v3-0.pdf",
        },
        {
            "title": "Expense Reimbursement Form",
            "doc_type": "Forms",
            "departments": ["Finance"],
            "last_updated": datetime(2025, 8, 2),
            "version": "v2.4",
            "latest": True,
            "size_kb": 41,
            "format": "XLSX",
            "canonical_id": "expense-reimbursement-form",
            "download_url": "https://example.com/docs/expense-reimbursement-form-v2-4.xlsx",
        },
        {
            "title": "Salary Increase Form",
            "doc_type": "Forms",
            "departments": ["Finance", "Operations"],
            "last_updated": datetime(2025, 9, 29),
            "version": "v1.5",
            "latest": True,
            "size_kb": 57,
            "format": "DOCX",
            "canonical_id": "salary-increase-form",
            "download_url": "https://example.com/docs/salary-increase-form-v1-5.docx",
        },
        {
            "title": "Job Description Templates",
            "doc_type": "Templates",
            "departments": ["Operations", "Design", "Marketing", "Sales"],
            "last_updated": datetime(2025, 2, 11),
            "version": "v1.0",
            "latest": True,
            "size_kb": 75,
            "format": "DOCX",
            "canonical_id": "job-description-templates",
            "download_url": "https://example.com/docs/job-description-templates-v1-0.docx",
        },
    ]
    if docs == 0:
        db["document"].insert_many(examples)


@app.on_event("startup")
async def on_startup():
    try:
        seed_if_empty()
    except Exception:
        pass


# --------------------- Routes ---------------------

@app.get("/")
def root():
    return {"message": "TechVista HR Document Access API"}


@app.get("/api/suggested")
def suggested():
    return {
        "suggested_types": ["Policies", "Forms", "Guides", "Templates", "Checklists"],
        "suggested_departments": [
            "Engineering",
            "Sales",
            "Marketing",
            "Operations",
            "Finance",
            "Customer Support",
            "Design",
        ],
    }


@app.get("/api/recents")
def recents(limit: int = 10):
    items = list(db["document"].find({}).sort("last_updated", -1).limit(limit))
    return [serialize_doc(x) for x in items]


@app.get("/api/documents")
def search_documents(
    q: Optional[str] = Query(None, description="Free text query on title"),
    doc_type: Optional[str] = None,
    departments: Optional[str] = Query(None, description="Comma separated departments"),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    sort: str = Query("relevance", enum=["relevance", "last_updated"]),
    limit: int = 50,
):
    filt = {}
    if q:
        filt["title"] = {"$regex": q, "$options": "i"}
    if doc_type:
        filt["doc_type"] = doc_type
    if departments:
        dept_list = [d.strip() for d in departments.split(",") if d.strip()]
        if dept_list:
            filt["departments"] = {"$in": dept_list}
    if date_from or date_to:
        rng = {}
        if date_from:
            try:
                rng["$gte"] = datetime.fromisoformat(date_from)
            except Exception:
                pass
        if date_to:
            try:
                rng["$lte"] = datetime.fromisoformat(date_to)
            except Exception:
                pass
        if rng:
            filt["last_updated"] = rng

    cursor = db["document"].find(filt)
    if sort == "last_updated":
        cursor = cursor.sort("last_updated", -1)
    else:
        # basic relevance: prefer title regex match already applied; keep as is
        pass

    cursor = cursor.limit(min(250, max(1, limit)))
    return [serialize_doc(x) for x in cursor]


@app.get("/api/documents/{doc_id}")
def get_document(doc_id: str):
    doc = db["document"].find_one({"_id": parse_object_id(doc_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return serialize_doc(doc)


@app.get("/api/canonical/{canonical_id}/latest")
def get_latest_by_canonical(canonical_id: str):
    doc = db["document"].find_one({"canonical_id": canonical_id, "latest": True})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return serialize_doc(doc)


@app.post("/api/favorites")
def add_favorite(payload: FavoriteCreate):
    # ensure document exists
    parse_object_id(payload.document_id)
    if not db["document"].find_one({"_id": ObjectId(payload.document_id)}):
        raise HTTPException(status_code=404, detail="Document not found")
    fav = {
        "user_id": payload.user_id,
        "document_id": payload.document_id,
        "note": payload.note,
        "created_at": datetime.utcnow(),
    }
    db["favorite"].update_one(
        {"user_id": payload.user_id, "document_id": payload.document_id},
        {"$set": fav},
        upsert=True,
    )
    return {"status": "ok"}


@app.get("/api/favorites")
def list_favorites(user_id: str):
    favs = list(db["favorite"].find({"user_id": user_id}).sort("created_at", -1))
    # expand document meta
    results = []
    for f in favs:
        doc = db["document"].find_one({"_id": ObjectId(f["document_id"])})
        if doc:
            item = serialize_doc(doc)
            item["saved_at"] = f.get("created_at")
            results.append(item)
    return results


@app.post("/api/bookmarks")
def add_bookmark(payload: BookmarkCreate):
    # ensure document exists
    parse_object_id(payload.document_id)
    if not db["document"].find_one({"_id": ObjectId(payload.document_id)}):
        raise HTTPException(status_code=404, detail="Document not found")
    bm = {
        "name": payload.name,
        "owner": payload.owner,
        "document_id": payload.document_id,
        "shared": payload.shared,
        "created_at": datetime.utcnow(),
    }
    db["bookmark"].insert_one(bm)
    return {"status": "ok"}


@app.get("/api/bookmarks")
def list_bookmarks(owner: Optional[str] = None, shared: Optional[bool] = None):
    filt = {}
    if owner:
        filt["owner"] = owner
    if shared is not None:
        filt["shared"] = shared
    items = list(db["bookmark"].find(filt).sort("created_at", -1))
    results = []
    for b in items:
        doc = db["document"].find_one({"_id": ObjectId(b["document_id"])})
        if doc:
            item = serialize_doc(doc)
            item["bookmark"] = {
                "name": b.get("name"),
                "owner": b.get("owner"),
                "shared": b.get("shared", False),
                "created_at": b.get("created_at"),
            }
            results.append(item)
    return results


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
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            collections = db.list_collection_names()
            response["collections"] = collections[:10]
            response["database"] = "✅ Connected & Working"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
