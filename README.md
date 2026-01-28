# Lactate Threshold Calculator

A Python application to calculate LT1 (aerobic threshold) and LT2 (anaerobic threshold) from exercise test data.

## Project Structure

```
LT-evaluation/
├── MODEL_DOCUMENTATION.md    # Complete documentation on building the model
├── lt_calculator.py          # Core calculation functions (LT1 and LT2)
├── gui.py                    # GUI application (CSV import, results display, graph)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Features

- **LT1 Calculation**: Determines aerobic threshold (typically at 2.0 mmol/L lactate)
- **LT2 Calculation**: Determines anaerobic threshold (typically at 4.0 mmol/L lactate)
- **CSV Import**: Load exercise test data from CSV files
- **Visualization**: Graph showing watts vs lactate with threshold markers
- **GUI Interface**: User-friendly graphical interface

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```python
from lt_calculator import LactateThresholdCalculator

calculator = LactateThresholdCalculator()
results = calculator.calculate('data.csv')

print(f"LT1: {results['LT1_watts']} W")
print(f"LT2: {results['LT2_watts']} W")
```

### Web GUI Application (Browser-based)

```bash
streamlit run streamlit_gui.py
```

This will open the application in your default web browser. Then:
1. Upload your CSV file using the sidebar
2. Click "Calculate Thresholds"
3. View results and interactive graph

The app will be available at `http://localhost:8501`

### Desktop GUI Application (Alternative)

```bash
python gui.py
```

Traditional desktop application using Tkinter.

## Input Data Format

CSV file must contain:
- `watts` or `power`: Power output in watts
- `lactate`: Blood lactate concentration in mmol/L
- `rpe` (optional): Rate of Perceived Exertion

Example:
```csv
watts,lactate,rpe
100,1.2,3
150,1.5,4
200,2.1,5
250,3.5,6
300,5.2,7
350,7.8,8
400,10.5,9
```

## Documentation

See `MODEL_DOCUMENTATION.md` for detailed information about:
- Model purpose and methodology
- Calculation algorithms
- Input/output specifications
- Implementation details

## Development Status

- ✅ Core calculation functions (LT1/LT2)
- ✅ CSV data loading
- ✅ Basic GUI framework
- 🔄 Advanced calculation methods (D-max, inflection point)
- 🔄 Statistical validation
- 🔄 Export functionality

## License

[Add your license here]
