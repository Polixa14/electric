from django.contrib import admin
from apparatus.models import Transformer, AutoTransformer, SyncMotor, \
    AsyncMotor, Generator


@admin.register(AutoTransformer)
class AutoTransformerAdmin(admin.ModelAdmin):
    list_display = ('id', )


@admin.register(Transformer)
class TransformerAdmin(admin.ModelAdmin):
    list_display = ('id', )


@admin.register(SyncMotor)
class SyncMotorAdmin(admin.ModelAdmin):
    list_display = ('id', )


@admin.register(AsyncMotor)
class AsyncMotorAdmin(admin.ModelAdmin):
    list_display = ('id', )


@admin.register(Generator)
class GeneratorAdmin(admin.ModelAdmin):
    list_display = ('id', )
