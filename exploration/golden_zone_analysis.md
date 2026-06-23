# Golden Zone Experiment Analysis Report

**Generated:** 2026-06-23  
**Data Source:** `experiments/results/golden_zone_data_20260623_210136.json`  
**Total Experiments:** 600

---

## Executive Summary

This analysis examines the relationship between three key parameters (regrowth rate, density, and energy) and two outcomes (curiosity rate and survival steps) in a resource-gathering simulation environment.

**Key Findings:**
1. **Density is the strongest predictor of curiosity rate** (r = -0.23, p < 0.001) - lower density correlates with higher curiosity
2. **Energy is the dominant factor for survival** (r = 0.97, p < 0.001) - more energy means longer survival
3. **No configurations meet the strict Golden Zone criteria** (curiosity > 10% AND survival > 100 steps)
4. **The simulation duration is limited** - max survival is 25 steps, indicating short episode lengths

---

## 1. Distribution of Curiosity Rates

### Overall Statistics

| Metric | Value |
|--------|-------|
| Max Curiosity Rate | 100.0% |
| Mean Curiosity Rate | 1.8% |
| Configurations > 5% | 33 (5.5%) |
| Configurations > 10% | 22 (3.7%) |

### Distribution Analysis

The curiosity rate distribution is highly right-skewed:
- Most configurations (94.5%) have curiosity rates below 5%
- A small subset achieves very high curiosity (up to 100%)
- High curiosity configurations share a common pattern: **low density (0.05) + moderate regrowth**

**Visualization:** `experiments/results/golden_zone_distributions.png`

---

## 2. Heatmap Analysis

### Curiosity Rate Heatmaps by Energy Level

The heatmaps reveal distinct patterns across energy levels:

| Energy | Peak Curiosity Region | Optimal Density Range |
|--------|----------------------|----------------------|
| 5 | Low regrowth, lowest density | 0.05 - 0.08 |
| 10 | Mid-high regrowth, lowest density | 0.05 - 0.13 |
| 15 | Mid regrowth, low density | 0.05 - 0.16 |
| 20 | Scattered, generally low density | 0.05 - 0.27 |

**Key Insight:** The lowest density (0.05) consistently produces the highest curiosity rates across all energy levels, suggesting that sparse resource environments encourage exploratory behavior.

**Visualizations:**
- `experiments/results/golden_zone_heatmaps_curiosity.png`
- `experiments/results/golden_zone_heatmaps_survival.png`

---

## 3. Statistical Analysis

### Correlation with Curiosity Rate

| Parameter | Correlation (r) | p-value | Significance |
|-----------|----------------|---------|--------------|
| Regrowth Rate | 0.018 | 0.660 | Not significant |
| Density | -0.233 | < 0.001 | ***Strongly significant*** |
| Energy | -0.078 | 0.055 | Marginally significant |

### Correlation with Survival Steps

| Parameter | Correlation (r) | p-value | Significance |
|-----------|----------------|---------|--------------|
| Regrowth Rate | 0.0004 | 0.992 | Not significant |
| Density | 0.005 | 0.905 | Not significant |
| Energy | 0.968 | < 0.001 | ***Extremely significant*** |

### Linear Regression Results

**For Curiosity Rate (R² = 0.06):**
- Model explains only 6% of variance
- Density coefficient: -0.025 (negative impact)
- Energy coefficient: -0.008 (slight negative impact)
- Regrowth coefficient: +0.002 (negligible)

**For Survival Steps (R² = 0.94):**
- Model explains 94% of variance
- Energy coefficient: +4.43 (dominant positive factor)
- Other parameters: negligible

### Interaction Effects

| Interaction | Correlation with Curiosity | p-value |
|-------------|---------------------------|---------|
| Regrowth × Density | -0.127 | 0.002 |
| Regrowth × Energy | -0.032 | 0.437 |
| Density × Energy | -0.176 | < 0.001 |

**Key Insight:** The Density × Energy interaction suggests that the negative effect of density on curiosity is amplified at higher energy levels.

**Visualization:** `experiments/results/golden_zone_correlations.png`

---

## 4. Golden Zone Identification

### Original Criteria (Curiosity > 10% AND Survival > 100)

**Result:** 0 configurations meet these criteria.

**Reason:** Maximum survival steps observed is 25, far below the 100-step threshold. The simulation appears to run for limited durations.

### Adjusted Golden Zone Analysis

Given the observed data ranges, we define a **Practical Golden Zone**:

#### Criteria A: High Curiosity (> 10%)
**Found:** 22 configurations

| Parameter | Range |
|-----------|-------|
| Regrowth Rate | 0.0045 - 0.0500 |
| Density | 0.0500 - 0.1333 |
| Energy | 5 - 15 |

**Top High-Curiosity Configurations:**

