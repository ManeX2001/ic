# MIMIC-Enhanced Hospital Management System

A Flask-based hospital management application with deep learning capabilities and real MIMIC dataset integration.

## Quick Start

### Step 1: Navigate to the project directory
```bash
cd routes
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the application
```bash
python simple_hospital_app.py
```

### Step 4: Open the website
Once you see the message "Running on http://127.0.0.1:5000", open your web browser and go to:

**http://localhost:5000**

## What You'll See

When the app starts, you'll see initialization messages like:
```
🔄 Initializing MIMIC-Enhanced Hospital System with Deep Learning...
📊 Loading MIMIC dataset...
✅ Loading PATIENTS.csv...
✅ Loading ICUSTAYS.csv...
🏥 MIMIC-INTEGRATED HOSPITAL AI STARTING...
🌐 Access: http://localhost:5000
```

## Available Features

- **Dashboard** - Hospital overview with real MIMIC data
- **Bed Management** - ICU, Ward, and ED capacity management  
- **Deep Learning** - AI-powered hospital optimization
- **Analytics** - MIMIC dataset insights and predictions
- **Discharge Recommendations** - Patient discharge planning

## Requirements

- Python 3.12+
- Flask 2.3.3
- MIMIC dataset files (automatically loaded from `/data/dataset Updated/`)

## Stopping the Application

Press `Ctrl+C` in the terminal to stop the server.

## Troubleshooting

**Problem**: Can't access the website
- **Solution**: Make sure the terminal shows "Running on http://127.0.0.1:5000" before opening the browser

**Problem**: "low >= high" errors during startup  
- **Solution**: These are normal and don't affect functionality - the app will still work

**Problem**: Port already in use
- **Solution**: Stop any other applications running on port 5000, or change the port in the code