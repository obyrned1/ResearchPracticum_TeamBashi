filename = "outliers.txt"
with open("rt_trips_2017_I_DB.txt") as f, open(filename,'w') as new:
    for line in f:
        line_list = line.strip('\n').split(";")
        if line_list[12]  != "" and line_list[13]  != "":
            new.write(line)

with open("rt_trips_2016_I_DB.txt") as f, open(filename,'a+') as new:
    for line in f:
        line_list = line.strip('\n').split(";")
        if line_list[12]  != "" and line_list[13]  != "":
            new.write(line)

                
        
    
