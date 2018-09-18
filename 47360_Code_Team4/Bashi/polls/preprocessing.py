import urllib.parse
import urllib.request
import json
import geopy
from geopy.distance import vincenty
import os
import sqlite3
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.externals import joblib
from django.apps import apps
Timetable = apps.get_model('stars', 'Timetable')
Stop = apps.get_model('stars', 'Stop')
from django.db.models import Func
from django.db.models import F, ExpressionWrapper, fields
from django.db import connection
import datetime
import time


def departQuery(departure, legHeadline, legRouteLine, timeNow, weekdayAdjust):
    if type(weekdayAdjust) is not list:
        weekdayAdjust=weekdayAdjust.split(", ")
    rows = Timetable.objects.filter(stop_headsign=legHeadline).filter(line_ID=legRouteLine).filter(weekday__in=weekdayAdjust).filter(stop_id__stop_id=departure).annotate(period=Func(F('departure_time')-int(timeNow), function='ABS')).order_by('period')[:3]
    #
    # rawsql = 'SELECT id, trip_id, prog_number, route_start_time FROM stars_Timetable WHERE weekday IN (' + weekdayAdjust + ') LEFT JOIN (SELECT * WHERE stop_id = "' + departure + '" FROM stars_stop) AND line_ID = "' + legRouteLine + '" AND weekday IN (' + weekdayAdjust + ') ORDER BY ABS( departure_time-' + timeNow + ')  LIMIT 3;'
    print("the_actual_query")
    print(rows.query)
    # rows = Timetable.objects.raw(rawsql)
    rowlist = []
    for i in rows.values("trip_id", "prog_number", "route_start_stop", "route_end_stop", "route_start_time"):
        rowlist += [(i["trip_id"], i["prog_number"], i["route_start_stop"], i["route_end_stop"], i["route_start_time"])]

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(rowlist)
    return rowlist


def arriveQuery(arrival, tripID):
    # cur = conn.cursor()
    # #    print("****************************************************************")
    # #    print('SELECT trip_ID, prog_number, route_start_stop, route_end_stop, route_start_time FROM timetable WHERE trip_ID IN ('+tripID+') AND new_stop_id = "'+arrival+'";')
    #
    # response = cur.execute(
    #     'SELECT trip_ID, prog_number, route_start_stop, route_end_stop, route_start_time FROM Timetable WHERE trip_ID IN (' + tripID + ') AND new_stop_id = "' + arrival + '";')
    print("This is arrival query")
    print(tripID)
    print(arrival)
    if type(tripID) is not list:
        tripID = tripID.split(", ")
        print(tripID)
    rows = Timetable.objects.filter(trip_id__in = tripID).filter(stop_id__stop_id=arrival).values("trip_id","prog_number","route_start_stop","route_end_stop","route_start_time")
    print("This is arrival query")

    rowList = []
    for i in rows:
        rowList += [(i["trip_id"], i["prog_number"], i["route_start_stop"], i["route_end_stop"], i["route_start_time"])]

    print(rowList)
    return rowList


