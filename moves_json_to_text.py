'''
Copyright (c) 2015 Michael Stebbins
Based on code from KainokiKaede (https://gist.github.com/KainokiKaede/7251872)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

USAGE
 1. Go to: http://moves-export.herokuapp.com/
 2. Authenticate by putting PIN number into Moves app on phone
 3. Pick export from date, and hit Start Export! button
 4. Once json text is done loading, copy text from output box
 5. Go to http://jsonlint.com/, paste in code, and hit Validate
    jsonlint will help identify problems in the file (extra commas, incomplete
    bracets, etc.) Delete out these extra elements until you have valid json.
 6. Copy valid json text from jsonlint, paste into text file in python directory.
 7. Put that filename in as INPUT_FILE below.
 8. Check all USER INPUTS below, set to appropriate values for you
 9. Run this script to generate text file of walks, runs, and bikes exceeding
    the threshold seconds set in INPUTS, with activity start time in UTC time.
10. Finally, open and run textToMongo.py to upload output file to MongoLab.
'''
'''
DATA FORMATS:
list_of_days = [date,walking steps, cycle miles, run miles, [walk segments],[bike segments],[run segments]]
[walk segments] = [['Walk','minutes','steps','start time Local',start time UTC],[next walk segment]]
[bike segments] = [['Bike','minutes',meters,'start time Local',start time UTC],[next bike segment]]
[run segments] = [['Run','minutes',meters,'start time Local',start time UTC],[next run segment]]

[list_walks] = [["Walk",duration_min_str,'steps',duration_secs,steps,time_start_local_str,time_start_utc,time_end_utc]]
[list_bikes] = [["Bike",duration_min_str,'dist_miles',duration_secs,dist_miles,time_start_local_str,time_start_utc,time_end_utc]]   
[list_runs] = [["Run",duration_min_str,'dist_miles',duration_secs,dist_miles,time_start_local_str,time_start_utc,time_end_utc]]   
'''

# IMPORTS
#---------------------------------------------------------------------------------------------------
import json
import datetime
from dateutil import tz

# USER INPUTS
#---------------------------------------------------------------------------------------------------
INPUT_FILE = 'moves-export.json'
OUTPUT_FILE = 'testoutput.txt'
WRITE_ONLY_TRUNCATED = True   # set to false for debug output
THRESHOLD_WALK_SECS = 300     # any walk with less seconds than this is discarded
THRESHOLD_BIKE_SECS = 120     # set any threshold to 0 to include all segments
THRESHOLD_RUN_SECS = 60
STEPS_PER_MILE = 2252    # from: http://www.nscsd.org/webpages/rbrown/file_viewer.cfm?secFile=919
ZONE_TO = tz.gettz('America/Los_Angeles')  # set to timezone that you live in
    # timezone names: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

# CONSTANTS
#---------------------------------------------------------------------------------------------------
METERS_PER_MILE = 1609.34
ZONE_FROM = tz.gettz('UTC')     # to convert timzezones from UTC to Pacific

# FUNCTIONS
#---------------------------------------------------------------------------------------------------
def open_data_file (INPUT_FILE_name):
    with open(INPUT_FILE_name) as data_file:    
        data = json.load(data_file)
        return data

