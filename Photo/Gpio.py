
import os

class Gpio():
    def __init__(self, pin, direction):
        # self.__path = os.path.normpath("/sys/class/gpio/")
        self.__pin = pin
        self.__direction = direction
        self.__exportPin(self.__pin)
        self.__setPinDirection(self.__pin, self.__direction)

    def __exportPin(self, pin):
        try:
            f = open("/sys/class/gpio/export","w")
            f.write(str(pin))
            f.close()
        except IOError:
            print( "GPIO %s already Exists, so skipping export gpio" % (str(pin), ))

    def __setPinDirection(self, pin, direction):
        gpiopin = "gpio%s" % (str(pin), )
        pin = open("/sys/class/gpio/"+gpiopin+"/direction", "w")
        pin.write(direction)
        pin.close()

    def writepin(self, pin, pin_value):
        gpiopin = "gpio%s" % (str(pin), )
        pin = open("/sys/class/gpio/"+gpiopin+"/value", "w")
        if pin_value == 1:
          pin.write("1")
        else:
          pin.write("0")
        pin.close()

    def readpins(self,pin):
        gpiopin = "gpio%s" % (str(pin), )
        pin = open("/sys/class/gpio/"+gpiopin+"/value", "r")
        value = pin.read()
        pin.close()
        return int(value)
    