from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math
import uvicorn

app = FastAPI(title="Curling Shot Advisor API")

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

# Constants
STONE_RADIUS = 14
HOUSE_X = 300
HOUSE_Y = 150
HOUSE_RADIUS = 100

def distance(a: tuple, b: tuple) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def find_closest_free(x0: float, y0: float, stones: list[Stone]) -> tuple:
    """
    Find closest free spot near (x0, y0) avoiding overlaps.
    Uses spiral search pattern to find available space.
    """
    max_attempts = 100
    step = STONE_RADIUS * 2 + 4  # Buffer for clearance
    radius = 0
    angle_step = 30  # degrees
    
    for attempt in range(max_attempts):
        angle_rad = math.radians(angle_step * attempt)
        candidate_x = x0 + radius * math.cos(angle_rad)
        candidate_y = y0 + radius * math.sin(angle_rad)
        
        # Check if position is free and within rink bounds
        is_free = not any(
            distance((candidate_x, candidate_y), (s.x, s.y)) < STONE_RADIUS * 2 + 4 
            for s in stones
        )
        
        # Keep within rink boundaries
        in_bounds = (50 + STONE_RADIUS < candidate_x < 550 - STONE_RADIUS and 
                    STONE_RADIUS < candidate_y < 1200 - STONE_RADIUS)
        
        if is_free and in_bounds:
            return candidate_x, candidate_y
        
        # Increase radius every full rotation
        if attempt % 12 == 0:
            radius += step
    
    # Fallback to original position if no space found
    return x0, y0

def analyze_position(blues: list[Stone], reds: list[Stone]) -> dict:
    """Analyze the current stone positions and return strategic information."""
    blues_in_house = [
        s for s in blues 
        if distance((s.x, s.y), (HOUSE_X, HOUSE_Y)) <= HOUSE_RADIUS
    ]
    
    reds_in_house = [
        s for s in reds 
        if distance((s.x, s.y), (HOUSE_X, HOUSE_Y)) <= HOUSE_RADIUS
    ]
    
    # Find closest stone to button for each team
    blue_closest = min(
        blues_in_house, 
        key=lambda s: distance((s.x, s.y), (HOUSE_X, HOUSE_Y)),
        default=None
    )
    
    red_closest = min(
        reds_in_house,
        key=lambda s: distance((s.x, s.y), (HOUSE_X, HOUSE_Y)),
        default=None
    )
    
    return {
        "blues_in_house": blues_in_house,
        "reds_in_house": reds_in_house,
        "blue_closest": blue_closest,
        "red_closest": red_closest
    }

@app.post("/recommend-shot")
def recommend_shot(data: ShotRequest):
    """
    Recommend a curling shot based on current stone positions.
    
    Strategy:
    - If opponent has no stones in house: Draw to center
    - If we have no stones but opponent does: Takeout their best stone
    - If both teams have stones: Guard our best stone
    """
    try:
        blues = [s for s in data.stones if s.color == "blue"]
        reds = [s for s in data.stones if s.color == "red"]
        
        # Analyze position
        analysis = analyze_position(blues, reds)
        
        rec_x, rec_y = HOUSE_X, HOUSE_Y
        recommended_shot = "Draw"
        
        if len(analysis["reds_in_house"]) == 0:
            # Opponent has no stones in house → Draw to button
            recommended_shot = "Draw to Button"
            rec_x, rec_y = find_closest_free(HOUSE_X, HOUSE_Y, data.stones)
            
        elif len(analysis["blues_in_house"]) == 0:
            # We have no stones but opponent does → Takeout
            recommended_shot = "Takeout"
            # Target their stone closest to button
            if analysis["red_closest"]:
                target = analysis["red_closest"]
                rec_x, rec_y = target.x, target.y
            else:
                rec_x, rec_y = find_closest_free(HOUSE_X, HOUSE_Y, data.stones)
                
        else:
            # Both teams have stones → Guard our best stone
            recommended_shot = "Guard"
            # Place guard in front of house
            guard_y = HOUSE_Y + HOUSE_RADIUS + 40
            rec_x, rec_y = find_closest_free(HOUSE_X, guard_y, data.stones)
        
        return {
            "recommended_shot": recommended_shot,
            "x": rec_x,
            "y": rec_y,
            "analysis": {
                "blue_stones_in_house": len(analysis["blues_in_house"]),
                "red_stones_in_house": len(analysis["reds_in_house"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Curling Shot Advisor API"
    }

@app.get("/health")
def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "version": "2.0"
    }

if __name__ == "__main__":
    print("🥌 Starting Curling Shot Advisor API...")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("📚 API docs available at: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)