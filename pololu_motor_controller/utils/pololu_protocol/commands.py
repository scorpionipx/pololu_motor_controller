import enum


BAUD_RATE_SYNC_BYTE = 0xAA

VARIABLE_ID_BYTE_INDEX = 1


class Command:
    """
    Command
    """
    def __init__(self, name, description, payload, response_bytes):
        """
        Initializer
        :param name: command's name
        :type name: str
        :param payload: command bytes without including first 2 bytes: 0xAA (170 in decimal) as the first (command)
        byte, used for baud rate synchronization and Device Number data byte
        :type payload: bytearray
        :param response_bytes: response number of bytes
        :type response_bytes: int
        """
        self.__name = name
        self.__description = description
        self.__payload = payload
        self.__response_bytes = response_bytes

    def set_payload_byte(self, byte_index, value):
        """
        Modify one payload byte.
        :param byte_index: byte index
        :type byte_index: int
        :param value: new byte value [0, 255]
        :type value: int
        :return: None
        """
        # account for the first 2 bytes missing
        if value < 0 or value > 255:
            raise ValueError(f'Invalid byte value: {value}! Must be within interval [0, 255]! ')
        self.payload[byte_index - 2] = value

    @property
    def payload(self):
        """
        Get payload.
        :return: payload
        :rtype: bytearray
        """
        return self.__payload

    @property
    def name(self):
        """
        Get name.
        :return: name
        :rtype: str
        """
        return self.__name

    @property
    def description(self):
        """
        Get description
        :return: description
        :rtype: str
        """
        return self.__description

    @property
    def response_bytes(self):
        """
        Get number of expected response bytes.
        :return: response bytes
        :rtype: int
        """
        return self.__response_bytes

    def normalizer(self, response):
        """
        Function to normalize received raw response.
        :param response: response received
        :type response: bytearray
        :return: normalized response
        :rtype: dict
        """
        raise NotImplemented('Not implemented!')


def cmd_get_firmware_version_response_normalizer(response):
    """
    Get firmware version normalizer.
    :param response: received response
    :type response: bytearray
    :return: normalized response
    :rtype: dict
    """
    normalized = {
        'product_id': f"0x{(int.from_bytes(bytes=response[:2], byteorder='little')):04x}",
        'firmware_version': f"{int.from_bytes(bytes=response[3:4], byteorder='little'):x}."
                            f"{int.from_bytes(bytes=response[2:3], byteorder='little'):02x}",
    }
    return normalized


cmd_get_firmware_version = Command(
    name='Get Firmware Version',
    description="""This command lets you read the Simple Motor Controller product number and firmware version number. 
    The first two bytes of the response are the low and high bytes of the product ID (each Simple Motor Controller 
    version has a unique product ID), and the last two bytes of the response are the firmware minor and major version 
    numbers in binary-coded decimal (BCD) format. BCD format means that the version number is the value you get when 
    you write it in hex and then read it as if it were in decimal. For example, a minor version byte of 0x15 (21) means 
    a the minor version number is 15, not 21.
""",
    payload=bytearray([0x42, ]),
    response_bytes=4,
)
cmd_get_firmware_version.normalizer = cmd_get_firmware_version_response_normalizer


cmd_exit_safe_start = Command(
    name='Exit Safe-Start (Serial/USB input mode only)',
    description="""If the Input Mode is Serial/USB, and you have not disabled Safe-start protection, then this command 
is required before the motor can run. Specifically, this command must be issued when the controller is first powered 
up, after any reset, and after any error stops the motor. This command has no serial response.
If you just want your motor to run whenever possible, you can transmit Exit Safe Start and motor speed commands 
regularly. One potential problem with this approach is that if there is an error (e.g. the battery becomes 
disconnected) then the motor will start running immediately when the error has been resolved (e.g. the battery is 
reconnected).
If you want to prevent your motor from starting up unexpectedly after the controller has recovered from an error, then 
you should only send an Exit Safe Start command after either waiting for user input or issuing a warning to the user.
""",
    payload=bytearray([0x03, ]),
    response_bytes=0,
)


