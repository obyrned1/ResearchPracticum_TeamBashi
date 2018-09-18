from django.http import HttpResponse
from django.shortcuts import render
import json
# Create your views here.
import django
django.setup()
from .models import Shape, Timetable
import datetime
import time
from .updateTimetable import test
from django.db import models
from django.db.models.functions import Length, Upper
import multiprocessing
from django.db import transaction
import pandas as pd
from sklearn.externals import joblib
import urllib.parse
import urllib.request
import os
import os.path
from polls import preprocessing
from django.db.models import F
from django_bulk_update.helper import bulk_update
from django.template.loader import render_to_string

def func(lineid):
    weatherday = WeatherForDay()
    weekdayAdjust = weekdayNow()
    start_time = time.time()
    modelname = "./polls/routeFiles/" + lineid + ".sav"
    normname = "./polls/routeFiles/n" + lineid + ".sav"
    columnname = "./polls/routeFiles/c" + lineid + ".csv"
    loaded_mlp = joblib.load(modelname)
    loaded_scaler = joblib.load(normname)
    columnsname = pd.read_csv(columnname).columns
    with transaction.atomic():
        line_145 = Timetable.objects.select_for_update().filter(weekday=weekdayAdjust).filter(line_ID=lineid).distinct()
        for i in line_145:
            weather = weatherday[i.hour]
            if i.hour == 25:
                hour = 1
            else:
                hour = i.hour
            data = [{
                "stopID_" + str(i.stop_id): 1,
                "progrnumber_" + str(i.prog_number): 1,
                "weekday_" + str(weekdayAdjust): 1,
                "hour_" + str(hour): 1,
                "route_start_stop_" + str(i.route_start_stop): 1,
                "route_end_stop_" + str(i.route_end_stop): 1,
                "rain": weather['rain'],
                "temp": weather['temp'],
                "wdsp": weather['wind'],
            }]

            df = pd.DataFrame(data, columns=columnsname)
            #    print(df)
            df = df.fillna(0)
            normalized_df = loaded_scaler.transform(df)
            big_df = pd.DataFrame(normalized_df, columns=columnsname)
            X_df = big_df.drop(['target'], axis=1)
            target = loaded_mlp.predict(X_df)
            big_df['target'] = target
            predictionTime = loaded_scaler.inverse_transform(big_df)
            predictionTime = pd.DataFrame(predictionTime, columns=columnsname)
            predict = str(predictionTime['target']).replace(" ", "")
            predict = predict[1:]
            i.planned_departure_time = i.route_start_time + int(predict.split(".")[0])
            i.save()
    # bulk_update(line_145, update_fields="planned_departure_time")

def weekdayNow():
    datetime_now = datetime.datetime.now()
    weekday = datetime_now.weekday()
    return preprocessing.getWeekdayAdjust(weekday)

def CountModels():
    file_set =set()
    file_list = os.listdir(os.path.join(os.path.dirname(__file__), "..\polls\\routeFiles"))
    for file in file_list:
        if file.endswith(".csv"):
            file_set.add(file.split('.')[0][1:])
    return file_set


def WeatherForDay():
    url = "http://api.openweathermap.org/data/2.5/forecast?id=2964574&units=metric&APPID=31f19a108384bc317e2d91c5621c791e"
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode('utf-8-sig'))
    # Return only the data for the next 24 hours
    weatherForday={}
    timestamp = data["list"][0]["dt"]
    date =datetime.datetime.fromtimestamp(timestamp)
    hour = date.hour
    print(hour)
    for i in range(9):
        hour_weather = data["list"][i-1]
        weatherDict = {}
        weatherDict["temp"] = hour_weather["main"]["temp"]
        weatherDict["wind"] = hour_weather["wind"]["speed"]
        try:
            rain = hour_weather["main"]["rain"]
        except KeyError:
            rain = 0
        weatherDict["rain"] = rain
        weatherForday[(hour + i*3)%26] = weatherDict
        weatherForday[(hour + i*3 + 1)%26] = weatherDict
        weatherForday[(hour + i*3 + 2)%26] = weatherDict

    return weatherForday


def testCreateActualtime():
    # num_processes = 2
    # pool = multiprocessing.Pool(processes=num_processes)
    test_lineList = CountModels()
    # Test the time without the multiprocessing
    # start_time = time.time()
    # pool.map(func, test_lineList)
    # print("The concurrent running time will be :")
    # print((time.time() - start_time))
    #Test the time without the multiprocessing
    print("NO multiprocessing :")
    start_time = time.time()
    for i in test_lineList:
        func(i)
    print((time.time()-start_time))




