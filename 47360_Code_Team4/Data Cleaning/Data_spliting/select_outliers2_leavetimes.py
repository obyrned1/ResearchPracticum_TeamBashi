lineID = set();
with open("outliers2_trips.txt") as f:
    for line in f:
        line_list = line.strip('\n').split(";")
        lineID.add((line_list[1],line_list[2]))

filename = "outliers2_leavetimes.txt"       
with open("rt_leavetimes_2017_I_DB.txt") as f, open(filename,'w+') as new:
    for line in f:
        line_list = line.strip('\n').split(";")
        if (line_list[1],line_list[2]) in lineID:
            new.write(line)

with open("rt_leavetimes_2016_I_DB.txt") as f, open(filename,'a+') as new:
    for line in f:
        line_list = line.strip('\n').split(";")
        if (line_list[1],line_list[2]) in lineID:
            new.write(line)