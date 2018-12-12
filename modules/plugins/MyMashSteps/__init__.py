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
        self.actor_on(int(self.hlt))
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
        self.actor_off(int(self.hlt))
        self.stop_stopwatch()

    def execute(self):
        '''
        This method is execute in an interval
        :return: 
        '''
        # Check if Target Sparge Temp is reached
        if self.get_kettle_temp(self.hlt) >= float(self.spargetemp):
#            self.actor_off(int(self.hlt))
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
#            self.actor_on(int(self.hlt))

        # Check if Target Mash Temp is reached
        if self.get_kettle_temp(self.mashtun) >= int(self.mashtemp):
            # Check if Timer is Running
            if self.is_timer_finished() is None:
                self.start_timer(int(self.timer) * 60)

        # Check if timer finished and go to next step
        if self.is_timer_finished() == True:
            self.notify("%s Finished!" % self.name, "Starting the next step", timeout=None)
            self.next()


@cbpi.step
class HeatStep(StepBase):
    '''
    Just put the decorator @cbpi.step on top of a method. The class name must be unique in the system
    '''
    # Properties
    kettle = StepProperty.Kettle("Kettle", description="Kettle in which to heat")
    temp = Property.Number("Temperature", configurable=True, description="Target Temperature")
    s = False

    def init(self):
        '''
        Initialize Step. This method is called once at the beginning of the step
        :return:
        '''
        cbpi.app.logger.info('HeatStep: init')
        # set target step
        self.s = False
        self.set_target_temp(self.temp, int(self.kettle))
#        #Start heating the strike water
#        self.kettle_heater_on(int(self.kettle), 100)
        #Start stopwatch
        self.start_stopwatch()

    def reset(self):
        pass

    def finish(self):
        cbpi.app.logger.info('HeatStep: finish')
        self.set_target_temp(0, int(self.kettle))
#        self.kettle_heater_off(int(self.kettle))
        self.stop_stopwatch()

    def execute(self):
        '''
        This method is execute in an interval
        :return: 
        '''
        # Check if Target Temp is reached
        if self.get_kettle_temp(self.kettle) >= float(self.temp):
            #Send notification... ONCE 
            if self.s is False:
                cbpi.app.logger.info('HeatStep: Execute %s Temp Reached' % self.name)
                self.s = True
                # Check if Stopwatch is Running
                notifyHeader = "%s Temp Reached!" % self.name
                if self.is_stopwatch_running():
                    elapsedTime = time.strftime('%H:%M:%S', time.gmtime(float(self.stop_stopwatch())))
                    notifyHeader = "%s Temp Reached in %s seconds!" % (self.name, elapsedTime)
                self.notify(notifyHeader, "Maintaining temp; Please press the next button when ready to continue", timeout=None)


@cbpi.step
class NonBrewStep(StepBase):
    '''
    Just put the decorator @cbpi.step on top of a method. The class name must be unique in the system
    '''

    def init(self):
        '''
        Initialize Step. This method is called once at the beginning of the step
        :return:
        '''
        self.start_stopwatch()

    def reset(self):
        self.stop_stopwatch()

    def finish(self):
        step_text = "%s Finished" % (self.name)
        # Check if Stopwatch is Running
        if self.is_stopwatch_running():
            elapsedTime = time.strftime('%H:%M:%S', time.gmtime(float(self.stop_stopwatch())))
            step_text = "%s Finished in %s" % (self.name, elapsedTime)
        self.notify(step_text, "Please press the next button when ready to continue", timeout=None)

