from dataclasses import dataclass, field
from typing import ClassVar, Dict, Tuple

"""
Physiological model of an astronaut for EVA simulation.
"""
@dataclass
class Astronaut:
    # === Class-level baseline constants (for easy reset) ==========
    _BASELINE: ClassVar[dict] = dict(
        heart_rate=70,                # bpm
        blood_pressure_sys=120,       # mmHg
        blood_pressure_dia=80,        # mmHg
        respiration_rate=12,          # breaths/min
        oxygen_saturation=0.98,       # fraction
        blood_o2_pa=95.0,             # mmHg
        blood_co2_pa=40.0,            # mmHg
        n2_saturation=1.0,            # fraction
        metabolic_rate=80.0,          # W
        core_temp=37.0,               # °C
        skin_temp=33.0,               # °C
        sweat_rate=0.0,               # g/h
        glucose_level=90.0,           # mg/dL
        radiation_dose_mSv=0.0,       # mSv
        muscle_fatigue=0.0,           # 0–1
        cognitive_load=0.1,           # 0–1
        stress_index=0.1,             # 0–1
        fear=0.0,                     # 0–1
        adrenaline_lvl=0.0,           # 0–1
    )

    # === Static / anthropometric =================================
    mass:   float = 80.0      # kg
    volume: float = 0.075     # m³
    age:    int   = 40        # years

    # === Mission specific ========================================
    mission_elapsed_time: float = 0.0

    # === Clamp limits for each dynamic variable (min, max) ======
    _LIMITS: ClassVar[Dict[str, Tuple[float, float]]] = dict(
        heart_rate=(40, 180),               # bpm, bradycardia to tachycardia
        blood_pressure_sys=(90, 180),       # mmHg systolic
        blood_pressure_dia=(60, 120),       # mmHg diastolic
        respiration_rate=(6, 30),           # breaths/min (deep sleep to exertion)
        oxygen_saturation=(0.80, 1.0),      # fraction (life-threatening < 0.85)
        blood_o2_pa=(60.0, 110.0),          # mmHg
        blood_co2_pa=(30.0, 55.0),          # mmHg (respiratory acidosis/alkalosis)
        n2_saturation=(0.0, 1.0),           # fraction (0 = full decompression)
        metabolic_rate=(80.0, 400.0),       # W (sleep to heavy EVA exertion)
        core_temp=(34.0, 39.0),             # °C (hypothermia to hyperthermia risk)
        skin_temp=(28.0, 36.0),             # °C (varies with suit environment)
        sweat_rate=(0.0, 2.0),              # g/h (typical inside suit)
        glucose_level=(60.0, 180.0),        # mg/dL (hypo- to hyperglycemia)
        radiation_dose_mSv=(0.0, 250.0),    # mSv (lethal acute ~1000 mSv)
        muscle_fatigue=(0.0, 1.0),          # normalized
        cognitive_load=(0.0, 1.0),          # normalized
        stress_index=(0.0, 1.0),            # normalized
        fear=(0.0, 1.0),                    # normalized
        adrenaline_lvl=(0.0, 1.0),          # normalized
    )

    # === Dynamic physiologic fields (initialised from _BASELINE) =
    heart_rate:         int   = _BASELINE["heart_rate"]
    blood_pressure_sys: int   = _BASELINE["blood_pressure_sys"]
    blood_pressure_dia: int   = _BASELINE["blood_pressure_dia"]
    respiration_rate:   int   = _BASELINE["respiration_rate"]
    oxygen_saturation:  float = _BASELINE["oxygen_saturation"]
    blood_o2_pa:        float = _BASELINE["blood_o2_pa"]
    blood_co2_pa:       float = _BASELINE["blood_co2_pa"]
    n2_saturation:      float = _BASELINE["n2_saturation"]
    metabolic_rate:     float = _BASELINE["metabolic_rate"]
    core_temp:          float = _BASELINE["core_temp"]
    skin_temp:          float = _BASELINE["skin_temp"]
    sweat_rate:         float = _BASELINE["sweat_rate"]
    glucose_level:      float = _BASELINE["glucose_level"]
    radiation_dose_mSv: float = _BASELINE["radiation_dose_mSv"]
    muscle_fatigue:     float = _BASELINE["muscle_fatigue"]
    cognitive_load:     float = _BASELINE["cognitive_load"]
    stress_index:       float = _BASELINE["stress_index"]
    fear:               float = _BASELINE["fear"]
    adrenaline_lvl:     float = _BASELINE["adrenaline_lvl"]

    # =============================================================
    # Utility: update value considering limits
    # =========================================================================
    def _update(self, name: str, delta: float) -> None:
        value = getattr(self, name) + delta
        low, high = self._LIMITS.get(name, (-float("inf"), float("inf")))
        setattr(self, name, max(low, min(high, value)))

    # -----------------------------------------------------------------
    # Helper: nudge value toward baseline without overshooting
    # -----------------------------------------------------------------
    def _toward_baseline(self, name: str, delta: float) -> None:
        """
        Move the attribute `name` by `delta` toward baseline, but:
        • never cross the baseline value
        • never exceed global limits
        Positive delta moves upward, negative delta moves downward.
        """
        baseline = self._BASELINE[name]
        current  = getattr(self, name)
        proposed = current + delta

        # If moving up but would pass baseline, pin at baseline
        if delta > 0 and proposed > baseline:
            delta = 0
        # If moving down but would pass baseline, pin at baseline
        if delta < 0 and proposed < baseline:
            delta = 0
        
        self._update(name, delta)


    # =============================================================
    # Public methods
    # =============================================================

    def reset_to_rest(self) -> None:
        """
        Restore all dynamic physiological parameters to baseline
        resting values. Anthropometric data (mass, volume, age) are
        unchanged.
        """
        for key, value in self._BASELINE.items():
            setattr(self, key, value)

    # -----------------------------------------------------------------
    # Drift models
    # -----------------------------------------------------------------
    def eva_rest_drift_1min(self) -> None:
        """
        Advance simulation by one minute of resting in the suit.
        Includes physiological recovery effects.
        """
        self.mission_elapsed_time += 1

        # Lowering stress markers
        self._toward_baseline("heart_rate",        -5.0)
        self._toward_baseline("respiration_rate",  -3.0)
        self._toward_baseline("blood_co2_pa",      -0.3)
        self._toward_baseline("metabolic_rate",    -10)
        self._toward_baseline("core_temp",         -0.01)
        self._toward_baseline("cognitive_load",    -0.005)
        self._toward_baseline("adrenaline_lvl",    -0.01)
        self._toward_baseline("blood_pressure_sys", -0.5)

        # Replenishing/restoring
        self._toward_baseline("oxygen_saturation", 0.002)
        self._toward_baseline("glucose_level",     0.1)

        # Still slow fatigue accumulation and sweat from suit burden
        self._update("muscle_fatigue",    0.0005)
        self._update("sweat_rate",        0.005)
        self._update("skin_temp",         -0.02)

        # Slight decrease in fear and stress
        self._toward_baseline("fear",              -0.002)
        self._toward_baseline("stress_index",      -0.002)

    # -----------------------------------------------------------------
    # 1-minute LOW workload  (sustainable >30 min)
    # -----------------------------------------------------------------
    def eva_work_low_1min(self) -> None:
        """
        One minute of light EVA activity — such as monitoring instruments,
        adjusting small equipment, or observing surroundings. Physically light.
        """
        self.mission_elapsed_time += 1

        # Cardiopulmonary
        self._update("heart_rate",        2)
        self._update("respiration_rate",  0.3)
        self._update("metabolic_rate",   5)

        # Gas exchange
        self._update("blood_co2_pa",      0.5)
        self._update("oxygen_saturation", -0.001)

        # Thermal
        self._update("core_temp",       0.005)
        self._update("skin_temp",       0.010)
        self._update("sweat_rate",      0.01)

        # Fatigue & cognition
        self._update("muscle_fatigue",  0.001)
        self._update("cognitive_load",  0.001)
        self._update("stress_index",    0.001)

        # Biochemistry
        self._update("glucose_level",  -0.05)
        self._update("adrenaline_lvl", 0.01)
        self._update("fear",           0.001)


    # -----------------------------------------------------------------
    # 1-minute NORMAL workload  (sustainable ≈15 min)
    # -----------------------------------------------------------------
    def eva_work_normal_1min(self) -> None:
        """
        One minute of moderate EVA activity—hand-rail translation,
        routine tool use. Tuned so 15 consecutive minutes stay
        within physiological limits.
        """
        self.mission_elapsed_time += 1

        # Cardiopulmonary
        self._update("heart_rate",        4)   
        self._update("respiration_rate",  1)
        self._update("metabolic_rate",    15)  
        self._update("blood_pressure_sys",    0.5)
        self._update("blood_pressure_dia",    0.02)

        # Gas exchange
        self._update("blood_o2_pa",      -0.2)
        self._update("blood_co2_pa",      1.0)
        self._update("oxygen_saturation", -0.003)

        # Thermal load
        self._update("core_temp",       0.010)
        self._update("skin_temp",       0.020)
        self._update("sweat_rate",      0.02)

        # Fatigue & cognition
        self._update("muscle_fatigue",  0.004)
        self._update("cognitive_load",  0.004)
        self._update("stress_index",    0.003)

        # Biochemical
        self._update("glucose_level",  -0.20)
        self._update("adrenaline_lvl", 0.03)
        self._update("fear",           0.002)


    # -----------------------------------------------------------------
    # 1-minute HARD workload  (tolerable ≈5 min)
    # -----------------------------------------------------------------
    def eva_work_hard_1min(self) -> None:
        """
        One minute of high-intensity EVA exertion—hauling hardware
        or emergency maneuvering. Tuned so 5 consecutive minutes
        approach, but do not exceed, safety limits.
        """
        self.mission_elapsed_time += 1

        # Cardiopulmonary
        self._update("heart_rate",        18)  # +90 bpm after 5 min
        self._update("respiration_rate",  5)
        self._update("metabolic_rate",    30)
        self._update("blood_pressure_sys",    1)
        self._update("blood_pressure_dia",    0.5)

        # Gas exchange
        self._update("blood_o2_pa",      -0.5)
        self._update("blood_co2_pa",      3.5)
        self._update("oxygen_saturation", -0.008)

        # Thermal load
        self._update("core_temp",         0.030)
        self._update("skin_temp",         0.060)
        self._update("sweat_rate",        0.07)

        # Fatigue & cognition
        self._update("muscle_fatigue", 0.010)
        self._update("cognitive_load", 0.008)
        self._update("stress_index",   0.006)

        # Biochemical
        self._update("glucose_level",  -0.50)
        self._update("adrenaline_lvl", 0.06)
        self._update("fear",           0.005)

    def event_lost_tether(self) -> None:
        """
        A minute of psychological and physiological spike when the astronaut
        realises they are drifting away from the station (tether lost).
        """
        self.mission_elapsed_time += 1

        # Immediate effects (no time increment yet)
        self._update("fear",           1.0)
        self._update("stress_index",   0.3)
        self._update("adrenaline_lvl", 0.4)
        self._update("heart_rate",     30)
        self._update("respiration_rate", 10)

        # Metabolic spike → knocks O₂ & glucose
        self._update("metabolic_rate",   100)
        self._update("oxygen_saturation", -0.015)
        self._update("glucose_level",     -0.3)


    # -----------------------------------------------------------------
    # 1-minute low-physical + cognitive load task
    # -----------------------------------------------------------------
    def eva_task_cognitive_1min(self) -> None:
        """
        One minute of cognitive-intensive task — such as solving engineering
        problems or making mission-critical decisions under pressure. Physical
        movement minimal, mental load high.
        """
        self.mission_elapsed_time += 1

        # Slight physical changes
        self._update("heart_rate",        1)
        self._update("respiration_rate",  0.2)
        self._update("metabolic_rate",   3)
        self._update("blood_pressure_sys",    0.1)

        # Minimal thermal effect
        self._update("core_temp",         0.003)
        self._update("skin_temp",         0.005)
        self._update("sweat_rate",        0.005)

        # Cognitive strain
        self._update("cognitive_load",    0.05)
        self._update("stress_index",      0.02)

        # Gas exchange
        self._update("blood_o2_pa",      -0.1)
        self._update("blood_co2_pa",      0.1)

        # Glucose and adrenaline use
        self._update("glucose_level",    -0.08)
        self._update("adrenaline_lvl",    0.005)
        self._update("fear",              0.002)

        # Biochemical
        self._update("muscle_fatigue",    0.0005)

    def eva_emergency_response_1min(self) -> None:
        """
        One minute of high-stress emergency handling (e.g., seal breach, hardware failure).
        Physically moderate, but cognitively demanding and emotionally taxing.
        """
        self.mission_elapsed_time += 1

        # Cardiopulmonary response (mild-moderate)
        self._update("heart_rate",         6)   # elevated
        self._update("respiration_rate",   2)
        self._update("metabolic_rate",    20)
        self._update("blood_pressure_sys",    0.5)
        self._update("blood_pressure_dia",    0.5)

        # Thermal & metabolic
        self._update("core_temp",         0.02)
        self._update("skin_temp",         0.03)
        self._update("sweat_rate",        0.03)

        # Gas exchange
        self._update("blood_o2_pa",      -0.5)
        self._update("blood_co2_pa",      2.0)
        self._update("oxygen_saturation", -0.006)

        # Cognitive and emotional load
        self._update("cognitive_load",    0.015)
        self._update("stress_index",      0.05)
        self._update("adrenaline_lvl",    0.04)
        self._update("fear",              0.02)

        # Biochemical
        self._update("glucose_level",     -0.25)
        self._update("muscle_fatigue",    0.004)




