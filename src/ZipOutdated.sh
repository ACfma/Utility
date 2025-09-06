#! bin/bash
# ________  ___  ___  _________  ________  ________  _________  _______   ________          ________  ___  ________  ________  _______   ________     
#|\   __  \|\  \|\  \|\___   ___\\   ___ \|\   __  \|\___   ___\\  ___ \ |\   ___ \        |\_____  \|\  \|\   __  \|\   __  \|\  ___ \ |\   __  \    
#\ \  \|\  \ \  \\\  \|___ \  \_\ \  \_|\ \ \  \|\  \|___ \  \_\ \   __/|\ \  \_|\ \        \|___/  /\ \  \ \  \|\  \ \  \|\  \ \   __/|\ \  \|\  \   
# \ \  \\\  \ \  \\\  \   \ \  \ \ \  \ \\ \ \   __  \   \ \  \ \ \  \_|/_\ \  \ \\ \           /  / /\ \  \ \   ____\ \   ____\ \  \_|/_\ \   _  _\  
#  \ \  \\\  \ \  \\\  \   \ \  \ \ \  \_\\ \ \  \ \  \   \ \  \ \ \  \_|\ \ \  \_\\ \         /  /_/__\ \  \ \  \___|\ \  \___|\ \  \_|\ \ \  \\  \| 
#   \ \_______\ \_______\   \ \__\ \ \_______\ \__\ \__\   \ \__\ \ \_______\ \_______\       |\________\ \__\ \__\    \ \__\    \ \_______\ \__\\ _\ 
#    \|_______|\|_______|    \|__|  \|_______|\|__|\|__|    \|__|  \|_______|\|_______|        \|_______|\|__|\|__|     \|__|     \|_______|\|__|\|__|
#Author: Andrea Carli
#This simple script takes all the outdated files from folder, zips them, and send them to a "cold" memory
#I suggest to schedule this script in the background (in my case, I'm using cron)


INDIR=$1 #path to directory with old files 
TIME=$2 #in days
OUTDIR=$3 #target "cold" memory

# Define the timestamp and use it to create the zip file name
timestamp=$(date +"%Y%m%d")
zip_filename="archive_${timestamp}.zip"

find $INDIR -type f -mtime +$TIME -exec zip $OUTDIR/$zip_filename {} \;

# Write the content of the zip file to a text file
zipinfo $OUTDIR/$zip_filename > $OUTDIR/"content_${timestamp}.txt"

#using a mv because otherwise, it may not find the file in the outputfolder
#mv "$INDIR/$zip_filename $INDIR/content_${timestamp}.txt" "$OUTDIR"

# If the file does not exist, create it
touch $OUTDIR/zipped_history.log

echo "Compressione ${timestamp} terminata." > $OUTDIR/zipped_history.log

find $INDIR -type f -mtime +$TIME -delete