def process_data_file (input_data):
    list_of_days = []
    list_walks = []
    list_bikes = []
    list_runs = []
    segments_per_day_walk = []
    segments_per_day_bike = []
    segments_per_day_run = []

    print('Length of data file =',len(data))
    counter = 1

    for i in range(0,len(data)-1):
        singleday = data[i]
        print('data :',counter,'of ',len(data))
        days_list_walk = []
        days_list_bike = []  
        days_list_run = []
        steps = 0
        count_steps = 0
        distance = 0
        count_bike = 0
        count_run = 0
        segments_walk = 0
        segments_bike = 0
        segments_run = 0
        
    #    # Each day has "date" and "segements".
        try:        
            todays_date = datetime.datetime.strptime(singleday['date'], '%Y%m%d')
            print('Processing: ',todays_date)
        except Exception:
            print ('Uh-oh......')            
            pass
        # each "segments" has several data, so create a loop for it.Sometimes, segments is 'null'.
        if not singleday['segments']: continue
        for segment in singleday['segments']:
            # Segments have several "type"s. Each types contain a location info in a different way.
            if segment['type'] == 'place':
                # "place" type has a single location info, and start & end time.
                time_start = segment['startTime']
                time_end   = segment['endTime'] 
                time_start_utc = datetime.datetime.strptime(time_start,'%Y%m%dT%H%M%SZ')            
                time_start_utc = time_start_utc.replace(tzinfo=ZONE_FROM)
                time_start_local = time_start_utc.astimezone(ZONE_TO)
                time_end_utc = datetime.datetime.strptime(time_end,'%Y%m%dT%H%M%SZ')                        
                time_end_utc = time_end_utc.replace(tzinfo=ZONE_FROM)
                time_end_local = time_end_utc.astimezone(ZONE_TO)

                try:
                    steps = segment['steps']
                    count_steps = count_steps + steps
                    duration_secs = (time_end_utc-time_start_utc).seconds
                    duration_min_str = '%.1f' %(int(duration_secs)/60.0)
                    time_start_local_str = str(time_start_local)
                    days_list_walk.append(["Walk",duration_min_str,str(steps),time_start_local_str,time_start_utc])
                    list_walks.append(["Walk",duration_min_str,str(steps),duration_secs,steps,time_start_local_str,time_start_utc,time_end_utc])                  
                    segments_walk = segments_walk + 1
                    steps = 0
                    duration_min_str = 0
                    time_start_local_str = ''
                    time_start_utc = 0
                    time_start_local_str = ''
                    time_end_utc = 0
                except:
                    pass
                               

                if 'activities' in segment:
                    activities = segment['activities']  
                    
                    for activity in activities:
                        activity_type = activity['activity']
                        
                        if activity_type == 'wlk':
                            time_start = activity['startTime']  
                            time_end = activity['endTime']  
                            time_start_utc = datetime.datetime.strptime(time_start,'%Y%m%dT%H%M%SZ')            
                            time_start_utc = time_start_utc.replace(tzinfo=ZONE_FROM)
                            time_start_local = time_start_utc.astimezone(ZONE_TO)
                            time_end_utc = datetime.datetime.strptime(time_end,'%Y%m%dT%H%M%SZ')                        
                            time_end_utc = time_end_utc.replace(tzinfo=ZONE_FROM)
                            time_end_local = time_end_utc.astimezone(ZONE_TO)
                            duration = activity['duration']
                            distance = activity['distance']
                            steps = activity['steps']
                            count_steps = count_steps + steps  
                            duration_secs = (time_end_utc-time_start_utc).seconds
                            duration_min_str = '%.1f' %(int(duration_secs)/60.0)
                            time_start_local_str = str(time_start_local)
                            days_list_walk.append(["Walk",duration_min_str,str(steps),time_start_local_str,time_start_utc])
                            list_walks.append(["Walk",duration_min_str,str(steps),duration_secs,steps,time_start_local_str,time_start_utc,time_end_utc])              
                            segments_walk = segments_walk + 1    
                            steps = 0 
                            duration_min_str = 0
                            time_start_local_str = ''
                            time_start_utc = 0
                            time_start_local_str = ''
                            time_end_utc = 0
                                                   
                        if activity_type == 'cyc':
                            time_start = activity['startTime']  
                            time_end = activity['endTime']  
                            time_start_utc = datetime.datetime.strptime(time_start,'%Y%m%dT%H%M%SZ')            
                            time_start_utc = time_start_utc.replace(tzinfo=ZONE_FROM)
                            time_start_local = time_start_utc.astimezone(ZONE_TO)
                            time_end_utc = datetime.datetime.strptime(time_end,'%Y%m%dT%H%M%SZ')                        
                            time_end_utc = time_end_utc.replace(tzinfo=ZONE_FROM)
                            time_end_local = time_end_utc.astimezone(ZONE_TO)
                            duration = activity['duration']
                            distance = activity['distance']
                            count_bike = count_bike + distance
                            dist_miles = distance/METERS_PER_MILE
                            duration_secs = (time_end_utc-time_start_utc).seconds
                            duration_min_str = '%.1f' %(int(duration_secs)/60.0)
                            time_start_local_str = str(time_start_local)
                            days_list_bike.append(["Bike",duration_min_str,str(dist_miles),time_start_local_str,time_start_utc])
                            list_bikes.append(["Bike",duration_min_str,'%.2f'%dist_miles,duration_secs,dist_miles,time_start_local_str,time_start_utc,time_end_utc])    
                            segments_bike = segments_bike + 1
                            distance = 0    

                        if activity_type == 'run':
                            time_start = activity['startTime']  
                            time_end = activity['endTime']  
                            time_start_utc = datetime.datetime.strptime(time_start,'%Y%m%dT%H%M%SZ')            
                            time_start_utc = time_start_utc.replace(tzinfo=ZONE_FROM)
                            time_start_local = time_start_utc.astimezone(ZONE_TO)
                            time_end_utc = datetime.datetime.strptime(time_end,'%Y%m%dT%H%M%SZ')                        
                            time_end_utc = time_end_utc.replace(tzinfo=ZONE_FROM)
                            time_end_local = time_end_utc.astimezone(ZONE_TO)
                            duration = activity['duration']
                            distance = activity['distance']
                            count_run = count_run + distance
                            dist_miles = distance/METERS_PER_MILE
                            duration_secs = (time_end_utc-time_start_utc).seconds
                            duration_min_str = '%.1f' %(int(duration_secs)/60.0)
                            time_start_local_str = str(time_start_local)
                            days_list_run.append(["Run",duration_min_str,str(dist_miles),time_start_local_str,time_start_utc])
                            list_bikes.append(["Run",duration_min_str,'%.2f'%dist_miles,duration_secs,dist_miles,time_start_local_str,time_start_utc,time_end_utc])    
                            segments_run = segments_run + 1
                            distance = 0   
                            
            elif segment['type'] == 'move':
            # "move" type has "activities": array of activities. Activity has "trackPoints": array of time and loc.
                for activity in segment['activities']:
                    activity_type = activity["activity"]
                    duration = activity["duration"]
                    time_start = activity['startTime']  
                    time_end = activity['endTime']  
                    time_start_utc = datetime.datetime.strptime(time_start,'%Y%m%dT%H%M%SZ')            
                    time_start_utc = time_start_utc.replace(tzinfo=ZONE_FROM)
                    time_start_local = time_start_utc.astimezone(ZONE_TO)
                    time_end_utc = datetime.datetime.strptime(time_end,'%Y%m%dT%H%M%SZ')                        
                    time_end_utc = time_end_utc.replace(tzinfo=ZONE_FROM)
                    time_end_local = time_end_utc.astimezone(ZONE_TO)

                    if activity_type == 'wlk':
                        steps = activity['steps']
                        count_steps = count_steps + steps
                        try:                
                            steps = activity['steps']
                            duration_secs = (time_end_utc-time_start_utc).seconds
                            duration_min_str = '%.1f' %(int(duration_secs)/60.0)
                            time_start_local_str = str(time_start_local)
                            days_list_walk.append(["Walk",duration_min_str,str(steps),time_start_local_str,time_start_utc])
                            list_walks.append(["Walk",duration_min_str,str(steps),duration_secs,steps,time_start_local_str,time_start_utc,time_end_utc])    
                            segments_walk = segments_walk + 1
                            steps = 0  
                            distance = 0
                            duration_min_str = 0
                            time_start_local_str = ''
                            time_start_utc = 0
                            time_start_local_str = ''
                            time_end_utc = 0                     
                        except:
                            pass
                        
                    if activity_type == 'cyc': 
                        distance = activity['distance']
                        count_bike = count_bike + distance
                        dist_miles = distance/METERS_PER_MILE
                        try:
                            duration_secs = (time_end_utc-time_start_utc).seconds
                            duration_min_str = '%.1f' %(int(duration_secs)/60.0)
                            time_start_local_str = str(time_start_local)
                            days_list_bike.append(["Bike",duration_min_str,str(dist_miles),time_start_local_str,time_start_utc])
                            list_bikes.append(["Bike",duration_min_str,'%.2f'%dist_miles,duration_secs,dist_miles,time_start_local_str,time_start_utc,time_end_utc])            
                            segments_bike = segments_bike + 1
                            duration_min_str = 0
                            time_start_local_str = ''
                            time_start_utc = 0
                            time_start_local_str = ''
                            time_end_utc = 0
                        except:
                            pass

                    if activity_type == 'run': 
                        distance = activity['distance']
                        count_run = count_run + distance
                        dist_miles = distance/METERS_PER_MILE
                        try:
                            duration_secs = (time_end_utc-time_start_utc).seconds
                            duration_min_str = '%.1f' %(int(duration_secs)/60.0)
                            time_start_local_str = str(time_start_local)
                            days_list_run.append(["Run",duration_min_str,str(dist_miles),time_start_local_str,time_start_utc])
                            list_runs.append(["Run",duration_min_str,'%.2f'%dist_miles,duration_secs,dist_miles,time_start_local_str,time_start_utc,time_end_utc])            
                            segments_run = segments_run + 1
                            duration_min_str = 0
                            time_start_local_str = ''
                            time_start_utc = 0
                            time_start_local_str = ''
                            time_end_utc = 0
                        except:
                            pass

        print()    
        print('----------------------------------------------------------------')
        print('days worth of steps =',count_steps)
        print('days worth of miles walked =',count_steps/STEPS_PER_MILE)
        print('days worth of cycle distance =',count_bike)
        print('days worth of cycle miles =',count_bike/METERS_PER_MILE)
        print('days worth of run distance =',count_run)
        print('days worth of run miles =',count_run/METERS_PER_MILE)
        print()    
        print('----------------------------------------------------------------')      

        list_of_days.append([todays_date,count_steps,count_bike/METERS_PER_MILE,
            count_run/METERS_PER_MILE,days_list_walk,days_list_bike,days_list_run])

        segments_per_day_walk.append(segments_walk)
        segments_per_day_bike.append(segments_bike)
        segments_per_day_run.append(segments_run)

        counter = counter + 1

    print('\n')
    print('----------------------------------------------------------------')
    print('walk segments / day = ', segments_per_day_walk)
    print('bike segments / day = ', segments_per_day_bike)
    print('run segments / day = ', segments_per_day_run)
    print('----------------------------------------------------------------')
    print('\n')

    returned_data = [list_walks,list_bikes,list_runs]
    return returned_data

