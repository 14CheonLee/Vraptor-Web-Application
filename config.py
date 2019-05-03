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
INTERPRETER_HOST = "vraptor-interpreter"
# INTERPRETER_HOST = "127.0.0.1"
INTERPRETER_PORT = 8080
INTERPRETER_NAME = "interpreter"
# INTERPRETER_NAME = "vraptor_interpreter_beta_0_0_1_war/interpreter"

CATEGORY_SENSOR = "sensor"
CATEGORY_FAN = "fan"
CATEGORY_NODE = "node"

SENSOR_DATA_CALL_TIME = 3
SENSOR_DATA_SEND_TIME = 0.001
CONSOLE_READ_TIME = 0.001

NODE_NUM = 1
# NODE_NUM = 32
SERIAL_BAUDRATE = 115200
SERIAL_PORT = {
    0: "/dev/ttyUSB0",
    1: "/dev/ttymxc1",
    2: "/dev/ttymxc2",
    3: "/dev/ttymxc3",
    4: "/dev/ttymxc4",
    5: "/dev/ttymxc5",
    6: "/dev/ttymxc6",
    7: "/dev/ttymxc7",
    8: "/dev/ttymxc8",
    9: "/dev/ttymxc9",
    10: "/dev/ttymxc10",
    11: "/dev/ttymxc11",
    12: "/dev/ttymxc12",
    13: "/dev/ttymxc13",
    14: "/dev/ttymxc14",
    15: "/dev/ttymxc15",
    16: "/dev/ttymxc16",
    17: "/dev/ttymxc17",
    18: "/dev/ttymxc18",
    19: "/dev/ttymxc19",
    20: "/dev/ttymxc20",
    21: "/dev/ttymxc21",
    22: "/dev/ttymxc22",
    23: "/dev/ttymxc23",
    24: "/dev/ttymxc24",
    25: "/dev/ttymxc25",
    26: "/dev/ttymxc26",
    27: "/dev/ttymxc27",
    28: "/dev/ttymxc28",
    29: "/dev/ttymxc29",
    30: "/dev/ttymxc30",
    31: "/dev/ttymxc31"
}

DATABASE_URI = "sqlite:///db.db"  # Should change it
