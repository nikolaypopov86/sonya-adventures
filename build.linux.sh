# Linux
python -m nuitka app.py \
--onefile \
--enable-plugin=numpy \
--include-package=arcade.gl.backends.opengl \
--include-data-files=".env"=".env" \
--include-data-dir=data=data \
--follow-imports \
--linux-icon=data/misc/paw.png \
--output-dir=./build \
--remove-output
