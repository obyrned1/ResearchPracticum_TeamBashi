from polls.views import routesClass
from polls.preprocessing import *

# sample data returned when directions requested from UCD to Trinity
data = [{'key': 'WALKING', 'value': '8 mins'}, {'key': 'TRANSIT', 'value': [[53.3094098, -6.218869199999972], [53.345969, -6.259292100000039], ' 46a', 'Phoenix Pk']}]

origin = [53.3094098, -6.218869199999972]
destination = [53.345969, -6.259292100000039]
legHeadline = 'Phoenix Pk'
legRouteLine = '46A'

timestamp = 1533999600000
stopDict = stopCordToID(legRouteLine)

#create the routeClass object
routeOption = routesClass(data, timestamp)
#returns the connection established with the sqlite db
conn = routeOption.getConn()


#*********** preprocessing.py ***********
def test_findStop():
    #returns the stopID closest to the given LatLng
    assert findStop(stopDict, origin) == '768'

def test_getWeekdayAdjust():
    #returns the day of the week code from the given weekday number
    assert getWeekdayAdjust(routeOption.getWeekday()) == '"y102o"'
    
def test_getWeatherInfo():
    assert getWeatherInfo(timestamp/1000) == {'rain': 0, 'temp': 18.45, 'wind': 3.35}
    
def test_departQuery():
    details =  departQuery(routeOption.getConn(), '768', legHeadline, legRouteLine, '44340', '"y102m"') 
    assert details == [('5161.y102m.60-46A-d12-1.349.I', 30, '2039', '807', 42480), ('5110.y102m.60-46A-d12-1.349.I', 30, '2039', '807', 42960), ('5130.y102m.60-46A-d12-1.349.I', 30, '2039', '807', 42000)]
        
def test_arriveQuery():
    arrival = findStop(stopDict, destination)
    details = arriveQuery(conn, arrival, "'5161.y102m.60-46A-d12-1.349.I', '5110.y102m.60-46A-d12-1.349.I','5130.y102m.60-46A-d12-1.349.I'")
    #the trips in the depart and arrive query should match up, there order may be different
    assert details == [('5110.y102m.60-46A-d12-1.349.I', 47, '2039', '807', 42960), ('5130.y102m.60-46A-d12-1.349.I', 47, '2039', '807', 42000), ('5161.y102m.60-46A-d12-1.349.I', 47, '2039', '807', 42480)]

def test_timePredict():
    #stopID, legRouteLine, prog_number, weekday, hour, route_start_stop, route_end_stop, weather
    result = timePredict('768', '46A', 30, routeOption.getWeekday(), routeOption.getHour(), '2039', '807', {'rain': 0, 'temp': 15.57, 'wind': 5.02})
    assert result == 1651
    

    
#*********** views.py ***********
def test_getTimestampConvert():
    #the timestamp is converted into a datetime object
    assert str(routeOption.getTimestampConvert()) == '2018-08-11 16:00:00'

def test_getTimeNow():
    #returns the number of seconds after midnight from the timestamp
    timestampConvert = routeOption.getTimestampConvert()
    assert routeOption.getTimeNow(timestampConvert) == 57600
    
def test_getWalkTime():
    #returns walk time in seconds from string
    assert routeOption.getWalkTime('8 mins') == 480
    
def test_getBusDetailDict():
    queryDetails = [('5161.y102m.60-46A-d12-1.349.I', 30, '2039', '807', 42480), ('5110.y102m.60-46A-d12-1.349.I', 30, '2039', '807', 42960), ('5130.y102m.60-46A-d12-1.349.I', 30, '2039', '807', 42000)]
    arrival = findStop(stopDict, destination)
    assert routeOption.getBusDetailDict(queryDetails, arrival, legRouteLine) == {'5110.y102m.60-46A-d12-1.349.I':{'bus_timetable': 42960, 'prog_number': 30, 'route_end_stop': '807', 'route_start_stop': '2039', 'travel_time': 2683}, '5161.y102m.60-46A-d12-1.349.I':{'bus_timetable': 42480, 'prog_number': 30, 'route_end_stop': '807', 'route_start_stop': '2039', 'travel_time': 2683}, '5130.y102m.60-46A-d12-1.349.I':{'bus_timetable': 42000, 'prog_number': 30, 'route_end_stop': '807', 'route_start_stop': '2039', 'travel_time': 2683}}

    
