from pymodbus.client.sync import ModbusTcpClient

#modbus connection
client = ModbusTcpClient('192.168.1.11')
connection = client.connect()

#read register
# request = client.read_input_registers(0,3) #covert to float
# result = request.registers
# print(result)
#write to register
# client.write_registers(0, [256,0,0])
# client.write_registers(0, [2816,0,0]) # reset gripper  
# client.write_registers(0, [2816,40,25640]) #open gripper
# client.write_registers(0, [2816,0,25640]) #close gripper
# client.close()



def gripper_activate():
    client.connect()
    client.write_registers(0, [2816,0,0])
    client.close()

def gripper_close():
    client.connect()
    client.write_registers(0, [2816,40,25640])
    client.close()


def gripper_open():
    client.connect()
    client.write_registers(0,[2816,0,25640])
    client.close()
    
