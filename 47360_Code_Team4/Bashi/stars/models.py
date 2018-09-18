from django.db import models
from django.urls import reverse

# Create your models here.


class Shape(models.Model):
    """A  class defining a  model which  is used to draw sny bas shape on the google map."""

    # Fields
    shape_id = models.CharField(max_length=20)
    shape_pt_lat = models.CharField(max_length=20)
    shape_pt_lon = models.CharField(max_length=20)
    shape_pt_sequence = models.IntegerField()
    prog_number = models.IntegerField(null=True, blank=True)
    stop_id = models.ForeignKey('Stop', on_delete=models.SET_NULL, null=True)
    next_shape_dist = models.FloatField(null=True, blank=True)
    shape_dist_traveled = models.FloatField(null=True, blank=True)

    # Metadata
    class Meta:
        ordering = ['shape_id']

    # Methods
    def __str__(self):
        return "No. "+str(self.shape_id) + " -" + str(self.shape_pt_sequence)

    def get_absolute_url(self):
        """ Returns the url to access a particular instance of the model. """
        return reverse('model-detail-view', args=[str(self.id)])


class Stop(models.Model):
    """ A  class defining a  model which  stores the information about bus stop """

    # Fields
    stop_name = models.CharField(max_length=50)
    stop_lat = models.CharField(max_length=20)
    stop_lon = models.CharField(max_length=20)
    stop_id = models.IntegerField(primary_key=True)

    # Metadata
    class Meta:
        ordering = ['stop_id']

    # Methods
    def __str__(self):
        return "No. "+str(self.stop_id) + " -"+self.stop_name

    def get_absolute_url(self):
        """ Returns the url to access a particular instance of the model. """
        return reverse('model-detail-view', args=[str(self.id)])


class Timetable(models.Model):
    """A  class defining a  model which  is used to draw sny bas shape on the google map."""

    # Fields
    trip_id = models.CharField(max_length=50)
    departure_time = models.IntegerField()
    prog_number = models.IntegerField()
    line_ID = models.CharField(max_length=5)
    service_option = (("y102m", "from Monday to Friday"), ("y102n", "sunday and monday"), ("y102o", "saturday"))
    previous_stopID = models.ForeignKey('Stop', on_delete=models.SET_NULL, null=True, blank=True, related_name="previous_stopID")
    route_start_stop = models.ForeignKey('Stop', on_delete=models.SET_NULL, null=True, blank=True,related_name="route_start_stop")
    route_end_stop = models.ForeignKey('Stop', on_delete=models.SET_NULL, null=True, blank=True,related_name="route_end_stop")
    route_start_time = models.IntegerField()
    route_end_time = models.IntegerField()
    weekday = models.CharField(max_length=5, choices=service_option)
    stop_id = models.ForeignKey('Stop', on_delete=models.SET_NULL, null=True)
    shape_id = models.CharField(max_length=20)
    planned_departure_time = models.IntegerField(null=True, blank=True)
    stop_headsign = models.CharField(max_length=50,null=True, blank=True)
    shape_dist_traveled = models.FloatField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    hour = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['trip_id']

    # Methods
    def __str__(self):
        return "No. "+self.trip_id + ' -'+str(self.prog_number)

    def get_absolute_url(self):
        """ Returns the url to access a particular instance of the model. """
        return reverse('model-detail-view', args=[str(self.id)])