from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math
import uvicorn
import json
from typing import Optional
from datetime import datetime

app = FastAPI(title="Curling Shot Advisor API")

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load strategy queries
def load_queries():
    try:
        with open('queries.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: queries.json not found")
        return []

STRATEGY_QUERIES = load_queries()

class Stone(BaseModel):
    x: float
    y: float
    color: str  # "blue" or "red"

class ShotRequest(BaseModel):
    stones: list[Stone]
    current_end: Optional[int] = 1
    blue_score: Optional[int] = 0
    red_score: Optional[int] = 0
    has_hammer: Optional[bool] = True

class GameState(BaseModel):
    end: int
    blue_score: int
    red_score: int
    has_hammer: bool
    
class MoveRecord(BaseModel):
    end: int
    stone_color: str
    position: dict
    recommended_shot: str
    timestamp: Optional[float] = None

# In-memory game history
game_history = {
    "current_game": None,
    "moves": [],
    "games": []
}

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
        "red_closest": red_closest,
        "blue_count": len(blues_in_house),
        "red_count": len(reds_in_house)
    }

def find_best_strategy(current_end: int, score_diff: int, has_hammer: bool) -> Optional[dict]:
    """
    Find matching strategy from queries.json based on game state.
    Returns the best matching query or None if no match found.
    """
    best_match = None
    best_score = -1
    
    for query in STRATEGY_QUERIES:
        match_score = 0
        
        # Prefer exact end matches
        if query.get("end") == current_end:
            match_score += 10
        elif abs(query.get("end", 1) - current_end) <= 2:
            match_score += 5
        
        # Match score difference
        if query.get("score_diff") == score_diff:
            match_score += 10
        elif abs(query.get("score_diff", 0) - score_diff) <= 1:
            match_score += 5
        
        # Match hammer status
        if query.get("hammer") == has_hammer:
            match_score += 10
        
        if match_score > best_score:
            best_score = match_score
            best_match = query
    
    return best_match if best_score > 0 else None

@app.post("/recommend-shot")
def recommend_shot(data: ShotRequest):
    """
    Recommend a curling shot based on current stone positions and game state.
    
    Uses queries.json strategy database + position analysis for smarter recommendations.
    
    Strategies:
    - Draw to Button: When opponent has no stones in house
    - Takeout: When we have no stones but opponent does
    - Guard: When both teams have stones (defensive play)
    """
    try:
        blues = [s for s in data.stones if s.color == "blue"]
        reds = [s for s in data.stones if s.color == "red"]
        
        # Get game context
        current_end = data.current_end or 1
        blue_score = data.blue_score or 0
        red_score = data.red_score or 0
        has_hammer = data.has_hammer if data.has_hammer is not None else True
        score_diff = blue_score - red_score
        
        # Analyze position
        analysis = analyze_position(blues, reds)
        
        # Try to find matching strategy from queries.json
        matched_strategy = find_best_strategy(current_end, score_diff, has_hammer)
        
        rec_x, rec_y = HOUSE_X, HOUSE_Y
        recommended_shot = "Draw"
        strategy_source = "position_analysis"
        
        # Use matched strategy if found
        if matched_strategy:
            recommended_shot = matched_strategy.get("shot", "Draw")
            strategy_source = "strategy_database"
            reason = matched_strategy.get("reason", "")
        else:
            # Fall back to position-based analysis
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
        
        # Record move in history
        move = {
            "end": current_end,
            "stone_color": "blue",
            "position": {"x": rec_x, "y": rec_y},
            "recommended_shot": recommended_shot,
            "blue_score": blue_score,
            "red_score": red_score,
            "has_hammer": has_hammer,
            "timestamp": datetime.now().isoformat()
        }
        game_history["moves"].append(move)
        
        return {
            "recommended_shot": recommended_shot,
            "x": rec_x,
            "y": rec_y,
            "analysis": {
                "blue_stones_in_house": len(analysis["blues_in_house"]),
                "red_stones_in_house": len(analysis["reds_in_house"]),
                "current_end": current_end,
                "score_diff": score_diff,
                "has_hammer": has_hammer
            },
            "strategy_source": strategy_source
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/game/new")
def new_game():
    """Start a new game."""
    game_history["current_game"] = {
        "start_time": datetime.now().isoformat(),
        "blue_score": 0,
        "red_score": 0,
        "current_end": 1,
        "has_hammer": True
    }
    game_history["moves"] = []
    return {"status": "Game started", "game": game_history["current_game"]}

@app.post("/game/update-state")
def update_game_state(state: GameState):
    """Update current game state (end, scores, hammer)."""
    if not game_history["current_game"]:
        game_history["current_game"] = {
            "start_time": datetime.now().isoformat(),
            "blue_score": 0,
            "red_score": 0,
            "current_end": 1,
            "has_hammer": True
        }
    
    game_history["current_game"].update({
        "blue_score": state.blue_score,
        "red_score": state.red_score,
        "current_end": state.end,
        "has_hammer": state.has_hammer
    })
    
    return {"status": "Game state updated", "game": game_history["current_game"]}

@app.get("/game/current")
def get_current_game():
    """Get current game state."""
    if not game_history["current_game"]:
        return {"status": "No active game", "game": None}
    return {
        "status": "Active game",
        "game": game_history["current_game"],
        "moves_count": len(game_history["moves"])
    }

@app.post("/game/end-end")
def end_current_end(blue_points: int = 0, red_points: int = 0):
    """Record end result and advance to next end."""
    if not game_history["current_game"]:
        raise HTTPException(status_code=400, detail="No active game")
    
    current = game_history["current_game"]
    current["blue_score"] += blue_points
    current["red_score"] += red_points
    current["current_end"] += 1
    
    # Toggle hammer
    current["has_hammer"] = not current["has_hammer"]
    
    return {
        "status": "End recorded",
        "game": current,
        "next_end": current["current_end"]
    }

@app.get("/game/history")
def get_game_history():
    """Get all moves from current game."""
    return {
        "current_game": game_history["current_game"],
        "moves": game_history["moves"],
        "total_moves": len(game_history["moves"])
    }

@app.get("/game/replay/{move_index}")
def get_move(move_index: int):
    """Get specific move from history for replay."""
    if 0 <= move_index < len(game_history["moves"]):
        return {
            "move": game_history["moves"][move_index],
            "move_number": move_index + 1,
            "total_moves": len(game_history["moves"])
        }
    raise HTTPException(status_code=404, detail="Move not found")

@app.delete("/game/clear-history")
def clear_history():
    """Clear all game history."""
    game_history["current_game"] = None
    game_history["moves"] = []
    return {"status": "History cleared"}

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Curling Shot Advisor API",
        "version": "3.0",
        "features": ["game_state_tracking", "replay", "strategy_database"]
    }

@app.get("/health")
def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "version": "3.0",
        "queries_loaded": len(STRATEGY_QUERIES),
        "active_game": game_history["current_game"] is not None,
        "recorded_moves": len(game_history["moves"])
    }
    print("🥌 Starting Curling Shot Advisor API...")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("📚 API docs available at: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)