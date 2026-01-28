"""
GUI Application for Lactate Threshold Calculator
Import CSV file, calculate LT1 and LT2, and display results with graph.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from lt_calculator import LactateThresholdCalculator
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LactateThresholdGUI:
    """GUI application for lactate threshold calculation."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Lactate Threshold Calculator")
        self.root.geometry("1000x700")
        
        self.calculator = LactateThresholdCalculator()
        self.data: Optional[pd.DataFrame] = None
        self.results: Optional[dict] = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Data Import", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(file_frame, text="Import CSV File", 
                  command=self.load_csv_file).pack(side=tk.LEFT, padx=5)
        
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, padx=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # LT1 display
        ttk.Label(results_frame, text="LT1 (Aerobic Threshold):", 
                 font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.lt1_label = ttk.Label(results_frame, text="--", font=("Arial", 14))
        self.lt1_label.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        # LT2 display
        ttk.Label(results_frame, text="LT2 (Anaerobic Threshold):", 
                 font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.lt2_label = ttk.Label(results_frame, text="--", font=("Arial", 14))
        self.lt2_label.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Calculate button
        ttk.Button(results_frame, text="Calculate Thresholds", 
                  command=self.calculate_thresholds).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Graph frame
        graph_frame = ttk.LabelFrame(main_frame, text="Lactate Curve", padding="10")
        graph_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)
        
        # Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initial empty plot
        self.ax.set_xlabel("Power (Watts)", fontsize=12)
        self.ax.set_ylabel("Lactate (mmol/L)", fontsize=12)
        self.ax.set_title("Lactate Threshold Analysis", fontsize=14, fontweight="bold")
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
    
    def load_csv_file(self):
        """Load CSV file and display filename."""
        filepath = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.calculator.load_data(filepath)
                self.data = self.calculator.get_data()
                self.file_label.config(text=f"Loaded: {filepath.split('/')[-1]}")
                logger.info(f"File loaded: {filepath}")
                
                # Auto-calculate if data is loaded
                self.calculate_thresholds()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
                logger.error(f"Error loading file: {e}")
    
    def calculate_thresholds(self):
        """Calculate LT1 and LT2 and update display."""
        if self.data is None:
            messagebox.showwarning("No Data", "Please load a CSV file first.")
            return
        
        try:
            # Calculate thresholds
            self.calculator.calculate_baseline_lactate()
            lt1 = self.calculator.calculate_lt1()
            lt2 = self.calculator.calculate_lt2()
            
            self.results = {
                "LT1_watts": lt1,
                "LT2_watts": lt2
            }
            
            # Update labels
            self.lt1_label.config(text=f"{lt1:.1f} W")
            self.lt2_label.config(text=f"{lt2:.1f} W")
            
            # Update graph
            self.update_graph()
            
            logger.info(f"Thresholds calculated: LT1={lt1:.1f}W, LT2={lt2:.1f}W")
            
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Failed to calculate thresholds:\n{str(e)}")
            logger.error(f"Error calculating thresholds: {e}")
    
    def update_graph(self):
        """Update the graph with data and threshold markers."""
        if self.data is None:
            return
        
        self.ax.clear()
        
        # Plot data
        watts = self.data['watts'].values
        lactate = self.data['lactate'].values
        
        self.ax.plot(watts, lactate, 'o-', linewidth=2, markersize=8, 
                     label='Lactate Data', color='blue')
        
        # Add threshold markers if calculated
        if self.results:
            lt1 = self.results['LT1_watts']
            lt2 = self.results['LT2_watts']
            
            # Get lactate values at thresholds (interpolate)
            lt1_lactate = np.interp(lt1, watts, lactate)
            lt2_lactate = np.interp(lt2, watts, lactate)
            
            # Vertical lines for thresholds
            self.ax.axvline(lt1, color='green', linestyle='--', linewidth=2, 
                           label=f'LT1: {lt1:.1f}W', alpha=0.7)
            self.ax.axvline(lt2, color='red', linestyle='--', linewidth=2, 
                           label=f'LT2: {lt2:.1f}W', alpha=0.7)
            
            # Mark threshold points
            self.ax.plot(lt1, lt1_lactate, 'go', markersize=10, 
                        markerfacecolor='green', markeredgecolor='darkgreen')
            self.ax.plot(lt2, lt2_lactate, 'ro', markersize=10, 
                        markerfacecolor='red', markeredgecolor='darkred')
        
        # Labels and formatting
        self.ax.set_xlabel("Power (Watts)", fontsize=12)
        self.ax.set_ylabel("Lactate (mmol/L)", fontsize=12)
        self.ax.set_title("Lactate Threshold Analysis", fontsize=14, fontweight="bold")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='best')
        
        self.canvas.draw()


def main():
    """Run the GUI application."""
    root = tk.Tk()
    app = LactateThresholdGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
