import serial
import time
import multiprocessing


## Change this to match your local settings
SERIAL1_PORT = '/dev/ttymxc0'	## node1
SERIAL2_PORT = '/dev/ttymxc1'	## node2
SERIAL_BAUDRATE = 115200

class SerialProcess(multiprocessing.Process):
 
    def __init__(self, input_queue, output_queue):
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.sp = [serial.Serial(SERIAL1_PORT, SERIAL_BAUDRATE, timeout=1), serial.Serial(SERIAL2_PORT, SERIAL_BAUDRATE, timeout=1)]
 
    def close(self, node):
        self.sp[node].close()
 
    def writeSerial(self, node, data):
        self.sp[node].write(data)
        # time.sleep(1)
        
    def readSerial(self, node):
        return self.sp[node].read()
 
    def run(self):
 
    	self.sp[0].flushInput()
    	self.sp[1].flushInput()
 
        while True:
            time.sleep(0.001)
            for node in range(2):
                if not self.input_queue[node].empty():
                    data = self.input_queue[node].get()
                    #print("write to serial:" + data)
                    # send it to the serial device
                    self.writeSerial(node, data)
     
                data = ''
                i = 0
                # look for incoming serial data
                waitlen = self.sp[node].inWaiting()
                while (waitlen > 0 and i < 1024):
                    data += self.sp[node].read(waitlen)
                    i += waitlen
                    waitlen = self.sp[node].inWaiting()
                    #print("read from serial:"+data)

                if data is not '':
                    # send it back to flask
                    self.output_queue[node].put(data)

