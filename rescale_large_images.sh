#!/bin/bash

# https://unix.stackexchange.com/questions/38943/use-mogrify-to-resize-large-images-while-ignoring-small-ones

minimumWidth=640
minimumHeight=640

for f in afu-group-trainer/frontend/static/img/technik_{e,a}/*
do
    imageWidth=$(identify -format "%w" "$f")
    imageHeight=$(identify -format "%h" "$f")

    if [ "$imageWidth" -gt "$minimumWidth" ] || [ "$imageHeight" -gt "$minimumHeight" ]; then
        mogrify -resize ''"$minimumWidth"x"$minimumHeight"'' $f
    fi
done

