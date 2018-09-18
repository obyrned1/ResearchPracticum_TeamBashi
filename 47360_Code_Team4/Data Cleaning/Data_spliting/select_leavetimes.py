lineID = set();
with open("rt_trips_2017_I_DB.txt") as f:
    for line in f:
        line_list = line.strip('\n').split(";")
        lineID.add(line_list[3])

with open("rt_trips_2016_I_DB.txt") as f:
    for line in f:
        line_list = line.strip('\n').split(";")
        lineID.add(line_list[3])
        


for i in lineID:
    filename = "trips_leavetimes/trips_leavetimes_" + i + ".txt"
    tripsname = "trips_routes/trips_" + i + ".txt"
    tripID = set();
    with open(tripsname) as f:
        for line in f:
            line_list = line.strip('\n').split(";")
            tripID.add(line_list[2])
            
    with open("rt_leavetimes_2017_I_DB.txt") as f, open(filename,'w+') as new:
        for line in f:
            line_list = line.strip('\n').split(";")
            if line_list[3] in tripID:
                new.write(line)

    with open("rt_leavetimes_2016_I_DB.txt") as f, open(filename,'a+') as new:
        for line in f:
            line_list = line.strip('\n').split(";")
            if line_list[3] in tripID:
                new.write(line)
        
    
