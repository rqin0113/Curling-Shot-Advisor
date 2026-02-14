# 🥌 Curling Shot Advisor

An interactive web app that analyzes stone positions on a curling rink and recommends the optimal next shot: **Draw**, **Guard**, or **Takeout**.

Built because I love both coding and curling, and wanted to make strategy more accessible for players learning the game.

## ✨ Features

- **Interactive Rink**: Click to place blue and red stones on an HTML5 Canvas curling sheet
- **Smart Recommendations**: Algorithm analyzes stone positions and suggests the best shot type
- **Real-time Updates**: Dynamically displays recommended green stone placement
- **Collision Detection**: Prevents overlapping stones for realistic gameplay
- **Strategy Practice**: Experiment with different scenarios to improve curling tactics

## 🛠️ Tech Stack

- **Backend**: Python + FastAPI
- **Frontend**: JavaScript + HTML5 Canvas
- **Algorithm**: Position-based scoring using geometric calculations

## 🚀 How It Works

1. User places stones by clicking on the rink
2. Backend calculates optimal shot based on:
   - Distance to the house center
   - Blocking angles and guard positions
   - Stone clustering and defensive opportunities
3. Frontend visualizes the recommended shot placement
4. Users can reset and try different scenarios

## 🤝 Contributing

Feel free to open issues or submit pull requests if you have ideas for improvements!
