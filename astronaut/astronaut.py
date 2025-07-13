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

        # Progressive Load. Go lower only at rest.
        muscle_fatigue=0.0,           # 0–100
        cognitive_load=0.0,           # 0–100
        stress_index=0.0,             # 0–100

        # TODO
        # fear
        # adrenalin
        # radiation
    )

    _BASELINE_NORMAL: ClassVar[dict] = dict(
        heart_rate=110.0,               
        blood_pressure_sys=122.0,       
        blood_pressure_dia=82,       
        respiration_rate=22.0,          
        oxygen_saturation=0.95,         
        blood_o2_pa=93.0,               
        blood_co2_pa=50.0,              
        metabolic_rate=230.0,           
        core_temp=37.5,                 
        skin_temp=33.2,                 
        sweat_rate=0.2,                 
        glucose_level=85.0,             
    )

    _BASELINE_HARD: ClassVar[dict] = dict(
        heart_rate=160,
        respiration_rate=30,
        metabolic_rate=330,
        blood_pressure_sys=125,
        blood_pressure_dia=85,
        blood_o2_pa=90,
        blood_co2_pa=57.5,
        oxygen_saturation=0.94,
        core_temp=38,
        skin_temp=33.3,
        sweat_rate=0.35,
        glucose_level=80,
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
        core_temp=37.2,            
        skin_temp=33.2,              
        sweat_rate=0.1,              
        glucose_level=87.0          
    )

    _BASELINE_COGNITIVE: ClassVar[dict] = dict(
        heart_rate=90.0,
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
        glucose_level=87.0
    )

    _BASELINE_EMERGENCY: ClassVar[dict] = dict(
        heart_rate=150.0,
        respiration_rate=30.0,
        metabolic_rate=280.0,
        blood_pressure_sys=130.0,
        blood_pressure_dia=90.0,
        blood_o2_pa=90.0,
        blood_co2_pa=50.0,
        oxygen_saturation=0.92,
        core_temp=37.5,
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
        muscle_fatigue=(0.0, 100),          # normalized
        cognitive_load=(0.0, 100),          # normalized
        stress_index=(0.0, 100),            # normalized
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
    # Drift toward basic rest BASELINE
    # -----------------------------------------------------------------
    def eva_rest_drift(self, minutes=1) -> None:
        """
        Advance simulation by one minute of resting in the suit.
        Includes physiological recovery effects.
        """

        assert minutes > 0, "Time in munutes should be > 0"

        for x in range(1, minutes+1):
            self.mission_elapsed_time += 1

             # Cardiopulmonary
            self._toward_target("heart_rate",         self._BASELINE["heart_rate"],         5.0)
            self._toward_target("respiration_rate",   self._BASELINE["respiration_rate"],   3.0)
            self._toward_target("metabolic_rate",     self._BASELINE["metabolic_rate"],     10.0)
            self._toward_target("blood_pressure_sys", self._BASELINE["blood_pressure_sys"], 0.5)
            self._toward_target("blood_pressure_dia", self._BASELINE["blood_pressure_dia"], 0.5)

            # Gas exchange
            self._toward_target("blood_o2_pa",        self._BASELINE["blood_o2_pa"],        2.0)
            self._toward_target("blood_co2_pa",       self._BASELINE["blood_co2_pa"],       1.0)
            self._toward_target("oxygen_saturation",  self._BASELINE["oxygen_saturation"],  0.002)

            # Thermal
            self._toward_target("core_temp",          self._BASELINE["core_temp"],          0.01)
            self._toward_target("skin_temp",          self._BASELINE["skin_temp"],          0.02)
            self._toward_target("sweat_rate",         self._BASELINE["sweat_rate"],         0.005)

           # Biochemistry
            self._toward_target("glucose_level",      self._BASELINE["glucose_level"],      0.01)

            # Progressive load stays or accumulates slowly (fatigue still slightly increases due to suit burden)
            self._update("muscle_fatigue", 0.01)

            # Lower load and stress at rest
            self._toward_target("cognitive_load", self._BASELINE["cognitive_load"],  0.01)
            self._toward_target("stress_index",   self._BASELINE["stress_index"],  0.01)
        

    # -----------------------------------------------------------------
    # LOW workload
    # -----------------------------------------------------------------
    def eva_work_low(self, minutes=1) -> None:
        """
        Light EVA activity — such as monitoring instruments,
        adjusting small equipment, or observing surroundings. Physically light.
        """
        assert minutes > 0, "Time in munutes should be > 0"

        for x in range(1, minutes+1):
            self.mission_elapsed_time += 1

            # Cardiopulmonary
            self._toward_target("heart_rate",         self._BASELINE_LOW["heart_rate"], 2.0)
            self._toward_target("respiration_rate",   self._BASELINE_LOW["respiration_rate"], 0.5)
            self._toward_target("metabolic_rate",     self._BASELINE_LOW["metabolic_rate"], 2.0)
            self._toward_target("blood_pressure_sys", self._BASELINE["blood_pressure_sys"], 0.5)
            self._toward_target("blood_pressure_dia", self._BASELINE["blood_pressure_dia"], 0.5)

            # Gas exchange
            self._toward_target("blood_o2_pa",        self._BASELINE_NORMAL["blood_o2_pa"], 0.1)
            self._toward_target("blood_co2_pa",       self._BASELINE_LOW["blood_co2_pa"], 0.5)
            self._toward_target("oxygen_saturation",  self._BASELINE_LOW["oxygen_saturation"], 0.001)

            # Thermal
            self._toward_target("core_temp",          self._BASELINE_LOW["core_temp"],  0.002)
            self._toward_target("skin_temp",          self._BASELINE_LOW["skin_temp"], 0.005)
            self._toward_target("sweat_rate",         self._BASELINE_LOW["sweat_rate"], 0.005)

            # Biochemistry
            self._toward_target("glucose_level",      self._BASELINE_LOW["glucose_level"], 0.01)

            # Fatigue & cognition (continue to accumulate slowly)
            self._update("muscle_fatigue",  0.01)
            self._update("cognitive_load",  0.02)
            self._update("stress_index",    0.01)

    # -----------------------------------------------------------------
    # NORMAL workload 
    # -----------------------------------------------------------------
    def eva_work_normal(self, minutes=1) -> None:
        """
        Moderate EVA activity—hand-rail translation, routine tool use.
        """
        assert minutes > 0, "Time in munutes should be > 0"

        for x in range(1, minutes+1):
            self.mission_elapsed_time += 1

            # Cardiopulmonary
            self._toward_target("heart_rate",         self._BASELINE_NORMAL["heart_rate"],         4)
            self._toward_target("respiration_rate",   self._BASELINE_NORMAL["respiration_rate"],   1)
            self._toward_target("metabolic_rate",     self._BASELINE_NORMAL["metabolic_rate"],     15)
            self._toward_target("blood_pressure_sys", self._BASELINE_NORMAL["blood_pressure_sys"], 0.5)
            self._toward_target("blood_pressure_dia", self._BASELINE_NORMAL["blood_pressure_dia"], 0.2)

            # Gas exchange
            self._toward_target("blood_o2_pa",        self._BASELINE_NORMAL["blood_o2_pa"],        0.2)
            self._toward_target("blood_co2_pa",       self._BASELINE_NORMAL["blood_co2_pa"],       1.0)
            self._toward_target("oxygen_saturation",  self._BASELINE_NORMAL["oxygen_saturation"],  0.003)

            # Thermal load
            self._toward_target("core_temp",          self._BASELINE_NORMAL["core_temp"],          0.010)
            self._toward_target("skin_temp",          self._BASELINE_NORMAL["skin_temp"],          0.020)
            self._toward_target("sweat_rate",         self._BASELINE_NORMAL["sweat_rate"],         0.02)

            # Biochemical
            self._toward_target("glucose_level",      self._BASELINE_NORMAL["glucose_level"],      0.20)

            # Progressive load (accumulating)
            self._update("muscle_fatigue",  0.1)
            self._update("cognitive_load",  0.04)
            self._update("stress_index",    0.05)


    # -----------------------------------------------------------------
    # HARD workload 
    # -----------------------------------------------------------------
    def eva_work_hard(self, minutes=1) -> None:
        """
        High-intensity EVA exertion—hauling hardware or emergency maneuvering.
        """
        assert minutes > 0, "Time in munutes should be > 0"

        for x in range(1, minutes+1):

            self.mission_elapsed_time += 1

            # Cardiopulmonary
            self._toward_target("heart_rate",         self._BASELINE_HARD["heart_rate"],         9)
            self._toward_target("respiration_rate",   self._BASELINE_HARD["respiration_rate"],   2.5)
            self._toward_target("metabolic_rate",     self._BASELINE_HARD["metabolic_rate"],     25)
            self._toward_target("blood_pressure_sys", self._BASELINE_HARD["blood_pressure_sys"], 1.0)
            self._toward_target("blood_pressure_dia", self._BASELINE_HARD["blood_pressure_dia"], 0.5)

            # Gas exchange
            self._toward_target("blood_o2_pa",        self._BASELINE_HARD["blood_o2_pa"],        0.5)
            self._toward_target("blood_co2_pa",       self._BASELINE_HARD["blood_co2_pa"],       1.8)
            self._toward_target("oxygen_saturation",  self._BASELINE_HARD["oxygen_saturation"],  0.004)

            # Thermal load
            self._toward_target("core_temp",          self._BASELINE_HARD["core_temp"],          0.015)
            self._toward_target("skin_temp",          self._BASELINE_HARD["skin_temp"],          0.020)
            self._toward_target("sweat_rate",         self._BASELINE_HARD["sweat_rate"],         0.035)

            # Biochemical
            self._toward_target("glucose_level",      self._BASELINE_HARD["glucose_level"],      0.5)
    
            # Progressive load (cumulative)
            self._update("muscle_fatigue",  0.5)
            self._update("cognitive_load",  0.04)
            self._update("stress_index",    0.1)


    # -----------------------------------------------------------------
    #  Cognitive load (low-physical) task
    # -----------------------------------------------------------------
    def eva_task_cognitive(self, minutes=1) -> None:
        """
        Cognitive-intensive task — such as solving engineering
        problems or making mission-critical decisions under pressure. 
        Physical movement minimal, mental load high.
        """

        assert minutes > 0, "Time in munutes should be > 0"

        for x in range(1, minutes+1):

            self.mission_elapsed_time += 1

            # Slight physical changes toward cognitive task baseline
            self._toward_target("heart_rate",         self._BASELINE_COGNITIVE["heart_rate"],        1)
            self._toward_target("respiration_rate",   self._BASELINE_COGNITIVE["respiration_rate"],  2)
            self._toward_target("metabolic_rate",     self._BASELINE_COGNITIVE["metabolic_rate"],    3)
            self._toward_target("blood_pressure_sys", self._BASELINE_COGNITIVE["blood_pressure_sys"], 0.1)
            self._toward_target("blood_pressure_dia", self._BASELINE_HARD["blood_pressure_dia"], 0.1)

            # Gas exchange
            self._toward_target("blood_o2_pa",        self._BASELINE_COGNITIVE["blood_o2_pa"],       0.1)
            self._toward_target("blood_co2_pa",       self._BASELINE_COGNITIVE["blood_co2_pa"],      0.1)
            self._toward_target("oxygen_saturation",  self._BASELINE_LOW["oxygen_saturation"],       0.001)

            # Minimal thermal effect
            self._toward_target("core_temp",          self._BASELINE_COGNITIVE["core_temp"],         0.003)
            self._toward_target("skin_temp",          self._BASELINE_COGNITIVE["skin_temp"],         0.005)
            self._toward_target("sweat_rate",         self._BASELINE_COGNITIVE["sweat_rate"],        0.005)

            # Glucose depletion
            self._toward_target("glucose_level",      self._BASELINE_COGNITIVE["glucose_level"],     0.08)

            # Progressive load (mental strain)
            self._update("muscle_fatigue",  0.01)
            self._update("cognitive_load",  0.7)
            self._update("stress_index",    0.05)



    def eva_emergency_response(self, minutes) -> None:
        """
        High-stress emergency handling (e.g., seal breach, hardware failure).
        Physically moderate, but cognitively demanding and emotionally taxing.
        """
        assert minutes > 0, "Time in munutes should be > 0"

        for x in range(1, minutes+1):

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
            self._update("muscle_fatigue",  0.04)
            self._update("cognitive_load",  0.15)
            self._update("stress_index",    0.5)






