#!/usr/bin/python

import sqlite3
import xml.etree.ElementTree as etree
import datetime
import http.cookiejar, urllib.request, shutil, os
import sys, getopt

dry = False
databaseFile = "./main.db"
cookieFile = "./cookies.txt"
pathPrefix = "./Skype Media Download"
errorLogFile = "./Skype Media Download/errors.log"
ErrorLog = True
successLogFile = "./Skype Media Download/success.log"
successLog = True
statement = """
SELECT Messages.id,Messages.timestamp,Messages.author,Conversations.displayname,Messages.body_xml FROM Messages
INNER JOIN Conversations ON Messages.convo_id=Conversations.id
WHERE Messages.type=201;
"""
helpMessage = "Usage: " + os.path.basename(sys.argv[0]) + """ [OPTIONS]

Downloads shared media that is found in messages in Skype's main.db file.

Options:
  -c [file]    Cookie file to use.
                 Default: '""" + cookieFile + """'
  -d [file]    Database file to use.
                 Default: '""" + databaseFile + """'
  -p [dir]     Output Directory.
                 Default: '""" + pathPrefix + """'

  -E           Disable error logging.
  -e [file]    Where to log download errors.
                 Default: '""" + errorLogFile + """'

  -S           Disable success logging and skipping.
  -s [file]    Where to log and read previous successful downloads.
               Used to skip files that have already been downloaded.
                 Default: '""" + successLogFile + """'

  -D           Dry run. Don't actually download or create any files."""

prevDownloads = []
statSuccess = 0
StatFailed = 0
statSkipped = 0

# Printing to stderr
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def isInPrevDownloads(url):
    for prevUrl in prevDownloads:
        if url + "\n" == prevUrl:
            return True
    return False

# Input handling
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv,"hDESc:d:p:e:s:")
except getopt.GetoptError:
    eprint(helpMessage)
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        eprint(helpMessage)
        sys.exit()
    elif opt == '-D':
        dry = True
    elif opt == '-c':
        cookieFile = arg
    elif opt == '-d':
        databaseFile = arg
    elif opt == '-p':
        pathPrefix = arg
    elif opt == '-e':
        errorLogFile = arg
    elif opt == '-E':
        ErrorLog = False
    elif opt == '-s':
        successLogFile = arg
    elif opt == '-S':
        successLog = False

# Sanity check paths
if not os.path.exists(cookieFile):
    eprint ("Cookie file '", cookieFile, "' does not exist. Exiting..", sep='')
    exit()

if not os.path.exists(databaseFile):
    eprint ("Database file '", databaseFile, "' does not exist. Exiting..", sep='')
    exit()

if not os.path.exists(pathPrefix):
    eprint ("Output path '", pathPrefix, "' does not exist. Exiting..", sep='')
    exit()

# Load previously downloaded links
if successLog and os.path.exists(successLogFile):
    with open(successLogFile) as f:
        prevDownloads = f.readlines()

# Setup http downloader
cj = http.cookiejar.MozillaCookieJar()
cj.load(cookieFile)
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Open skype database and run sql statement
conn = sqlite3.connect(databaseFile)
cursor = conn.execute(statement)

for row in cursor:
    # Read row's contents into variables
    messageId = row[0]
    timestamp = datetime.datetime.fromtimestamp(row[1])
    author = row[2]
    convName = row[3]

    # Make a proper url
    root = etree.fromstring(row[4])
    url = root.attrib['uri'] + "/views/imgpsh_fullsize"

    # Make output directory/file path/name
    dirName = pathPrefix + "/" + convName + "/"
    fileName = author + timestamp.strftime("@%Y-%m-%d_%H.%M.%S.jpg")

    # Print some information
    print (url)
    eprint ("Message ID:", messageId)
    eprint ("Output file:", dirName + fileName)

    # Check previous already downloaded urls
    if successLog and isInPrevDownloads(url):
        eprint("Url found in success log. Skipping..\n")
        statSkipped += 1
        continue

    if dry:
        eprint("Download complete.\n")
        statSuccess += 1
    else:
        try:
            # Create output direcorty
            if not os.path.exists(dirName):
                os.makedirs(dirName)

            # Download file
            with opener.open(url) as response, open(dirName + fileName, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

            # Write success log
            if successLog:
                with open(successLogFile, 'a') as succ:
                    succ.write(url + "\n")

            eprint("Download complete.\n")
            statSuccess += 1

        except urllib.error.HTTPError as exept:
            # Log HTTP errors to a file
            with open(errorLogFile, 'a') as err:
                err.write(url + "\n")
                err.write("  Message ID: " + str(messageId) + "\n")
                err.write("  Author: " + author + "\n")
                err.write("  Conversation: " + convName + "\n")
                err.write("  Error: " + str(exept.code) + " " + exept.reason + "\n\n")

            eprint ("Download failed with code: '", exept.code, ": ", exept.reason, "' Logging to '", errorLogFile, "'\n", sep='')
            StatFailed += 1

conn.close()

eprint ("All done!")
eprint ("Successful:", statSuccess, "Skipped:", statSkipped, "Failed:", StatFailed)
