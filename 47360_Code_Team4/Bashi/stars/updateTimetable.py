import django
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bashi.settings")
from .models import Shape, Timetable
import datetime
import time
from polls import preprocessing
import multiprocessing

def func(lineid):
    weather = preprocessing.getWeatherInfo()
    weekdayAdjust = weekdayNow()
    print("weekdayAdjust")
    line_145 = Timetable.objects.filter().filter(line_ID=lineid).distinct()
    start_time = time.time()
    for i in line_145:
        i.planned_departure_time = i.route_start_time + preprocessing.timePredict(i.stop_id, i.line_ID, i.prog_number, weekdayAdjust, i.hour, i.route_start_stop, i.route_end_stop, weather)
        i.save()
    print(lineid, (time.time() - start_time), 'finished')

def weekdayNow():
    datetime_now = datetime.datetime.now()
    weekday = datetime_now.weekday()
    return preprocessing.getWeekdayAdjust(weekday)

# def weatherforWholeDay()


# if __name__ == '__main__':
def test():
    num_processes = multiprocessing.cpu_count()-1
    pool = multiprocessing.Pool(processes=num_processes)
    test_lineList = ['145', '39A', '46A', '11', '17', '1']
    start_time = time.time()
    result = pool.map(func, test_lineList)
    print("The concurrent running time will be :")
    print((time.time() - start_time))
    # Test the time without the multiprocessing
    print("NO multiprocessing :")
    start_time = time.time()
    for i in test_lineList:
        func(i)
    print((time.time()-start_time))