def write_to_file(input_list):
    for each in input_list:
        temp = each[0:6]
        outFile.write(str(temp))
        outFile.write('\n')     

#-----------------------------------------------------------------------------
# MAIN FUNCTION
#-----------------------------------------------------------------------------
data = open_data_file(INPUT_FILE)['export']
parsed_data = process_data_file(data)
list_walks = parsed_data[0]
list_bikes = parsed_data[1]
list_runs = parsed_data[2]

print()
print()
print('--------------------------------------------------------------------')
print('all collected walk/bike/run segments')
print('--------------------------------------------------------------------')

for each in list_walks:
    temp = each[0:5]    
    temp.append(str(each[6]))
    print (temp)
    
for each in list_bikes:
    temp = each[0:5]    
    temp.append(str(each[6]))
    print (temp)

for each in list_runs:
    temp = each[0:5]    
    temp.append(str(each[6]))
    print (temp)

if WRITE_ONLY_TRUNCATED == False:
    # write all walks/bikes/runs to output file
    outFile = open(OUTPUT_FILE,'w')

    outFile.write('Beginning of all walks obtained ------------------------------------------------------')
    outFile.write('\n')
    write_to_file(list_walks)

    outFile.write('Beginning of all bikes obtained ------------------------------------------------------')
    outFile.write('\n')
    write_to_file(list_bikes)

    outFile.write('Beginning of all runs obtained ------------------------------------------------------')
    outFile.write('\n')
    write_to_file(list_runs)

    outFile.close()

