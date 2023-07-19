from electro.mixins.models import PKMixin
from django.contrib.auth import get_user_model
from django.db import models
import math
from electro.model_choices import LineTypeChoices
from django_lifecycle import hook, BEFORE_SAVE
User = get_user_model()


class BaseApparatus(PKMixin):
    """
    Just base model for inheritance.
    Model using field "is_moderated" to don`t show to users not moderated
    instances (which can be added by any user with any params).
    All the fields with physical values using International System of Units
    """
    name = models.CharField(max_length=255)
    normative_doc = models.CharField(max_length=255)
    added_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    is_moderated = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def active_resistance(self, *args, **kwargs):
        raise NotImplementedError

    @property
    def reactive_resistance(self, *args, **kwargs):
        raise NotImplementedError

    @property
    def full_resistance_modal(self, *args, **kwargs):
        return math.sqrt(math.pow(self.active_resistance, 2) +
                         math.pow(self.reactive_resistance, 2))

    @property
    def full_resistance_complex(self, *args, **kwargs):
        return complex(self.active_resistance, self.reactive_resistance)

    class Meta:
        abstract = True


class BaseMotor(BaseApparatus):
    supertrancsient_resistance_relative = models.FloatField(
        blank=True,
        null=True
    )
    nominal_active_power = models.FloatField()
    nominal_voltage = models.FloatField()
    efficiency = models.FloatField()
    cos_fi = models.FloatField()
    damping_constant = models.FloatField()

    @property
    def active_resistance(self, *args, **kwargs):
        return self.reactive_resistance / (2 * math.pi * 50 *
                                           self.damping_constant)

    @property
    def reactive_resistance(self, *args, **kwargs):
        return ((self.supertrancsient_resistance_relative *
                 math.pow(self.nominal_voltage, 2)) /
                (self.nominal_active_power / (self.cos_fi * self.efficiency)))

    class Meta:
        abstract = True


class SyncMotor(BaseMotor):

    @property
    def supertrancient_emf(self, *args, **kwargs):
        sin_fi = math.sin(math.acos(self.cos_fi))
        return math.sqrt(math.pow(1 * self.cos_fi, 2) +
                         math.pow(1 * sin_fi + 1 *
                                  self.supertrancsient_resistance_relative, 2))


class AsyncMotor(BaseMotor):
    starting_current_factor = models.FloatField(blank=True, null=True)

    @property
    def supertrancient_emf(self, *args, **kwargs):
        sin_fi = math.sin(math.acos(self.cos_fi))
        return math.sqrt(math.pow(1 * self.cos_fi, 2) +
                         math.pow(1 * sin_fi - 1 *
                                  self.supertrancsient_resistance_relative, 2))

    @hook(BEFORE_SAVE)
    def pre_save_signal(self, *args, **kwargs):
        if not self.supertrancsient_resistance_relative:
            self.supertrancsient_resistance_relative = \
                1 / self.starting_current_factor


class Transformer(BaseApparatus):
    nominal_voltage_high = models.FloatField()
    nominal_voltage_low = models.FloatField()
    nominal_power = models.FloatField()
    short_circuit_voltage = models.FloatField()
    short_circuit_active_losses = models.FloatField()

    @property
    def active_resistance(self, *args, **kwargs):
        return (math.pow(self.nominal_voltage_high, 2) *
                self.short_circuit_active_losses * math.pow(10, -3) /
                math.pow(self.nominal_power, 2))

    @property
    def reactive_resistance(self, *args, **kwargs):
        return (self.short_circuit_voltage *
                math.pow(self.nominal_voltage_high, 2) /
                (self.nominal_power * 100))


class AutoTransformer(BaseApparatus):
    nominal_voltage_high = models.FloatField()
    nominal_voltage_mid = models.FloatField()
    nominal_voltage_low = models.FloatField()
    nominal_power = models.FloatField()
    short_circuit_voltage_high_mid = models.FloatField()
    short_circuit_voltage_high_low = models.FloatField()
    short_circuit_voltage_mid_low = models.FloatField()
    short_circuit_active_losses_high_mid = models.FloatField()
    short_circuit_active_losses_high_low = models.FloatField()
    short_circuit_active_losses_mid_low = models.FloatField()

    @property
    def active_resistance(self, high_stage=None, low_stage=None):
        # Todo: exception
        active_losses = None
        if high_stage == 'high' and low_stage == 'mid':
            active_losses = self.short_circuit_active_losses_high_mid
        elif high_stage == 'high' and low_stage == 'low':
            active_losses = self.short_circuit_active_losses_high_low
        elif high_stage == 'mid' and low_stage == 'low':
            active_losses = self.short_circuit_active_losses_mid_low
        return (math.pow(self.nominal_voltage_high, 2) * active_losses *
                math.pow(10, -3) /
                math.pow(self.nominal_power, 2))

    @property
    def reactive_resistance(self, high_stage=None, low_stage=None):
        # Todo: exception
        short_circuit_voltage = None
        if high_stage == 'high' and low_stage == 'mid':
            short_circuit_voltage = self.short_circuit_voltage_high_mid
        elif high_stage == 'high' and low_stage == 'low':
            short_circuit_voltage = self.short_circuit_voltage_high_low
        elif high_stage == 'mid' and low_stage == 'low':
            short_circuit_voltage = self.short_circuit_voltage_mid_low
        return (short_circuit_voltage * math.pow(self.nominal_voltage_high, 2)
                / (self.nominal_power * 100))


class Generator(BaseMotor):

    @property
    def supertrancient_emf(self, *args, **kwargs):
        sin_fi = math.sin(math.acos(self.cos_fi))
        return math.sqrt(math.pow(1 * self.cos_fi, 2) +
                         math.pow(1 * sin_fi + 1 *
                                  self.supertrancsient_resistance_relative, 2))
