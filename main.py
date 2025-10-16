from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from schemas import Spolek, SpolekCreate
import utils

app = FastAPI(title="Evidence spolků psů")

@app.get("/spolky/", response_model=List[Spolek])
def seznam_spolku(search: Optional[str] = Query(None)):
    spolky = utils.load_spolky()
    if search:
        spolky = [s for s in spolky if search.lower() in s.nazev.lower()]
    return spolky

@app.get("/spolky/{spolek_id}", response_model=Spolek)
def detail_spolku(spolek_id: int):
    spolky = utils.load_spolky()
    spolek = utils.get_spolek_by_id(spolky, spolek_id)
    if not spolek:
        raise HTTPException(status_code=404, detail="Spolek nenalezen")
    return spolek

@app.post("/requests/", response_model=Spolek)
def vytvorit_zadost(spolek: SpolekCreate):
    requests = utils.load_requests()
    new_id = utils.get_next_id(requests)
    req = Spolek(id=new_id, **spolek.dict())
    requests.append(req)
    utils.save_requests(requests)
    return req

@app.get("/requests/", response_model=List[Spolek])
def seznam_zadosti():
    return utils.load_requests()

@app.post("/requests/{request_id}/approve", response_model=Spolek)
def schvalit_zadost(request_id: int):
    requests = utils.load_requests()
    spolky = utils.load_spolky()
    req = utils.get_spolek_by_id(requests, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Žádost nenalezena")
    new_id = utils.get_next_id(spolky)
    new_spolek = Spolek(id=new_id, **req.dict(exclude={"id"}))
    spolky.append(new_spolek)
    utils.save_spolky(spolky)
    requests = [r for r in requests if r.id != request_id]
    utils.save_requests(requests)
    return new_spolek

@app.put("/spolky/{spolek_id}", response_model=Spolek)
def upravit_spolek(spolek_id: int, updated: SpolekCreate):
    spolky = utils.load_spolky()
    spolek = utils.get_spolek_by_id(spolky, spolek_id)
    if not spolek:
        raise HTTPException(status_code=404, detail="Spolek nenalezen")
    for key, value in updated.dict().items():
        setattr(spolek, key, value)
    utils.save_spolky(spolky)
    return spolek

@app.delete("/spolky/{spolek_id}")
def smazat_spolek(spolek_id: int):
    spolky = utils.load_spolky()
    spolek = utils.get_spolek_by_id(spolky, spolek_id)
    if not spolek:
        raise HTTPException(status_code=404, detail="Spolek nenalezen")
    spolky = [s for s in spolky if s.id != spolek_id]
    utils.save_spolky(spolky)
    return {"message": "Spolek odstraněn"}

