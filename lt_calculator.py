"""
Lactate Threshold Calculator
Calculates LT1 and LT2 from exercise test data (watts, lactate, and optional RPE 1-10).
Implements methods from MODEL_DOCUMENTATION.md:
- LT1: Log-Log Transformation (preferred) or Baseline Plus (fallback)
- LT2: Modified Dmax (preferred), Standard Dmax, or OBLA 4.0 (fallback)
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple, Optional, List
import logging
import warnings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LactateThresholdCalculator:
    """Calculate LT1 and LT2 from exercise test data using advanced methods."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.data = None
        self.lt1 = None
        self.lt2 = None
        self.baseline_lactate = None
        self.poly_coeffs = None  # Polynomial coefficients [a, b, c, d] for f(P) = aP^3 + bP^2 + cP + d
        self.poly_r2 = None  # R-squared for polynomial fit
    
    def load_data(self, filepath) -> pd.DataFrame:
        """
        Load exercise test data from CSV file.
        
        Args:
            filepath: Path to CSV file (string) or file-like object (for Streamlit)
            
        Returns:
            DataFrame with loaded data
        """
        logger.info(f"Loading data from {type(filepath)}")
        
        try:
            # Handle both file paths (strings) and file-like objects (Streamlit uploads)
            if isinstance(filepath, str):
                df = pd.read_csv(filepath)
            else:
                # File-like object (Streamlit UploadedFile or BytesIO)
                # Ensure we're at the beginning of the file
                if hasattr(filepath, 'seek'):
                    filepath.seek(0)
                df = pd.read_csv(filepath)
            
            # Normalize column names (handle variations)
            df.columns = df.columns.str.lower().str.strip()
            
            # Check for power/watts column
            if 'watts' in df.columns:
                power_col = 'watts'
            elif 'power' in df.columns:
                power_col = 'power'
                df['watts'] = df['power']
            else:
                raise ValueError("CSV must contain 'watts' or 'power' column")
            
            # Validate required columns
            if 'lactate' not in df.columns:
                raise ValueError("CSV must contain 'lactate' column")
            
            # Sort by power output
            df = df.sort_values('watts').reset_index(drop=True)
            
            # Validate data
            if len(df) < 4:
                raise ValueError("Need at least 4 data points for polynomial fitting")
            
            if df['watts'].isna().any() or df['lactate'].isna().any():
                raise ValueError("Missing values in watts or lactate columns")
            
            # Ensure positive values for log transformation
            if (df['watts'] <= 0).any():
                raise ValueError("All watts values must be positive")
            if (df['lactate'] <= 0).any():
                raise ValueError("All lactate values must be positive (required for log transformation)")
            
            self.data = df
            logger.info(f"Loaded {len(df)} data points")
            
            # Fit polynomial curve (may fail, but don't crash)
            try:
                self._fit_polynomial()
            except Exception as e:
                logger.warning(f"Polynomial fitting failed: {e}. Some methods may not be available.")
                self.poly_coeffs = None
                self.poly_r2 = None
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def _fit_polynomial(self, degree: int = 3):
        """
        Fit 3rd-order polynomial to Lactate vs Power data.
        f(P) = aP^3 + bP^2 + cP + d
        
        Args:
            degree: Polynomial degree (default 3)
        """
        if self.data is None:
            return
        
        watts = self.data['watts'].values
        lactate = self.data['lactate'].values
        
        if len(watts) < degree + 1:
            logger.warning(f"Not enough data points ({len(watts)}) for degree {degree} polynomial")
            self.poly_coeffs = None
            self.poly_r2 = None
            return
        
        try:
            # Fit polynomial using numpy
            coeffs = np.polyfit(watts, lactate, degree)
            # numpy.polyfit returns coefficients in descending order: [a, b, c, d]
            # where f(x) = ax^3 + bx^2 + cx + d
            self.poly_coeffs = coeffs
            
            # Calculate R-squared
            poly_func = np.poly1d(coeffs)
            y_pred = poly_func(watts)
            ss_res = np.sum((lactate - y_pred) ** 2)
            ss_tot = np.sum((lactate - np.mean(lactate)) ** 2)
            self.poly_r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            logger.info(f"Polynomial fit: R² = {self.poly_r2:.4f}")
            
            if self.poly_r2 < 0.7:
                logger.warning(f"Low R² ({self.poly_r2:.4f}). Curve fitting may be unreliable.")
                
        except np.linalg.LinAlgError as e:
            logger.error(f"Linear algebra error in polynomial fitting: {e}")
            self.poly_coeffs = None
            self.poly_r2 = None
        except Exception as e:
            logger.error(f"Error fitting polynomial: {e}")
            self.poly_coeffs = None
            self.poly_r2 = None
    
    def _polynomial_func(self, P: np.ndarray) -> np.ndarray:
        """
        Evaluate polynomial function f(P) = aP^3 + bP^2 + cP + d.
        
        Args:
            P: Power values (watts)
            
        Returns:
            Lactate values (mmol/L)
        """
        if self.poly_coeffs is None:
            raise ValueError("Polynomial not fitted. Call load_data() first.")
        
        return np.polyval(self.poly_coeffs, P)
    
    def _polynomial_derivative(self, P: np.ndarray) -> np.ndarray:
        """
        Evaluate derivative of polynomial: f'(P) = 3aP^2 + 2bP + c.
        
        Args:
            P: Power values (watts)
            
        Returns:
            Derivative values
        """
        if self.poly_coeffs is None:
            raise ValueError("Polynomial not fitted. Call load_data() first.")
        
        a, b, c = self.poly_coeffs[0], self.poly_coeffs[1], self.poly_coeffs[2]
        return 3 * a * P**2 + 2 * b * P + c
    
    def calculate_baseline_lactate(self, n_points: int = 3) -> float:
        """
        Calculate baseline lactate from first n data points.
        
        Args:
            n_points: Number of initial points to use for baseline
            
        Returns:
            Baseline lactate value
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        n_points = min(n_points, len(self.data))
        baseline = self.data['lactate'].head(n_points).mean()
        self.baseline_lactate = baseline
        
        logger.info(f"Baseline lactate: {baseline:.2f} mmol/L")
        return baseline
    
    def _segmented_regression_loglog(self, log_power: np.ndarray, log_lactate: np.ndarray) -> Optional[float]:
        """
        Perform segmented linear regression on log-transformed data.
        Finds intersection point of two linear segments.
        
        Args:
            log_power: Log-transformed power values
            log_lactate: Log-transformed lactate values
            
        Returns:
            Intersection point x' (log power) or None if failed
        """
        n = len(log_power)
        if n < 4:
            return None
        
        best_r2 = -np.inf
        best_breakpoint = None
        
        # Try different breakpoints (minimum 2 points per segment)
        for break_idx in range(2, n - 1):
            # Segment 1: baseline (first break_idx points)
            x1 = log_power[:break_idx]
            y1 = log_lactate[:break_idx]
            
            # Segment 2: rise (remaining points)
            x2 = log_power[break_idx:]
            y2 = log_lactate[break_idx:]
            
            try:
                # Fit linear regression to each segment
                slope1, intercept1, r1, p1, se1 = stats.linregress(x1, y1)
                slope2, intercept2, r2, p2, se2 = stats.linregress(x2, y2)
                
                # Calculate intersection point
                if abs(slope1 - slope2) < 1e-10:
                    continue  # Parallel lines, skip
                
                x_int = (intercept2 - intercept1) / (slope1 - slope2)
                
                # Check if intersection is within valid range
                if log_power[0] <= x_int <= log_power[-1]:
                    # Calculate combined R²
                    y1_pred = slope1 * x1 + intercept1
                    y2_pred = slope2 * x2 + intercept2
                    ss_res = np.sum((y1 - y1_pred)**2) + np.sum((y2 - y2_pred)**2)
                    ss_tot = np.sum((log_lactate - np.mean(log_lactate))**2)
                    r2_combined = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                    
                    if r2_combined > best_r2:
                        best_r2 = r2_combined
                        best_breakpoint = x_int
                        
            except Exception as e:
                logger.debug(f"Error in segmented regression at breakpoint {break_idx}: {e}")
                continue
        
        return best_breakpoint
    
    def calculate_lt1(self, method: str = "loglog") -> float:
        """
        Calculate LT1 (aerobic threshold).
        
        Args:
            method: Calculation method
                - "loglog": Log-Log transformation with segmented regression (preferred)
                - "baseline_plus": Baseline Plus method (fallback)
                - "fixed_2mmol": Fixed threshold at 2.0 mmol/L (simple fallback)
        
        Returns:
            LT1 power in watts
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if self.baseline_lactate is None:
            self.calculate_baseline_lactate()
        
        watts = self.data['watts'].values
        lactate = self.data['lactate'].values
        
        if method == "loglog":
            # Method A: Log-Log Transformation (Segmented Regression)
            try:
                # Transform to log scale
                log_power = np.log10(watts)
                log_lactate = np.log10(lactate)
                
                # Perform segmented regression
                log_lt1 = self._segmented_regression_loglog(log_power, log_lactate)
                
                if log_lt1 is not None:
                    # Back-transform to power
                    lt1 = 10 ** log_lt1
                    
                    # Validate result is within data range
                    if watts[0] <= lt1 <= watts[-1]:
                        self.lt1 = lt1
                        logger.info(f"LT1 calculated (Log-Log): {lt1:.1f} watts")
                        return lt1
                    else:
                        logger.warning("Log-Log LT1 outside data range, falling back to Baseline Plus")
                else:
                    logger.warning("Segmented regression failed, falling back to Baseline Plus")
                    
            except Exception as e:
                logger.warning(f"Log-Log method failed: {e}, falling back to Baseline Plus")
        
        # Fallback to Baseline Plus
        if method == "baseline_plus" or method == "loglog":
            # Method B: Baseline Plus (Bsln+)
            delta = 0.5  # Standard delta: 0.5 mmol/L
            target_lactate = self.baseline_lactate + delta
            
            # Use polynomial if available, otherwise interpolate
            if self.poly_coeffs is not None:
                # Find P where f(P) = target_lactate
                poly_func = np.poly1d(self.poly_coeffs)
                # Find roots of f(P) - target_lactate = 0
                roots = np.roots(self.poly_coeffs - [0, 0, 0, target_lactate])
                # Filter real roots within valid range
                real_roots = roots[np.isreal(roots)].real
                valid_roots = real_roots[(real_roots >= watts[0]) & (real_roots <= watts[-1])]
                
                if len(valid_roots) > 0:
                    lt1 = valid_roots[0]  # Take first valid root
                else:
                    # Fallback to interpolation
                    lt1 = np.interp(target_lactate, lactate, watts)
            else:
                # Simple interpolation
                lt1 = np.interp(target_lactate, lactate, watts)
            
            self.lt1 = lt1
            logger.info(f"LT1 calculated (Baseline Plus): {lt1:.1f} watts")
            return lt1
        
        elif method == "fixed_2mmol":
            # Simple fixed threshold
            threshold = 2.0
            idx = np.where(lactate >= threshold)[0]
            
            if len(idx) == 0:
                lt1 = np.interp(threshold, lactate, watts)
            else:
                first_idx = idx[0]
                if first_idx == 0:
                    lt1 = watts[0]
                else:
                    lt1 = np.interp(threshold, 
                                  lactate[first_idx-1:first_idx+1], 
                                  watts[first_idx-1:first_idx+1])
            
            self.lt1 = lt1
            logger.info(f"LT1 calculated (Fixed 2.0 mmol/L): {lt1:.1f} watts")
            return lt1
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _find_start_point_for_moddmax(self) -> Tuple[float, float]:
        """
        Find start point for Modified Dmax: point preceding first rise >0.4 mmol/L.
        Falls back to first point if no such rise found.
        
        Returns:
            Tuple of (power, lactate) for start point
        """
        watts = self.data['watts'].values
        lactate = self.data['lactate'].values
        
        # Check for rise >0.4 mmol/L
        for i in range(1, len(lactate)):
            if lactate[i] - lactate[0] > 0.4:
                # Return previous point
                return watts[i-1], lactate[i-1]
        
        # No significant rise found, use first point
        return watts[0], lactate[0]
    
    def calculate_lt2(self, method: str = "moddmax") -> float:
        """
        Calculate LT2 (anaerobic threshold).
        
        Args:
            method: Calculation method
                - "moddmax": Modified Dmax (preferred)
                - "dmax": Standard Dmax
                - "obla": OBLA 4.0 mmol/L (fallback)
        
        Returns:
            LT2 power in watts
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if self.poly_coeffs is None:
            logger.warning("Polynomial not fitted. Falling back to OBLA method.")
            method = "obla"
        
        watts = self.data['watts'].values
        lactate = self.data['lactate'].values
        
        if method == "moddmax" or method == "dmax":
            # Modified Dmax or Standard Dmax
            try:
                if method == "moddmax":
                    # Modified Dmax: use adjusted start point
                    P_start, La_start = self._find_start_point_for_moddmax()
                else:
                    # Standard Dmax: use first data point
                    P_start, La_start = watts[0], lactate[0]
                
                # End point: last data point
                P_end, La_end = watts[-1], lactate[-1]
                
                # Calculate secant line slope
                m = (La_end - La_start) / (P_end - P_start) if (P_end - P_start) > 0 else 0
                
                # Get polynomial coefficients: [a, b, c, d] for aP^3 + bP^2 + cP + d
                a, b, c, d = self.poly_coeffs[0], self.poly_coeffs[1], self.poly_coeffs[2], self.poly_coeffs[3]
                
                # Solve quadratic: 3aP^2 + 2bP + (c - m) = 0
                # Using quadratic formula: P = (-2b ± sqrt((2b)^2 - 4(3a)(c-m))) / (2(3a))
                discriminant = (2*b)**2 - 4*(3*a)*(c - m)
                
                if discriminant < 0:
                    raise ValueError("No real solution for Dmax (negative discriminant)")
                
                sqrt_disc = np.sqrt(discriminant)
                root1 = (-2*b + sqrt_disc) / (2 * 3 * a)
                root2 = (-2*b - sqrt_disc) / (2 * 3 * a)
                
                # Select root within valid range
                valid_roots = [r for r in [root1, root2] if P_start <= r <= P_end]
                
                if len(valid_roots) == 0:
                    raise ValueError("No valid root found in data range")
                
                lt2 = valid_roots[0]  # Take first valid root
                
                self.lt2 = lt2
                logger.info(f"LT2 calculated ({method.upper()}): {lt2:.1f} watts")
                return lt2
                
            except Exception as e:
                logger.warning(f"{method.upper()} method failed: {e}, falling back to OBLA")
                method = "obla"
        
        if method == "obla":
            # Method C: OBLA 4.0 mmol/L
            threshold = 4.0
            
            # Use polynomial if available
            if self.poly_coeffs is not None:
                poly_func = np.poly1d(self.poly_coeffs)
                # Find roots of f(P) - 4.0 = 0
                roots = np.roots(self.poly_coeffs - [0, 0, 0, threshold])
                real_roots = roots[np.isreal(roots)].real
                valid_roots = real_roots[(real_roots >= watts[0]) & (real_roots <= watts[-1])]
                
                if len(valid_roots) > 0:
                    lt2 = valid_roots[0]
                else:
                    lt2 = np.interp(threshold, lactate, watts)
            else:
                # Simple interpolation
                idx = np.where(lactate >= threshold)[0]
                if len(idx) == 0:
                    lt2 = np.interp(threshold, lactate, watts)
                else:
                    first_idx = idx[0]
                    if first_idx == 0:
                        lt2 = watts[0]
                    else:
                        lt2 = np.interp(threshold,
                                      lactate[first_idx-1:first_idx+1],
                                      watts[first_idx-1:first_idx+1])
            
            self.lt2 = lt2
            logger.info(f"LT2 calculated (OBLA 4.0): {lt2:.1f} watts")
            return lt2
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def validate_rpe(self) -> Dict[str, any]:
        """
        Validate thresholds using RPE data (if available).
        
        Returns:
            Dictionary with validation results
        """
        if self.data is None or 'rpe' not in self.data.columns:
            return {"available": False, "message": "RPE data not available"}
        
        if self.lt1 is None or self.lt2 is None:
            return {"available": False, "message": "Thresholds not calculated"}
        
        watts = self.data['watts'].values
        rpe = self.data['rpe'].values
        
        # Interpolate RPE at thresholds
        rpe_lt1 = np.interp(self.lt1, watts, rpe)
        rpe_lt2 = np.interp(self.lt2, watts, rpe)
        
        # Check if RPE values are in expected ranges (1-10 scale)
        # LT1: ~4-5 ("Moderate"), LT2: ~7-8 ("Very Hard")
        lt1_valid = 3 <= rpe_lt1 <= 6
        lt2_valid = 6 <= rpe_lt2 <= 9
        
        warnings = []
        if not lt1_valid:
            warnings.append(f"LT1 RPE ({rpe_lt1:.1f}) outside expected range (4-5)")
        if not lt2_valid:
            warnings.append(f"LT2 RPE ({rpe_lt2:.1f}) outside expected range (7-8)")
        
        return {
            "available": True,
            "rpe_lt1": round(rpe_lt1, 1),
            "rpe_lt2": round(rpe_lt2, 1),
            "lt1_valid": lt1_valid,
            "lt2_valid": lt2_valid,
            "warnings": warnings
        }
    
    def calculate(self, 
                  filepath: str,
                  lt1_method: str = "loglog",
                  lt2_method: str = "moddmax") -> Dict[str, float]:
        """
        Calculate both LT1 and LT2 from a CSV file.
        
        Args:
            filepath: Path to CSV file
            lt1_method: Method for LT1 calculation ("loglog", "baseline_plus", "fixed_2mmol")
            lt2_method: Method for LT2 calculation ("moddmax", "dmax", "obla")
        
        Returns:
            Dictionary with LT1 and LT2 values in watts and metadata
        """
        self.load_data(filepath)
        self.calculate_baseline_lactate()
        
        lt1 = self.calculate_lt1(method=lt1_method)
        lt2 = self.calculate_lt2(method=lt2_method)
        
        # Validate results
        if lt1 >= lt2:
            logger.warning(f"LT1 ({lt1:.1f}W) >= LT2 ({lt2:.1f}W). Results may be invalid.")
        
        # Calculate FTP as 95% of LT2
        # FTP represents the maximum power sustainable for ~1 hour
        ftp = round(lt2 * 0.95, 1)
        
        results = {
            "LT1_watts": round(lt1, 1),
            "LT2_watts": round(lt2, 1),
            "FTP_watts": ftp,
            "baseline_lactate": round(self.baseline_lactate, 2),
            "polynomial_r2": round(self.poly_r2, 4) if self.poly_r2 else None,
            "lt1_method": lt1_method,
            "lt2_method": lt2_method
        }
        
        # Add RPE validation if available
        rpe_validation = self.validate_rpe()
        if rpe_validation.get("available"):
            results["rpe_validation"] = rpe_validation
        
        return results
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """Get the loaded data."""
        return self.data
    
    def get_polynomial_coeffs(self) -> Optional[np.ndarray]:
        """Get polynomial coefficients."""
        return self.poly_coeffs


if __name__ == "__main__":
    # Example usage
    calculator = LactateThresholdCalculator()
    
    print("Lactate Threshold Calculator")
    print("=" * 50)
    print("\nTo use this calculator:")
    print("1. Prepare a CSV file with columns: watts, lactate, rpe (optional)")
    print("2. Call: calculator.calculate('path/to/data.csv')")
    print("\nExample:")
    print("  results = calculator.calculate('test_data.csv')")
    print("  print(f\"LT1: {results['LT1_watts']}W\")")
    print("  print(f\"LT2: {results['LT2_watts']}W\")")
    print("\nMethods:")
    print("  LT1: 'loglog' (preferred), 'baseline_plus', 'fixed_2mmol'")
    print("  LT2: 'moddmax' (preferred), 'dmax', 'obla'")
