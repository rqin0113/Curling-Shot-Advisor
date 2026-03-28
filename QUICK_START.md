# 🚀 Quick Start Guide - Curling Shot Advisor v3.0

## Installation & Setup (2 minutes)

### Prerequisites
- Python 3.8+
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Step 1: Install Dependencies
```bash
pip install fastapi uvicorn
```

Or if you have requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 2: Start Backend Server
```bash
python main.py
```

You should see:
```
🥌 Starting Curling Shot Advisor API...
📍 Server will be available at: http://127.0.0.1:8000
📚 API docs available at: http://127.0.0.1:8000/docs
```

### Step 3: Open Frontend
- Open `index.html` in your web browser
- Or navigate to: `file:///path/to/index.html`

**Done! 🎉**

---

## Testing the New Features

### Test 1: Game State Tracking ✅
1. Click **"New Game"** button
2. Verify scores show 0-0
3. Verify End shows 1
4. Verify Hammer shows "Blue (You)"

**Expected**: Game state card updates

### Test 2: Stone Placement 🥌
1. Select "Blue" stone color
2. Click 5 times on the rink to place 5 blue stones
3. Select "Red" stone color
4. Click 4 times to place 4 red stones
5. Verify stone count shows Blue: 5, Red: 4

**Expected**: Stones appear on canvas

### Test 3: Smart Recommendations 🎯
1. With stones placed, click **"Get Recommendation"**
2. Green stone appears on board
3. Recommendation shows (Draw, Takeout, or Guard)
4. Shows "Strategy: position_analysis" or "strategy_database"

**Expected**: 
- For first move with no opponent stones: "Draw to Button"
- With opponent stones and no blue stones: "Takeout"
- With both having stones: "Guard"

### Test 4: Game State in Recommendations 🔄
1. Change "Current End" to 6
2. Add some blue score (e.g., click score 5)
3. Click "Get Recommendation" again
4. Response should show current_end: 6 in analysis

**Expected**: Recommendation adapts to game context

### Test 5: Recording an End ✅
1. Place some stones (any setup)
2. Enter "Blue Points: 3" and "Red Points: 0"
3. Click **"Record End & Advance"**
4. Verify:
   - Scores update to 3-0
   - End advances to 2
   - Hammer toggles to Red
   - Stones are cleared

**Expected**: All fields update correctly

### Test 6: Game Replay 🎬
1. Make 3 recommendations by:
   - Placing stones
   - Clicking "Get Recommendation"
   - Records one move automatically
   - Repeat 2 more times (don't record end, just get recommendations)
2. Look at "Game Replay" section
3. Move counter shows "3 moves recorded"
4. Click **"Next →"** button
5. Details appear for Move 1 of 3
6. Continue clicking Next to see all 3 moves
7. Click **"Previous ←"** to go back

**Expected**: 
- Can navigate through all recorded moves
- Each move shows: End, Shot, Score, Position, Time
- Move counter updates correctly

### Test 7: Clear and New Game 🔄
1. Click **"New Game"** again
2. Move counter in replay should reset to "No moves yet"
3. Stones should clear
4. Scores should be 0-0

**Expected**: Complete reset of game state

### Test 8: Strategy Database ⚙️
1. Look at server output or browser console
2. Should show "queries.json loaded successfully"
3. Make a recommendation
4. Check if `strategy_source` field shows:
   - "strategy_database" (matched queries.json)
   - "position_analysis" (no match, fell back to analysis)

**Expected**: Strategy database is working

---

## API Testing (Advanced)

### Test API Endpoints with curl

#### Start a New Game
```bash
curl -X POST http://127.0.0.1:8000/game/new
```

#### Update Game State
```bash
curl -X POST http://127.0.0.1:8000/game/update-state \
  -H "Content-Type: application/json" \
  -d '{
    "end": 3,
    "blue_score": 5,
    "red_score": 2,
    "has_hammer": true
  }'
```

#### Get Current Game
```bash
curl http://127.0.0.1:8000/game/current
```

#### Get Recommendation
```bash
curl -X POST http://127.0.0.1:8000/recommend-shot \
  -H "Content-Type: application/json" \
  -d '{
    "stones": [
      {"x": 300, "y": 300, "color": "blue"},
      {"x": 280, "y": 350, "color": "red"}
    ],
    "current_end": 3,
    "blue_score": 5,
    "red_score": 2,
    "has_hammer": true
  }'
```

#### Get Game History
```bash
curl http://127.0.0.1:8000/game/history
```

#### Check Health
```bash
curl http://127.0.0.1:8000/health
```

---

## Troubleshooting

### Problem: "Cannot place stone outside boundaries"
**Solution**: Click closer to the center of the rink

### Problem: CORS errors in browser console
**Solution**: Make sure backend is running (`python main.py`)

### Problem: "Error: Make sure the backend server is running"
**Solution**:
1. Check if terminal shows server started message
2. Verify http://127.0.0.1:8000/health returns JSON in browser
3. Restart server if needed

### Problem: Recommendations aren't using game state
**Solution**: Make sure you set End/Scores before clicking "Get Recommendation"

### Problem: No stones appear when clicking
**Solution**:
1. Verify radio button is selected (Blue or Red)
2. Make sure you're clicking inside the white rink area
3. Check browser console for JavaScript errors

### Problem: Queries.json not found error
**Solution**:
1. Verify `queries.json` is in same folder as `main.py`
2. Backend will still work but will only use position analysis
3. Check server console output

---

## Development Tips

### Enable Debug Logging
Add to `main.py` at the top:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Frontend Without Backend
Comment out the fetch call in JavaScript to test UI without server.

### Load Test Data
Pre-populate some moves by making multiple recommendations:
```javascript
// In browser console
for(let i = 0; i < 5; i++) {
  document.getElementById('recommendBtn').click();
  // Wait for response
}
```

### Check Local Storage
- Game history is stored in-memory (not persisted to disk)
- To save games, add database backend

---

## Performance Notes

- **Stone Placement**: Should be instant (<50ms)
- **Recommendation**: Should return in <100ms
- **Replay Navigation**: Should be instant (cached in memory)
- **Max Moves**: Can handle 100+ moves before slowdown

---

## Next Steps

1. ✅ Try all test cases above
2. 🎮 Play a full game (10 ends)
3. 📊 Review game history
4. 🚀 Deploy to web (see README_ENHANCED.md)
5. 🤝 Customize queries.json for your strategy

---

**Questions?** Check API docs at: http://127.0.0.1:8000/docs

**Enjoy the enhanced Curling Shot Advisor! 🥌**
