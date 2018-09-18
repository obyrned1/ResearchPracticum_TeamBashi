from django.contrib import admin

# Register your models here.
from .models import Shape, Timetable, Stop

# admin.site.register(Shape)
#
# admin.site.register(Timetable)

# admin.site.register(Stop)

# Define the admin class
class StopAdmin(admin.ModelAdmin):
    list_display = ('stop_id', 'stop_name', 'stop_lat', 'stop_lon')
    fields = ('stop_id', 'stop_name', ('stop_lat', 'stop_lon'))

# Register the admin class with the associated model
admin.site.register(Stop, StopAdmin)

# Register the Admin classes for Shape using the decorator
@admin.register(Shape)
class ShapeAdmin(admin.ModelAdmin):
    list_display = ('shape_id', 'shape_pt_lat', 'shape_pt_lon', 'shape_pt_sequence')
    fieldsets = (('Shape_information', {'fields': ('shape_id',  'shape_pt_sequence', ('shape_pt_lat', 'shape_pt_lon'))}), ('Related_stop_information', {"fields": ('prog_number', 'stop_id')}))

# Register the Admin classes for TimeTable using the decorator
@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('trip_id', 'departure_time', 'prog_number', 'line_ID')
    list_filter = ('line_ID', 'weekday')