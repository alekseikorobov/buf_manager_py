
RMDIR dist_windows /S /Q
RMDIR build /S /Q
DEL main.spec
pyinstaller main.py --noconsole

MOVE dist dist_windows
COPY params.json dist_windows\params.json