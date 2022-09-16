from ast import Break
from nntplib import GroupInfo
from os import waitstatus_to_exitcode
from pickle import TRUE
from re import T
from tkinter import Y
from rtde_control import RTDEControlInterface as RTDEControl
from rtde_receive import RTDEReceiveInterface as RTDEReceive
from rtde_io import RTDEIOInterface as RTDEIO
import time
import math
from rtde_control import Path, PathEntry
from pymodbus.client.sync import ModbusTcpClient

rtde_io_ = RTDEIO("192.168.1.2")
rtde_c = RTDEControl("192.168.1.2")
rtde_r = RTDEReceive("192.168.1.2")
client = ModbusTcpClient('192.168.1.11')
connection = client.connect()

# init_q = rtde_r.getActualQ()
# initpose = rtde_r.getActualTCPPose()
# request = client.read_input_registers(0,3) 
# result = request.registers
# print(result)
# print(init_q)
# print(initpose) 

def gripper_activate():
    client.connect()
    client.write_registers(0, [256,0,0])
    # client.close()

def gripper_close():
    client.connect()
    # client.write_registers(0, [2816,20,51240])
    client.write_registers(0, [2816,30,65535])
    # client.close()

def gripper_open():
    client.connect()
    client.write_registers(0,[2816,0,51240])
    # client.close()






Home_position_Q = [-0.17660361925234014, -1.3390533340028306, -2.5158050060272217, -2.4327007732787074, -1.703329865132467, 0.796628475189209]
Waiting_position_Q=[-3.2888758818255823, -1.7659584484496058, -2.5688564777374268, 1.1808911997028808, 1.6163935661315918, 3.9280617237091064]

p_pick_wait = [-0.600,0.195,0.311,0.550,-1.530,-0.687]
p_pick = [-0.795,0.068075,0.24451,0.550,-1.530,-0.687]

p_place_new1 = [0.9794276306931491, -0.04131798093645892, 0.100, 1.7099031506989701, 0.7289580658726769, 1.7637410252833001]
p_place_new2 = [0.82667, -0.17344, 0.100, 1.7099031506989701, 0.7289580658726769, 1.7637410252833001]
p_place_new3 = [0.679, -0.33582, 0.100, 1.7099031506989701, 0.7289580658726769, 1.7637410252833001]


p_place_new1_up = [0.9794276306931491, -0.04131798093645892, 0.250, 1.7099031506989701, 0.7289580658726769, 1.7637410252833001]
p_place_new2_up = [0.82667, -0.17344, 0.250, 1.7099031506989701, 0.7289580658726769, 1.7637410252833001]
p_place_new3_up = [0.679, -0.33582, 0.250, 1.7099031506989701, 0.7289580658726769, 1.7637410252833001]

def moveJ(q):
    spd = 0.8
    acc = 0.3
    rtde_c.moveJ(q, spd, acc,True)
def moveL(p):
    spd = 0.4
    acc = 0.2
    rtde_c.moveL(p, spd, acc,True)
def  moveL_FK(q):
    spd = 0.4
    acc = 0.2
    rtde_c.moveL_FK(q, spd, acc,True)

def moveJ_IK(p):
    spd = 0.8
    acc = 0.2
    rtde_c.moveJ_IK(p,spd,acc,True)
            

def place_3box():
    global r
    if r == 0:
        moveL(p_place_new1)
    elif r == 1:
        moveL(p_place_new2)
    elif r == 2:
        moveL(p_place_new3)

def upper_3box():
    global r
    if r == 0:
        moveL(p_place_new1_up)
        r +=1
    elif r == 1:
        moveL(p_place_new2_up)
        r +=1
    elif r == 2:
        moveL(p_place_new3_up)
        r = 0
        
def state_light(red,yellow,green):
    rtde_io_.setStandardDigitalOut(0, red)
    rtde_io_.setStandardDigitalOut(1, yellow)
    rtde_io_.setStandardDigitalOut(2, green)
                    

def path2grip_3product(xpos,ypos,zpos):
    global step
    global completeflag
    global r
    global p_place_offset
    state_light(0,1,0)
    while True:
        if rtde_c.getAsyncOperationProgress() != 0:
            if step == 0:
                print('step0')
                moveJ(Home_position_Q) 
                step += 1
            elif step == 1:
                print('step1')
                moveJ(Waiting_position_Q)
                step += 1
            elif step == 2:
                print('step2')
                # p_pick_wait[0] = xpos/1000
                p_pick_wait[1] = ypos/1000
                p_pick_wait[2] = zpos/1000
                moveL(p_pick_wait) # IK from pic offset X -550
                step += 1  
            elif step == 3:
                print('step3')
                p_pick[0] = xpos/1000
                p_pick[1] = ypos/1000
                p_pick[2] = zpos/1000
                moveL(p_pick) # IK from pic X -775
                step += 1
            elif step == 4:
                print('step4')
                gripper_close()
                time.sleep(1)
                moveL(p_pick_wait)
                step += 1
            elif step == 5:
                print('step5')
                moveL_FK(Waiting_position_Q)
                step += 1 
            elif step == 6:
                print('step6')
                moveJ(Home_position_Q) 
                step += 1  
            elif step == 7:
                print('step7')
                place_3box()
                step += 1
            elif step == 8:
                print('step8')
                gripper_open()
                time.sleep(1)
                upper_3box() 
                step += 1
            elif step == 9:
                print('step9')
                gripper_open()
                time.sleep(1)
                moveL_FK(Home_position_Q) 
                step += 1    
        if step == 10:
            step = 0 
            completeflag = True
            state_light(0,0,1)
            break
step = 0 
r = 0
completeflag = False
# gripper_activate()
# time.sleep(1)
gripper_close()
time.sleep(1)
gripper_open()
# place_box_test()

state_light(0,0,1)
# moveJ(Home_position_Q)

# path2grip(-92.245,240.335)
# path2grip(0.068075,0.24451)