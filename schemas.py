from pydantic import BaseModel, Field
from typing import List

class SpolekBase(BaseModel):
    """Základní model spolku bez ID."""
    nazev: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Název spolku",
        example="Spolek jezevčíků Praha"
    )
    kontakt: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Kontaktní email nebo telefon",
        example="info@jezevcici.cz"
    )
    adresa: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Adresa sídla spolku",
        example="Praha 3, Žižkov"
    )
    plemeno: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Hlavní plemeno, na které se spolek specializuje",
        example="Jezevčík"
    )

class SpolekCreate(SpolekBase):
    """Model pro vytvoření nové žádosti o registraci spolku."""
    pass

class Spolek(SpolekBase):
    """Kompletní model spolku s ID."""
    id: int = Field(
        ...,
        description="Unikátní identifikátor spolku",
        example=1
    )

    class Config:
        orm_mode = True

class SpolkyList(BaseModel):
    """Model pro stránkovaný seznam spolků."""
    items: List[Spolek] = Field(
        ...,
        description="Seznam spolků na aktuální stránce"
    )
    total: int = Field(
        ...,
        description="Celkový počet spolků odpovídajících kritériím",
        example=42
    )
    page: int = Field(
        ...,
        description="Aktuální stránka (1-based)",
        example=1
    )
    pageSize: int = Field(
        ...,
        description="Počet položek na stránku",
        example=20
    )

class ErrorResponse(BaseModel):
    """Standardní chybová odpověď."""
    detail: str = Field(
        ...,
        description="Popis chyby",
        example="Spolek nenalezen"
    )
