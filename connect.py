import time
import os
import subprocess

def do(str): 
    try: 
        #This command could have multiple commands separated by a new line \n
        some_command = "export PATH=$PATH://server.sample.mo/app/bin \n customupload abc.txt"

        p = subprocess.Popen(str, stdout=subprocess.PIPE, shell=True)   

        (output, err) = p.communicate()  

        #This makes the wait possible
        p_status = p.wait()
        print ("rc should be.. :")
        rc = p.returncode
        print (rc)
        if (rc!=0): 
                return (-2)
        #output = os.popen(str)
        time.sleep(0.1)
        print ("ok")
        return 1 
        
    except: 
        return -1 



i=0
tries =0
while ((i!=9) and  (tries!=5)):
    i=0 
    tries=tries+1

    if (do("qmicli -d /dev/cdc-wdm0 --dms-set-operating-mode='online'")==1):
        i=i+1
    if (do("qmicli -d /dev/cdc-wdm0 --dms-set-operating-mode='online'")==1):
        i=i+1
    if (do("ip link set wwan0 down")==1):
        i=i+1
    if (do("echo 'Y' | sudo tee /sys/class/net/wwan0/qmi/raw_ip")==1):
        i=i+1
    if (do("ip link set wwan0 up")==1):
        i=i+1
    if (do("qmicli -p -d /dev/cdc-wdm0 --device-open-net='net-raw-ip|net-no-qos-header' --wds-start-network=\"apn='internet',username=' ',password=' ',ip-type=4\" --client-no-release-cid")==1):
        i=i+1
    if (do("timeout 3 udhcpc -i wwan0")==1):
        i=i+1
    if (do("timeout 3 ip a s wwan0")==1):
        i=i+1
    if (do("timeout 3 ip r s")==1):
        i=i+1

    print (i)
    time.sleep(5)
