from zipfile import ZipFile
import os
import shutil
import winsound
from time import sleep
from pathlib import Path

with ZipFile("program.zip", 'r') as zObject: 
        # Extracting all the members of the zip  
        # into a specific location. 
        zObject.extractall(path="") 

def test_folders():
    #Important directory creation
    try:
        os.mkdir('engines\wads')
    except:
        print('Directory Exists Already')

    try:
        os.mkdir('mods')
    except:
        print('Directory Exists Already')

    try:
        os.mkdir('engines')
    except:
        print('Directory Exists Already')

doomlist = [
    'DOOM.WAD',
    'DOOM2.WAD',
    'PLUTONIA.WAD',
    'TNT.WAD'
]


def window_pause():
    print("Sound Playing. Please wait for next intruction.")
    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
    input('Press Enter to continue...')

def clsc():
    os.system('cls')

#Downlaod, extract, and copy gzdoom
def get_gzdoom():
    os.system('python downloadgit.py -d engines\gzdoom https://github.com/ZDoom/gzdoom g4.12.1')
    # Website i "learned" this from -> https://www.geeksforgeeks.org/unzipping-files-in-python/
    # loading the gzdoom-4-12-1-windows.zip and creating a zip object 
    with ZipFile("engines\gzdoom\g4.12.1\gzdoom-4-12-1-windows.zip", 'r') as zObject: 
        # Extracting all the members of the zip  
        # into a specific location. 
        zObject.extractall(path="engines\gzdoom") 

#Downlaod, extract, and copy freedoom
def get_freedoom():
    os.system('python downloadgit.py -d wadsmoosh\source_wads https://github.com/freedoom/freedoom  v0.13.0')
    with ZipFile("wadsmoosh\\source_wads\\v0.13.0\\freedoom-0.13.0.zip", 'r') as zObject: 
        zObject.extractall(path="wadsmoosh\source_wads") 
    shutil.copyfile(r'wadsmoosh\source_wads\freedoom-0.13.0\freedoom1.wad',r'wadsmoosh\source_wads\freedoom1.wad')
    shutil.copyfile(r'wadsmoosh\source_wads\freedoom-0.13.0\freedoom2.wad',r'wadsmoosh\source_wads\freedoom2.wad')
    
#downloads and extracts prboom plus
def get_prboom():
    os.system('python downloadgit.py -d engines https://github.com/coelckers/prboom-plus  v2.6.66')
    #prboom extract and copy to it's folder
    with ZipFile(r"engines\v2.6.66\prboom-plus-2666-ucrt64.zip", 'r') as zObject: 
            zObject.extractall(path="engines")



# copies the .WAD files from your steam libary
def steam2smoosh():
    global drive
    drive = 'c' # input("What drive are your steam doom copies installed to? I.e.[c,d,e,f,...]_").upper()
    shutil.copyfile(rf'{drive}:\Program Files (x86)\Steam\steamapps\common\Doom 2\base\DOOM2.WAD',r'wadsmoosh\source_wads\DOOM2.WAD')
    print(rf'Copying {drive}:\Program Files (x86)\Steam\steamapps\common\Doom 2\base\DOOM2.WAD to wadsmoosh\source_wads\DOOM2.WAD')
    shutil.copyfile(rf'{drive}:\Program Files (x86)\Steam\steamapps\common\Ultimate Doom\base\DOOM.WAD',r'wadsmoosh\source_wads\DOOM.WAD')
    print(rf'Copying {drive}:\Program Files (x86)\Steam\steamapps\common\Ultimate Doom\base\DOOM.WAD to wadsmoosh\source_wads\DOOM.WAD')
    shutil.copyfile(rf'{drive}:\Program Files (x86)\Steam\steamapps\common\Doom 2\finaldoombase\PLUTONIA.WAD',r'wadsmoosh\source_wads\PLUTONIA.WAD')
    print(rf'Copying {drive}:\Program Files (x86)\Steam\steamapps\common\Doom 2\finaldoombase\PLUTONIA.WAD to wadsmoosh\source_wads\PLUTONIA.WAD')
    shutil.copyfile(rf'{drive}:\Program Files (x86)\Steam\steamapps\common\Doom 2\finaldoombase\TNT.WAD',r'wadsmoosh\source_wads\TNT.WAD')
    print(rf'Copying {drive}:\Program Files (x86)\Steam\steamapps\common\Doom 2\finaldoombase\TNT.WAD to wadsmoosh\source_wads\TNT.WAD')

#This will copy the main doom games to the engines folder for prboom (I might add the rest of the comersial doom wad's to the list later.)
def steam2engine():
    shutil.copyfile(rf'{drive}:\Program Files (x86)\Steam\steamapps\common\Doom 2\base\DOOM2.WAD',r'engines\wads\DOOM2.WAD')
    print(rf'Copying {drive}:\Program Files (x86)\Steam\steamapps\common\Doom 2\base\DOOM2.WAD to engines\wads\DOOM2.WAD')
    shutil.copyfile(rf'{drive}:\Program Files (x86)\Steam\steamapps\common\Ultimate Doom\base\DOOM.WAD',r'engines\wads\DOOM.WAD')
    print(rf'Copying {drive}:\Program Files (x86)\Steam\steamapps\common\Ultimate Doom\base\DOOM.WAD to engines\wads\DOOM.WAD')

    master_list = os.listdir(r'C:\Program Files (x86)\Steam\steamapps\common\Doom 2\masterbase\master\wads')
    for i in master_list:    
        if i.endswith('.WAD'):
            shutil.copyfile(rf'C:\Program Files (x86)\Steam\steamapps\common\Doom 2\masterbase\master\wads\{i}',rf'wadsmoosh\source_wads\{i}')