def timePredict(stopID, legRouteLine, prog_number, weekday, hour, route_start_stop, route_end_stop, weather):
    #    print()
    #    print("prog number ", prog_number)
    #    print()
    modelname = "polls/routeFiles/" + legRouteLine + ".sav"
    normname = "polls/routeFiles/n" + legRouteLine + ".sav"
    columnname = "polls/routeFiles/c" + legRouteLine + ".csv"

    loaded_mlp = joblib.load(modelname)
    loaded_scaler = joblib.load(normname)
    columnsname = pd.read_csv(columnname).columns

    data = [{
        "stopID_" + str(stopID): 1,
        "progrnumber_" + str(prog_number): 1,
        "weekday_" + str(weekday): 1,
        "hour_" + str(hour): 1,
        "route_start_stop_" + str(route_start_stop): 1,
        "route_end_stop_" + str(route_end_stop): 1,
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
    predict = predict.split(".")[0]
    #    print(predict)
    return int(predict)


def getWeekdayAdjust(weekday):
    if weekday < 5 and weekday > 0:
        weekdayAdjust = ['y102m', ]
    elif weekday == 5:
        weekdayAdjust = ['y102o', ]
    elif weekday == 6:
        weekdayAdjust = ['y102n', ]
    else:
        weekdayAdjust = ['y102n', 'y102m']

    return weekdayAdjust


def stopCordToID(routeID):
    # Parse the URL and get the bus route info
    stopsDict = {}
    url = "https://data.dublinked.ie/cgi-bin/rtpi/routeinformation?routeid=" + routeID + "&operator=bac&format=json"
    with urllib.request.urlopen(url) as req:
        stopsInfo = json.loads(req.read().decode("utf-8"))
        # print("3", stopsInfo)
    if stopsInfo["errorcode"] == "0":
        if stopsInfo["numberofresults"] > 0:
            for routes in stopsInfo["results"]:
                for stop in routes["stops"]:
                    stopID = stop["stopid"]
                    latitude = float(stop["latitude"])
                    longitude = float(stop['longitude'])
                    stopsDict[stopID] = {"lat": latitude, "lon": longitude}
        else:
            possibleStops = Timetable.objects.filter(line_ID=routeID).values("stop_id").distinct()
            stopInfoFromDataBase = Stop.objects.filter(stop_id__in=possibleStops).values()
            for stop in list(stopInfoFromDataBase):
                stopID = stop["stop_id"]
                latitude = float(stop["stop_lat"])
                longitude = float(stop["stop_lon"])
                stopsDict[stopID] = {"lat": latitude, "lon": longitude}

    return stopsDict


def findStop(stopsDict, stopCord):
    # Find the march stopID in the stopsDict based on stop cord
    for key in stopsDict.keys():
        stopsDict[key].update(
            {"distance": geopy.distance.vincenty([stopsDict[key]["lat"], stopsDict[key]["lon"]], stopCord).km})
    # print(stopsDict)
    s = sorted(stopsDict.items(), key=lambda x_y: x_y[1]["distance"])
    # print(s)
    return s[0][0]


def getBusstopInfo(stopID, routeID):
    # get the schedule information about bus stops
    url = "https://data.dublinked.ie/cgi-bin/rtpi/realtimebusinformation?stopid=" + stopID + "&routeid=" + routeID + "&maxresults&operator&format=json"
    with urllib.request.urlopen(url) as req:
        stopsInfo = json.loads(req.read().decode("utf-8"))

def testCreateActualtime():
    weather = getWeatherInfo()
    hour = 10
    line_145 = Timetable.objects.filter(weekday="y102n").filter().filter(line_ID=145).distinct()
    start_time = time.time()
    for i in line_145:
        i.planned_departure_time = timePredict(i.stop_id, i.line_ID, i.prognumber, "y102n", hour, i.route_start_stop, i.route_end_stop, weather)
        i.save()
    print("update the field-planned-departure-time")
    print((time.time() - start_time))


def getWeatherInfo(dt):
    url = "http://api.openweathermap.org/data/2.5/forecast?id=2964574&units=metric&APPID=31f19a108384bc317e2d91c5621c791e"
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode('utf-8-sig'))
    # Return only the data for the next 24 hours
    weatherDict = {}
    dtNow = data["list"][0]["dt"]
    indexnumber = int((dt - dtNow)/10800)
    if(indexnumber < 0):
        indexnumber = 0
    weatherDict["temp"] = data["list"][indexnumber]["main"]["temp"]
    weatherDict["wind"] = data["list"][indexnumber]["wind"]["speed"]
    try:
        rain = data["list"][indexnumber]["main"]["rain"]
    except KeyError:
        rain = 0
    weatherDict["rain"] = rain
    return weatherDict

if __name__ == "__main__":
    testCreateActualtime()
