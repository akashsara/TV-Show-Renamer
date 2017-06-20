#!python3
'''
Uses the TvMaze API to retrieve a list of episodes of a TV series and renames the files on disk to the following format:
    Episode X - Episode Name
You need to only set the path of the TV show in the area marked below.
For the safety's sake, the actual rename commands have been commented out. The console will simply print the old and new names of each file
in the following format:
    Old Name
    New Name

If you are unfamiliar with the console, a changelog.txt file will also appear in the directory you selected. This file contains the same text
printed by the console.

To proceed with the renaming, uncomment the two lines containing 'shutil.move' by removing the '#' at the start of the line
IMPORTANT:
All TV Shows must be in the following format:
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
folderPath = r"J:\Shows\Live-Action\Community"
'''
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
'''

#Get show name from folder path
showName = os.path.basename(folderPath)
#Regex expressions to get the file extension, episode number & name and to check if the episode name has invalid characters
extensionCheck = re.compile(r'\.[a-z0-9]{3,4}$')
episodeFormat = re.compile(r'(^Season\s\d)(::)(.*$)')
invalidChars = re.compile(r'[\/?*><|]+')
#Date for changelog
now = datetime.datetime.now()
date = now.strftime('%d-%m-%Y')

def getEpisodeList():
    #Search TVMaze for show and find its ID
    showURL = r'http://api.tvmaze.com/search/shows?q=' + showName
    response = requests.get(showURL)
    response.raise_for_status()
    showInfo = json.loads(response.text)
    showID = showInfo[0]['show']['id']

    #Using the ID, get the details of every episode
    episodesURL = r'http://api.tvmaze.com/shows/%s/episodes' %showID
    response = requests.get(episodesURL)
    response.raise_for_status()
    episodeInfo = json.loads(response.text)

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
    seasonList = []
    for folders, subfolders, files in os.walk(folderPath):
        #Get number of seasons and add to list
        seasonList.append(subfolders)
    return seasonList[0]

def getCurrentSeasonList(seasons, episodeList):
    #Empty the list of episodes in the current season
    currentSeason = []
    #Add every episode from the list of this season's episodes to the currentSeason list
    for episodes in episodeList:
        #Get the season the episode is from
        episodeData = episodeFormat.search(episodes)
        #Check if episode is in the current season
        if seasons == episodeData[1]:
            #Add it to the list
            currentSeason.append(episodeData[3])
    return currentSeason

def generatePath(fileName):
    return folderPath + '\\' + seasons + '\\' + fileName

def checkFileType(fileExt):
    if(fileExt == '.mkv' or fileExt == '.mp4' or fileExt == '.avi'):
        return 'video'
    elif(fileExt == '.srt' or fileExt == '.sub'):
        return 'sub'

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
            #If it is a video file
            if(checkFileType(fileExt) == 'video'):
                #If the previous file was also a video, it means no subtitle file existed for the previous file. So we increment the count
                if(previousFile == 'video'):
                    episodeCount += 1
                #Generate the absolute path of the file to rename and the new name
                oldPath = generatePath(files)
                newPath = generatePath(currentSeason[episodeCount] + fileExt)
                #Try to rename the file, print it in the console and log it. Increment renameCount
                try:
                    '''UNCOMMENT THIS TO RENAME'''
                    #shutil.move(oldPath, newPath)
                    '''!!!!!!!!!!!!!!!!!!!!!!!!'''
                    print(oldPath, newPath, '', sep='\n')
                    changeLog.write('\n' + oldPath + '\n' + newPath + '\n')
                    renameCount += 1
                #If rename fails, print error message, log it and increment errorCount
                except:
                    changeLog.write('\nError renaming ' + oldPath + 'to' + newPath + '!')
                    print('\nError renaming ' + oldPath + 'to' + newPath + '!')
                    errorCount += 1
            #If it is a subtitle file
            elif(checkFileType(fileExt) == 'sub'):
                #Generate the absolute path of the file to rename and the new name
                oldPath = generatePath(files)
                newPath = generatePath(currentSeason[episodeCount] + fileExt)
                #Try to rename the file, print it in the console and log it. Increment renameCount
                try:
                    '''UNCOMMENT THIS TO RENAME'''
                    #shutil.move(oldPath, newPath)
                    '''!!!!!!!!!!!!!!!!!!!!!!!!'''
                    print(oldPath, newPath, '', sep='\n')
                    changeLog.write('\n' + oldPath + '\n' + newPath + '\n')
                    renameCount += 1
                #If rename fails, print error message, log it and increment errorCount
                except:
                    changeLog.write('\nError renaming ' + oldPath + 'to' + newPath + '!')
                    print('\nError renaming ' + oldPath + 'to' + newPath + '!')
                    errorCount += 1
                #Increment episode count after each subtitle file since subtitle files are always after the its corresponding video file
                episodeCount += 1
            #Set the value of previousFile to the current file extension for future use
            previousFile = checkFileType(fileExt)

print('Successfully renamed ' + str(renameCount) + ' files with ' + str(errorCount) + ' errors!')
changeLog.close()
