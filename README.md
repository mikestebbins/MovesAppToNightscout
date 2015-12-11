# MovesAppToNightscout
Parses JSON text export from the Moves App into chunks of exercise activity and then uploads it into mongolab as Nightscout exercise events.

#### Tool instructions:
##### moves_json_to_text.py

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
10. Next run text_to_mongo.py to upload the text output file to mongolab.

##### text_to_mongo.py
 1. Use moves_json_to_text.py to generate text file of threshold-exceeding walks, runs, bikes
 2. Set INPUT_FILENAME below to the name of the text file generated
 3. Ensure .config file has example text replaced with your actual mongolab URL and DB name
 4. Run script. All lines from text file will be entered as separate exercise events
     into mongolab database.
 5. Run reports in Nightscout to see your exercise data on your day-to-day plots
 6. Keep fighting the good fight, and kicking diabetes' %$$!
