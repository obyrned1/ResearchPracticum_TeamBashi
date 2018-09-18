import urllib.parse
import urllib.request
import json
import time
import pandas as pd
from sklearn.externals import joblib
import multiprocessing
import numpy as np

def getWeatherInfo():
    url = "http://api.openweathermap.org/data/2.5/weather?id=2964574&units=metric&APPID=31f19a108384bc317e2d91c5621c791e"
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode('utf-8-sig'))
    # Return only the data for the next 24 hours
    weatherDict = {}
    weatherDict["temp"] = data["main"]["temp"]
    weatherDict["wind"] = data["wind"]["speed"]
    try:
        rain = data["main"]["rain"]
    except KeyError:
        rain = 0
    weatherDict["rain"] = rain
    return weatherDict


def timePredict(stopID, legRouteLine, prog_number, weekday, hour, route_start_stop, route_end_stop, weather):
    #    print()
    #    print("prog number ", prog_number)
    #    print()
    modelname = "models/" + legRouteLine + ".sav"
    normname = "models/n" + legRouteLine + ".sav"
    columnname = "models/c" + legRouteLine + ".csv"

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

def func(d):
	weather = getWeatherInfo()
	for index, row in d.iterrows():
		planned_departure_time = row["route_start_time"] + timePredict(row["stop_id"],row["line_ID"],row["prog_number"],row["weekday"],row["hour"],row["route_start_stop"],row["route_end_stop"],weather)
		d.loc[index, "planned_departure_time"] = planned_departure_time 
	print("finished")
	return d

# weather = getWeatherInfo()

# timetable = pd.read_csv("timetable.csv",dtype={"line_ID":str})

# timetable["planned_departure_time"] = np.nan

# timetable_145 = timetable[timetable["line_ID"]=="145"]

# start_time = time.time()
# for index, row in timetable_145.iterrows():
# 	planned_departure_time =  timePredict(row["stop_id"],row["line_ID"],row["prog_number"],row["weekday"],row["hour"],row["route_start_stop"],row["route_end_stop"],weather)
#         # planned.append(planned_departure_time)
#     timetable[index,"planned_departure_time"] = planned_departure_time 
# print((time.time() - start_time))

# num_processes = multiprocessing.cpu_count()
# chunk_size = int(timetable_145.shape[0]/num_processes)
# chunks = [timetable_145.iloc[i:i + chunk_size,:] for i in range(0, timetable_145.shape[0], chunk_size)]

# pool = multiprocessing.Pool(processes=num_processes)

# start_time = time.time()
# result = pool.map(func, chunks)
# print((time.time() - start_time))

# for i in range(len(result)):
#    # since result[i] is just a dataframe
#    # we can reassign the original dataframe based on the index of each chunk
#    timetable.ix[result[i].index] = result[i]

if __name__ == '__main__':
	timetable = pd.read_csv("timetable.csv",dtype={"line_ID":str})
	timetable["planned_departure_time"] = np.nan
	timetable_145 = timetable[timetable["line_ID"]=="145"]
	num_processes = multiprocessing.cpu_count()
	chunk_size = int(timetable_145.shape[0]/num_processes)
	chunks = [timetable_145.iloc[i:i + chunk_size,:] for i in range(0, timetable_145.shape[0], chunk_size)]
	pool = multiprocessing.Pool(processes=num_processes)
	start_time = time.time()
	result = pool.map(func, chunks)
	print((time.time() - start_time))

