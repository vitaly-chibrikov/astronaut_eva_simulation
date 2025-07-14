import pandas as pd
from dataclasses import dataclass, field
from typing import ClassVar, Dict, Tuple

"""
Physiological model of an astronaut for EVA simulation.
"""
@dataclass
class Astronaut:
    # === Mission specific ========================================
    mission_elapsed_time: float
    _ATTR_DF: ClassVar[pd.DataFrame] = None

    _BASELINE: ClassVar[Dict[str, str]] = {}
    _LIMITS: ClassVar[Dict[str, Tuple[float, float]]] = {}

    @classmethod
    def init(cls, csv_path: str = "attributes.csv"):
        df = pd.read_csv(csv_path, index_col=0)
        cls._ATTR_DF = df

        # Convert all baseline values to float explicitly
        cls._BASELINE = df["BASELINE_0"].astype(float).to_dict()

        # Read min/max limits
        cls._LIMITS = {
            attr: (float(row["MIN"]), float(row["MAX"])) for attr, row in df.iterrows()
        }

    def __init__(self):
        base = self.__class__._BASELINE

        # Initialize dynamic fields from baseline
        self.mission_elapsed_time = 0.0

        self.heart_rate         = base["heart_rate"]
        self.blood_pressure_sys = base["blood_pressure_sys"]
        self.blood_pressure_dia = base["blood_pressure_dia"]
        self.respiration_rate   = base["respiration_rate"]
        self.oxygen_saturation  = base["oxygen_saturation"]
        self.blood_o2_pa        = base["blood_o2_pa"]
        self.blood_co2_pa       = base["blood_co2_pa"]
        self.n2_saturation      = base["n2_saturation"]
        self.metabolic_rate     = base["metabolic_rate"]
        self.core_temp          = base["core_temp"]
        self.skin_temp          = base["skin_temp"]
        self.sweat_rate         = base["sweat_rate"]
        self.glucose_level      = base["glucose_level"]
        self.muscle_fatigue     = base["muscle_fatigue"]
        self.cognitive_load     = base["cognitive_load"]
        self.stress_index       = base["stress_index"]

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
        assert minutes > 0, "Time in minutes should be > 0"

        for _ in range(minutes):
            self.mission_elapsed_time += 1

            for attr, row in self._ATTR_DF.iterrows():
                target = row["R_BASE"]
                rate = row["R_RATE"]
                if pd.notna(target) and pd.notna(rate):
                    self._toward_target(attr, target, abs(rate))
        

    # -----------------------------------------------------------------
    # LOW workload
    # -----------------------------------------------------------------
    def eva_work_low(self, minutes=1) -> None:
        """
        Light EVA activity — such as monitoring instruments,
        adjusting small equipment, or observing surroundings. Physically light.
        """
        assert minutes > 0, "Time in minutes should be > 0"

        for _ in range(minutes):
            self.mission_elapsed_time += 1

            for attr, row in self._ATTR_DF.iterrows():
                target = row["L_BASE"]
                rate = row["L_RATE"]
                if pd.notna(target) and pd.notna(rate):
                    self._toward_target(attr, target, abs(rate))

    # -----------------------------------------------------------------
    # NORMAL workload 
    # -----------------------------------------------------------------
    def eva_work_normal(self, minutes=1) -> None:
        """
        Moderate EVA activity—hand-rail translation, routine tool use.
        """
        assert minutes > 0, "Time in minutes should be > 0"

        for _ in range(minutes):
            self.mission_elapsed_time += 1

            for attr, row in self._ATTR_DF.iterrows():
                target = row["N_BASE"]
                rate = row["N_RATE"]
                if pd.notna(target) and pd.notna(rate):
                    self._toward_target(attr, target, abs(rate))


    # -----------------------------------------------------------------
    # HARD workload 
    # -----------------------------------------------------------------
    def eva_work_hard(self, minutes=1) -> None:
        """
        High-intensity EVA exertion—hauling hardware or emergency maneuvering.
        """
        assert minutes > 0, "Time in minutes should be > 0"

        for _ in range(minutes):
            self.mission_elapsed_time += 1

            for attr, row in self._ATTR_DF.iterrows():
                target = row["H_BASE"]
                rate = row["H_RATE"]
                if pd.notna(target) and pd.notna(rate):
                    self._toward_target(attr, target, abs(rate))


    # -----------------------------------------------------------------
    #  Cognitive load (low-physical) task
    # -----------------------------------------------------------------
    def eva_task_cognitive(self, minutes=1) -> None:
        """
        Cognitive-intensive task — such as solving engineering
        problems or making mission-critical decisions under pressure. 
        Physical movement minimal, mental load high.
        """
        assert minutes > 0, "Time in minutes should be > 0"

        for _ in range(minutes):
            self.mission_elapsed_time += 1

            for attr, row in self._ATTR_DF.iterrows():
                target = row["C_BASE"]
                rate = row["C_RATE"]
                if pd.notna(target) and pd.notna(rate):
                    self._toward_target(attr, target, abs(rate))



