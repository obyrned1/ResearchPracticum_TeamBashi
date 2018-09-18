#!/usr/bin/env python
import os
import pandas as pd
import numpy as np
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bashi.settings")
django.setup()
from stars.models import Shape
from stars.models import Stop
from stars.models import Timetable
import time

def import_stop():
    from stars.models import Stop
    Stop.objects.all().delete()

    df = pd.read_csv("stop.csv")

    for index, row in df.iterrows():
        Stop.objects.get_or_create(stop_name = row["stop_name"], stop_lat=row["stop_lat"], stop_lon=row["stop_lon"], stop_id=row["stop_id"])
    print("********************")
    print(len(Stop.objects.all()))

def import_shape():
    from stars.models import Shape
    from stars.models import Stop
    Shape.objects.all().delete()
    df = pd.read_csv("shape.csv")

    shapes = []

    for index, row in df.iterrows():
        if(row["stop_id"] == 0):
            # print("this is none")
            stop_id = None
        else:
            # print(row["stop_id"])
            try:
                stop_id = Stop.objects.get(stop_id=row["stop_id"])
            except :
                print(row["stop_id"])
        if(row["prog_number"] == 0):
            # print("this is none")
            prog = None
        else:
            prog = row["prog_number"]
        shapes.append(Shape(shape_id=row["shape_id"], shape_pt_lat=row["shape_pt_lat"], shape_pt_lon=row["shape_pt_lon"], shape_pt_sequence=row["shape_pt_sequence"], prog_number=prog, stop_id=stop_id, next_shape_dist=row["next_shape_dist"], shape_dist_traveled=row["shape_dist_traveled"]))
    print("********************")

    Shape.objects.bulk_create(shapes)
    print(len(Shape.objects.all()))


def import_timetable():
    from stars.models import Shape
    from stars.models import Stop
    from stars.models import Timetable
    Timetable.objects.all().delete()
    df = pd.read_csv("timetable.csv", dtype={"line_ID": str})
    timetables = []
    for index, row in df.iterrows():
        if pd.isnull(row['previous_stopID']):
            # print("this is none")
            previous = None
        else:
            # print(row["stop_id"])
            previous = Stop.objects.get(stop_id=row["previous_stopID"])

        route_start_stop = Stop.objects.get(stop_id=row["route_start_stop"])
        route_end_stop = Stop.objects.get(stop_id=row["route_end_stop"])
        stop_id = Stop.objects.get(stop_id=row["stop_id"])

        timetables.append(Timetable(trip_id=row["trip_id"], departure_time=row["departure_time"], prog_number=row["prog_number"], line_ID=row["line_ID"], previous_stopID=previous, route_start_stop=route_start_stop, route_end_stop=route_end_stop, route_end_time=row["route_end_time"], route_start_time=row["route_start_time"], weekday=row["weekday"], shape_id=row["shape_id"], stop_id=stop_id, stop_headsign=row["stop_headsign"], shape_dist_traveled=row["shape_dist_traveled"], distance=row["distance"], hour=row["hour"]))
    print("********************")

    Timetable.objects.bulk_create(timetables)
    print(len(Timetable.objects.all()))

if __name__ == "__main__":
    start_time = time.time()
    import_shape()
    print((time.time() - start_time))
    print('Done!')

