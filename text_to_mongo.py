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
 1. Use movesjson2text.py to generate text file of threshold-exceeding walks, runs, bikes
 2. Set INPUT_FILENAME below to the name of the text file generated
 3. Ensure .config file has example text replaced with your actual MongoLab URL and DB name
 4. Run script. All lines from text file will be entered as separate exercise events
     into Mongolab database.
 5. Run reports in Nightscout to see your exercise data on your day-to-day plots
 6. Keep fighting the good fight, and kicking diabetes' %$$!
'''

# IMPORTS
#---------------------------------------------------------------------------------------------------
from pymongo import MongoClient
import time
import datetime

# USER INPUTS
#---------------------------------------------------------------------------------------------------
INPUT_FILENAME = 'testoutput.txt'

# MONGOLAB DATABASE LOG-IN INFO PULLED FROM CONFIG FILE (CREATE YOUR OWN LIKE IN EXAMPLE)
with open('.config') as f:
    config = f.read().splitlines()

MONGO_URL = config[0]
DB_NAME = config[1]

#-----------------------------------------------------------------------------
# MAIN FUNCTION
#-----------------------------------------------------------------------------
print('----------------------------------------------------------------------')
time_then = time.time()

try:
    DBclient = MongoClient(MONGO_URL)
    DB = DBclient[DB_NAME]
    COLLECTION_TREATMENTS = DB['treatments']
    print("connected to MongoDB")
except:
    print ('can not connect to DB make sure MongoDB is running')

time.sleep(0.1)
   
try:
    number_of_entries = COLLECTION_TREATMENTS.count()
    print ('number of posts already existing = ',number_of_entries) 
except Exception:
    print ('error: could not count posts for some reason or another')
    number_of_entries = 0
print()         
file = open(INPUT_FILENAME, 'r')

counter = 0

for line in file:
    counter =  counter + 1
    # strip beginning and ending square brackets from string-ized list
    temp1 = line[1:-2]
    # remove the single quotations, replace with nothing
    temp2 = temp1.replace("'","")
    # split the string into a list, separated by comma-space
    temp3 = temp2.split(', ')
    # grab time component of list 
    create_time = temp3[5]
    # remove the utc offset string from the main string
    create_time_base = create_time[0:19]
    # create a datetime object from the remaining string
#    time_local = datetime.datetime.strptime(create_time_base,'%Y-%m-%d %H:%M:%S')
    # wrote out UTC time in movesjson2mongo script, can eliminate all of this
    # conversion nonsense here.  Mongolab DB uses UTC time.
#    time_utc = time_local + datetime.timedelta(hours=8)
    time_utc = datetime.datetime.strptime(create_time_base,'%Y-%m-%d %H:%M:%S')
#    print(time_utc)
    # change the utc datetime to the appropriate string
    datetime_str = datetime.datetime.strftime(time_utc,'%Y-%m-%dT%H:%M:%S.000Z')
    # round the duration time to the nearest minute    
    duration = round(float(temp3[1]))
    
    post = {
    "eventType":"Exercise",
    "enteredBy":"computer",
    "duration":duration,
    "notes":temp3[0]+':'+str(duration),
    "created_at":datetime_str
    }    
    print(post)
 
    post_id = COLLECTION_TREATMENTS.insert_one(post) 
    
time_now = time.time()
print()
print('time taken =',time_now-time_then,'seconds')
print(counter,' posts added to DB')
          
file.close()
DBclient.close()