print('--------------------------------------------------------------------')
print('filter out small walk/bike segments, what is left?')
print('--------------------------------------------------------------------')
 
if WRITE_ONLY_TRUNCATED == True:
    outFile = open(OUTPUT_FILE,'w')
else:
    outFile = open(OUTPUT_FILE,'a')

if WRITE_ONLY_TRUNCATED == False:
    outFile.write('\n')
    outFile.write('Beginning of truncated walks ------------------------------------------------------')
    outFile.write('\n')

for each in list_walks:
    if THRESHOLD_WALK_SECS == 0:
        temp = each[0:5]
        temp.append(str(each[6]))        
        print(temp)
        outFile.write(str(temp))
        outFile.write('\n') 
    elif each[3] >= THRESHOLD_WALK_SECS:
        temp = each[0:5]
        temp.append(str(each[6]))        
        print(temp)
        outFile.write(str(temp))
        outFile.write('\n') 

if WRITE_ONLY_TRUNCATED == False:
    outFile.write('\n')
    outFile.write('Beginning of truncated bikes ------------------------------------------------------')
    outFile.write('\n')

for each in list_bikes:
    if THRESHOLD_BIKE_SECS == 0:
        temp = each[0:5]
        temp.append(str(each[6]))        
        print(temp)
        outFile.write(str(temp))
        outFile.write('\n') 
    elif each[3] >= THRESHOLD_BIKE_SECS:
        temp = each[0:5]
        temp.append(str(each[6]))        
        print(temp)
        outFile.write(str(temp))
        outFile.write('\n') 

if WRITE_ONLY_TRUNCATED == False:
    outFile.write('\n')
    outFile.write('Beginning of truncated runs ------------------------------------------------------')
    outFile.write('\n')

for each in list_runs:
    if THRESHOLD_RUN_SECS == 0:
        temp = each[0:5]
        temp.append(str(each[6]))        
        print(temp)
        outFile.write(str(temp))
        outFile.write('\n') 
    elif each[3] >= THRESHOLD_RUN_SECS:
        temp = each[0:5]
        temp.append(str(each[6]))        
        print(temp)
        outFile.write(str(temp))
        outFile.write('\n') 

outFile.close()