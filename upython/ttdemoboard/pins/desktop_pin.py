'''
Created on Jan 22, 2024

@author: Pat Deegan
@copyright: Copyright (C) 2024 Pat Deegan, https://psychogenic.com
'''

import ttboard.logging as logging 
log = logging.getLogger(__name__)

class Pin:
    '''
        Stub class for desktop testing,
        i.e. where machine module DNE
    '''
    OUT = 1
    IN = 2
    IRQ_FALLING = 3
    IRQ_RISING = 4
    PULL_DOWN = 5
    PULL_UP = 6
    OPEN_DRAIN = 7
    def __init__(self, gpio:int, direction:int=0, mode:int=0, pull:int=0):
        self.gpio = gpio
        self.dir = direction
        self.val = 0 
        
    def value(self, setTo:int = None):
        if setTo is not None:
            log.debug(f'Setting GPIO {self.gpio} to {setTo}')
            self.val = setTo 
        return self.val
        
    def init(self, direction:int):
        log.debug(f'Setting GPIO {self.gpio} to direction {direction}')
        self.dir = direction

