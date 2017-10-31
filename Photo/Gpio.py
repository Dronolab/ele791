
import os

class Gpio():
    def __init__(self, pin, direction):
        # self.__path = os.path.normpath("/sys/class/gpio/")
        self.__pin = pin
        self.__direction = direction
        self.__exportPin(self.__pin)
        self.__setPinDirection(self.__pin, self.__direction)
        gpiopin = "gpio%s" % (str(self.__pin),)
        self.__valuefilename = "/sys/class/gpio/"+gpiopin+"/value"
        self.__exportPin()
        self.__setPinDirection()

    def __exportPin(self):
        try:
            f = open("/sys/class/gpio/export","w")
            f.write(str(self.__pin))
            f.close()
        except IOError:
            print( "GPIO %s already Exists, so skipping export gpio" % (str(self.__pin)))

    def getFileName(self):
        return self.__valuefilename

    def __setPinDirection(self):
        gpiopin = "gpio%s" % (str(self.__pin))
        pin = open("/sys/class/gpio/"+gpiopin+"/direction", "w")
        pin.write(self.__direction)
        pin.close()

    def writepin(self,pin_value):
        gpiopin = "gpio%s" % (str(self.__pin))
        pin = open("/sys/class/gpio/"+gpiopin+"/value", "w")
        if pin_value == 1:
          pin.write("1")
        else:
          pin.write("0")
        pin.close()

    def readpins(self):
        gpiopin = "gpio%s" % (str(self.__pin))
        pin = open("/sys/class/gpio/"+gpiopin+"/value", "r")
        value = pin.read()
        pin.close()
        return int(value)
    