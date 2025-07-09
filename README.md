# 🚀 Astronaut EVA Physiological and Cognitive Simulation

## **Objective**

Simulate the physiological and cognitive state of an astronaut during Extra-Vehicular Activity (EVA) under various task conditions. The system tracks minute-by-minute changes in response to physical work, cognitive load, stress, and recovery.

---

## **Core Components**

### Astronaut State Model

Each astronaut is modeled using a class with dynamic parameters, including:

- **Cardiovascular**: `heart_rate`, `blood_pressure_sys`, `blood_pressure_dia`
- **Respiratory**: `respiration_rate`, `blood_o2_pa`, `blood_co2_pa`, `oxygen_saturation`
- **Metabolic**: `metabolic_rate`, `core_temp`, `skin_temp`, `sweat_rate`, `glucose_level`
- **Cognitive/Emotional**: `cognitive_load`, `stress_index`, `fear`, `adrenaline_lvl`, `muscle_fatigue`
- **Other**: `radiation_dose_mSv`, `n2_saturation`, `mission_elapsed_time`

Baseline (`_BASELINE`) and constraint (`_LIMITS`) dictionaries define realistic value ranges.

---

## **Activity Functions**

Each task is simulated as a 1-minute function that modifies the astronaut's state:

| Function | Description |
|----------|-------------|
| `eva_rest_drift_1min()` | Passive rest; returns variables toward baseline, reduces stress/adrenaline |
| `eva_work_normal_1min()` | Standard EVA work; moderate physiological/cognitive increases |
| `eva_work_hard_1min()` | Intense workload; high cardiovascular/metabolic load |
| `eva_work_low_1min()` | Light movement; low metabolic impact |
| `eva_work_cognitive_1min()` | High mental load; increases adrenaline, cognitive stress |
| `eva_emergency_response_1min()` | Combines moderate work with high emotional strain |

---

## **Simulation Engine**

### Main Loop

- Simulates 1-minute steps based on a string of task codes:  
  `H = hard work`, `N = normal`, `L = low work`, `C = cognitive`, `R = rest`
- Each task updates the astronaut's state.
- Logged in a table (Pandas DataFrame) with:
  - Initial `B` column (baseline)
  - `MIN` and `MAX` limits
  - One column per simulated minute

### Output

- Saved to CSV via:  
  `log_df.to_csv("eva_log.csv", float_format="%.4g")`
- Formats values for readability and analysis.

---

## **Testing and Verification**

- Unit tests for each public method ensure valid physiological transformations.
- Special method for **rest** pulls variables toward baseline instead of clamping below it.
- Tested with different 10–45 minute profiles.

---

## **Simulated Scenarios**

| Scenario | Duration | Result |
|----------|----------|--------|
| Hard Work | 20 min | Realistic but hits upper limits (unsustainable >15 min) |
| Cognitive Task | 20 min | Manageable, mentally exhausting |
| Normal Work | 20 min | Sustainable, mild load |
| Low Work | 20 min | Minimal stress accumulation |
| Normal + Rest | 10 + 10 min | Demonstrates recovery pattern |
| Mixed Profile | 45 min | Complex but plausible; includes rest and emergency load |

---

## **Realism Evaluation**

✔️ **Realistic physiological responses**  
✔️ **Stress, fear, and adrenaline dynamics match expected psychological reactions**  
✔️ **Fatigue accumulates correctly and does not self-resolve**  
✔️ **Clamped and baseline-pulled values ensure realism under load or recovery**

---

## **Planned Enhancements**

- Trauma simulation (e.g. heat stroke, hypoxia, panic)
- Suit feedback control (O₂ injection, emergency cooling)
- Extended duration missions (90–180 minutes)
- Visual GUI or web dashboard
- Integration with mission scheduling planners


