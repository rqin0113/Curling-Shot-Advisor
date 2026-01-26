from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Stone(BaseModel):
    x: float
    y: float
    color: str  # "blue" or "red"

class ShotRequest(BaseModel):
    stones: list[Stone]

stone_radius = 14
house_x = 300
house_y = 150
house_radius = 100

def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def find_closest_free(x0, y0, stones):
    """Find closest free spot near (x0, y0) avoiding overlaps"""
    max_attempts = 50
    step = stone_radius*2 + 2
    radius = 0
    angle_step = 15
    for attempt in range(max_attempts):
        rad = math.radians(angle_step * attempt)
        candidate_x = x0 + radius * math.cos(rad)
        candidate_y = y0 + radius * math.sin(rad)
        if not any(distance((candidate_x, candidate_y), (s.x, s.y)) < stone_radius*2+2 for s in stones):
            return candidate_x, candidate_y
        if attempt % 24 == 0:
            radius += step
    return x0, y0  # fallback

@app.post("/recommend-shot")
def recommend_shot(data: ShotRequest):
    blues = [s for s in data.stones if s.color=="blue"]
    reds = [s for s in data.stones if s.color=="red"]

    # Opponent stones in house
    reds_in_house = [s for s in reds if distance((s.x, s.y), (house_x, house_y)) <= house_radius]
    blues_in_house = [s for s in blues if distance((s.x, s.y), (house_x, house_y)) <= house_radius]

    rec_x, rec_y = house_x, house_y

    if len(reds_in_house) == 0:
        # Button open → Draw
        recommended_shot = "Draw"
        rec_x, rec_y = find_closest_free(house_x, house_y, data.stones)

    else:
        if len(blues_in_house) == 0:
            # Takeout
            recommended_shot = "Takeout"
            target = min(reds_in_house, key=lambda s: distance((s.x, s.y), (house_x, house_y)))
            rec_x, rec_y = target.x, target.y
        else:
            # Guard
            recommended_shot = "Guard"
            rec_x, rec_y = house_x, house_y - 50
            rec_x, rec_y = find_closest_free(rec_x, rec_y, data.stones)

    return {
        "recommended_shot": recommended_shot,
        "x": rec_x,
        "y": rec_y
    }