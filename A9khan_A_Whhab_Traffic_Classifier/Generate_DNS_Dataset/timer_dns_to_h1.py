import time
import urllib.request
import urllib.error
import os


def uptime_bot(msg):
    while True:
        try:
            os.system("ITGSend script_file_1 -l sender_log_file_1")
        except: 
            print('Error')
        time.sleep(3)

if __name__ == '__main__':
    msg = 'In the name of Allah'
    uptime_bot(msg)