#Clears out the freedoom folders from the wadsmoosh program so that it doesn't die vioenlty
def freedoom_clean_up():
    print('FreeDoom clean up')
    sleep(0.3)
    shutil.rmtree(r'wadsmoosh\source_wads\freedoom-0.13.0')
    shutil.rmtree(r'wadsmoosh\source_wads\v0.13.0')

#run the wadsmoosh script 
def wad_smoosh_time():
    print('Starting wadsmoosh')  
    sleep(0.3)  
    os.chdir('wadsmoosh')
    os.system('python wadsmoosh.py')
    os.chdir('..')
    print('Wadsmoosh Done')  
    sleep(0.3)  
    shutil.move(rf'wadsmoosh\doom_complete.ipk3',r'engines\wads\doom_complete.pk3')
    
    print('Wadsmoosh Copied')  
    sleep(0.3)  

#Un-used #Used to smoosh wads if you are installing from folder 
def wadsmoosh_classic():
    print('Starting wadsmoosh')  
    sleep(0.3)  
    os.chdir('wadsmoosh')
    os.chdir('wadsmoosh_classic')
    os.system('python wadsmoosh.py')
    os.chdir('..')
    os.chdir('..')
    print('Wadsmoosh Done')  
    sleep(0.3)  
    shutil.move(rf'wadsmoosh\wadsmoosh_classic\doom_complete.pk3',r'engines\wads\doom_complete.pk3')
    
    print('Wadsmoosh Copied')  
    sleep(0.3)  


# #clean up
def clean_up():
    print('Finnal Clean up')
    sleep(0.3)
    shutil.rmtree('engines\gzdoom\g4.12.1')
    shutil.rmtree(r'engines\v2.6.66')
    shutil.rmtree(r'wadsmoosh\ipk3')
    shutil.rmtree(r'wadsmoosh\source_wads')

def downlaod_file(gitlink = 'https://github.com/ODDdavidster/dummyfile',tag = 'v1.0',filename = 'dummy.py' ,desination = 'downloads'):
    os.system(rf'python downloadgit.py -d {desination} {gitlink} {tag}')
    with ZipFile(rf"{desination}\{filename}", 'r') as zObject: 
        zObject.extractall(path=f"{desination}") 


#Main
#Initial Messaging 
os.system('@echo off')
clsc()

def test_location(file_path):#this is used to see if a file can be copied to the engines folder. 
    try:
        shutil.copyfile(rf'{file_path}','engines')
    except:
        input("Doom or 2 from steam isn't installed. Please install Ultimate Doom and Doom 2 from steam to your C:")
        exit()
# shutil.copyfile(rf'{drive}:\Program Files (x86)\Steam\steamapps\common\Ultimate Doom\base\DOOM.WAD',r'wadsmoosh\source_wads\DOOM.WAD')

# test_location(r'C:\Program Files (x86)\Steam\steamapps\common\Doom 2\base\DOOM2.WAD')
# test_location(r'C:\Program Files (x86)\Steam\steamapps\common\Ultimate Doom\base\DOOM.WAD')



#The code that controls user inputs
def main():
    temp_input = 'n'
    if temp_input.upper() in ['N','NO']:
        test_folders()
        get_gzdoom()
        get_freedoom()
        get_prboom()
        steam2smoosh()
        steam2engine()
        freedoom_clean_up()
        wad_smoosh_time()
        clean_up()
    elif temp_input.upper() in ['Y','YES']:
        pass
        # #A work around for if you can't install doom from steam
        # #this i unessisary. As This won't be given to anyone who doesn't own doom... uugggg.
        # input('Install from folder Only works with DOOM,DOOM2,TNT,PLUTONIA. Press Enter to continue...')
        # work_list = []
        # work_name = []
        # for i in os.listdir('your_wads_here'):
        #     if i in doomlist:
        #         work_list.append('your_wads_here/'+ i)
        #         work_name.append(i)
        #     else:
        #         print(f'{i} is not a comersial Doom wad. It has been excluded')

        # n = 0
        # for i in work_list:
        #     shutil.copyfile(i,rf'wadsmoosh\wadsmoosh_classic\source_wads\{work_name[n]}')
        #     shutil.copyfile(i,rf'engines\wads\{work_name[n]}')
        #     n =+ 1
        # get_gzdoom()
        # get_prboom()
        # # get_freedoom()
        # # freedoom_clean_up()
        # wadsmoosh_classic()
        # clean_up()
main()
os. remove('program.zip')
os. remove('downloadgit.py')
os. remove(__file__) 