| Rank | Regrowth | Density | Energy | Curiosity | Survival |
|------|----------|---------|--------|-----------|----------|
| 1 | 0.0465 | 0.0500 | 10 | 100.0% | 10 |
| 2 | 0.0500 | 0.0500 | 10 | 100.0% | 10 |
| 3 | 0.0185 | 0.0778 | 5 | 100.0% | 5 |
| 4 | 0.0150 | 0.0778 | 15 | 100.0% | 15 |
| 5 | 0.0045 | 0.0500 | 5 | 100.0% | 5 |
| 6 | 0.0360 | 0.0500 | 5 | 80.0% | 5 |
| 7 | 0.0220 | 0.0500 | 15 | 50.0% | 20 |
| 8 | 0.0395 | 0.0500 | 10 | 46.7% | 15 |
| 9 | 0.0500 | 0.1333 | 10 | 40.0% | 15 |
| 10 | 0.0045 | 0.0500 | 10 | 40.0% | 15 |

#### Criteria B: Long Survival (> 20 steps)
**Found:** 10 configurations

| Parameter | Range |
|-----------|-------|
| Regrowth Rate | 0.0080 - 0.0465 |
| Density | 0.0500 - 0.2722 |
| Energy | 20 (exclusively) |

**Top Long-Survival Configurations:**

| Rank | Regrowth | Density | Energy | Curiosity | Survival |
|------|----------|---------|--------|-----------|----------|
| 1 | 0.0220 | 0.0778 | 20 | 12.0% | 25 |
| 2 | 0.0465 | 0.1611 | 20 | 4.0% | 25 |
| 3 | 0.0080 | 0.0500 | 20 | 16.0% | 25 |
| 4 | 0.0465 | 0.0500 | 20 | 4.3% | 23 |
| 5 | 0.0185 | 0.0778 | 20 | 0.0% | 23 |

#### Practical Golden Zone Definition

Based on the data, we propose **Adjusted Golden Zone Boundaries**:

```
Curiosity Rate > 10% AND Survival > 20 steps
```

**Found:** 1 configuration meets this relaxed criteria:
- Regrowth: 0.0220, Density: 0.0778, Energy: 20
- Curiosity: 12.0%, Survival: 25 steps

### Trade-off Analysis

| Goal | Best Parameter Range | Trade-off |
|------|---------------------|-----------|
| Maximize Curiosity | Density = 0.05, Energy = 5-15 | Short survival (5-20 steps) |
| Maximize Survival | Energy = 20 | Lower curiosity (0-16%) |
| Balanced | Density = 0.05-0.08, Energy = 15-20 | Moderate both |

**Visualization:** `experiments/results/golden_zone_visualization.png`

---

## 5. Parameter Impact Analysis

### Regrowth Rate Impact
- **Effect on Curiosity:** Minimal direct effect (r = 0.018)
- **Effect on Survival:** Negligible (r = 0.0004)
- **Optimal Range:** 0.015 - 0.050 (for high curiosity)

### Density Impact
- **Effect on Curiosity:** Strong negative correlation (r = -0.233)
- **Effect on Survival:** No effect (r = 0.005)
- **Optimal Range:** 0.05 - 0.08 (lowest values tested)

### Energy Impact
- **Effect on Curiosity:** Slight negative correlation (r = -0.078)
- **Effect on Survival:** Extremely strong positive (r = 0.968)
- **Optimal Range:** 
  - For curiosity: 5-15
  - For survival: 20

**Visualization:** `experiments/results/golden_zone_parameter_impact.png`

---

## 6. Recommendations

### For High Curiosity Behavior
1. **Minimize density** to 0.05 (lowest tested value)
2. **Use moderate energy** (5-15) to allow exploration
3. **Regrowth rate** is flexible; 0.02-0.05 works well

### For Long Survival
1. **Maximize energy** to 20
2. **Density and regrowth** have minimal impact

### For Balanced Performance
1. **Energy = 20** for survival buffer
2. **Density = 0.05-0.08** to enable curiosity
3. **Regrowth = 0.02-0.04** for resource sustainability

### Suggested Next Experiments
1. **Extend simulation duration** to test if survival patterns hold at 100+ steps
2. **Test lower density values** (< 0.05) to find if curiosity increases further
3. **Test intermediate energy levels** (e.g., 17, 18) to optimize the trade-off
4. **Vary episode length** as a parameter to understand time-dependence

---

## 7. Conclusion

The experiment reveals a fundamental **curiosity-survival trade-off**:

- **High curiosity** requires sparse environments (low density) with limited energy
- **Long survival** requires abundant energy
- **Both together** is difficult to achieve

The "Golden Zone" as originally defined (curiosity > 10% AND survival > 100) cannot be achieved within the current simulation parameters. The maximum survival of 25 steps suggests the simulation may be running short episodes.

**Practical Finding:** The best balanced configuration found is:
- Regrowth: 0.022
- Density: 0.0778
- Energy: 20
- Result: 12% curiosity, 25 steps survival

This represents the **practical golden zone** given current simulation constraints.

---

## Generated Visualizations

| File | Description |
|------|-------------|
| `golden_zone_distributions.png` | Distribution histograms for curiosity and survival |
| `golden_zone_heatmaps_curiosity.png` | Curiosity rate heatmaps by energy level |
| `golden_zone_heatmaps_survival.png` | Survival steps heatmaps by energy level |
| `golden_zone_correlations.png` | Correlation analysis bar charts |
| `golden_zone_visualization.png` | 3D parameter space and golden zone visualization |
| `golden_zone_parameter_impact.png` | Parameter impact analysis with error bars |

---

*Analysis completed on 2026-06-23 using Python with NumPy, SciPy, and Matplotlib.*
