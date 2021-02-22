import subprocess
import time
import requests
from requests import HTTPError
import json
import pytz
import datetime
import logging 
import os
import signal
import serial

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 
handler = logging.FileHandler('stream.log')
handler.setLevel(logging.DEBUG)

f_format = logging.Formatter('%(asctime)s-%(levelname)s-%(message)s')
handler.setFormatter(f_format)
logger.addHandler(handler)

class MsgHandler:
    """
    Class Description: handles the message content and execution
    """

    def __init__(self):
        self.api_endpoint = 'http://62.74.232.210:9010/api/cameras'
        self.api_endpoint_send = 'http://62.74.232.210:9010/api/cameras/1'
        url = 'http://62.74.232.210:9010/authenticate'
        myobj = '{"username":"skironis","password":"password"}'
        headers = {'Content-type': 'application/json'}
        x_resp = requests.post(url, headers=headers, data=myobj, verify=False)              # Request for authentication
        byt = json.loads(x_resp.text)
        self.headers = {'content-type':'application/vnd.api+json', 'Authorization': 'Token '+byt["token"]}
        current_time = get_time()                                                           # Get timestamp
        self.message = {
            "data": {
                "type": "camera",
                "id": "1",
                "attributes": {
                    "status": False,
                    "response": "stopped",
                    "timestamp": str(current_time.isoformat()),
                }
            }
        }

    def send_message(self):
        """
        Method Description: send patch message with positive response when streaming
        """
        try:
            current_time = get_time()
            self.message["data"]["attributes"]["timestamp"] = str(current_time.isoformat())
            byt = json.dumps(self.message).encode('utf8')
            response = requests.patch(url=self.api_endpoint_send, data=byt, headers=self.headers, verify=False)
            response.raise_for_status()
        except HTTPError as http_err:
            logger.exception(f'SENDING MSG: HTTP error occured: {http_err}')
        except Exception as error:
            logger.exception(f'SENDING MSG: Some error occured: {error}')


    def get_message(self):
        """
        Method Description: send http 'get' request to server
        """
        try:
            response = requests.get(url=self.api_endpoint_send, headers=self.headers, verify=False)
            response.raise_for_status()
            r = response.json()
            self.message["data"]["attributes"]["status"] = r["data"]["attributes"]["status"]
            self.message["data"]["attributes"]["duration"] = r["data"]["attributes"]["duration"]
        except HTTPError as http_err:
            logger.exception(f'GETTING MSG: HTTP error occured: {http_err}')
        except Exception as error:
            logger.exception(f'GETTING MSG: Some error occured: {error}')

def get_time():
    """
    Function Description : returns the current UTC time
    """
    cur_time = pytz.utc.localize(datetime.datetime.utcnow())
    return cur_time

def get_rssi(modem, rssi_array):
    try:
        stri = 'AT+CSQ\r\n'
        modem.write(stri.encode('utf-8'))
        time.sleep(1)
        t = modem.read(1000)
        t = t.decode('utf-8')
        idx = t.find(":")
        print(float(t[idx+2:idx+4]))
        if 2 < int(t[idx+2:idx+4])+1 < 30:
             logger.info(f'RSSI: {rssi_array[str(int(t[idx+2:idx+4])+1)]} dBm')
        else:
             logger.info(f'RSSI out of bounds or not known. Returned {int(t[idx+2:idx+4])+1}')
    except:
        logger.warning('Could not read RSSI from modem')

def main():
    try:
        # Translate AT+CSQ command returns to rssi 
        rssi_array = {'2':-109,
                 '3':-107,
                 '4':-105,
                 '5':-103,
                 '6':-101,
                 '7':-99,
                 '8':-97,
                 '9':-95,
                 '10':-93,
                 '11':-91,
                 '12':-89,
                 '13':-87,
                 '14':-85,
                 '15':-83,
                 '16':-81,
                 '17':-79,
                 '18':-77,
                 '19':-75,
                 '20':-73,
                 '21':-71,
                 '22':-69,
                 '23':-67,
                 '24':-65,
                 '25':-63,
                 '26':-61,
                 '27':-59,
                 '28':-57,
                 '29':-55,
                 '30':-53}


        # Create object that handles parsing and getting messages
        msg = MsgHandler()
        l = ["ffmpeg", "-i", "rtsp://192.168.1.88", "-s", "480x320", "-pix_fmt", "yuv420p", "-vcodec", "libx264", "-r", "15", "-f", "flv", "rtmp://62.74.232.210:9000/live/stream"]

        # if at least one subprocess has been created, then p_exists =  True
        p_exists = False
        logger.info('Process for streaming started ...\n\n')

        c =0

        while 1:                    # main loop
            modem = serial.Serial("/dev/ttyS0", baudrate = 115200, timeout = 1.0)
            while 1:                    # keep getting requests until you have to stream
                msg.get_message()
                time.sleep(1)
                c=c+1
                #logger.info(f'request received is {msg.message["data"]["attributes"]["status"]}')
                if int(msg.message["data"]["attributes"]["status"]):            # if status is True, then break loop and start streaming
                    logger.info('Starting streaming ...')
                    break
                else:                                                           # else wait 1 min, and then repeat request
                    time.sleep(59)
                    pass
            

            p = subprocess.Popen(l, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid)     # create subprocess p that streams video
            p_exists = True                                                             

            if p.poll() is None:                                                        # if p is active, then update logs and send positive response to server
                msg.message["data"]["attributes"]["response"] = "running"
                msg.send_message()
                logger.info('Video streaming started!')
            

            # Get duration
            cnt =0
            d = int(msg.message["data"]["attributes"]["duration"])
            if d<0:         # if duration (min) is given negative, then stream for maximum 2 hours
                d = 60*2
                logger.info(f'No duration given. MAX DEFAULT: {d} mins')


            while cnt < d:                      # main streaming loop
                msg.get_message()
                time.sleep(1)
                get_rssi(modem, rssi_array)     # get rssi for signal quality
                cnt+=1
                if not int(msg.message["data"]["attributes"]["status"]):            # If status is changed on server then stop streaming and
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)                    # Send the kill signal to all the process groups
                    logger.warning('Request received to stop streaming!')
                    break
                else:                                                               # Else just sleep for 1 min
                    time.sleep(58)
                    pass
            os.killpg(os.getpgid(p.pid), signal.SIGTERM) 
            msg.message["data"]["attributes"]["status"] = False
            msg.message["data"]["attributes"]["response"] = "stopped"
            logger.warning(f'Streaming stopped after {cnt} minutes')
            msg.send_message()
            modem.close()
    except (KeyboardInterrupt, SystemExit):                                     # in the case of keyboard interrupt or unexpected program exit, make sure the streaming process stops
        modem.close()
        if p_exists:
            if p.poll() is None:                                                # if the streaming process is running then,
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)                    # send the signal to all the process groups to kill it

if __name__ == '__main__':
    main()
