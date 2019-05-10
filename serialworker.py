import serial
import time
import multiprocessing
import config

SERIAL_TEST_PORT = "/dev/ttys000"
SERIAL_TEST_BAUDRATE = 115200

# SERIAL1_PORT = '/dev/ttymxc0'	## node1
# SERIAL2_PORT = '/dev/ttymxc1'	## node2
# SERIAL_BAUDRATE = 115200


class SerialProcess(multiprocessing.Process):

    def __init__(self, input_queue, output_queue):
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.sp = [serial.Serial(SERIAL_TEST_PORT, SERIAL_TEST_BAUDRATE, timeout=1)]
        # self.sp = [serial.Serial(config.SERIAL_PORT[node_number], config.SERIAL_BAUDRATE, timeout=1) for node_number in range(config.NODE_NUM)]

    def close(self, node):
        self.sp[node].close()

    def write_serial(self, node, data):
        self.sp[node].write(data)
        # time.sleep(1)

    def read_serial(self, node):
        return self.sp[node].read()

    def run(self):
        self.sp[0].flushInput()
        # for serial_instance in self.sp:
        #     print(serial_instance)
        #     serial_instance.flushInput()

        # self.sp[0].flushInput()
        # self.sp[1].flushInput()

        while True:
            time.sleep(0.001)

            # for node in range(config.NODE_NUM):
            for node in range(config.NODE_NUM):
                if not self.input_queue[node].empty():
                    data = self.input_queue[node].get()
                    # print("write to serial:" + data)
                    # send it to the serial device
                    self.write_serial(node, data)

                data = ''
                i = 0
                # look for incoming serial data
                waitlen = self.sp[node].inWaiting()
                while waitlen > 0 and i < 1024:
                    data += self.sp[node].read(waitlen).decode("UTF-8")
                    i += waitlen
                    waitlen = self.sp[node].inWaiting()
                    # print("read from serial:"+data)

                if data is not '':
                    # send it back to flask
                    self.output_queue[node].put(data)