def checkBusPosition(timeNow, trip_ID, prog_numebr):
    weather = preprocessing.getWeatherInfo()
    prognumber =prog_numebr
    # hour = 22
    predictedtime = list(Timetable.objects.filter(trip_id=trip_ID).filter(prog_number=prognumber).values("stop_id","line_ID","weekday","route_start_stop","route_end_stop","route_start_time"))[0]
    print("The number of record has been changed.")
    print(len(predictedtime))
    predictedPeriod = preprocessing.timePredict(predictedtime["stop_id"], predictedtime["line_ID"], prognumber, predictedtime["weekday"], hour, predictedtime["route_start_stop"],predictedtime["route_end_stop"], weather)
    predictedNow =  predictedtime["route_start_time"] + predictedPeriod
    start_predictedNow =  predictedNow
    end_predictedNow = predictedNow
    while True:
        if start_predictedNow > timeNow:
            prognumber = prognumber - 1
            if prognumber == 1:
                break
            end_predictedNow = start_predictedNow
            print("The single request to database is")
            start_time = time.time()
            predictedtime = list(Timetable.objects.filter(trip_id=trip_ID).filter(prog_number=prognumber).values("stop_id","line_ID","weekday","route_start_stop","route_end_stop","route_start_time"))[0]
            print((time.time() - start_time))
            print(predictedtime)
            print("The time to call each model is")
            start_time = time.time()
            predictedPeriod = preprocessing.timePredict(predictedtime["stop_id"], predictedtime["line_ID"], prognumber,
                                                        predictedtime["weekday"], hour,
                                                        predictedtime["route_start_stop"],
                                                        predictedtime["route_end_stop"], weather)
            print((time.time() - start_time))
            start_predictedNow = predictedtime["route_start_time"]+predictedPeriod
        else:
            prognumber = prognumber + 1
            start_predictedNow = end_predictedNow
            predictedtime = list(Timetable.objects.filter(trip_id=trip_ID).filter(prog_number=prognumber).values("stop_id", "line_ID","weekday","route_start_stop","route_end_stop","route_start_time"))[0]
            print(predictedtime)
            predictedPeriod = preprocessing.timePredict(predictedtime["stop_id"], predictedtime["line_ID"], prognumber, predictedtime["weekday"], hour, predictedtime["route_start_stop"], predictedtime["route_end_stop"], weather)
            end_predictedNow = predictedtime["route_start_time"]+predictedPeriod

        if start_predictedNow <= timeNow and end_predictedNow >= timeNow:
            break

    print("the start of predicted time")
    print(start_predictedNow)
    print("the end of predicted time")
    print(end_predictedNow)
    print("the prognumber is ")
    print(prognumber)

    return prognumber

def findBusPosition(tripID, secondNow):
    res = Timetable.objects.filter(trip_id=tripID).annotate(departureDiff = F("planned_departure_time") - secondNow).filter(departureDiff__lt=0).order_by("-departureDiff").values("prog_number", "line_ID", "trip_id", "planned_departure_time", "distance", "shape_dist_traveled")[0]
    print(res)

def index(request):
    return render(request, 'stars/loading.html')






