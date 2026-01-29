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

@app.route('/submit-test', methods=['POST'])
def submit_test():
    """Handle manual form data submission for lactate tests."""
    try:
        data = request.json
        tests = data.get('tests', [])
        
        if not tests:
            return jsonify({'error': 'No test data provided'}), 400
        
        validated_tests = []
        
        for test in tests:
            test_date = test.get('date', '')
            intervals = test.get('intervals', [])
            
            if not test_date:
                return jsonify({'error': 'Test date is required'}), 400
            
            if not intervals or len(intervals) < 3:
                return jsonify({'error': 'At least 3 intervals required per test'}), 400
            
            # Convert to DataFrame format
            watts_list = []
            lactate_list = []
            rpe_list = []
            
            for interval in intervals:
                try:
                    power = float(interval.get('power', 0))
                    lactate = float(interval.get('lactate', 0))
                    rpe = interval.get('rpe', '')
                    
                    if power <= 0 or lactate <= 0:
                        continue
                    
                    watts_list.append(power)
                    lactate_list.append(lactate)
                    rpe_list.append(float(rpe) if rpe and str(rpe).strip() else None)
                    
                except (ValueError, TypeError):
                    continue
            
            if len(watts_list) < 3:
                return jsonify({'error': f'Test {test_date}: insufficient valid data points'}), 400
            
            # Create CSV-like string for existing calculator
            csv_lines = ['watts,lactate,rpe']
            for w, l, r in zip(watts_list, lactate_list, rpe_list):
                rpe_str = str(r) if r is not None else ''
                csv_lines.append(f'{w},{l},{rpe_str}')
            csv_data = '\n'.join(csv_lines)
            
            validated_tests.append({
                'test_name': f'Test {test_date}',
                'date': test_date,
                'csv_data': csv_data,
                'data_points': len(watts_list)
            })
        
        return jsonify({
            'success': True,
            'tests': validated_tests
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        
        # Support both old 'files_data' and new 'tests' format
        tests_data = data.get('tests') or data.get('files_data')
        
        if not tests_data:
            return jsonify({'error': 'No data provided'}), 400
        
        results = []
        
        for file_info in tests_data:
            # Support both 'test_name' (new format) and 'filename' (old format)
            filename = file_info.get('test_name') or file_info.get('filename')
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
                # Set x-axis to start at first data point with small margin
                ax.set_xlim(left=watts_array.min() - 10)
                ax.set_ylim(bottom=0)
                plt.tight_layout()
                
                # Convert plot to base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100)
                buffer.seek(0)
                plot_base64 = base64.b64encode(buffer.read()).decode()
                plt.close()
                
                # Calculate 5-zone power zones based on LT1 and LT2
                # Z1: Recovery (up to 70% of LT1)
                # Z2: Endurance (70% of LT1 to LT1)
                # Z3: Tempo (LT1 to midpoint between LT1 and LT2)
                # Z4: Threshold (midpoint to LT2)
                # Z5: VO2 Max (above LT2)
                
                z1_max = int(lt1 * 0.70)
                z2_min = z1_max + 1
                z2_max = int(lt1)
                z3_min = z2_max + 1
                z3_max = int((lt1 + lt2) / 2)
                z4_min = z3_max + 1
                z4_max = int(lt2)
                z5_min = z4_max + 1
                
                zones = {
                    'Z1': {
                        'name': 'Active Recovery',
                        'watts': f'< {z1_max}W',
                        'duration': '> 3 hours',
                        'color': '#90CAF9'
                    },
                    'Z2': {
                        'name': 'Endurance',
                        'watts': f'{z2_min} - {z2_max}W',
                        'duration': '2-6 hours',
                        'color': '#66BB6A'
                    },
                    'Z3': {
                        'name': 'Tempo',
                        'watts': f'{z3_min} - {z3_max}W',
                        'duration': '1-3 hours',
                        'color': '#FFD54F'
                    },
                    'Z4': {
                        'name': 'Threshold',
                        'watts': f'{z4_min} - {z4_max}W',
                        'duration': '30-60 min',
                        'color': '#FF9800'
                    },
                    'Z5': {
                        'name': 'VO2 Max',
                        'watts': f'{z5_min}W+',
                        'duration': '3-8 min',
                        'color': '#EF5350'
                    }
                }
                
                results.append({
                    'filename': filename,
                    'lt1': lt1,
                    'lt2': lt2,
                    'zones': zones,
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
