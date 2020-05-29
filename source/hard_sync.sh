#!/usr/bin/env sh

rclone -v sync remote:"#Scale Test Data" "~/pi/pct-scalewiz/Scale Test Data"
echo "Done syncing"
read -n 1 -s
