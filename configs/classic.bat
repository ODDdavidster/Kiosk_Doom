if "%1"=="-1" (
	set "doom_game=DOOM"
) else (
	set "doom_game=DOOM2"
)
cd ..\engines\
copy wads\%doom_game%.WAD prboom-plus-2666-ucrt64
cd ..\configs\
copy classic.cfg ..\engines\prboom-plus-2666-ucrt64\prboom-plus.cfg
cd ..\engines\prboom-plus-2666-ucrt64\
prboom-plus.exe -iwad %doom_game%.WAD -complevel 9
del %doom_game%.WAD
exit