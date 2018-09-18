import csv
import pandas as pd
import numpy as np
import re
import geopy
from geopy.distance import vincenty
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn import linear_model
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
from itertools import groupby
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error

def get_destinationstop(group):
    group.sort_values(['progrnumber'],ascending=False)
    max_sequence_row = group.ix[group['progrnumber'].idxmax()]
    group["route_end_stop"] = max_sequence_row.stop_id
    return group

def get_departurestop(group):
    group.sort_values(['progrnumber'],ascending=True)
    max_sequence_row = group.ix[group['progrnumber'].idxmin()]
    group["route_start_stop"] = max_sequence_row.stop_id
    return group


bankHolidays =["2016-01-01","2016-03-17","2016-03-25","2016-03-28","2016-05-02","2016-06-06","2016-08-01","2016-10-31","2016-12-25","2016-12-26","2016-12-27","2016-12-28","2017-01-01","2017-01-02","2017-03-17","2017-04-14","2017-04-17","2017-05-01","2017-06-05","2017-08-07","2017-10-30","2017-12-25","2017-12-26","2017-12-27"]

lineID = set(('18','47','68','69','69X','7D','46A','1','145','39A'))
# lineID = ['145']

#with open("rt_trips_2017_I_DB.txt") as f:
#    for line in f:
#        line_list = line.strip('\n').split(";")
#        lineID.add(line_list[3])

#with open("rt_trips_2016_I_DB.txt") as f:
#    for line in f:
#        line_list = line.strip('\n').split(";")
#        lineID.add(line_list[3])

#existed = set(('lineid','4','7B','11','14','14c','25B','26','31A','33','33X','37','38B','40D','41X','43','44B','51D','51X','53','56A','63','66','66B','66X','67','76','77A','83','104','130','184','236','239','69X','114','16','17A','40B','7A','33A','45A','7','122','185','38A','18','32','25','31D','70D','123','41C','46A','44','13','15A','102','79','14C','68X'))
#existed2 = set(('79A','41B','29A','77X','7D','40','25X','270','65B','33B','84X','145','27B','220','65','83A','61','8'))
#existed3 = set(('161','27X','120','39','38D','27A','76A','84','27','54A','1','68','16C','46E','116','15B','31B','42','84A','47','142','68A','42D','118'))
#lineID = lineID.difference(existed)
#lineID = lineID.difference(existed2)
#lineID = lineID.difference(existed3)




