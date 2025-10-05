# Quick Start Guide - AI Stock Trading Platform

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.8+ installed
- Node.js 14+ installed
- Git installed

### Step 1: Install Dependencies

```bash
# Backend dependencies
cd backend
pip install flask flask-cors yfinance pandas numpy python-dotenv sqlalchemy bcrypt pyjwt

# Frontend dependencies
cd ../frontend
npm install
```

### Step 2: Start Backend Server

```bash
cd backend
python api_server.py
```

✅ Server running at `http://localhost:8080`

### Step 3: Start Frontend (New Terminal)

```bash
cd frontend
npm start
```

✅ Frontend running at `http://localhost:3000`

### Step 4: Verify Everything Works

```bash
# In project root (new terminal)
python test_all_functionality.py
```

✅ All tests should pass!

---

## 📱 Features Available

### 1. AI Assistant
- Navigate to: http://localhost:3000/ai-assistant
- Ask: "What's the price of AAPL?"
- Get real-time stock predictions and analysis

### 2. Trading Bot
- Navigate to: http://localhost:3000/trading-bot
- Click "Start Bot"
- Watch it trade automatically with AI

### 3. Portfolio Management
- Navigate to: http://localhost:3000/portfolio
- Initialize with $100,000
- Buy/sell stocks
- Track performance

---

## 🔧 Troubleshooting

### Server won't start?
- Check port 8080 is free
- Install missing dependencies: `pip install -r backend/requirements.txt`

### Tests failing?
- Make sure server is running
- Check `http://localhost:8080/api/health`

### Frontend won't start?
- Delete `node_modules` and run `npm install` again
- Check port 3000 is free

---

## 📊 Test All Functionality

```bash
# Test backend API
python test_all_functionality.py

# Test mobile integration
python test_mobile_integration.py
```

---

## 🎯 Next Steps

1. **Explore the Platform**
   - Try AI Assistant
   - Start Trading Bot
   - Manage Portfolio

2. **Run Tests**
   - Verify all features work
   - Check mobile integration

3. **Deploy**
   - See TESTING_README.md for deployment guide
   - See FIXES_SUMMARY.md for details

---

## 📚 Documentation

- **Full Testing Guide:** TESTING_README.md
- **All Fixes:** FIXES_SUMMARY.md
- **API Reference:** See TESTING_README.md

---

## ✅ Production Ready

All functionality verified working:
- ✅ AI Assistant
- ✅ Trading Bot
- ✅ Portfolio Management
- ✅ Mobile Apps
- ✅ Multi-user support (Users, Agents, Admins)

**Status:** Ready for Production 🚀
