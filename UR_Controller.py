from ast import Break
from nntplib import GroupInfo
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
# request = client.read_input_registers(0,3) 
# result = request.registers
# print(result)
# print(init_q)

def gripper_activate():
    client.connect()
    client.write_registers(0, [256,0,0])
    client.close()

def gripper_close():
    client.connect()
    # client.write_registers(0, [2816,20,51240])
    client.write_registers(0, [2816,30,65535])
    client.close()

def gripper_open():
    client.connect()
    client.write_registers(0,[2816,0,51240])
    client.close()



q_home = [math.radians(-88),math.radians(-98), math.radians(-146.50), math.radians(-113), math.radians(-89),math.radians(45)]
q_home_flip = [math.radians(-90),math.radians(-109), math.radians(-133.66), math.radians(62.16), math.radians(90),math.radians(225)]
q_point_wait = [math.radians(-185),math.radians(-109),math.radians(-133),math.radians(62),math.radians(90), math.radians(225)]

p_point_wait = [-0.600,0.195,0.311,0.550,-1.530,-0.687]
p_pick_wait = [-0.500,0.195,0.311,0.550,-1.530,-0.687]
p_pick = [-0.770,0.068075,0.24451,0.550,-1.530,-0.687]

q_point_place1 = [math.radians(8),math.radians(-75),math.radians(-148),math.radians(-136),math.radians(-79), math.radians(45)]
q_point_place2 = [math.radians(-5.46),math.radians(-143.56),math.radians(-65.84),math.radians(-150),math.radians(-94), math.radians(45)]


p_place1 = [0.9714276306931491, 0.047, 0.10332644670148668, 1.7099031506989701, 0.7289580658726769, 1.7637410252833001]
p_place2 = [0.9714276306931491, -0.30031798093645892, 0.10332644670148668, 1.7099031506989701, 0.7289580658726769, 1.7637410252833001]

p_place_new1 = [0.9794276306931491, -0.04131798093645892, 0.150, 1.7099031506989701, 0.7289580658726769, 1.7637410252833001]
p_place_new2 = [0.82667, -0.17344, 0.150, 1.7099031506989701, 0.7289580658726769, 1.7637410252833001]
p_place_new3 = [0.679, -0.33582, 0.150, 1.7099031506989701, 0.7289580658726769, 1.7637410252833001]


p_point_place_up1 = [0.971,0.047,0.29834,1.710,0.729,1.764]
p_point_place_up2 = [0.971,-0.30031798093645892,0.29834,1.710,0.729,1.764]

def moveJ(q):
    spd = 0.9
    acc = 0.5
    rtde_c.moveJ(q, spd, acc,True)
def moveL(p):
    spd = 0.5
    acc = 0.2
    rtde_c.moveL(p, spd, acc,True)
def  moveL_FK(q):
    spd = 0.3
    acc = 0.1
    rtde_c.moveL_FK(q, spd, acc,True)

def moveJ_IK(p):
    spd = 0.8
    acc = 0.3
    rtde_c.moveJ_IK(p,spd,acc,True)
            
def place_box():
    global r
    global p_place_offset
    offsetx = 0.07
    if r == 0:
        moveL(p_place_offset)
        p_place_offset[0] = p_place_offset[0] - offsetx
        p_point_place_up1[0] = p_place_offset[0] 
    elif r == 1:
        moveL(p_place_offset)
        p_place_offset[0] = p_place_offset[0] - offsetx
        p_point_place_up2[0] = p_place_offset[0]

def place_3box():
    global r
    if r == 0:
        moveL(p_place_new1)
        r +=1
    elif r == 1:
        moveL(p_place_new2)
        r +=1
    elif r == 2:
        moveL(p_place_new3)
        r = 0
        
            

def state_light(red,yellow,green):
    rtde_io_.setStandardDigitalOut(0, red)
    rtde_io_.setStandardDigitalOut(1, yellow)
    rtde_io_.setStandardDigitalOut(2, green)
                    
