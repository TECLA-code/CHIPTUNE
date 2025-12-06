import time

from music.converters import bpm_to_sleep_time, smooth_value


class MasterClock:
    """Clock centralitzat que sincronitza totes les tasques segons BPM."""

    def __init__(self, config, max_catchup_ticks=3):
        self.cfg = config
        self.max_catchup_ticks = max_catchup_ticks
        initial_bpm = config.filtered_bpm if config.filtered_bpm else config.bpm
        self.filtered_bpm = max(1.0, float(initial_bpm))
        self.period = bpm_to_sleep_time(self.filtered_bpm)
        now = time.monotonic()
        self.last_tick = now
        self.next_tick = now + self.period

    def update(self, raw_bpm, current_time):
        """Actualitza el període segons el BPM mesurat amb suavitzat."""
        filtered = smooth_value(self.filtered_bpm, raw_bpm, self.cfg.bpm_smoothing)
        if filtered is None:
            filtered = raw_bpm
        filtered = max(1.0, float(filtered))

        self.filtered_bpm = filtered
        self.period = bpm_to_sleep_time(filtered)

        # Actualitzar estat global per a mòduls dependents
        self.cfg.bpm_raw = raw_bpm
        self.cfg.filtered_bpm = filtered
        self.cfg.current_sleep_time = self.period
        self.cfg.filtered_sleep_time = self.period
        self.cfg.bpm = int(round(filtered))

        # Evitar que un canvi brusc deixi la següent nota massa llunyana
        if self.next_tick - current_time > self.period * 2:
            self.next_tick = current_time + self.period

        return self.period

    def consume_ticks(self, current_time, active=True):
        """Retorna una llista de ticks que s'han de disparar fins al temps actual."""
        if not active:
            self.last_tick = current_time
            self.next_tick = current_time + self.period
            return []

        ticks = []
        while current_time >= self.next_tick and len(ticks) < self.max_catchup_ticks:
            tick_time = self.next_tick
            ticks.append(tick_time)
            self.last_tick = tick_time
            self.next_tick = tick_time + self.period

        # Si hem quedat massa enrere, resincronitzar per evitar bucles infinits
        if current_time - self.next_tick > self.period * self.max_catchup_ticks:
            self.last_tick = current_time
            self.next_tick = current_time + self.period

        return ticks

    def idle_sleep(self, current_time):
        """Repos curt adaptatiu fins al proper tick."""
        remaining = self.next_tick - current_time
        if remaining <= 0:
            return

        loop_sleep = max(
            self.cfg.loop_sleep_min,
            min(self.cfg.loop_sleep_max, remaining * self.cfg.loop_sleep_factor)
        )
        time.sleep(loop_sleep)
