'''
    Auto FTP File Transfer
    Transfer files which have changed since last run to FTP
    Shane Frost
    Nov 2022
'''

import glob
import json
import os
import time
import datetime
import subprocess
import paramiko
from ftplib import FTP
from pathlib import Path
from datetime import datetime
from pathlib import Path

def GetConfiguration():
    f = open('config.json')
    data = json.load(f)    
    f.close()
    return data

def UpdateConfigDatetime(curTime):
    with open("config.json", "r+") as jsonFile:
        data = json.load(jsonFile)
        data["lastChange"] = curTime 
        jsonFile.seek(0)  # rewind
        json.dump(data, jsonFile)
        jsonFile.truncate()

def convertDatetimeStringToDatetime(Str):
    print(Str)
    result = datetime.strptime(Str, '%Y-%m-%d %H:%M:%S')
    return result
        
def formatDateTime(dateTime):
    correctedDateTime = datetime.strptime(dateTime, '%a %b %d %H:%M:%S %Y')
    return correctedDateTime

def GetLastCreatedModifiedTime(file, lastUpdate):
    ti_c = os.path.getctime(file)
    ti_m = os.path.getmtime(file)
    c_ti = time.ctime(ti_c) # created
    m_ti = time.ctime(ti_m) # modified
    return formatDateTime(m_ti)


def GetFilesChangedSinceLast(source, lastUpdate):
    filesChanged = []
    for path in Path(source).rglob('*.*'):
        lastMod = GetLastCreatedModifiedTime(path, lastUpdate)
        if (lastMod - lastUpdate).total_seconds() > 0:
            cFile = []
            cFile.append(path.name)
            cFile.append(path)
            filesChanged.append(cFile)
    return filesChanged

def TransferFileViaFTP(serverAddress, Username, Password, keyfile, sourcePath, targetPath):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(serverAddress, username=Username,password=Password ,key_filename=keyfile)

    sftp = client.open_sftp() 
    sftp.put(sourcePath, targetPath)

    sftp.close()
    
        
def main():
    # Load the config data
    username = GetConfiguration()['username']
    password = GetConfiguration()['password']
    source = GetConfiguration()['source']
    target = GetConfiguration()['target']
    serverAddress = GetConfiguration()['ftpaddress']
    keyfile = GetConfiguration()['pem']
    lastChange = convertDatetimeStringToDatetime(GetConfiguration()['lastChange'])
    
    # Heading
    print('Transfer modified files to FTP')
    print('********************************')

    # Check if any files have changed
    filesChanged = GetFilesChangedSinceLast(source, lastChange)

    if len(filesChanged) > 0:
        print('The following have changed and are being uploaded to FTP')
        for file in filesChanged:
            print(file[0])
            Target = target.replace('\\','/')
            SubDir = str(file[1]).replace(source.replace('/','\\'),'').replace('\\','/')[1:]
            
            TransferFileViaFTP(serverAddress, username, password, keyfile, file[1], Target + '/' + SubDir)

            UpdateConfigDatetime( str(datetime.now())[0:19])
    else:
        print('No changes found.')
    	
if __name__ == '__main__':
    main()



