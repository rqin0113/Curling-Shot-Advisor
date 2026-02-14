# 🥌 Curling Shot Advisor

An interactive web application that provides strategic shot recommendations for curling games.

## ✨ Improvements Made

### Visual Design
- **Modern gradient background** with purple theme
- **Improved stone appearance** with shadows and highlights
- **Better rink visualization** with labeled house and hog lines
- **Responsive layout** that works on different screen sizes
- **Professional color scheme** matching curling aesthetics
- **Smooth animations** for user feedback
- **Stone counter** showing number of each color placed

### User Experience
- **Radio buttons** for stone color selection (no more prompts!)
- **Clear button** to reset the board
- **Better error messages** with auto-dismiss
- **Visual feedback** for all actions
- **Boundary checking** - can't place stones outside rink
- **Overlap detection** improved
- **Instructions card** built into the interface
- **Loading states** when getting recommendations

### Technical Improvements

#### Frontend (index.html)
- Added viewport meta tag for mobile responsiveness
- Improved stone rendering with gradients and shadows
- Better canvas interaction with hover effects
- Removed previous recommendation stones before adding new ones
- Added boundary validation
- Better error handling with try-catch
- Stone counter updates automatically

#### Backend (main.py)
- Added proper type hints and documentation
- Better error handling with HTTPException
- Improved spiral search algorithm for stone placement
- Added health check endpoints (`/` and `/health`)
- Better strategic analysis with position evaluation
- More defensive programming with default values
- Added uvicorn server configuration
- Console messages when server starts

#### CSS (style.css)
- Mobile responsive design with media queries
- Modern CSS Grid and Flexbox layouts
- Smooth transitions and animations
- Accessibility improvements
- Better color contrast
- Professional button styles with hover effects

## 🚀 How to Run

### Backend
```bash
python main.py
```
Server starts at: http://127.0.0.1:8000

### Frontend
Simply open `index.html` in your web browser.

## 📋 How to Use

1. **Select stone color** using the radio buttons (Blue = you, Red = opponent)
2. **Click on the rink** to place stones
3. **Click "Get Recommendation"** to see the suggested shot
4. **Green stone** shows where you should aim
5. **Clear All Stones** button resets the board

## 🎯 Shot Strategies

The advisor recommends three main shot types:

- **Draw to Button**: When opponent has no stones in the house
- **Takeout**: When they have stones but you don't - removes their best stone
- **Guard**: When both teams have stones - protects your position

## 🐛 Bug Fixes

1. Fixed overlapping stone detection
2. Added boundary checking for stone placement
3. Improved recommendation stone handling (removes old ones)
4. Better error messages when server is offline
5. Fixed coordinate system consistency
6. Prevented stones from being placed outside rink boundaries

## 📦 Files

- `index.html` - Main application interface
- `style.css` - All styling and animations
- `main.py` - FastAPI backend server
- `queries.json` - (Not currently used in main logic)

## 🔧 Technologies Used

- **Frontend**: HTML5 Canvas, Vanilla JavaScript
- **Backend**: Python, FastAPI
- **Styling**: CSS3 with Flexbox/Grid

## 📝 Future Enhancements

- Add end/score tracking
- Implement hammer logic
- Add more shot types (freeze, peel, etc.)
- Save/load game states
- Multiplayer support
- Shot power/curl visualization