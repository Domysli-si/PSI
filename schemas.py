from pydantic import BaseModel

class SpolekBase(BaseModel):
    nazev: str
    kontakt: str
    adresa: str
    plemeno: str

class SpolekCreate(SpolekBase):
    pass

class Spolek(SpolekBase):
    id: int

    class Config:
        orm_mode = True

