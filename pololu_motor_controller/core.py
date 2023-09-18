import serial
import time


from pololu_motor_controller.utils.pololu_protocol.variables import Variables
from pololu_motor_controller.utils.pololu_protocol.commands import (
    BAUD_RATE_SYNC_BYTE,

    VARIABLE_ID_BYTE_INDEX,

    Command,
    Commands,
)


class PololuMotorController:
    """
    PololuMotorController
    """
    def __init__(self, com_port, baud_rate=115200, device_number=0x0D):
        """

        :param com_port: COM Port
        :type com_port: str
        """
        # commands
        # ==============================================================================================================
        self.__commands = Commands
        # ==============================================================================================================

        # connection
        # ==============================================================================================================
        self.__com_port = com_port
        self.__baud_rate = baud_rate

        self.__connected = False
        self.__connection = self.__connect()
        # ==============================================================================================================

        # device
        # ==============================================================================================================
        self.__device_number = device_number

        device_info = self.get_firmware_version()
        self.__product_id = device_info.get('product_info', 'N/A')
        self.__firmware_version = device_info.get('firmware_version', 'N/A')
        # ==============================================================================================================

    def __log_error(self, error):  # noqa
        """

        :param error:
        :return:
        """
        print(error)

    def __connection_required(method):  # noqa
        """

        :param method:
        :return:
        """
        def wrapper(self, *args, **kwargs):
            """

            :param self:
            :param args:
            :param kwargs:
            :return:
            """
            if not self.__connected:
                raise ConnectionError('A connection must be established first!')
            return method(self, *args, **kwargs)  # noqa

        return wrapper

    def __connect(self):
        """
        Establish connection.
        :return: connection
        :rtype: serial.Serial
        """
        if not self.__connected:
            try:
                connection = serial.Serial(
                    port=self.__com_port,
                    baudrate=self.__baud_rate,
                    timeout=None,
                    bytesize=8,
                    parity='N',
                    stopbits=1,
                )
                self.__connected = True
                return connection
            except Exception as exception:
                self.__connected = False
                error = f'Failed to establish connection: {exception}'
                self.__log_error(error)
                raise ConnectionError(error)

    def __disconnect(self):
        """
        Disconnect
        :return: None
        """
        if self.__connected:
            self.__connection.close()
            self.__connected = False

    def terminate(self):
        """
        Terminate application. To be called before closing.
        :return: None
        """
        if self.__connected:
            self.stop_motor()
        self.__disconnect()

    @__connection_required  # noqa
    def send_command(self, command):
        """
        Send command to the board
        :param command: command to be sent
        :type command: Commands
        :return: sent status and received response
        :rtype: tuple
        """
        command = command.value
        command: Command

        response = None

        try:
            self.__send_bytes(bytearray([BAUD_RATE_SYNC_BYTE, self.device_number]) + command.payload)
            sent = True
        except Exception as exception:
            error = f'Failed to send command: {command}!\n{exception}'
            self.__log_error(error)
            sent = False
            response = None

        if sent:
            if command.response_bytes:
                response = self.__receive_bytes(command.response_bytes)

        return sent, response

    @__connection_required  # noqa
    def __send_bytes(self, bytes_array):
        """
        Send specified bytes to the board.
        :param bytes_array: bytes array to be sent
        :type bytes_array: bytearray
        :return: None
        """
        self.__connection.write(bytes_array)

    @__connection_required  # noqa
    def __receive_bytes(self, expected_bytes=1):
        """
        Read bytes from the board.
        :param expected_bytes: number of expected bytes
        :type expected_bytes: int
        :return: received bytes
        :rtype: bytearray
        """
        return self.__connection.read(expected_bytes)

    @property
    def com_port(self):
        """
        Get COM Port.
        :return: com port
        :rtype: str
        """
        return self.__com_port

    @property
    def baud_rate(self):
        """
        Get baud rate.
        :return: baud_rate
        :rtype: int
        """
        return self.__baud_rate

    @property
    def connected(self):
        """
        Get connected status.
        :return: connected
        :rtype: bool
        """
        return self.__connected

    @property
    def device_number(self):
        """
        Get device number.
        :return: device number
        :rtype: int
        """
        return self.__device_number

    @property
    def device_number_hex(self):
        """
        Get device number as hex value.
        :return: device number
        :rtype: str
        """
        return hex(self.__device_number)

    @property
    def commands(self):
        """
        Get commands.
        :return: commands enumeration
        :rtype: Commands
        """
        return self.__commands

    @staticmethod
    def __normalize_response(response, command):
        """__normalize_response
        Normalize response.
        :param response: received response
        :type response: bytearray
        :param command: target command
        :type command: Commands
        :return: normalized value
        :rtype: dict
        """
        normalized = command.value.normalizer(response)
        return normalized

    @__connection_required  # noqa
    def get_firmware_version(self):
        """
        Get firmware version (and product id).
        :return: firmware version and product id
        :rtype: dict
        """
        sent, response = self.send_command(self.commands.get_firmware_version)
        response = self.__normalize_response(response, self.commands.get_firmware_version)
        return response

    @__connection_required  # noqa
    def exit_safe_start(self):
        """
        Exit Safe-Start. Description available within command definition.
        :return: sent status
        :rtype: bool
        """
        self.send_command(self.commands.exit_safe_start)  # no response expected

    @__connection_required  # noqa
    def motor_forward(self, speed):
        """
        Motor Forward. Description available within command definition.
        :param speed: desired speed [0-3200]
        :type speed: int
        :return: None
        """
        speed_byte_1 = speed & 0x1F  # as specified in documentation
        speed_byte_2 = speed >> 5  # as specified in documentation

        motor_forward_command = self.commands.motor_forward.value
        motor_forward_command.set_payload_byte(3, speed_byte_1)
        motor_forward_command.set_payload_byte(4, speed_byte_2)

        self.send_command(self.commands.motor_forward)  # no response expected

    @__connection_required  # noqa
    def motor_reverse(self, speed):
        """
        Motor Reverse. Description available within command definition.
        :param speed: desired speed [0-3200]
        :type speed: int
        :return: None
        """
        speed_byte_1 = speed & 0x1F  # as specified in documentation
        speed_byte_2 = speed >> 5  # as specified in documentation

        motor_forward_command = self.commands.motor_reverse.value
        motor_forward_command.set_payload_byte(3, speed_byte_1)
        motor_forward_command.set_payload_byte(4, speed_byte_2)

        self.send_command(self.commands.motor_reverse)  # no response expected

    @__connection_required  # noqa
    def motor_brake(self, brake_amount=1):
        """
        Motor Brake. Description available within command definition.
        :param brake_amount: desired brake amount [0-32]
        :type brake_amount: int
        :return: None
        """
        motor_forward_command = self.commands.motor_forward.value
        motor_forward_command.set_payload_byte(3, brake_amount)

        self.send_command(self.commands.motor_brake)  # no response expected

    @__connection_required  # noqa
    def stop_motor(self):
        """
        Stop Motor. Description available within command definition.
        Exit Safe Start command required in order to control motor again.
        :return: None
        """
        self.send_command(self.commands.stop_motor)  # no response expected

    @__connection_required  # noqa
    def get_input_voltage(self):
        """
        Get input voltage.
        :return: input voltage in mV
        :rtype: int
        """
        get_variable_command = self.commands.get_variable.value
        get_variable_command.set_payload_byte(VARIABLE_ID_BYTE_INDEX, Variables.INPUT_VOLTAGE.value)

        sent, response = self.send_command(self.commands.get_variable)
        voltage_mv = int.from_bytes(bytes=response, byteorder='little')
        return voltage_mv

    @__connection_required  # noqa
    def get_temperature(self):
        """
        Get temperature.
        :return: board temperature as measured by a temperature sensor near the motor driver
        :rtype: float
        """
        get_variable_command = self.commands.get_variable.value
        get_variable_command.set_payload_byte(VARIABLE_ID_BYTE_INDEX, Variables.TEMPERATURE.value)

        sent, response = self.send_command(self.commands.get_variable)
        temperature = int.from_bytes(bytes=response, byteorder='little') / 10
        return temperature


def test():
    """
    test

    :return:
    """
    pmc = PololuMotorController(
        com_port='COM7',
    )

    fv = pmc.get_firmware_version()
    print(fv)
    voltage = pmc.get_input_voltage()
    print(f'input voltage: {voltage}mV')
    temperature = pmc.get_temperature()
    print(f'temperature: {temperature}°C')
    pmc.exit_safe_start()
    pmc.motor_forward(300)
    time.sleep(3)
    pmc.motor_brake(10)
    time.sleep(3)
    pmc.motor_reverse(300)
    time.sleep(3)

    pmc.terminate()


if __name__ == '__main__':
    test()
