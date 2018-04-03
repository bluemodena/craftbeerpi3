# -*- coding: utf-8 -*-
import time

from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
from modules import cbpi

@cbpi.step
class MyMashStep(StepBase):
    '''
    Just put the decorator @cbpi.step on top of a method. The class name must be unique in the system
    '''
    # Properties
    mashtun = StepProperty.Kettle("Mash Kettle", description="Kettle in which the mashing takes place")
    mashtemp = Property.Number("Mash Temperature", configurable=True, description="Target Temperature of Mash Step")
    hlt = StepProperty.Kettle("Sparge Kettle", description="Kettle in which the sparge water is being heated")
    spargetemp = Property.Number("Sparge Temperature", configurable=True, description="Target Temperature of Sparge Step")
    timer = Property.Number("Timer in Minutes", configurable=True, description="Timer is started when the target mash temperature is reached")
    s = False
 
    def init(self):
        '''
        Initialize Step. This method is called once at the beginning of the step
        :return: 
        '''
        # set mash target step
        self.set_target_temp(self.mashtemp, self.mashtun)

        #Start heating the sparge water
        self.set_target_temp(self.spargetemp, self.hlt)
        self.actor_on(1)
        self.start_stopwatch()
        self.s = False

    @cbpi.action("Start Timer Now")
    def start(self):
        '''
        Custom Action which can be execute form the brewing dashboard.
        All method with decorator @cbpi.action("YOUR CUSTOM NAME") will be available in the user interface
        :return: 
        '''
        if self.is_timer_finished() is None:
            self.start_timer(int(self.timer) * 60)

    def reset(self):
        self.stop_timer()
        self.set_target_temp(self.mashtemp, self.mashtun)
        self.stop_stopwatch()

    def finish(self):
        self.stop_timer()
        self.set_target_temp(self.spargetemp, self.hlt)
        self.actor_off(1)
        self.stop_stopwatch()

    def execute(self):
        '''
        This method is execute in an interval
        :return: 
        '''
        # Check if Target Sparge Temp is reached
        if self.get_kettle_temp(self.hlt) >= float(self.spargetemp):
#            self.actor_off(1)
            #Send notification... ONCE
            if self.s is False:
                cbpi.app.logger.info('MyMashStep: sparge temp reached')
                self.s = True
                # Check if Stopwatch is Running
                notifyHeader = "Sparge Water Temp Reached!"
                if self.is_stopwatch_running():
                    elapsedTime = time.strftime('%H:%M:%S', time.gmtime(float(self.stop_stopwatch())))
                    notifyHeader = "Sparge Water Temp Reached in %s!" % (elapsedTime)
                self.notify(notifyHeader, "Maintaining temp", timeout=None)
#        else:
#            self.actor_on(1)

        # Check if Target Mash Temp is reached
        if self.get_kettle_temp(self.mashtun) >= int(self.mashtemp):
            # Check if Timer is Running
            if self.is_timer_finished() is None:
                self.start_timer(int(self.timer) * 60)

        # Check if timer finished and go to next step
        if self.is_timer_finished() == True:
            self.notify("Mash Step Completed!", "Starting the next step", timeout=None)
            self.next()

@cbpi.step
class StrikeWater(StepBase):
    '''
    Just put the decorator @cbpi.step on top of a method. The class name must be unique in the system
    '''
    # Properties
    temp = Property.Number("Temperature", configurable=True,  description="Target Temperature of Strike Water")
    kettle = StepProperty.Kettle("Kettle", description="Kettle in which the the strike water is heated")
    s = False

    def init(self):
        '''
        Initialize Step. This method is called once at the beginning of the step
        :return:
        '''
        cbpi.app.logger.info('StrikeWater: init')

        # set target step
        self.s = False
        self.set_target_temp(self.temp, self.kettle)

        #Start heating the strike water
        self.actor_on(1)

        self.start_stopwatch()

    @cbpi.action("Change Power")
    def change_power(self):
        self.actor_power(1, 100)
    
    def reset(self):
        cbpi.app.logger.info('StrikeWater: reset')
        self.set_target_temp(self.temp, self.kettle)
        self.stop_stopwatch()
        self.actor_off(1)

    def finish(self):
        cbpi.app.logger.info('StrikeWater: finish')
        self.set_target_temp(0, self.kettle)
        self.stop_stopwatch()
        self.actor_off(1)

    def execute(self):
        '''
        This method is execute in an interval
        :return: 
        '''
        # Check if Target Temp is reached
        if self.get_kettle_temp(self.kettle) >= float(self.temp):
#            self.actor_off(1)
            #Send notification... ONCE 
            if self.s is False:
                cbpi.app.logger.info('StrikeWater: Execute strike temp reached')
                self.s = True
                # Check if Stopwatch is Running
                notifyHeader = "Strike Water Temp Reached!"
                if self.is_stopwatch_running():
                    elapsedTime = time.strftime('%H:%M:%S', time.gmtime(float(self.stop_stopwatch())))
                    notifyHeader = "Strike Water Temp Reached in %s!" % (elapsedTime)
                self.notify(notifyHeader, "Maintaining temp; Please press the next button when ready to continue", timeout=None)
#        else:
#            self.actor_on(1)

@cbpi.step
class SpargeStep(StepBase):
    '''
    Just put the decorator @cbpi.step on top of a method. The class name must be unique in the system
    '''
    # Properties
    temp = Property.Number("Temperature", configurable=True,  description="Target Temperature of Sprage Water")
    kettle = StepProperty.Kettle("Kettle", description="Kettle in which the the sparge water is heated")
    s = False

    def init(self):
        '''
        Initialize Step. This method is called once at the beginning of the step
        :return:
        '''
        cbpi.app.logger.info('SpargeStep: init')

        # set target step
        self.s = False
        self.set_target_temp(self.temp, self.kettle)

        #Start heating the sparge water
        self.actor_on(1)

        self.start_stopwatch()

    @cbpi.action("Change Power")
    def change_power(self):
        self.actor_power(1, 100)
    
    def reset(self):
        cbpi.app.logger.info('SpargeStep: reset')
        self.set_target_temp(self.temp, self.kettle)
        self.stop_stopwatch()
        self.actor_off(1)

    def finish(self):
        cbpi.app.logger.info('SpargeStep: finish')
        self.set_target_temp(0, self.kettle)
        self.stop_stopwatch()
        self.actor_off(1)

    def execute(self):
        '''
        This method is execute in an interval
        :return: 
        '''
        # Check if Target Temp is reached
        if self.get_kettle_temp(self.kettle) >= float(self.temp):
            self.actor_off(1)
            #Send notification... ONCE 
            if self.s is False:
                cbpi.app.logger.info('SpargeStep: Execute sparge temp reached')
                self.s = True
                # Check if Stopwatch is Running
                notifyHeader = "Sparge Water Temp Reached!"
                if self.is_stopwatch_running():
                    elapsedTime = time.strftime('%H:%M:%S', time.gmtime(float(self.stop_stopwatch()))) 
                    notifyHeader = "Sprage Water Temp Reached in %s!" % (elapsedTime)
                self.notify(notifyHeader, "Maintaining temp; Please press the next button when ready to continue", timeout=None)
        else:
            self.actor_on(1)


