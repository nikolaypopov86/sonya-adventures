mkdir -p release
rm ./release/* 2> /dev/null
tar -cjvf release/sonya-adventures.bz2 ./data ./build/app.bin
