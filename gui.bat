pyinstaller gui.py -D -F -n "gUDPT GUI" -w -i "util/icon.ico" --add-data "util/icon.ico;util"  --clean --distpath "."
del ".\gUDPT GUI.spec"
pause