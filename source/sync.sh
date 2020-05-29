#!/usr/bin/env sh

# first copy everything up
echo -n "Uploading files"
rclone -v copy "~/pct-scalewiz/Scale Test Data" remote:"#Scale Test Data"

# then sync downstream
echo -n "Downloading files"
rclone -v sync remote:"#Scale Test Data" "~/pct-scalewiz/Scale Test Data"

echo -n "Done syncing"
read -n 1 -s
