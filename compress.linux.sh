mkdir -p release
rm ./release/* 2> /dev/null
cp ./build/app.bin ./app.bin
tar --exclude='./data/app.tiled-*' -cjvf release/sonya-adventures.bz2 ./data ./app.bin
rm ./app.bin