def path2grip_Stacker(ypos,zpos):
    global step
    global completeflag
    global r
    global p_place_offset
    state_light(0,1,0)
    while True:
        if rtde_c.getAsyncOperationProgress() != 0:
            if step == 0:
                print('step0')
                moveJ(q_home_flip) 
                step += 1
            elif step == 1:
                print('step1')
                moveJ(q_point_wait)
                step += 1
            elif step == 2:
                print('step2')
                p_pick_wait[1] = ypos/1000
                p_pick_wait[2] = zpos/1000
                moveL(p_pick_wait) # IK from pic offset X -550
                step += 1  
            elif step == 3:
                print('step3')
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
                moveL(p_point_wait)
                step += 1 
            elif step == 6:
                print('step6')
                moveJ(q_home_flip)
                step += 1  
            elif step == 7:
                print('step7')
                moveJ(q_home)
                step += 1
            elif step == 8: #step place row
                print('step8')
                moveJ(q_point_place1)
                step += 1
            elif step == 9:
                print('step9')
                place_box()
                step += 1
            elif step == 10:
                print('step10')
                gripper_open()
                time.sleep(1)
                if r == 0 :
                    moveL(p_point_place_up1)
                    if p_place_offset[0] < 0.60:
                        r = 1
                        p_place_offset = p_place2
                elif r == 1:
                    moveL(p_point_place_up2)
                    if p_place_offset[0] < 0.60:
                        r = 0
                        p_place_offset = p_place1
                step += 1
            elif step == 11:
                print('step11')
                gripper_open()
                time.sleep(1)
                moveL_FK(q_point_place1)
                step += 1  
            elif step == 12:
                print('step12')
                gripper_open()
                time.sleep(1)
                moveJ(q_home)
                step += 1 
        if step == 13:
            step = 0 
            completeflag = True
            state_light(0,0,1)
            break

def place_box_test():
    global r
    global p_place_offset
    global step
    offsetx = 0.07
    while True:
        if rtde_c.getAsyncOperationProgress() != 0:
            if step == 0:
                if r == 0:
                    moveL(p_place_offset)
                    p_place_offset[0] = p_place_offset[0] - offsetx
                    p_point_place_up1[0] = p_place_offset[0]
                    print(p_place_offset)
                    if p_place_offset[0] < 0.60:
                        r = 1
                        p_place_offset = []
                        p_place_offset = p_place2
                elif r == 1:
                    moveL(p_place_offset)
                    p_place_offset[0] = p_place_offset[0] - offsetx
                    p_point_place_up2[0] = p_place_offset[0]
                    print(p_place_offset)
                    if p_place_offset[0] < 0.60:
                        r = 0
                        p_place_offset = []
                        p_place_offset = p_place1
                step +=1
            elif step ==1:
                if r == 0 :
                    moveL(p_point_place_up1)
                elif r == 1:
                    moveL(p_point_place_up2)
                step =0
   
def path2grip_3product(ypos,zpos):
    global step
    global completeflag
    global r
    global p_place_offset
    state_light(0,1,0)
    while True:
        if rtde_c.getAsyncOperationProgress() != 0:
            if step == 0:
                print('step0')
                moveJ(q_home_flip) 
                step += 1
            elif step == 1:
                print('step1')
                moveJ(q_point_wait)
                step += 1
            elif step == 2:
                print('step2')
                p_pick_wait[1] = ypos/1000
                p_pick_wait[2] = zpos/1000
                moveL(p_pick_wait) # IK from pic offset X -550
                step += 1  
            elif step == 3:
                print('step3')
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
                moveL(p_point_wait)
                step += 1 
            elif step == 6:
                print('step6')
                moveJ(q_home_flip)
                step += 1  
            elif step == 7:
                print('step7')
                moveJ(q_home)
                step += 1
            elif step == 8: #step place row
                print('step8')
                moveJ(q_point_place1)
                step += 1
            elif step == 9:
                print('step9')
                place_3box()
                step += 1
            elif step == 10:
                print('step10')
                gripper_open()
                time.sleep(1)
                moveL_FK(q_point_place1)
                step += 1  
            elif step == 11:
                print('step11')
                gripper_open()
                time.sleep(1)
                moveJ(q_home)
                step += 1 
        if step == 12:
            step = 0 
            completeflag = True
            state_light(0,0,1)
            break
step = 0 
r = 0
completeflag = False
p_place_offset = p_place1
gripper_activate()
gripper_open()
# place_box_test()
# gripper_close()
state_light(0,0,1)

# path2grip(-92.245,240.335)
# path2grip(0.068075,0.24451)