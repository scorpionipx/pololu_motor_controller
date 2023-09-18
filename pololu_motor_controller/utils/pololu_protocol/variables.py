import enum


class Variables(enum.Enum):
    """

    """
    # Status Flag Registers
    # ==================================================================================================================
    ERROR_STATUS = 0
    ERRORS_OCCURRED = 1
    SERIAL_ERRORS_OCCURRED = 2
    LIMIT_STATUS = 3
    RESET_FLAGS = 127
    # ==================================================================================================================

    # RC Channel Inputs
    # ==================================================================================================================
    RC1_UNLIMITED_RAW_VALUE = 4
    RC1_RAW_VALUE = 5
    RC1_SCALED_VALUE = 6
    RC2_UNLIMITED_RAW_VALUE = 8
    RC2_RAW_VALUE = 9
    RC2_SCALED_VALUE = 10
    # ==================================================================================================================

    # Analog Channel Inputs
    # ==================================================================================================================
    AN1_UNLIMITED_RAW_VALUE = 12
    AN1_RAW_VALUE = 13
    AN1_SCALED_VALUE = 14
    AN2_UNLIMITED_RAW_VALUE = 16
    AN2_RAW_VALUE = 17
    AN2_SCALED_VALUE = 18
    # ==================================================================================================================

    # Diagnostic Variables
    # ==================================================================================================================
    TARGET_SPEED = 20
    SPEED = 21
    BRAKE_AMOUNT = 22
    INPUT_VOLTAGE = 23
    TEMPERATURE = 24
    RC_PERIOD = 26
    BAUD_RATE_REGISTER = 27
    SYSTEM_TIME_LOW = 28
    SYSTEM_TIME_HIGH = 29
    # ==================================================================================================================

    # Temporary Motor Limits
    # ==================================================================================================================
    MAX_SPEED_FORWARD = 30
    MAX_ACCELERATION_FORWARD = 31
    MAX_DECELERATION_FORWARD = 32
    BRAKE_DURATION_FORWARD = 33
    MAX_SPEED_REVERSE = 36
    MAX_ACCELERATION_REVERSE = 37
    MAX_DECELERATION_REVERSE = 38
    BRAKE_DURATION_REVERSE = 39
    # ==================================================================================================================