cmd_motor_forward = Command(
    name='Motor Forward (Serial/USB input mode only)',
    description="""This command lets you set the full-resolution motor target speed in the forward direction. The motor 
speed must be a number from 0 (motor stopped) to 3200 (motor forward at full speed) and is specified using two data 
bytes. The first data byte contains the low five bits of the speed and the second data byte contains the high seven 
bits of the speed.
The first speed data byte can be computed by taking the full (0-3200) speed modulo 32, which is the same as dividing 
the speed by 32, discarding the quotient, and keeping only the remainder. We can get the same result using binary math 
by bitwise-ANDing the speed with 0x1F (31). In C (and many other programming languages), these operations can be 
carried out with the following expressions:
speed_byte_1 = speed % 32;
or, equivalently:
speed_byte_1 = speed & 0x1F;
The second speed data byte can be computed by dividing the full (0-3200) speed by 32, discarding the remainder, and 
keeping only the quotient (i.e. turn the division result into a whole number by dropping everything after the decimal 
point). We can get the same result using binary math by bit-shifting the speed right five places. In C (and many other 
programming languages), these operations can be carried out with the following expressions:
speed_byte_2 = speed / 32;
or, equivalently:
speed_byte_2 = speed >> 5;
This command has no serial response.
""",
    payload=bytearray([0x05, 0x00, 0x00]),  # last 2 bytes to be changed accordingly to the desired speed
    response_bytes=0,
)


cmd_motor_reverse = Command(
    name='Motor Reverse (Serial/USB input mode only)',
    description="""This command lets you set the full-resolution motor target speed in the reverse direction. The motor 
speed must be a number from 0 (motor stopped) to 3200 (motor reverse at full speed) and is specified using two data 
bytes, the first containing the low five bits of the speed and the second containing the high seven bits of the speed. 
This command behaves the same as the Motor Forward command except the motor moves in the opposite direction.
""",
    payload=bytearray([0x06, 0x00, 0x00]),  # last 2 bytes to be changed accordingly to the desired speed
    response_bytes=0,
)


cmd_motor_brake = Command(
    name='Motor Brake (Serial/USB input mode only)',
    description="""This command causes the motor to immediately brake by the specified amount (configured deceleration 
limits are ignored). The Brake Amount byte can have a value from 0 to 32, with 0 resulting in maximum coasting (the 
motor leads are floating almost 100% of the time) and 32 resulting in full braking (the motor leads are shorted 
together 100% of the time). Requesting a brake amount greater than 32 results in a Serial Format Error. This command 
has no serial response.
""",
    payload=bytearray([0x12, 0x00]),  # last byte to be changed accordingly to the desired brake amount
    response_bytes=0,
)


cmd_stop_motor = Command(
    name='Stop Motor (any input mode)',
    description="""This command sets the motor target speed to zero and makes the controller susceptible to a 
safe-start violation error if Safe Start is enabled. Put another way, this command will stop the motor (configured 
deceleration limits will be respected) and not allow the motor to start again until the Safe-Start conditions required 
by the Input Mode are satisfied. This command has no serial response.
""",
    payload=bytearray([0x60, ]),
    response_bytes=0,
)


cmd_get_variable = Command(
    name='Get Variable (any input mode)',
    description="""This command lets you read a 16-bit variable from the Simple Motor Controller. See Section 6.4 for a 
list of all of available variables. The value of the requested variable is transmitted as two bytes, with the low byte 
sent first. You can reconstruct the variable value from these bytes using the following equation:
variable_low_byte + 256 * variable_high_byte
If the variable type is signed and the above result is greater than 32767, you will need to subtract 65536 from the 
result to obtain the correct, signed value. Alternatively, if it is supported by the language you are using, you can 
cast the result to a signed 16-bit data type.
Requesting variable IDs between 41 and 127 results in a Serial Format Error, and the controller does not transmit a 
response.
""",
    payload=bytearray([0x21, 0x00, ]),  # last byte to be changed accordingly to the desired variable id
    response_bytes=2,
)


class Commands(enum.Enum):
    """
    Commands
    """
    get_firmware_version: Command = cmd_get_firmware_version
    exit_safe_start: Command = cmd_exit_safe_start
    motor_forward: Command = cmd_motor_forward
    motor_reverse: Command = cmd_motor_reverse
    motor_brake: Command = cmd_motor_brake
    stop_motor: Command = cmd_stop_motor
    get_variable: Command = cmd_get_variable