for i in lineID:
    print(i)
    tripsname = "trips_routes/trips_" + i + ".txt"
    trips = pd.read_csv(tripsname, sep=';',names = ["datasource","dayofservice","tripID","lineid","routeid","direction","plannedtime_arr","plannedtime_dep","actualtime_arr","actualtime_dep","basin","tenderlot","suppressed","justificationid","lastupdate","note"])
    trips = trips.drop_duplicates()
    trips['dayofservice'] = pd.to_datetime(trips['dayofservice'])
    trips = trips.drop(['lineid','datasource','basin','tenderlot','lastupdate','note'], axis=1)
    trips.rename(columns ={'tripid':"tripID"},inplace = True )
    trips = trips[trips['suppressed'].isnull() & trips['justificationid'].isnull()]
    leavename = "trips_leavetimes/trips_leavetimes_" + i + ".txt"
    leavetimes = pd.read_csv(leavename, sep=';',names = ["datasource","dayofservice","tripID","progrnumber","stop_id","plannedtime_arr_stop","plannedtime_dep_stop","actualtime_arr_stop","actualtime_dep_stop","vehicleid","passengers","passengersin","passengersout","distance","suppressed_stop","justificationid_stop","lastupdate","note"])
    leavetimes = leavetimes.drop(['datasource','vehicleid','passengers','passengersin','passengersout','distance','lastupdate','note'], axis=1)
    leavetimes = leavetimes.drop_duplicates()
    leavetimes['dayofservice'] = pd.to_datetime(leavetimes['dayofservice'])
    leavetimes = leavetimes[leavetimes['suppressed_stop'].isnull() & leavetimes['justificationid_stop'].isnull()]
    leavetimes = leavetimes.drop(['suppressed_stop','justificationid_stop'],axis = 1)
    final = pd.merge(leavetimes, trips, on=['tripID','dayofservice'])
    final['dayofservice_new'] = final.dayofservice.values.astype(np.int64) // 10 ** 9
    final = final.dropna(how='all')
    final = final.drop(['suppressed','justificationid'],axis =1)
    weatherstation = pd.read_csv("bus_stops-stations.csv", sep=',')
    weatherstation = weatherstation.drop(['stop_name','stop_lat','stop_lon'], axis=1)
    final = pd.merge(final, weatherstation, on=['stop_id'])
    weather = pd.read_csv("weather.csv", sep=',')
    final["timeofarrival"] = final["dayofservice_new"] + final["plannedtime_arr_stop"]
    final['timeofarrival']=pd.to_datetime(final['timeofarrival'],unit='s')
    final["date"] = pd.DatetimeIndex(final['timeofarrival']).round('H').values.astype(np.int64) // 10 ** 9
    final["year"] = pd.DatetimeIndex(final['timeofarrival']).year
    final["month"] = pd.DatetimeIndex(final['timeofarrival']).month
    final["hour"] = pd.DatetimeIndex(final['timeofarrival']).hour
    final["weekday"] = pd.DatetimeIndex(final['timeofarrival']).weekday
    final = pd.merge(final, weather, on=['date','stationid'])
    final = final.loc[~ final["dayofservice"].isin(bankHolidays)]
    # drop the month not in june and july
    final = final.loc[final["month"].isin([6,7])]
    final = final.drop(['year','month'], axis=1)
    # get the destiantion stop and departure stop
    final = final.groupby(["dayofservice","tripID"]).apply(get_destinationstop)
    final = final.groupby(["dayofservice","tripID"]).apply(get_departurestop)
    timetable = pd.read_csv("timetable.csv",dtype = {"line_ID": object})
    timetable_1 = timetable[timetable["line_ID"] == i]
    timetable_stop_1 = timetable_1[["route_end_stop","route_start_stop"]].drop_duplicates()
    final = pd.merge(final,timetable_stop_1, on = ["route_end_stop","route_start_stop"] ,how ="inner" )
    final['target'] = final['actualtime_arr_stop'] - final['plannedtime_dep']
    dataForModel =  final[["progrnumber","weekday","hour",'rain',"temp","wdsp","target","route_start_stop","route_end_stop", "stop_id"]]
    dataForModel.rename(columns = {'stop_id':'stopID'},inplace = True)
    dataForModels = pd.get_dummies(data=dataForModel, columns=['stopID','progrnumber','weekday','hour',"route_start_stop","route_end_stop"])
    #The lineRegression Results
    lr_y = dataForModels["target"]
    lr_X_train,lr_X_test, lr_y_train, lr_y_test = train_test_split(dataForModels, lr_y, test_size=0.1, random_state=0)
    lr = linear_model.LinearRegression()
    lr.fit(lr_X_train,lr_y_train)
    lr_predictions = lr.predict(lr_X_test)
    print("The linear Regression Results:")
    print(r2_score(lr_y_test,lr_predictions))
    print(mean_absolute_error(lr_y_test,lr_predictions))
    print(mean_squared_error(lr_y_test,lr_predictions))
    #Normallie the dataFrames
    scaler= StandardScaler().fit(dataForModels)
    normalized_sparsed = scaler.transform(dataForModels)
    DF = pd.DataFrame(normalized_sparsed, columns=dataForModels.columns,index=dataForModels.index)
    y = DF['target']
    X_train_y, X_test_y, y_train, y_test = train_test_split(DF,y,test_size = 0.3, random_state= 0 )
    X_train = X_train_y.drop(['target'],axis=1)
    X_test = X_test_y.drop(['target'],axis=1)
    mlp = MLPRegressor(hidden_layer_sizes=(200,200,200), max_iter = 1000, solver='lbfgs', \
                   alpha=0.01, activation = 'tanh', random_state = 8)
    mlp.fit(X_train,y_train)
    predictions = mlp.predict(X_test)
    print("The result for ANN")
    print(r2_score(y_test, predictions))

    #Denormalize for the MAE
    X_test_y.target = predictions
    prediction = scaler.inverse_transform(X_test_y)
    X_test_y.target = y_test
    actual = scaler.inverse_transform(X_test_y)
    DF_actual = pd.DataFrame(actual, columns=dataForModels.columns,index= X_test_y.index)
    DF_prediction = pd.DataFrame(prediction, columns=dataForModels.columns,index= X_test_y.index)
    print(mean_absolute_error(DF_actual.target,DF_prediction.target))
    print(r2_score(DF_actual.target,DF_prediction.target))
    print(mean_squared_error(DF_actual.target,DF_prediction.target))


    modelname =  "models/"+i + ".sav"
    normname = "models/n"+ i +".sav"
    joblib.dump(mlp,modelname)
    joblib.dump(scaler, normname)
    columnname = "models/c" +i +".csv"
    dataForModels.head(1).to_csv(columnname,header=True, index=False,columns = dataForModels.columns)


        
