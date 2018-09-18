import csv
tripID = set();
with open("rt_trips_2017_I_DB.txt") as f:
    for line in f:
        line_list = line.strip('\n').split(";")
        tripID.add(line_list[3])

with open("rt_trips_2016_I_DB.txt") as f:
    for line in f:
        line_list = line.strip('\n').split(";")
        tripID.add(line_list[3])
        
for i in tripID:
    filename = "trips_routes/trips_" + i + ".txt"
    with open("rt_trips_2017_I_DB.txt") as f, open(filename,'a+') as new:
        for line in f:
            line_list = line.strip('\n').split(";")
            if line_list[3]  == i:
                new.write(line)

                
        
    
