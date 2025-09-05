# Linux
python -m nuitka app.py \
--onefile \
--include-package=arcade.gl.backends.opengl \
--include-data-files=".env"=".env" \
--include-data-dir=data=data \
--follow-imports \
--linux-icon=data/misc/paw.png \
--output-dir=./build \
--remove-output

# Windows
# python -m nuitka app.py --onefile --include-package=arcade.gl.backends.opengl --include-data-files=".env"=".env" --include-data-dir=data=data --follow-imports --windows-icon-from-ico=data/misc/paw.png --output-dir=build --remove-output  --mingw64 --windows-console-mode=disable