def mapper(request):
    """ View function for home page of site."""

    timeNow = datetime.datetime.now().time()
    secondNow = (timeNow.hour * 60 + timeNow.minute) * 60 + timeNow.second

    # CountModels()
    # print(WeatherForDay())
    # testCreateActualtime()
    # line_145 = list(Timetable.objects.filter(weekday="y102n").filter().filter(line_ID=145).distinct().values("trip_id","prog_number","departure_time","planned_departure_time"))
    # for i in line_145:
    #     print(i)
    shapeID  = Timetable.objects.filter(route_start_time__lte=secondNow).filter(route_end_time__gte=secondNow).filter(line_ID=145).distinct()


    shapeID_sql = "SELECT DISTINCT T3.id, T3.trip_id, T3.shape_id, T3.line_ID FROM( SELECT id, trip_id, MAX(planned_departure_time) AS end_time From stars_Timetable GROUP BY trip_id HAVING  MAX(planned_departure_time) >= %s) T1" + \
    " JOIN (SELECT id, trip_id, MIN(planned_departure_time) AS start_time FROM stars_Timetable GROUP BY trip_id HAVING MIN(planned_departure_time) <= %s ) T2 ON T1.trip_id = T2.trip_id JOIN stars_Timetable T3 ON T3.trip_id = T2.trip_id"


    third_sql = "SELECT DISTINCT T4.id, T4.trip_id, T4.shape_id, T4.prog_number, T4.line_ID FROM( SELECT id,trip_id, MIN(planned_departure_time - %s) AS minperiod FROM (SELECT DISTINCT T3.id, T3.trip_id, T3.planned_departure_time FROM( SELECT id, trip_id, MAX(planned_departure_time) AS end_time From stars_Timetable GROUP BY trip_id HAVING  MAX(planned_departure_time) >= %s) T1" + \
    " JOIN (SELECT id, trip_id, MIN(planned_departure_time) AS start_time FROM stars_Timetable GROUP BY trip_id HAVING MIN(planned_departure_time) <= %s ) T2 ON T1.trip_id = T2.trip_id JOIN stars_Timetable T3 ON T3.trip_id = T2.trip_id) GROUP BY trip_id) T5" + \
                " JOIN ( SELECT *, MIN(planned_departure_time- %s) AS period  FROM ( SELECT id,trip_id, MIN(planned_departure_time - %s) AS minperiod FROM (SELECT DISTINCT T3.id, T3.trip_id, T3.planned_departure_time FROM( SELECT id, trip_id, MAX(planned_departure_time) AS end_time From stars_Timetable GROUP BY trip_id HAVING  MAX(planned_departure_time) >= %s) T1" + \
    " JOIN (SELECT id, trip_id, MIN(planned_departure_time) AS start_time FROM stars_Timetable GROUP BY trip_id HAVING MIN(planned_departure_time) <= %s ) T2 ON T1.trip_id = T2.trip_id JOIN stars_Timetable T3 ON T3.trip_id = T2.trip_id ) T4 ON T4.trip_id = T5.trip_id AND T4.period = T5.minperiod"



    all_sql = "SELECT DISTINCT T4.id, T4.line_ID, T4.trip_id, T4.shape_id, T6.prog_number AS next_prognumber, T4.prog_number, T4.line_ID,%s - T4.planned_departure_time AS previoustime, ABS(T6.planned_departure_time - %s) AS nexttime FROM( SELECT id, trip_id, MAX(planned_departure_time) AS end_time From stars_Timetable GROUP BY trip_id HAVING  MAX(planned_departure_time) >= %s) T1" + \
    " JOIN (SELECT id, trip_id, MIN(planned_departure_time) AS start_time FROM stars_Timetable GROUP BY trip_id HAVING MIN(planned_departure_time) <= %s ) T2 ON T1.trip_id = T2.trip_id"+ \
              " JOIN ( SELECT trip_id, MIN( %s - planned_departure_time) AS minperiod FROM stars_Timetable WHERE planned_departure_time - %s < 0  GROUP BY trip_id) T5 ON T2.trip_id = T5.trip_id AND T4.period = T5.minperiod" + \
        " JOIN ( SELECT *,  %s - planned_departure_time AS period  FROM stars_Timetable ) T4  ON T4.trip_id = T2.trip_id AND T4.period = T5.minperiod" + \
    " JOIN ( SELECT * FROM stars_Timetable) T6 ON T4.trip_id = T6.trip_id AND T4.prog_number = T6.prog_number - 1 "
    start_time = time.time()
    shapeDict = {}
    shapeRoutesSet = set()
    allQuerySet = Timetable.objects.raw(all_sql, [secondNow, secondNow, secondNow, secondNow, secondNow, secondNow, secondNow])
    for i in allQuerySet:
        shapeRoutesSet.add(i.shape_id)
        if i.shape_id in shapeDict:
            shapeDict[i.shape_id]["position"].append({i.trip_id: [i.line_ID, i.previoustime/(i.previoustime+i.nexttime)* i.distance + i.shape_dist_traveled]})
        else:
            shapeDict[i.shape_id] ={ "position": [{i.trip_id: [i.line_ID, i.previoustime/(i.previoustime+i.nexttime)* i.distance + i.shape_dist_traveled]}]}
    # print(allQuerySet.length)
    print((time.time() - start_time))
    print("******************************************")
    print()
    print("******************************************")

    # start_time = time.time()
    # shapeQuerySet = Timetable.objects.raw(shapeID_sql, [secondNow, secondNow])
    #
    # print(shapeQuerySet.query)
    #
    # shapeset = set()
    # shapeRoutesSet = set()
    # for i in shapeQuerySet:
    #     shapeset.add(i.trip_id)
    #     shapeRoutesSet.add(i.shape_id)
    #     # if i.route_start_time >= secondNow or i.route_end_time <= secondNow:
    #     #     print("The selection has some problems.")
    # for i in shapeset:
    #     findBusPosition(i, secondNow)
    #
    # print(shapeset)
    # print((time.time() - start_time))
    # print(len(shapeset))
    # print("******************************************")
    # print()
    # print("******************************************")

    # new_subquery = shapeID.annotate(mycolumn = F("departure_time") - secondNow)
    # max_subquery = new_subquery.values("trip_id").annotate(maxcolumn = Max('mycolumn'))
    # queryset = new_subquery.filter(mycolumn = Subquery(max_subquery.values("trip_Id"))).values("departure_time","mycolumn","trip_id")

    raw_sql = "SELECT DISTINCT T1.id, T1.trip_id, T1.planned_departure_time, T1.prog_number, T1.line_ID" + \
