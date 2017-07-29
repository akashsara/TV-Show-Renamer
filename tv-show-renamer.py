#!python3
'''
GENERAL INFORMATION:
Uses the TvMaze API to retrieve a list of episodes of a TV series and renames the files on disk to the following format:
    Episode X - Episode Name
For safety's sake, the actual rename commands have been commented out. The console will simply print the old and new names of each file
in the following format:
    Old Name
    New Name

If you are unfamiliar with the console, a changelog.txt file will also appear in the directory you selected. This file contains the same text
printed by the console.

REQUIREMENTS:
    * python3
    * requests module

INSTRUCTIONS:
    1. Set the path of the TV show you want to rename in the area indicated.
    2. To proceed with the renaming, uncomment the two lines containing 'shutil.move' by removing the '#' at the start of the line

IMPORTANT:
All TV Shows must be in the following format:
    * The entire show must be within a folder named by the original name of the show. So 'Arrow' or 'The Flash' for example
    * Each season of the show must be in its own folder named 'Season X' where X is the season number.
    * All episodes of each season must be in ascending order. So Episode 1, Episode 2, Episode 3 etc
    * If there are subtitles, each episode's subtitle must be sorted after that episode. So episode X, subtitle X, episode Y, subtitle Y
    * There is no problem if only some episodes have subtitles. So Episode X, Episode Y, Episode Z, Subtitle Z is fine.
    * Only .mkv and .mp4 video files and .srt and .sub subtitle files are supported.
'''

import os, shutil, re, json, requests, datetime

'''
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
'''
#Set folder path here
folderPath = r"J:\Shows\Live-Action\The Big Bang Theory"
'''
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
'''

#Get show name from folder path
showName = os.path.basename(folderPath)
#Regex expressions to get the file extension, episode number & name and to check if the episode name has invalid characters
extensionCheck = re.compile(r'\.[a-z0-9]{3,4}$')
episodeFormat = re.compile(r'(^Season\s\d{1,2})(::)(.*$)')
invalidChars = re.compile(r'[\/?*><|]+')
#Date for changelog
now = datetime.datetime.now()
date = now.strftime('%d-%m-%Y')

def getEpisodeList():
    print('Connecting to server...')
    #Search TVMaze for show and find its ID
    showURL = r'http://api.tvmaze.com/search/shows?q=' + showName
    response = requests.get(showURL)
    response.raise_for_status()
    showInfo = json.loads(response.text)
    showID = showInfo[0]['show']['id']

    print('Retrieving data...')
    #Using the ID, get the details of every episode
    episodesURL = r'http://api.tvmaze.com/shows/%s/episodes' %showID
    response = requests.get(episodesURL)
    response.raise_for_status()
    episodeInfo = json.loads(response.text)

    print('Data retrieved!')
    #Create an empty list
    episodeList = []

    #Add each episode in the show ordered by season and episode number
    for episodes in episodeInfo:
        #if condition to make all single digit episode numbers have a preceding 0
        if episodes['number'] > 0 and episodes['number'] < 10:
            episodeNumber = '0' + str(episodes['number'])
        else:
            episodeNumber = str(episodes['number'])
        #Get rid of all invalid characters not allowed in a Windows file/folder name
        episodeName = str(episodes['name'])
        while invalidChars.search(episodeName):
            episodeName = re.sub(invalidChars, '', episodeName)
        #Replace : with a -
        episodeName = episodeName.replace(':', " -")
        #Generate name of the format {Season X}{::}{Episode Y - Episode Name}
        episodeList.append('Season ' + str(episodes['season']) + '::Episode ' + episodeNumber + ' - ' + episodeName)

    #return the list of episodes
    return episodeList

def getSeasonList():
    #initialize empty list
    print('Analyzing folder...')
    seasonList = [subfolders for folders, subfolders, files in os.walk(folderPath)]
    return seasonList[0]

def getCurrentSeasonList(seasons, episodeList):
    #Get the season the episode is from, check if episode is in the current season and add it to the list
    currentSeason = [
        episodeFormat.search(episodes)[3]
        for episodes in episodeList
        if seasons == episodeFormat.search(episodes)[1]
    ]
    return currentSeason

def generatePath(fileName):
    return folderPath + '\\' + seasons + '\\' + fileName

def checkFileType(fileExt):
    if(fileExt in ['.mkv', '.mp4', '.avi']):
        return 'video'
    elif(fileExt in ['.srt', '.sub']):
        return 'sub'

def renameFiles(oldPath, newPath):
    '''UNCOMMENT THIS TO RENAME'''
    #shutil.move(oldPath, newPath)
    '''!!!!!!!!!!!!!!!!!!!!!!!!'''
    print(oldPath, newPath, '', sep='\n')
    changeLog.write('\n' + oldPath + '\n' + newPath + '\n')
    return 1

def renameError(oldPath, newPath):
    changeLog.write('\nError renaming ' + oldPath + 'to' + newPath + '!')
    print('\nError renaming ' + oldPath + 'to' + newPath + '!')
    return 1

#get episode list and number of seasons on disk
episodeList = getEpisodeList()
seasonList = getSeasonList()

#Open logfile
changeLog = open(folderPath + '\\' + 'changelog.txt', 'a', encoding='utf-8')
changeLog.write('\nChanges made on ' + date + ':\n')

renameCount = 0
errorCount = 0

#For each season in the folder
for seasons in seasonList:
    #Get list of episodes in this season
    currentSeason = getCurrentSeasonList(seasons, episodeList)
    #Set the current episode index as 0
    episodeCount = 0
    previousFile = 'none'
    #for all the files in the folder
    for files in os.listdir(folderPath + '\\' + seasons):
        #Check if extension exists
        if(extensionCheck.search(files)):
            print('Renaming...')
            #Retrieve the extension
            fileExt = extensionCheck.search(files).group()
            #If it is a video file or a subtitle file
            if(checkFileType(fileExt) == 'video' or checkFileType(fileExt) == 'sub'):
                #If the previous file was also a video, it means no subtitle file existed for the previous file. So we increment the count
                if(checkFileType(fileExt) == 'video' and previousFile == 'video'):
                    episodeCount += 1
                #Generate the absolute path of the file to rename and the new name
                oldPath = generatePath(files)
                newPath = generatePath(currentSeason[episodeCount] + fileExt)
                #Try to rename the file, print it in the console and log it. Increment renameCount
                try:
                    renameCount += renameFiles(oldPath, newPath)
                #If rename fails, print error message, log it and increment errorCount
                except:
                    errorCount += renameError(oldPath, newPath)
                #Increment episode count after each subtitle file since subtitle files are always after the its corresponding video file
                if(checkFileType(fileExt) == 'sub'):
                    episodeCount += 1
            #Set the value of previousFile to the current file extension for future use
            previousFile = checkFileType(fileExt)

print('Successfully renamed ' + str(renameCount) + ' files with ' + str(errorCount) + ' errors!')
changeLog.close()
