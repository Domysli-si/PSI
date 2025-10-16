import json
from pathlib import Path
from typing import List, Optional
from schemas import Spolek

DATA_FILE = Path("./spolky.json")
REQUESTS_FILE = Path("./requests.json")

def load_spolky() -> List[Spolek]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Spolek(**item) for item in data]

def save_spolky(spolky: List[Spolek]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([s.dict() for s in spolky], f, ensure_ascii=False, indent=4)

def load_requests() -> List[Spolek]:
    if not REQUESTS_FILE.exists():
        return []
    with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Spolek(**item) for item in data]

def save_requests(requests: List[Spolek]):
    with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
        json.dump([r.dict() for r in requests], f, ensure_ascii=False, indent=4)

def get_spolek_by_id(spolky: List[Spolek], spolek_id: int) -> Optional[Spolek]:
    for s in spolky:
        if s.id == spolek_id:
            return s
    return None

def get_next_id(spolky: List[Spolek]) -> int:
    if not spolky:
        return 1
    return max(s.id for s in spolky) + 1

