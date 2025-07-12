from dataclasses import dataclass, field
from typing import ClassVar, Dict, Tuple

"""
Physiological model of an astronaut for EVA simulation.
"""
@dataclass
class Astronaut:
    # === Class-level baseline constants (for easy reset) ==========
    _BASELINE: ClassVar[dict] = dict(

        # Homeostatic Response
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

        # Progressive Load
        muscle_fatigue=0.0,           # 0–1
        cognitive_load=0.0,           # 0–1
        stress_index=0.0,             # 0–1

        # TODO
        # fear
        # adrenalin
        # radiation
    )

    _BASELINE_NORMAL: ClassVar[dict] = dict(
        heart_rate=110.0,               
        blood_pressure_sys=125.0,       
        blood_pressure_dia=80.2,       
        respiration_rate=22.0,          
        oxygen_saturation=0.95,         
        blood_o2_pa=93.0,               
        blood_co2_pa=50.0,              
        metabolic_rate=230.0,           
        core_temp=37.1,                 
        skin_temp=33.2,                 
        sweat_rate=0.2,                 
        glucose_level=88.0,             
    )

    _BASELINE_HARD: ClassVar[dict] = dict(
        heart_rate=160,
        respiration_rate=30,
        metabolic_rate=330,
        blood_pressure_sys=130,
        blood_pressure_dia=85,
        blood_o2_pa=90,
        blood_co2_pa=57.5,
        oxygen_saturation=0.94,
        core_temp=37.15,
        skin_temp=33.3,
        sweat_rate=0.35,
        glucose_level=85,
    )   

    _BASELINE_LOW: ClassVar[dict] = dict(
        heart_rate=80,               
        respiration_rate=15,         
        metabolic_rate=100,          
        blood_pressure_sys=120,
        blood_pressure_dia=80,
        blood_o2_pa=94.0,            
        blood_co2_pa=45.0,           
        oxygen_saturation=0.975,     
        core_temp=37.05,            
        skin_temp=33.2,              
        sweat_rate=0.1,              
        glucose_level=89.0          
    )

    _BASELINE_COGNITIVE: ClassVar[dict] = dict(
        heart_rate=80.0,
        respiration_rate=14.0,
        metabolic_rate=110.0,
        blood_pressure_sys=120,
        blood_pressure_dia=80,
        blood_o2_pa=94.0,
        blood_co2_pa=41.0,
        oxygen_saturation=0.975, 
        core_temp=37.03,
        skin_temp=33.05,
        sweat_rate=0.05,
        glucose_level=89.2
    )

    _BASELINE_EMERGENCY: ClassVar[dict] = dict(
        heart_rate=130.0,
        respiration_rate=30.0,
        metabolic_rate=280.0,
        blood_pressure_sys=125.0,
        blood_pressure_dia=85.0,
        blood_o2_pa=90.0,
        blood_co2_pa=50.0,
        oxygen_saturation=0.92,
        core_temp=37.20,
        skin_temp=33.30,
        sweat_rate=0.30,
        glucose_level=87.5
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
        muscle_fatigue=(0.0, 1.0),          # normalized
        cognitive_load=(0.0, 1.0),          # normalized
        stress_index=(0.0, 1.0),            # normalized
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
    muscle_fatigue:     float = _BASELINE["muscle_fatigue"]
    cognitive_load:     float = _BASELINE["cognitive_load"]
    stress_index:       float = _BASELINE["stress_index"]

    # =============================================================
    # Utility: update value considering limits
    # =========================================================================
    def _update(self, name: str, delta: float) -> None:
        value = getattr(self, name) + delta
        low, high = self._LIMITS.get(name, (-float("inf"), float("inf")))
        setattr(self, name, max(low, min(high, value)))

    # -----------------------------------------------------------------
    # Helper: nudge value toward a given baseline (up or down)
    # -----------------------------------------------------------------
    def _toward_target(self, name: str, target_baseline: float, delta: float) -> None:
        """
        Move attribute `name` toward `target_baseline` by up to `delta` (always positive).
        The value will:
        • move in the correct direction (up/down),
        • stop at the baseline (no overshoot),
        • stay within the global _LIMITS.
        """
        assert delta >= 0, "Delta must be non-negative"

        current = getattr(self, name)
        direction = 1 if target_baseline > current else -1
        raw_step = direction * delta
        proposed = current + raw_step

        # Clamp to baseline if we're going to overshoot
        if direction > 0 and proposed > target_baseline:
            proposed = target_baseline
        elif direction < 0 and proposed < target_baseline:
            proposed = target_baseline

        # Respect global limits
        low, high = self._LIMITS.get(name, (-float("inf"), float("inf")))
        proposed = max(low, min(high, proposed))

        setattr(self, name, proposed)



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
    # Drift toward basic BASELINE (rest) for 1 minute
    # -----------------------------------------------------------------
    def eva_rest_drift_1min(self) -> None:
        """
        Advance simulation by one minute of resting in the suit.
        Includes physiological recovery effects.
        """
        self.mission_elapsed_time += 1

        # Homeostatic variables recover toward baseline
        self._toward_target("heart_rate",         self._BASELINE["heart_rate"],         delta=5.0)
        self._toward_target("respiration_rate",   self._BASELINE["respiration_rate"],   delta=3.0)
        self._toward_target("blood_o2_pa",        self._BASELINE["blood_o2_pa"],        delta=0.2)
        self._toward_target("blood_co2_pa",       self._BASELINE["blood_co2_pa"],       delta=1.0)
        self._toward_target("metabolic_rate",     self._BASELINE["metabolic_rate"],     delta=10.0)
        self._toward_target("core_temp",          self._BASELINE["core_temp"],          delta=0.01)
        self._toward_target("blood_pressure_sys", self._BASELINE["blood_pressure_sys"], delta=0.5)
        self._toward_target("blood_pressure_dia", self._BASELINE["blood_pressure_dia"], delta=0.5)
        self._toward_target("oxygen_saturation",  self._BASELINE["oxygen_saturation"],  delta=0.002)
        self._toward_target("glucose_level",      self._BASELINE["glucose_level"],      delta=0.1)
        self._toward_target("skin_temp",          self._BASELINE["skin_temp"],          delta=0.02)
        self._toward_target("sweat_rate",         self._BASELINE["sweat_rate"],         delta=0.005)

        # Progressive load stays or accumulates slowly (fatigue still slightly increases due to suit burden)
        self._update("muscle_fatigue", 0.0005)
        

    # -----------------------------------------------------------------
    # 1-minute LOW workload  (sustainable >30 min)
    # -----------------------------------------------------------------
    def eva_work_low_1min(self) -> None:
        """
        One minute of light EVA activity — such as monitoring instruments,
        adjusting small equipment, or observing surroundings. Physically light.
        Parameters stabilize near LOW_BASELINE after ~10 minutes.
        """
        self.mission_elapsed_time += 1

        # Cardiopulmonary
        self._toward_target("heart_rate",         self._BASELINE_LOW["heart_rate"], 2.0)
        self._toward_target("respiration_rate",   self._BASELINE_LOW["respiration_rate"], 0.3)
        self._toward_target("metabolic_rate",     self._BASELINE_LOW["metabolic_rate"], 2.0)
        self._toward_target("blood_pressure_sys", self._BASELINE["blood_pressure_sys"], 0.5)
        self._toward_target("blood_pressure_dia", self._BASELINE["blood_pressure_dia"], 0.5)

        # Gas exchange
        self._toward_target("blood_co2_pa",       self._BASELINE_LOW["blood_co2_pa"], 0.5)
        self._toward_target("oxygen_saturation",  self._BASELINE_LOW["oxygen_saturation"], 0.001)

        # Thermal
        self._toward_target("core_temp",          self._BASELINE_LOW["core_temp"],  0.002)
        self._toward_target("skin_temp",          self._BASELINE_LOW["skin_temp"], 0.005)
        self._toward_target("sweat_rate",         self._BASELINE_LOW["sweat_rate"], 0.005)

        # Biochemistry
        self._toward_target("glucose_level",      self._BASELINE_LOW["glucose_level"], 0.05)

        # Fatigue & cognition (continue to accumulate slowly)
        self._update("muscle_fatigue",  0.001)
        self._update("cognitive_load",  0.001)
        self._update("stress_index",    0.001)

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
        self._toward_target("heart_rate",         self._BASELINE_NORMAL["heart_rate"],         delta=4)
        self._toward_target("respiration_rate",   self._BASELINE_NORMAL["respiration_rate"],   delta=1)
        self._toward_target("metabolic_rate",     self._BASELINE_NORMAL["metabolic_rate"],     delta=15)
        self._toward_target("blood_pressure_sys", self._BASELINE_NORMAL["blood_pressure_sys"], delta=0.5)
        self._toward_target("blood_pressure_dia", self._BASELINE_NORMAL["blood_pressure_dia"], delta=0.02)

        # Gas exchange
        self._toward_target("blood_o2_pa",        self._BASELINE_NORMAL["blood_o2_pa"],        delta=0.2)
        self._toward_target("blood_co2_pa",       self._BASELINE_NORMAL["blood_co2_pa"],       delta=1.0)
        self._toward_target("oxygen_saturation",  self._BASELINE_NORMAL["oxygen_saturation"],  delta=0.003)

        # Thermal load
        self._toward_target("core_temp",          self._BASELINE_NORMAL["core_temp"],          delta=0.010)
        self._toward_target("skin_temp",          self._BASELINE_NORMAL["skin_temp"],          delta=0.020)
        self._toward_target("sweat_rate",         self._BASELINE_NORMAL["sweat_rate"],         delta=0.02)

        # Biochemical
        self._toward_target("glucose_level",      self._BASELINE_NORMAL["glucose_level"],      delta=0.20)

        # Progressive load (accumulating)
        self._update("muscle_fatigue",  0.004)
        self._update("cognitive_load",  0.004)
        self._update("stress_index",    0.003)


    # -----------------------------------------------------------------
    # 1-minute HARD workload  (sustainable ≈5 min)
    # -----------------------------------------------------------------
    def eva_work_hard_1min(self) -> None:
        """
        One minute of high-intensity EVA exertion—hauling hardware
        or emergency maneuvering. Tuned so 5 consecutive minutes
        approach, but do not exceed, safety limits.
        """

        self.mission_elapsed_time += 1

        # Cardiopulmonary
        self._toward_target("heart_rate",         self._BASELINE_HARD["heart_rate"],         delta=18)
        self._toward_target("respiration_rate",   self._BASELINE_HARD["respiration_rate"],   delta=5)
        self._toward_target("metabolic_rate",     self._BASELINE_HARD["metabolic_rate"],     delta=50)
        self._toward_target("blood_pressure_sys", self._BASELINE_HARD["blood_pressure_sys"], delta=2.0)
        self._toward_target("blood_pressure_dia", self._BASELINE_HARD["blood_pressure_dia"], delta=1)

        # Gas exchange
        self._toward_target("blood_o2_pa",        self._BASELINE_HARD["blood_o2_pa"],        delta=1)
        self._toward_target("blood_co2_pa",       self._BASELINE_HARD["blood_co2_pa"],       delta=3.5)
        self._toward_target("oxygen_saturation",  self._BASELINE_HARD["oxygen_saturation"],  delta=0.008)

        # Thermal load
        self._toward_target("core_temp",          self._BASELINE_HARD["core_temp"],          delta=0.030)
        self._toward_target("skin_temp",          self._BASELINE_HARD["skin_temp"],          delta=0.060)
        self._toward_target("sweat_rate",         self._BASELINE_HARD["sweat_rate"],         delta=0.07)

        # Biochemical
        self._toward_target("glucose_level",      self._BASELINE_HARD["glucose_level"],      delta=0.1)

        # Progressive load (cumulative)
        self._update("muscle_fatigue",  0.010)
        self._update("cognitive_load",  0.008)
        self._update("stress_index",    0.006)


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

        # Slight physical changes toward cognitive task baseline
        self._toward_target("heart_rate",         self._BASELINE_COGNITIVE["heart_rate"],        1)
        self._toward_target("respiration_rate",   self._BASELINE_COGNITIVE["respiration_rate"],  0.2)
        self._toward_target("metabolic_rate",     self._BASELINE_COGNITIVE["metabolic_rate"],    3)
        self._toward_target("blood_pressure_sys", self._BASELINE_COGNITIVE["blood_pressure_sys"], 0.1)

        # Minimal thermal effect
        self._toward_target("core_temp",          self._BASELINE_COGNITIVE["core_temp"],         0.003)
        self._toward_target("skin_temp",          self._BASELINE_COGNITIVE["skin_temp"],         0.005)
        self._toward_target("sweat_rate",         self._BASELINE_COGNITIVE["sweat_rate"],        0.005)

        # Gas exchange
        self._toward_target("blood_o2_pa",        self._BASELINE_COGNITIVE["blood_o2_pa"],       0.1)
        self._toward_target("blood_co2_pa",       self._BASELINE_COGNITIVE["blood_co2_pa"],      0.1)

        # Glucose depletion
        self._toward_target("glucose_level",      self._BASELINE_COGNITIVE["glucose_level"],     0.08)

        # Progressive load (mental strain)
        self._update("cognitive_load",  0.05)
        self._update("stress_index",    0.02)
        self._update("muscle_fatigue",  0.0005)


    def eva_emergency_response_1min(self) -> None:
        """
        One minute of high-stress emergency handling (e.g., seal breach, hardware failure).
        Physically moderate, but cognitively demanding and emotionally taxing.
        """
        self.mission_elapsed_time += 1

        # Cardiopulmonary response
        self._toward_target("heart_rate",         self._BASELINE_EMERGENCY["heart_rate"],        6)
        self._toward_target("respiration_rate",   self._BASELINE_EMERGENCY["respiration_rate"],  2)
        self._toward_target("metabolic_rate",     self._BASELINE_EMERGENCY["metabolic_rate"],    20)
        self._toward_target("blood_pressure_sys", self._BASELINE_EMERGENCY["blood_pressure_sys"], 0.5)
        self._toward_target("blood_pressure_dia", self._BASELINE_EMERGENCY["blood_pressure_dia"], 0.5)

        # Thermal & metabolic
        self._toward_target("core_temp",    self._BASELINE_EMERGENCY["core_temp"],    0.02)
        self._toward_target("skin_temp",    self._BASELINE_EMERGENCY["skin_temp"],    0.03)
        self._toward_target("sweat_rate",   self._BASELINE_EMERGENCY["sweat_rate"],   0.03)

        # Gas exchange
        self._toward_target("blood_o2_pa",       self._BASELINE_EMERGENCY["blood_o2_pa"],      0.5)
        self._toward_target("blood_co2_pa",      self._BASELINE_EMERGENCY["blood_co2_pa"],     2.0)
        self._toward_target("oxygen_saturation", self._BASELINE_EMERGENCY["oxygen_saturation"], 0.006)

        # Biochemistry
        self._toward_target("glucose_level", self._BASELINE_EMERGENCY["glucose_level"], 0.25)

        # Progressive load (mental/physical toll)
        self._update("cognitive_load",  0.015)
        self._update("stress_index",    0.05)
        self._update("muscle_fatigue",  0.004)





