
import os
import GeneralSettings

class Gpio():
    def __init__(self, pin, direction):
        # self.__path = os.path.normpath("/sys/class/gpio/")
        self.__pin = pin
        self.__direction = direction
        gpiopin = "gpio%s" % (str(self.__pin),)
        self.__valuefilename = "/sys/class/gpio/"+gpiopin+"/value"

        #initialise GPIO
        self.__exportPin()
        self.__setPinDirection()

    def __exportPin(self):
        try:
            f = open("/sys/class/gpio/export","w")
            f.write(str(self.__pin))
            f.close()
        except IOError:
            #print( "GPIO %s already Exists, so skipping export gpio" % (str(self.__pin)))
            pass

    def getFileName(self):
        print(self.__valuefilename)
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

class triggerGPIO(Gpio):
    ON_VALUE = 1
    OFF_VALUE = 0
    DIRECTION = "out"
    def __init__(self):
        super(triggerGPIO, self).__init__(GeneralSettings.TRIGGERGPIOPIN, self.DIRECTION)

    def activatePin(self):
        self.writepin(self.ON_VALUE)

    def unActivatePin(self):
        self.writepin(self.OFF_VALUE)

class flashGPIO(Gpio):
    ON_VALUE = 0
    OFF_VALUE = 1
    DIRECTION = "in"
    def __init__(self):
        super(flashGPIO, self).__init__(GeneralSettings.FLASHGPIOPIN, self.DIRECTION)


class cameraAlimGPIO(Gpio):
    ON_VALUE = 1
    OFF_VALUE = 0
    DIRECTION = "out"
    def __init__(self):
        super(cameraAlimGPIO, self).__init__(GeneralSettings.CAMALIMGPIO, self.DIRECTION)

    def unpower_camera(self):
        self.writepin(self.OFF_VALUE)

    def power_camera(self):
        self.writepin(self.ON_VALUE)