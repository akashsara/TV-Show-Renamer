# TV-Show-Renamer
Script that renames all episodes of any TV show to a 'Episode X - Episode Name' format.

# General Information:

Uses the TvMaze API to retrieve a list of episodes of a TV series and renames the files on disk to the following format:
> Episode X - Episode Name

For safety's sake, the actual rename commands have been commented out. The console will simply print the old and new names of each file
in the following format:

>Old Name

>New Name

> 

If you are unfamiliar with the console, a changelog.txt file will also appear in the directory you selected. This file contains the same text
printed by the console.

# Requirements:

* python3
* requests module

# Instructions:

1. Set the path of the TV show you want to rename in the area indicated.
2. To proceed with the renaming, uncomment the two lines containing 'shutil.move' by removing the '#' at the start of the line

# Important:

All TV Shows must be in the following format:

* Each season of the show must be in its own folder named 'Season X' where X is the season number.
* All episodes of each season must be in ascending order. So Episode 1, Episode 2, Episode 3 etc
* If there are subtitles, each episode's subtitle must be sorted after that episode. So episode X, subtitle X, episode Y, subtitle Y
* There is no problem if only some episodes have subtitles. So Episode X, Episode Y, Episode Z, Subtitle Z is fine.
* Only .mkv and .mp4 video files and .srt and .sub subtitle files are supported.