" FROM ( SELECT trip_id, MIN(period) AS minperiod FROM ( SELECT DISTINCT id, trip_id, planned_departure_time, prog_number, ABS(planned_departure_time - %s) AS period FROM stars_Timetable WHERE weekday= 'y102m' AND route_start_time < %s AND route_end_time >= %s ) AS s2" + \
" GROUP BY trip_id ) AS T2  LEFT JOIN ( SELECT DISTINCT id, trip_id, planned_departure_time, prog_number, line_ID, ABS(planned_departure_time - %s) AS period FROM stars_Timetable WHERE route_start_time <= %s AND route_end_time >= %s) AS T1" + \
" ON T1.trip_id = T2.trip_id AND T1.period= T2.minperiod"


    # start_time = time.time()
    # params = {}
    # params["now"] = str(secondNow)
    # paramsList = [secondNow, secondNow, secondNow, secondNow, secondNow, secondNow]
    # rawQueryset = Timetable.objects.raw(raw_sql, paramsList)
    # print(rawQueryset.query)
    # raw = list(rawQueryset)
    # print(len(raw))
    # for s in rawQueryset:
    #     print(s.trip_id, s.departure_time, s.prog_number, s.line_ID)
        # iod = checkBusPosition(secondNow, s.trip_id, s.prog_number)
        # print(iod)
    # print((time.time() - start_time))

    # print("&&&&&&&&&&&&&&&&&&&")
    # trips = list(set(shapeID.values_list("trip_id", flat=True)))
    # print("trips")
    # print(len(trips))
    # tripDict = {}
    # start_time = time.time()
    # for trip in trips:
    #     tripsOnRoad = shapeID.filter(trip_id=trip).filter(departure_time__lte=secondNow).order_by('-departure_time').values("departure_time", "trip_id", "prog_number")[0]
    #     tripDict[trip] = tripsOnRoad
    # print("Triptime")
    # print((time.time()-start_time))
    # print(len(tripDict))

    # print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&The second way")
    # start_time = time.time()
    # tripOnroad2 = [
    #     shapeID.filter(trip_id=trip).filter(departure_time__lte=secondNow).order_by('-departure_time').values(
    #         "departure_time", "trip_id", "prog_number")[0] for trip in shapeID.values_list("trip_id", flat=True)]
    # print((time.time() - start_time))
    # print(len(tripOnroad2))

    print('****************************')
    # shapes = list(set(shapeID.values_list("shape_id", flat=True)))
    # print(shapes)
    start_time = time.time()
    for shape in shapeRoutesSet:
        shapeQuerySet = Shape.objects.filter(shape_id=shape).order_by('shape_pt_sequence').values()
        shapeDict[shape]["shapeList"] = list(shapeQuerySet)
    # print(shapeQuerySet)
    # shapeList = list(shapeQuerySet)
    print("Shapetime")
    print((time.time()-start_time))
    print(len(shapeDict))
    # print((set(shapeID)))
    # print(len(shapeID))
    # shapeID1 = Timetable.objects.filter(trip_id="1319.y102m.60-39A-d12-1.286.I").distinct().values_list("shape_id", flat=True)
    # print("*****************")
    # # print(shapeID1)
    # shapeQuerySet1 = Shape.objects.filter(shape_id=shapeID1[0]).order_by('shape_pt_sequence').values()
    # shapeList1 = list(shapeQuerySet1)
    #
    # shapeID2 = Timetable.objects.filter(trip_id="14153.y102n.60-11-d12-1.17.I").distinct().values_list("shape_id", flat=True)
    # print("*****************")
    # # print(shapeID2)
    # shapeQuerySet2 = Shape.objects.filter(shape_id=shapeID2[0]).order_by('shape_pt_sequence').values()
    # shapeList2 = list(shapeQuerySet2)
    #
    # shapeList ={ 0: shapeList1, 1: shapeList2}

    shape_json = json.dumps(shapeDict)
    return HttpResponse(shape_json)




def trip_info(request):
    trip_id = request.GET.get('id')
    position = request.GET.get('pos')
    print(position)
    print("The request has been received! ")
    print("########################")
    timeNow = datetime.datetime.now().time()
    print(time)
    rows = Timetable.objects.filter(trip_id=trip_id).order_by('prog_number')
    data = list(rows.values("prog_number", "stop_id__stop_id", "stop_id__stop_name", "stop_id__stop_lat", "stop_id__stop_lon"))
    stop = list(rows.values("line_ID", "stop_headsign").distinct())[0]
    html = render_to_string('stars/info.html', {'trip_info': data, 'stop': stop})
    return HttpResponse(html)