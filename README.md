# ⚽ Football League Simulator

A Python simulation of the English football league pyramid:

**Premier League → Championship → League One → League Two**

This project simulates multi-season league progression with promotion, relegation, club reputation dynamics and random real-world style events.

---

## ✨ Features

### 🏆 League System
- 4-tier English football pyramid
- Promotion & relegation between leagues
- Championship / League One / League Two playoffs

### 📈 Club Reputation System
Each club has a dynamic **reputation rating** that affects performance.

Reputation changes based on:
- League performance
- Promotion / relegation
- Random events

### 💰 Random Football World Events
The simulation includes chaotic real-world style events:

- Middle Eastern takeovers  
- Big club meltdowns  
- Squad poaching from smaller clubs  
- Rise of new powerhouse clubs  

Every season feels different and unpredictable.

### 📊 Long-term Tracking
The simulator tracks league rankings of:
- Big 6 clubs
- Mid-table clubs
- Custom tracked clubs

At the end of simulation, a ranking history graph is generated.

---

## 🖼 Example Output

After running multiple seasons, the script generates a chart showing ranking changes across seasons.

---

## 🛠 Requirements

Install dependencies:

```bash
pip install numpy pandas matplotlib
```
## ▶️ How to Run

1️⃣ Install dependencies

```bash
pip install numpy pandas matplotlib
```
2️⃣ Run the simulator
```bash
python main.py
```
The script will automatically:

- Simulate multiple seasons
- Apply promotion & relegation
- Update club reputations
- Generate a ranking history chart
