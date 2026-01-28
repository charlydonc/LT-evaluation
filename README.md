# 📊 Lactate Threshold Calculator

Professional web application for calculating LT1 (aerobic threshold) and LT2 (anaerobic threshold) from exercise test data.

![Flask](https://img.shields.io/badge/Flask-3.0-blue)
![Python](https://img.shields.io/badge/Python-3.11-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- **🔬 Scientifically Accurate Methods**
  - **LT1:** Log-Log Transformation with Segmented Regression
  - **LT2:** Modified Dmax Method
- **📊 Multiple File Comparison** - Upload multiple tests and track progress over time
- **📈 Beautiful Visualizations** - Smooth lactate curves with threshold markers
- **📉 Progress Tracking** - Automatic calculation of improvements between consecutive tests
- **🎨 Modern UI** - Clean, professional interface with drag & drop support

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/charlydonc/LT-evalutation.git
cd LT-evalutation

# Install dependencies
pip install -r requirements.txt

# Run the application
python flask_app.py
```

Visit `http://localhost:8501` in your browser.

## 🌐 Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed instructions on deploying to Render.com (free hosting).

### Quick Deploy to Render

1. Push this repo to GitHub
2. Sign up at [render.com](https://render.com)
3. Create new Web Service from your GitHub repo
4. Render auto-detects settings from `Procfile`
5. Deploy! 🚀

## 📖 Usage

### Upload CSV Files

Your CSV file must contain:
- `watts` (or `power`) - Power output in watts
- `lactate` - Blood lactate concentration in mmol/L
- `rpe` (optional) - Rating of Perceived Exertion

Example format:
```csv
watts,lactate,rpe
200,1.2,2
220,1.4,3
240,1.8,4
260,2.5,5
280,4.1,7
300,5.8,9
```

### Multiple File Comparison

Upload multiple CSV files (named with dates like `test_2024-01-15.csv`) to:
- Compare results side-by-side
- Track progress over time
- See improvement indicators between tests

## 🧪 Technical Details

### LT1 Calculation (Log-Log Method)
1. Log-transforms power and lactate data
2. Performs segmented linear regression
3. Identifies breakpoint where lactate starts rising
4. Back-transforms to watts

### LT2 Calculation (Modified Dmax)
1. Fits 3rd-order polynomial to lactate curve
2. Identifies start point (before first rise >0.4 mmol/L)
3. Calculates maximum perpendicular distance from secant line
4. Solves quadratic equation for threshold power

See [MODEL_DOCUMENTATION.md](MODEL_DOCUMENTATION.md) for complete mathematical specification.

## 📁 Project Structure

```
LT-evalutation/
├── flask_app.py              # Main Flask application
├── lt_calculator.py          # Threshold calculation logic
├── templates/
│   └── index.html           # Web interface
├── MODEL_DOCUMENTATION.md   # Technical specification
├── DEPLOYMENT.md            # Deployment guide
├── requirements.txt         # Python dependencies
├── Procfile                 # Render.com config
├── runtime.txt             # Python version
└── test_*.csv              # Example data files
```

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## 📄 License

MIT License - feel free to use this project for any purpose.

## 🙏 Acknowledgments

Based on scientific literature on lactate threshold determination methods, including:
- Dmax method (Cheng et al.)
- Log-Log transformation (Beaver et al.)
- Modified Dmax (Bishop et al.)

## 📧 Contact

Questions? Open an issue on GitHub or visit the deployed app.

---

Made with ❤️ for athletes and coaches
