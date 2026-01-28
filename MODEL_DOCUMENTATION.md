# Lactate Threshold Model Documentation

## Overview

This project implements a lactate threshold calculation model that determines LT1 (aerobic threshold) and LT2 (anaerobic threshold) from exercise test data.

## Model Purpose

The model analyzes exercise test data containing:
- **Watts** (power output)
- **Lactate** (blood lactate concentration in mmol/L)
- **RPE** (Rate of Perceived Exertion, optional)

And calculates:
- **LT1**: First lactate threshold (aerobic threshold) - the point where lactate begins to rise above baseline
- **LT2**: Second lactate threshold (anaerobic threshold) - the point of rapid lactate accumulation

## Input Data Format

The model expects a CSV file with the following columns:
- `watts` or `power`: Power output in watts
- `lactate`: Blood lactate concentration in mmol/L
- `rpe` (optional): Rate of Perceived Exertion (1-10 scale)

Example CSV structure:
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

## Calculation Methods

### LT1 (Aerobic Threshold)

LT1 is typically identified as:
- The point where lactate rises 0.5 mmol/L above baseline
- The point where lactate first exceeds 2.0 mmol/L
- The point of first significant increase in lactate concentration

**Method**: D-max method or fixed threshold method (2.0 mmol/L)

### LT2 (Anaerobic Threshold)

LT2 is typically identified as:
- The point where lactate reaches 4.0 mmol/L (OBLA - Onset of Blood Lactate Accumulation)
- The point of maximum lactate steady state (MLSS)
- The point where lactate increases rapidly (inflection point)

**Method**: Fixed threshold (4.0 mmol/L) or D-max method

---

## Technical Specification: Lactate Threshold Estimation (LT1 & LT2)

*Comprehensive technical documentation designed to inform algorithmic processing tools on how to mathematically estimate Lactate Threshold 1 (LT1) and Lactate Threshold 2 (LT2). This documentation emphasizes the **Dmax method**, **Log-Log transformation**, and **Baseline+** methods, as these are statistically robust approaches found in the literature.*

### 1. System Context & Objective

The objective is to algorithmically determine physiological breakpoints (LT1 and LT2) from incremental exercise test data containing Power (Watts), Blood Lactate (mmol/L), and Rating of Perceived Exertion (RPE).

#### 1.1 Input Data Structure

The algorithm requires a dataset $D$ consisting of $n$ stages.
- **$P$ (Power):** Independent variable (Watts). Monotonically increasing.
- **$La$ (Lactate):** Dependent variable (mmol/L).
- **$RPE$ (Subjective):** Dependent variable (Borg 6-20 or 0-10 scale).

$$ D = \{ (P_i, La_i, RPE_i) \mid i = 1, ..., n \} $$

---

### 2. Pre-processing and Curve Fitting

Raw lactate data is often noisy. To perform derivative-based calculations (like Dmax), the data must first be fitted to a continuous mathematical function.

#### 2.1 Polynomial Regression (For Dmax methods)

For LT2 determination via Dmax, fit the Lactate vs. Power data to a **3rd-order polynomial**.

$$ f(P) = aP^3 + bP^2 + cP + d $$

- **Inputs:** Array of $P$ (Watts) and $La$ (mmol/L).
- **Output:** Coefficients $a, b, c, d$.
- **Constraint:** Ensure $R^2$ is evaluated to confirm fit quality.

#### 2.2 Exponential Regression (Alternative Model)

Some sources suggest an exponential model may fit the physiological reality of lactate accumulation better than polynomials for specific subjects.

$$ f(P) = a + b \cdot e^{(c \cdot P)} $$

---

### 3. Estimating Lactate Threshold 1 (LT1)

LT1 represents the "Aerobic Threshold," the point where lactate begins to rise above baseline levels.

#### Method A: Log-Log Transformation (Segmented Regression)

This is the preferred mathematical method for detecting the first breakpoint.

