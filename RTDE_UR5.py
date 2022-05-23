from ast import Break
from nntplib import GroupInfo
from pickle import TRUE
from re import T
from tkinter import Y
from rtde_control import RTDEControlInterface as RTDEControl
from rtde_receive import RTDEReceiveInterface as RTDEReceive
import time
import math
from rtde_control import Path, PathEntry
from pymodbus.client.sync import ModbusTcpClient

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
    client.write_registers(0, [2816,0,0])
    client.close()

def gripper_close():
    client.connect()
    client.write_registers(0, [2816,40,51240])
    client.close()

def gripper_open():
    client.connect()
    client.write_registers(0,[2816,0,51240])
    client.close()



q_home = [math.radians(-88),math.radians(-98), math.radians(-146.50), math.radians(-113), math.radians(-89),math.radians(45)]
q_home_flip = [math.radians(-90),math.radians(-109), math.radians(-133.66), math.radians(62.16), math.radians(90),math.radians(225)]
q_point_wait = [math.radians(-185),math.radians(-109),math.radians(-133),math.radians(62),math.radians(90), math.radians(225)]
p_pick_wait = [-0.600,0.068075,0.24451,0.550,-1.530,-0.687]
p_pick = [-0.770,0.068075,0.24451,0.550,-1.530,-0.687]

q_point_place1 = [math.radians(0),math.radians(-77),math.radians(-147),math.radians(-136),math.radians(-87.80), math.radians(45)]
q_point_place2 = [math.radians(-5.46),math.radians(-143.56),math.radians(-65.84),math.radians(-150),math.radians(-94), math.radians(45)]

p_place1 = [0.9714276306931491, -0.20131798093645892, 0.12532644670148668, 1.7099031506989701, 0.7289580658726769, 1.7637410252833001]
p_place2 = [0.9714276306931491, 0, 0.15032644670148668, 1.2599031506989701, 0.7289580658726769, 1.7637410252833001]


def moveJ(q):
    spd = 0.8
    acc = 0.3
    rtde_c.moveJ(q, spd, acc,True)
def moveL(p):
    spd = 0.3
    acc = 0.1
    rtde_c.moveL(p, spd, acc,True)

def moveJ_IK(p):
    spd = 0.8
    acc = 0.3
    rtde_c.moveJ_IK(p,spd,acc,True)

def place_box():
    global step
    global r
    global p_place_offset
    offsetx = 0.1
    while True:
        if rtde_c.getAsyncOperationProgress() != 0:
            if step == 0:
                moveJ(q_point_place1)
                step += 1
            elif step == 1:
                if r == 0:
                    moveJ_IK(p_place_offset)
                    p_place_offset[0] = p_place_offset[0] - offsetx
                    step = 0
                    # print(p_place_offset)
                    if p_place_offset[0] < 0.65:
                        r = 1
                        p_place_offset = p_place2
                elif r == 1:
                    moveJ_IK(p_place_offset)
                    p_place_offset[0] = p_place_offset[0] - offsetx
                    step = 0
                    # print(p_place_offset)
                    if p_place_offset[0] < 0.65:
                        r = 0
                        p_place_offset = p_place1
                        break
def place_box2():
    global step
    global r
    global p_place_offset
    offsetx = 0.1
    if r == 0:
        moveJ_IK(p_place_offset)
        p_place_offset[0] = p_place_offset[0] - offsetx
        if p_place_offset[0] < 0.65:
            r = 1
            p_place_offset = p_place2
    elif r == 1:
        moveJ_IK(p_place_offset)
        p_place_offset[0] = p_place_offset[0] - offsetx
        step +=1
        if p_place_offset[0] < 0.65:
            r = 0
            p_place_offset = p_place1                  
                    



def path2grip(ypos,zpos):
    global step
    global completeflag
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
                p_pick_wait[1] = ypos
                p_pick_wait[2] = zpos
                moveL(p_pick_wait) # IK from pic offset X -550
                step += 1  
            elif step == 3:
                print('step3')
                p_pick[1] = ypos
                p_pick[2] = zpos
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
                moveJ(q_point_wait)
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
                place_box2()
                step += 1
            elif step == 10:
                print('step10')
                gripper_open()
                time.sleep(1)
                moveJ(q_point_place1)
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
            break

# no.1 Y = -92.245 Z =240.335
# No.2 Y = 615.835 Z =479.98
# No.3 Y =68.075 Z = 244.51       
step = 0 
r = 0
completeflag = False
p_place_offset = p_place1
gripper_open()
path2grip(-0.092245,0.240335)
path2grip(0.068075,0.24451)


# init_TCP = rtde_r.getActualTCPPose()
# print(init_TCP)
# place_box()
# moveJ(q_point_place1)

#close gripper [2816,40,25640]
#opengripper [2816,0,65535]

# path = Path()
# vel = 0.5
# acc = 0.5
# init_q = rtde_r.getActualQ()


# # path.addEntry(PathEntry(PathEntry.MoveJ, PathEntry.PositionTcpPose, [-0.140, -0.400, 0.100, 0, 3.14, 0, vel, acc, 0.0]))
# status=rtde_c.getAsyncOperationProgress()
# print(status)
# gripper_activate()
# gripper_close()
# gripper_open()
# rtde_c.moveJ(q_home, 0.2, 0.2,True)
# status=rtde_c.getAsyncOperationProgress()
# print(status)



    

    






# path.addEntry(PathEntry(PathEntry.MoveJ, PathEntry.PositionJoint, q_home))
# print(path)


# rtde_c.moveJ(q_home, 0.5, 0.5,True)
# rtde_c.stopScript()
# print(init_q)
# print(init_TCP)
# velocity = 0.5
# acceleration = 0.5
# blend_1 = 0.0
# blend_2 = 0.02
# blend_3 = 0.0
# path_pose1 = [-0.15314810893578093, -0.4873042028194518, 0.2892340309193333, -1.250778471234512, -2.8747639401026372, 0.004345026568780956]
# path_pose2 = [0.4921030043189896, -0.136957882249183, 0.2893284134639842, 1.1978891036477592, -2.901760525131191, 0.010303644640238066, velocity, acceleration]
# path = [path_pose1, path_pose2]
# IK = rtde_c.getInverseKinematics(path_pose1)
# print(IK)
# rtde_c.moveL(path_pose1)

# q_start = [0, -1.5785452328123988, -1.574337124824524, -1.586041112939352, 1.564824104309082, 0.788540780544281]
# q_stop = [-1.57, -1.5785452328123988, -1.574337124824524, -1.586041112939352, 1.564824104309082, 0.788540780544281]
# print(init_q)
# new_q = init_q[:]
# new_q[0] = -1.57 
# print(new_q)

# status=rtde_c.getAsyncOperationProgress()

# status1=rtde_c.getAsyncOperationProgress()
# print(status)
# print(status1)
# time.sleep(0.2)
# rtde_c.moveJ(q_stop ,0.5, 0.5)
# rtde_c.stopScript()

