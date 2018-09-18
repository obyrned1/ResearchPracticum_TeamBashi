from django.http import HttpResponse
from django.shortcuts import render
import json
from . import preprocessing
import datetime
import time



def index(request):
    file = "polls/static/polls/stops.json"
    with open(file) as f:
        stopData = json.load(f)
    stop_data = json.dumps(stopData)
    return render(request, 'polls/index.html', {'stop_data': stop_data})


def AJAX(request):
    if request.method == "POST":
        print()
        print()
        print("****Receive Post****")
        print()
        print()

        # retrieve information passed back from index
        routesDict = json.loads(request.POST["routesDict"])
        print(routesDict)
        timestamp = int(request.POST['timestamp'])
        print("timestamp: ", timestamp)

        finalRoutes = []
        for j in range(0, len(routesDict)):
            routeOption = routesClass(routesDict[j], timestamp)
            finalRoutes.append(routeOption.getRouteOption())
            print(finalRoutes)

        return HttpResponse(json.dumps(finalRoutes))
    return render(request)


class routesClass():

    def __init__(self, routeOption, timestamp):

        self.routeOption = routeOption
        self.timestamp = timestamp

        self.timestampConvert = datetime.datetime.fromtimestamp(self.timestamp / 1000.0)
        self.timeNowSecs = self.getTimeNow(self.timestampConvert)
        self.hour = self.timestampConvert.hour
        self.weekday = self.timestampConvert.weekday()
        self.weekdayAdjust = preprocessing.getWeekdayAdjust(self.weekday)
        self.weather = preprocessing.getWeatherInfo(timestamp / 1000)
        self.getRouteInfo()

    def getRouteOption(self):
        return self.routeOption

    def getTimestampConvert(self):
        return self.timestampConvert

    def getHour(self):
        return self.hour

    def getWeekday(self):
        return self.weekday

    def getTimeNow(self, timestampConvert):

        x = str(timestampConvert.time())
        timeNow = x[:8]

        # convert these times to number of seconds since midnight, so they are comparable
        t1 = time.strptime(timeNow, '%H:%M:%S')
        timeNowSecs = int(datetime.timedelta(hours=t1.tm_hour, minutes=t1.tm_min, seconds=t1.tm_sec).total_seconds())

        return timeNowSecs

    def getRouteInfo(self):
        for i in range(0, len(self.routeOption), 1):
            if self.routeOption[i]['key'] == 'WALKING':
                # get the walktime in secs
                walkTime = self.routeOption[i]['value']
                walkTimeSecs = self.getWalkTime(walkTime)

                self.timeNowSecs += walkTimeSecs
                walkTimeMins = int(walkTimeSecs / 60)

                # pass the result back to the dict
                self.routeOption[i]['value'] = walkTimeMins
                errorC = 0
                self.routeOption[i]['error_code'] = errorC
                print()


            else:
                routeLeg = self.routeOption[i]['value']
                # print("routeleg", routeLeg)
                legOrigin = str(routeLeg[0])
                print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy", legOrigin)
                legDestination = str(routeLeg[1])
                RouteLine = str(routeLeg[2])
                legRouteLine = RouteLine.upper()
                legRouteLine = legRouteLine.strip()
                # print(legRouteLine)
                legHeadline = str(routeLeg[3])
                stopsDict = preprocessing.stopCordToID(legRouteLine)
                # print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",stopsDict)
                departure = preprocessing.findStop(stopsDict, legOrigin)
                if departure == None:
                    self.routeOption = {}
                    break
                    # if we cant map the latlong to stop id, we need another stop id
                    # we need to figure out how to get another ID
                    # or else dont use our prediciton and just use googles info
                    # sunday timetable seems to be a nightmare

                arrival = preprocessing.findStop(stopsDict, legDestination)

                departDetails = preprocessing.departQuery(departure, legHeadline, legRouteLine,
                                                          str(self.timeNowSecs), self.weekdayAdjust)

                print("depart query returns:", departDetails)

                departDict = self.getBusDetailDict(departDetails, departure, legRouteLine)

                # make the list into a string
                tripIDs = list(departDict.keys())
                # must strip out the [] for the query to work -> " "key", "key"..."
                # want to extract the keys and use them for one query, rather than a query for each tripID
                # print(tripIDs)

                arriveDetails = preprocessing.arriveQuery(arrival, tripIDs)

                print("arrive query returns:", arriveDetails)

                arriveDict = self.getBusDetailDict(arriveDetails, arrival, legRouteLine)

                # print(arriveDict)
                # print(departDict)

                self.handleWaitTimes(departDict, arriveDict, i)

        print(self.routeOption)
        return self.routeOption

    def getWalkTime(self, walkTime):
        # print("walkitimexxxxx", walkTime)
        walkTime = walkTime.split(' ')  # split number of mins and 'mins
        walkTime = int(walkTime[0])  # just take number of mins
        walkTimeSecs = walkTime * 60  # turn it into seconds
        print("walk time is ", walkTimeSecs)
        return walkTimeSecs

    def getBusDetailDict(self, details, stopID, legRouteLine):
        legDict = {}
        for k in range(0, len(details), 1):
            detailDict = {}
            detailDict['prog_number'] = details[k][1]
            detailDict['route_start_stop'] = details[k][2]
            detailDict['route_end_stop'] = details[k][3]
            detailDict['bus_timetable'] = details[k][4]
            #            print()
            #            print("xoxoxoxxooxoxoxoxoxo", legDict)
            # each tripID has to be separated by a comma for the arrive query to work
            # tripIDs += '"'+departDetails[k][0]+'",'

            # add the travel time of the jounrey to the dict
            detailDict['travel_time'] = preprocessing.timePredict(stopID, legRouteLine, details[k][1], self.weekday,
                                                                  self.hour, details[k][2], details[k][3], self.weather)

            legDict[details[k][0]] = detailDict

        return legDict

    def handleWaitTimes(self, departDict, arriveDict, legNumber):

        current_low_wait_time = 0
        current_low_bus_time = 0
        timetable_results = []
        count = 0
        for key in arriveDict:
            print()
            #            print(departDict[key])
            count += 1
            # select the info from the arrive Dict and put it in the relevant palce in the depart dict
            departDict[key]['arrive_prog_number'] = arriveDict[key]['prog_number']
            # add the arrive prog number
            departDict[key]['arrive_travel_time'] = arriveDict[key]['travel_time']  # append the time to stop

            timeToStart = departDict[key]['travel_time']
            timetableTime = departDict[key]['bus_timetable']

            bus_arrives_at_stop = timeToStart + timetableTime

            print()
            print("now inspecting:", timetableTime)
            print()
            print("bus_arrives_at_stop:", bus_arrives_at_stop)
            print("time after walk / time now: ", self.timeNowSecs)
            if self.timeNowSecs < bus_arrives_at_stop:
                bus_arrives_adjust = str(datetime.timedelta(seconds=bus_arrives_at_stop))
                final_time = " " + str(bus_arrives_adjust)[:-3]
                if final_time not in timetable_results:
                    timetable_results.append(final_time)
            timetable_results = sorted(timetable_results)

            wait_time = bus_arrives_at_stop - self.timeNowSecs
            print("waiting time:", wait_time)
            if wait_time > 0:
                timeToStop = departDict[key]['arrive_travel_time']
                print("time to start", timeToStart)
                print("time to stop", timeToStop)
                busTime = timeToStop - timeToStart
                print("bus journey time is ", busTime)
                print()
                if current_low_wait_time == 0:
                    current_low_wait_time = wait_time
                    current_low_bus_time = busTime
                    print("current_low_wait_time ", current_low_wait_time)
                elif wait_time < current_low_wait_time:
                    current_low_wait_time = wait_time
                    current_low_bus_time = busTime

            if count == len(departDict.keys()):
                print()
                if current_low_wait_time > 0:
                    current_low_bus_time_Mins = int(current_low_bus_time / 60)
                    current_low_wait_time_Mins = int(current_low_wait_time / 60)
                    print("the low wait time and bus times: ", current_low_wait_time_Mins, "   ",
                          current_low_bus_time_Mins)
                    if current_low_bus_time_Mins > 0:
                        self.routeOption[legNumber]['value'] = [current_low_bus_time_Mins,
                                                                current_low_wait_time_Mins], timetable_results
                        errorCode = 0
                        self.routeOption[legNumber]['error_code'] = errorCode
                        print("submit to dict:", self.routeOption[legNumber]['value'])
                        self.timeNowSecs += current_low_wait_time
                        self.timeNowSecs += current_low_bus_time
                    else:
                        errorCode = 1
                        self.routeOption[legNumber]['error_code'] = errorCode
                else:
                    errorCode = 1
                    self.routeOption[legNumber]['error_code'] = errorCode
                print()
                print()
                print("----------------------------------------------------------------------------------------")
                print("dict is:", self.routeOption[legNumber])
                print("----------------------------------------------------------------------------------------")
                print()
                print()

        print()
        print()
        print("----------------------------------------------------------------------------------------")
        print("final dict is:", self.routeOption)
        print("----------------------------------------------------------------------------------------")
        print()
        print()
