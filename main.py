from fastapi import FastAPI, HTTPException, Query, status, Response
from typing import List, Optional
from schemas import Spolek, SpolekCreate, SpolkyList, ErrorResponse
import utils

app = FastAPI(
    title="Evidence spolku psu API",
    version="1.0.0",
    description="REST API pro spravu evidencnich spolku chovatelu psu",
    contact={
        "name": "API Support",
        "email": "support@spolky-psu.cz"
    }
)

@app.get(
    "/spolky/",
    response_model=SpolkyList,
    tags=["Spolky"],
    summary="Seznam registrovanych spolku",
    responses={
        200: {"description": "Seznam spolku uspesne nacten"},
        500: {"model": ErrorResponse, "description": "Interni chyba serveru"}
    }
)
def seznam_spolku(
    search: Optional[str] = Query(None, description="Fulltextove vyhledavani v nazvu spolku"),
    page: int = Query(1, ge=1, description="Cislo stranky (1-based)"),
    pageSize: int = Query(20, ge=1, le=100, description="Pocet polozek na stranku")
):
    """Vraci seznam vsech registrovanych spolku s moznosti vyhledavani a strankovani.
    Pristup: verejny (bez autentizace)
    """
    spolky = utils.load_spolky()
    if search:
        spolky = [s for s in spolky if search.lower() in s.nazev.lower()]
    total = len(spolky)
    start_idx = (page - 1) * pageSize
    end_idx = start_idx + pageSize
    paginated_spolky = spolky[start_idx:end_idx]
    return SpolkyList(items=paginated_spolky, total=total, page=page, pageSize=pageSize)


@app.get(
    "/spolky/{spolek_id}",
    response_model=Spolek,
    tags=["Spolky"],
    summary="Detail spolku",
    responses={
        200: {"description": "Detail spolku uspesne nacten"},
        404: {"model": ErrorResponse, "description": "Spolek nenalezen"},
        500: {"model": ErrorResponse, "description": "Interni chyba serveru"}
    }
)
def detail_spolku(spolek_id: int):
    """Vraci detailni informace o konkretnim spolku."""
    spolky = utils.load_spolky()
    spolek = utils.get_spolek_by_id(spolky, spolek_id)
    if not spolek:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spolek nenalezen")
    return spolek


@app.post(
    "/requests/",
    response_model=Spolek,
    status_code=status.HTTP_201_CREATED,
    tags=["Zadosti"],
    summary="Vytvorit zadost o registraci",
    responses={
        201: {"description": "Zadost uspesne vytvorena"},
        400: {"model": ErrorResponse, "description": "Validacni chyba"},
        409: {"model": ErrorResponse, "description": "Konflikt - duplicitni nazev"},
        500: {"model": ErrorResponse, "description": "Interni chyba serveru"}
    }
)
def vytvorit_zadost(spolek: SpolekCreate, response: Response):
    """Vytvori novou zadost o registraci spolku do evidence."""
    requests = utils.load_requests()
    existing = [r for r in requests if r.nazev.lower() == spolek.nazev.lower()]
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Zadost se stejnym nazvem jiz existuje")
    new_id = utils.get_next_id(requests)
    req = Spolek(id=new_id, **spolek.dict())
    requests.append(req)
    utils.save_requests(requests)
    response.headers["Location"] = f"/requests/{new_id}"
    return req


@app.get(
    "/requests/",
    response_model=List[Spolek],
    tags=["Zadosti"],
    summary="Seznam zadosti o registraci",
    responses={
        200: {"description": "Seznam zadosti uspesne nacten"},
        500: {"model": ErrorResponse, "description": "Interni chyba serveru"}
    }
)
def seznam_zadosti():
    """Vraci vse cekajici zadosti o registraci novych spolku."""
    return utils.load_requests()


@app.post(
    "/requests/{request_id}/approve",
    response_model=Spolek,
    status_code=status.HTTP_201_CREATED,
    tags=["Zadosti"],
    summary="Schvalit zadost",
    responses={
        201: {"description": "Zadost schvalena a spolek zaregistrovan"},
        404: {"model": ErrorResponse, "description": "Zadost nenalezena"},
        500: {"model": ErrorResponse, "description": "Interni chyba serveru"}
    }
)
def schvalit_zadost(request_id: int, response: Response):
    """Schvali zadost a prevede ji do evidence registrovanych spolku."""
    requests = utils.load_requests()
    spolky = utils.load_spolky()
    req = utils.get_spolek_by_id(requests, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zadost nenalezena")
    new_id = utils.get_next_id(spolky)
    new_spolek = Spolek(id=new_id, **req.dict(exclude={"id"}))
    spolky.append(new_spolek)
    utils.save_spolky(spolky)
    requests = [r for r in requests if r.id != request_id]
    utils.save_requests(requests)
    response.headers["Location"] = f"/spolky/{new_id}"
    return new_spolek


@app.put(
    "/spolky/{spolek_id}",
    response_model=Spolek,
    tags=["Spolky"],
    summary="Upravit spolek",
    responses={
        200: {"description": "Spolek uspesne aktualizovan"},
        404: {"model": ErrorResponse, "description": "Spolek nenalezen"},
        500: {"model": ErrorResponse, "description": "Interni chyba serveru"}
    }
)
def upravit_spolek(spolek_id: int, updated: SpolekCreate):
    """Aktualizuje informace o existujicim spolku."""
    spolky = utils.load_spolky()
    spolek = utils.get_spolek_by_id(spolky, spolek_id)
    if not spolek:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spolek nenalezen")
    for key, value in updated.dict().items():
        setattr(spolek, key, value)
    utils.save_spolky(spolky)
    return spolek


@app.delete(
    "/spolky/{spolek_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Spolky"],
    summary="Smazat spolek",
    responses={
        204: {"description": "Spolek uspesne odstranen"},
        404: {"model": ErrorResponse, "description": "Spolek nenalezen"},
        500: {"model": ErrorResponse, "description": "Interni chyba serveru"}
    }
)
def smazat_spolek(spolek_id: int):
    """Odstrani spolek z evidence."""
    spolky = utils.load_spolky()
    spolek = utils.get_spolek_by_id(spolky, spolek_id)
    if not spolek:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spolek nenalezen")
    spolky = [s for s in spolky if s.id != spolek_id]
    utils.save_spolky(spolky)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

