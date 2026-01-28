"""
Flask Web Application for Lactate Threshold Calculator
A more reliable alternative to Streamlit
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import io
import json
from lt_calculator import LactateThresholdCalculator
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import base64

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files[]')
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        results = []
        
        for file in files:
            if not file.filename.endswith('.csv'):
                return jsonify({'error': f'{file.filename} is not a CSV file'}), 400
            
            # Read CSV
            csv_content = file.read()
            df = pd.read_csv(io.BytesIO(csv_content))
            
            # Normalize columns
            df.columns = df.columns.str.lower().str.strip()
            
            # Validate
            if 'power' in df.columns and 'watts' not in df.columns:
                df['watts'] = df['power']
            
            if 'watts' not in df.columns:
                return jsonify({'error': f'{file.filename} missing watts/power column'}), 400
            
            if 'lactate' not in df.columns:
                return jsonify({'error': f'{file.filename} missing lactate column'}), 400
            
            # Return data preview - convert to native Python types
            preview_df = df.head(10).copy()
            for col in preview_df.select_dtypes(include=['int64', 'float64']).columns:
                preview_df[col] = preview_df[col].astype(float)
            
            results.append({
                'filename': file.filename,
                'rows': int(len(df)),
                'columns': list(df.columns),
                'preview': preview_df.to_dict('records'),
                'csv_data': df.to_csv(index=False)
            })
        
        return jsonify({
            'success': True,
            'files': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        files_data = data.get('files_data')
        
        if not files_data:
            return jsonify({'error': 'No data provided'}), 400
        
        results = []
        
        for file_info in files_data:
            filename = file_info.get('filename')
            csv_data = file_info.get('csv_data')
            
            try:
                # Create calculator
                calc = LactateThresholdCalculator()
                file_obj = io.StringIO(csv_data)
                calc.load_data(file_obj)
                
                # Calculate baseline
                baseline = calc.calculate_baseline_lactate()
                
                # Calculate LT1 using Log-Log method
                lt1 = float(round(calc.calculate_lt1(method='loglog'), 1))
                
                # Calculate LT2 using Modified Dmax method
                lt2 = float(round(calc.calculate_lt2(method='moddmax'), 1))
        
                # Get data for plotting
                data_df = calc.get_data()
                watts = data_df['watts'].tolist()
                lactate = data_df['lactate'].tolist()
                
                # Create plot
                fig, ax = plt.subplots(figsize=(10, 5))
                
                # Create smooth curve using polynomial fit
                import numpy as np
                watts_array = np.array(watts)
                lactate_array = np.array(lactate)
                
                # Create smooth curve points
                watts_smooth = np.linspace(watts_array.min(), watts_array.max(), 200)
                
                # Use polynomial interpolation
                if calc.poly_coeffs is not None:
                    poly_func = np.poly1d(calc.poly_coeffs)
                    lactate_smooth = poly_func(watts_smooth)
                else:
                    lactate_smooth = np.interp(watts_smooth, watts_array, lactate_array)
                
                # Plot smooth curve
                ax.plot(watts_smooth, lactate_smooth, '-', linewidth=2.5, color='#1f77b4', label='Lactate Curve', alpha=0.8)
                
                # Plot data points
                ax.plot(watts, lactate, 'o', markersize=8, color='#1f77b4', markeredgecolor='white', markeredgewidth=1.5, zorder=3)
                
                # Add thresholds
                lt1_lactate = np.interp(lt1, watts, lactate)
                lt2_lactate = np.interp(lt2, watts, lactate)
                
                ax.axvline(lt1, color='green', linestyle='--', linewidth=2, label=f'LT1: {lt1:.1f}W', alpha=0.8)
                ax.axvline(lt2, color='red', linestyle='--', linewidth=2, label=f'LT2: {lt2:.1f}W', alpha=0.8)
                ax.plot(lt1, lt1_lactate, 'go', markersize=10)
                ax.plot(lt2, lt2_lactate, 'ro', markersize=10)
                
                ax.set_xlabel('Power (Watts)', fontsize=11, fontweight='bold')
                ax.set_ylabel('Lactate (mmol/L)', fontsize=11, fontweight='bold')
                ax.set_title(filename, fontsize=12, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.legend(fontsize=9)
                ax.set_xlim(left=0)
                ax.set_ylim(bottom=0)
                plt.tight_layout()
                
                # Convert plot to base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100)
                buffer.seek(0)
                plot_base64 = base64.b64encode(buffer.read()).decode()
                plt.close()
                
                results.append({
                    'filename': filename,
                    'lt1': lt1,
                    'lt2': lt2,
                    'baseline': float(round(baseline, 2)),
                    'r2': float(round(calc.poly_r2, 4)) if calc.poly_r2 else None,
                    'plot': plot_base64
                })
                
            except Exception as e:
                results.append({
                    'filename': filename,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8501)
