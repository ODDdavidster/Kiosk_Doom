@echo off
copy "classic+.ini" ..\engines\gzdoom\
cd ..\engines\
copy wads\DOOM2.WAD gzdoom\
cd gzdoom\
gzdoom.exe -iwad DOOM2.WAD -file "%cd%\..\wads\doom_complete.pk3" -config "classic+.ini"
del DOOM.WAD
exit