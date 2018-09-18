from django.db import models

class distance_timetable_test(models.Model):
    trip_id = models.CharField(max_length = 500)
    arrival_time = models.CharField(max_length = 500)
    departure_time = models.CharField(max_length = 500)
    prog_number = models.CharField(max_length = 500)
    stop_headsign = models.CharField(max_length = 500)
    shape_dist_traveled = models.CharField(max_length = 500)
    new_stop_id = models.CharField(max_length = 500)
    line_ID = models.CharField(max_length = 500)
    weekday = models.CharField(max_length = 500)
    direction = models.CharField(max_length = 500)
    distance= models.CharField(max_length = 500)
    previous_stopID = models.CharField(max_length = 500)
    
    def __str__(self):
        return self.trip_id + ", " + self.arrival_time

