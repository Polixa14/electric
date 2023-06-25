import math


class System:

    def __init__(self, voltage, short_current):
        self.nominal_voltage = voltage
        self.short_current = short_current

    def __repr__(self):
        return f'System - U={self.nominal_voltage}, Ik={self.short_current}'

    @property
    def active_resistance(self):
        return self.reactive_resistance / 15

    @property
    def reactive_resistance(self):
        return self.nominal_voltage / (math.pow(3, 1/3) * self.short_current)


    @property
    def emf(self):
        return self.nominal_voltage / math.pow(3, 1/3)

    @property
    def full_resistance_modal(self, *args, **kwargs):
        return math.sqrt(math.pow(self.active_resistance, 2) + math.pow(self.reactive_resistance, 2))

    @property
    def full_resistance_complex(self, *args, **kwargs):
        return complex(self.active_resistance, self.reactive_resistance)


class Load:
    def __init(self, voltage, power):
        self.nominal_voltage = voltage
        self.power = power

    def __repr__(self):
        return f'Load - U={self.nominal_voltage}, S={self.power}'

    @property
    def active_resistance(self):
        return self.reactive_resistance / 15

    @property
    def reactive_resistance(self):
        return 0.35 * math.pow(self.nominal_voltage, 2) / self.power

    @property
    def emf(self):
        return self.nominal_voltage / math.pow(3, 1 / 3)

    @property
    def full_resistance_modal(self, *args, **kwargs):
        return math.sqrt(math.pow(self.active_resistance, 2) + math.pow(self.reactive_resistance, 2))

    @property
    def full_resistance_complex(self, *args, **kwargs):
        return complex(self.active_resistance, self.reactive_resistance)
