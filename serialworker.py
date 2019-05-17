import serial
import time
import multiprocessing
import config


class SerialProcess(multiprocessing.Process):

    def __init__(self, input_queue, output_queue):
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.sp = [serial.Serial(config.SERIAL_PORT[node_number], config.SERIAL_BAUDRATE, timeout=1)
                   for node_number in range(config.NODE_NUM)]

    def close(self, node):
        self.sp[node].close()

    def write_serial(self, node, data):
        self.sp[node].write(data)
        # time.sleep(1)

    def read_serial(self, node):
        return self.sp[node].read()

    def run(self):
        # Setting flush of the Serial instance
        for serial_instance in self.sp:
            serial_instance.flushInput()

        while True:
            time.sleep(config.SERIAL_RUN_INTERVAL_TIME)

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

                # Checking whether using serial with UART
                try:
                    while waitlen > 0 and i < config.SERIAL_BUFFER_SIZE:
                        data += self.sp[node].read(waitlen).decode("UTF-8")
                        i += waitlen
                        waitlen = self.sp[node].inWaiting()

                except serial.SerialException:
                    """
                    @TODO
                    > Redirect to the reject page
                    """
                    print("Occurring an Error")

                if data is not '':
                    # send it back to flask
                    self.output_queue[node].put(data)