1. **Transformation:** Convert Power and Lactate to logarithmic scales.
   $$ x' = \log(P), \quad y' = \log(La) $$
2. **Segmentation:** Apply a segmented regression (two linear segments) to the transformed data.
   - Segment 1 (Baseline): $y'_1 = m_1x' + c_1$
   - Segment 2 (Rise): $y'_2 = m_2x' + c_2$
3. **Intersection:** Find the intersection point of the two lines.
   $$ x'_{int} = \frac{c_2 - c_1}{m_1 - m_2} $$
4. **Back-transformation:** Calculate Power at LT1.
   $$ P_{LT1} = 10^{(x'_{int})} $$

#### Method B: Baseline Plus (Bsln+)

This method identifies the power where lactate increases by a fixed amount above the baseline.

1. **Calculate Baseline ($La_{base}$):** Average the lactate values of the first stages (where $\Delta La \approx 0$) or take the minimum observed value.
2. **Target Lactate:**
   $$ La_{target} = La_{base} + \delta $$
   - *Standard $\delta$:* 0.5 mmol/L (often used for elite precision) or 1.0 mmol/L.
3. **Interpolation:** Find $P$ where modeled $f(P) = La_{target}$.

---

### 4. Estimating Lactate Threshold 2 (LT2)

LT2 represents the "Anaerobic Threshold" or "Maximal Lactate Steady State" (MLSS) estimation. The Dmax method is considered objective and reliable for this estimation.

#### Method A: The Dmax Method (Standard)

This determines the point on the polynomial regression curve that yields the maximum perpendicular distance to the straight line connecting the first and last data points.

**Mathematical Logic:**

1. **Secant Line ($L$):** Create a line connecting the first data point $(P_1, La_1)$ and the last data point $(P_n, La_n)$.
   - Slope $m = \frac{La_n - La_1}{P_n - P_1}$
   - Intercept $k = La_1 - m \cdot P_1$
2. **Maximization:** The point of maximum distance occurs where the slope of the tangent to the polynomial curve equals the slope of the secant line ($m$).
3. **Differentiation:**
   - Polynomial: $f(P) = aP^3 + bP^2 + cP + d$
   - Derivative: $f'(P) = 3aP^2 + 2bP + c$
4. **Solve for P:** Set $f'(P) = m$ and solve the quadratic equation for $P$.
   $$ 3aP^2 + 2bP + (c - m) = 0 $$
   $$ P_{LT2} = \frac{-2b + \sqrt{(2b)^2 - 4(3a)(c-m)}}{2(3a)} $$
   *(Note: Use the root that falls within the valid range of P)*.

#### Method B: Modified Dmax (ModDmax)

This method is often preferred as it avoids the influence of the low-intensity baseline lag. It is considered a valid estimate of MLSS.

1. **Start Point Adjustment:** Instead of the *first* data point, use the data point immediately preceding the first rise in lactate of $>0.4$ mmol/L (or use the calculated LT1 point).
2. **Secant Line:** Connect this new start point to the final data point $(P_n, La_n)$.
3. **Solve:** Repeat the maximization logic from Method A using this steeper secant line.

#### Method C: Fixed Blood Lactate Accumulation (OBLA)

A fallback method if curve fitting fails, though less individualized.
- **OBLA 4.0:** Interpolate $P$ where $La = 4.0$ mmol/L.

---

### 5. RPE Validation and Cross-Reference

RPE can serve as a non-invasive validation metric or a proxy when lactate data is erroneous.

#### 5.1 RPE Thresholds (Borg 6-20 Scale)
- **LT1 Check:** Check if $P_{LT1}$ aligns with RPE $\approx 11-12$ ("Light").
- **LT2 Check:** Check if $P_{LT2}$ aligns with RPE $\approx 15-17$ ("Hard" to "Very Hard").

#### 5.2 Dmax RPE

The Dmax method can be applied directly to RPE data.

1. Plot RPE vs. Power.
2. Fit a polynomial to the RPE curve.
3. Calculate Dmax (as defined in Section 4, Method A) on the RPE curve.
4. **Result:** $P_{DmaxRPE}$ is statistically similar to $P_{LT2}$ (Lactate Dmax).

---

### 6. Implementation Logic (For Cursor Context)

When writing the code, apply the following logic flow:

```python
def calculate_thresholds(power, lactate, rpe):
    """
    Inputs: arrays of Power (W), Lactate (mmol/L), RPE
    """
    
    # 1. Curve Fitting
    # Fit 3rd order polynomial to Lactate vs Power
    # coeffs = polyfit(power, lactate, 3)
    # model_poly = poly1d(coeffs)

    # 2. LT1 Calculation (Log-Log)
    # Log transform Power and Lactate
    # Perform segmented linear regression (2 segments)
    # LT1_Power = intersection_of_segments_x_axis
    # IF segmented_regression fails:
    #    LT1_Power = Baseline_Plus_Method(baseline_lactate + 0.5)

    # 3. LT2 Calculation (Modified Dmax)
    # Identify Start Point: Point preceding rise of >0.4 mmol/L
    # Identify End Point: Final data point
    # Calculate slope (m) between Start and End Points
    # Calculate derivative of model_poly: f'(x) = 3ax^2 + 2bx + c
    # Solve quadratic: 3ax^2 + 2bx + (c - m) = 0
    # LT2_Power = positive_root

    # 4. RPE Cross-Validation
    # RPE_at_LT2 = interpolate_RPE(LT2_Power)
    # Warning_Flag = True IF (RPE_at_LT2 < 14 OR RPE_at_LT2 > 18)

    return LT1_Power, LT2_Power
```

---

### 7. Mathematical Constraints & Edge Cases

- **Data Sufficiency:** The Dmax method requires a curvilinear response. If the lactate curve is linear (no exponential rise), Dmax cannot be calculated accurately.
- **Step Duration:** Be aware that protocol step duration affects lactate values. Shorter steps (<3-4 min) may result in a "right shift" of the curve (overestimation of Power at LT2) due to lactate lag.
- **MRT Correction:** If the data comes from a ramp test (continuous increase) rather than a step test, the Power output must be adjusted by the Mean Response Time (MRT) to align with steady-state reality.
  - $P_{corrected} = P_{ramp} - MRT$

## Algorithm Overview

1. **Data Preprocessing**
   - Load CSV data
   - Validate data quality
   - Handle missing values
   - Sort by power output (watts)

2. **Baseline Calculation**
   - Calculate baseline lactate (typically first few data points)
   - Determine resting/baseline lactate level

3. **LT1 Detection**
   - Find point where lactate exceeds baseline + 0.5 mmol/L
   - Or find point where lactate first exceeds 2.0 mmol/L
   - Interpolate exact power value if needed

4. **LT2 Detection**
   - Find point where lactate reaches 4.0 mmol/L
   - Or find inflection point in lactate curve
   - Interpolate exact power value if needed

5. **Validation**
   - Ensure LT1 < LT2
   - Check that thresholds are within data range
   - Validate physiological plausibility

## Output

The model outputs:
- **LT1** (watts): Power at aerobic threshold
- **LT2** (watts): Power at anaerobic threshold
- **Visualization**: Graph showing watts vs lactate with threshold markers

## Implementation Notes

- Use interpolation for precise threshold values
- Handle edge cases (no clear thresholds, insufficient data)
- Provide confidence intervals or uncertainty estimates
- Support multiple calculation methods (user-selectable)

## References

Based on research from NotebookLM notebook:
- D-max method for threshold detection
- MLSS (Maximal Lactate Steady State) concepts
- Field-based vs laboratory-based testing approaches
- Individual variability considerations

## Future Enhancements

- Support for heart rate data
- Multiple calculation algorithms
- Statistical validation
- Export results to various formats
- Comparison with reference values
