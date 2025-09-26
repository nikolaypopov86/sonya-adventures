#!/bin/bash
# Скрипт для linux
mkdir -p release-win
rm -rf ./build-win/data/*
rm ./release-win/* 2> /dev/null
cp -r data ./build-win/
rm ./build-win/data/app.tiled-project ./build-win/data/app.tiled-session
zip -r ./release-win/sonya-adventures.win-x86_64.zip ./build-win/*
#rm ./app.bin
