# Pololu Protocol
# This protocol is compatible with the serial protocol used by our other serial motor and servo controllers. As such,
# you can daisy-chain a Simple Motor Controller on a single serial line along with our other serial controllers
# (including additional Simple Motor Controllers) and, using this protocol, send commands specifically to the desired
# controller without confusing the other devices on the line.
# To use the Pololu protocol, you must transmit 0xAA (170 in decimal) as the first (command) byte, followed by a Device
# Number data byte. The default Device Number for the Simple Motor Controller is 0x0D (13 in decimal), but this is a
# configuration parameter you can change. Any controller on the line whose device number matches the specified device
# number accepts the command that follows; all other Pololu devices ignore the command. The remaining bytes in the
# command packet are the same as the compact protocol command packet you would send, with one key difference: the
# compact protocol command byte is now a data byte for the command 0xAA and hence must have its most significant bit
# cleared.

# https://www.pololu.com/docs/0J44/6.2
