"""
Config
"""
PROTOCOL = "http"
HOST = "0.0.0.0"
PORT = 9001

ADMIN_USER_ID = "admin"
ADMIN_USER_PW = "admin"
ADMIN_EMAIL = "admin@admin.com"

INTERPRETER_PROTOCOL = "http"
# INTERPRETER_HOST = "vraptor-interpreter"
INTERPRETER_HOST = "127.0.0.1"
# INTERPRETER_PORT = 9002
INTERPRETER_PORT = 5001
INTERPRETER_NAME = "interpreter"
# INTERPRETER_NAME = "vraptor_interpreter_beta_0_0_1_war/interpreter"

CATEGORY_SENSOR = "sensor"
CATEGORY_FAN = "fan"
CATEGORY_NODE = "node"

SENSOR_DATA_CALL_TIME = 3
SENSOR_DATA_SEND_TIME = 0.001
CONSOLE_READ_TIME = 0.001

NODE_NUM = 2
SERIAL_BAUDRATE = 115200
SERIAL_RUN_INTERVAL_TIME = 0.001
SERIAL_BUFFER_SIZE = 1024
SERIAL_PORT = {
    0: "/dev/ttymxc0",
    1: "/dev/ttymxc1",
}

DATABASE_URI = "sqlite:///db.db"  # Should change it
