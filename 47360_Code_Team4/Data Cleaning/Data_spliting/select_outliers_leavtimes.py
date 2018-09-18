filename = "outliers_leavetimes.txt"
with open("rt_leavetimes_2017_I_DB.txt") as f, open(filename,'w') as new:
    for line in f:
        line_list = line.strip('\n').split(";")
        if len(line_list) == 18:
            if line_list[14]  != "" or line_list[15]  != "":
                new.write(line)

with open("rt_leavetimes_2016_I_DB.txt") as f, open(filename,'a+') as new:
    for line in f:
        line_list = line.strip('\n').split(";")
        if len(line_list) == 18:
            if line_list[14]  != "" or line_list[15]  != "":
                new.write(line)

                
        
    
