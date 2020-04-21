#!/usr/bin/env python
import numpy as np
import random


class Model(object):
    DEFAULT_SPEED = 0.001  # dt multiplier

    def __init__(self, sea=0.0, temp=0.0, pop=0.0, tech=0.0, speed=1):
        self.sea = sea
        self.temp = temp
        self.pop = pop
        self.tech = tech
        self.speed = speed * self.DEFAULT_SPEED
        self.enlightened = False
        self.event_warnings = []  # A list of events that have yet to be acknowledged by the game engine

    def tick(self, dt):
        pass

    def start_event(self, name):
        '''Called by the model when we would like to trigger an event.'''
        print("Starting event", name)
        self.event_warnings.append(name)

    def execute_event(self, name):
        '''Called by the game engine some time after start_event, when it is time
         for the event to actually happen.'''
        pass


class SineModel(Model):
    SEA_SPEED = 0.1
    TEMP_SPEED = 0.1
    POP_SPEED = 0.01
    TECH_SPEED = 0.01

    # The range of temp and sea values required for pop growth
    GOOD_TEMP_ZONE = 0.3
    GOOD_SEA_ZONE = 0.3
    GOOD_POP_ZONE = 0.25  # width around 0.5 pop for tech growth

    EVENT_DELTA = {  # dsea,dtemp,pop factor,dtech
        'world_war': (0.0, 0.3, 0.5, 0.0),
        'war': (0.0, 0.2, 0.8, 0.0),
        'plauge': (0.0, 0.0, 0.4, 0.0),
        'monsoon': (0.3, -0.0, 0.90, 0.0),
        'sandstorm': (-0.3, 0.0 , 0.90 , 0.0),
        'blizzard'   : (0, 0.3 , 0.90 , 0.0),
        'wildfire'   : (0, -0.3 , 0.90 , 0.0),
    }
    EVENT_PERIOD = 4
    ENLIGHTENED_FIX_STRENGTH = 0.1
    def __init__(self):
        # Choose random starting values
        super().__init__(
            sea=np.random.uniform(-self.GOOD_SEA_ZONE, self.GOOD_SEA_ZONE),
            temp=np.random.uniform(-self.GOOD_TEMP_ZONE, self.GOOD_TEMP_ZONE),
            pop=0.1, tech=0.0
        )
        self.event_timer = 0

        self.probability_world_war = 0
        self.probability_war = 0
        self.probability_plague = 0
        self.probability_monsoon = 0
        self.probability_sandstorm = 0
        self.probability_blizzard = 0
        self.probability_wildfire = 0
        self.status = ""
        self.status_timer = 0
    def create_event(self):
        # Probability of event happening (worldwar,war,plague,monsoon,sandstorm)
        event_prob = np.random.uniform(0, 1)
        self.event_timer += 1
        if 0.75 < self.pop < 0.9 and self.event_timer > 30:
            self.probability_war = 0.003
            if event_prob < self.probability_war :
                self.start_event("war")
                self.event_timer = 0 
                self.status = "War"
            if self.pop > 0.8 and self.event_timer > 30:
                self.probability_world_war = 0.001
                self.probability_plaque = 0.001
                event_prob2 = np.random.randint(0,2)
                if event_prob < self.probability_world_war and event_prob2 == 0:
                    self.start_event("world_war")
                    self.event_timer = 0
                    self.status = "World_War"
                if event_prob < self.probability_plague and event_prob2 == 1:
                    self.start_event("plauge")
                    self.event_timer = 0
                    self.status = "Plague"
            
        if self.sea > 0.5  and self.event_timer > 30:
            self.probability_monsoon = 0.003
            if event_prob < self.probability_monsoon :
                self.start_event("monsoon")
                self.event_timer = 0
                self.status = "Monsoon"
        if self.sea <  - 0.5  and self.event_timer > 30:
            self.probability_sandstorm = 0.003
            if event_prob < self.probability_sandstorm :
                self.start_event("sandstorm")
                self.event_timer = 0
                self.status = "Sandstorm"
        if self.temp > 0.5  and self.event_timer > 30:
            self.probability_wildfire = 0.003
            if event_prob < self.probability_wildfire :
                self.start_event("wildfire")
                self.event_timer = 0
                self.status = "Wildfire"
        if self.temp < -0.5  and self.event_timer > 30:
            self.probability_blizzard = 0.003
            if event_prob < self.probability_blizzard :
                self.start_event("blizzard")
                self.event_timer = 0
                self.status = "Blizzard"
            
    def tick(self, dt):
        ds = self.speed * dt
        self.create_event()
        if self.status != "":
           self.status_timer += dt
        if self.status_timer >= 3000:
           self.status_timer = 0
           self.status = "Enlightened" if self.enlightened else ""
           
        if self.status == "" and self.enlightened :
           self.status = "Enlightened"
           
        # Maybe start an event
        # if self.event_timer > self.EVENT_PERIOD:
        #   self.event_timer = 0
        #   self.start_event(random.choice(list(self.EVENT_DELTA)))
        # self.event_timer += ds
        # Handle behavior
        if not self.enlightened:
            self.temp += -self.sea * ds * self.TEMP_SPEED
            self.sea += self.temp * ds * self.SEA_SPEED
            if -self.GOOD_TEMP_ZONE < self.temp < self.GOOD_TEMP_ZONE and \
                    -self.GOOD_SEA_ZONE < self.sea < self.GOOD_SEA_ZONE:
                self.pop += self.POP_SPEED * ds
            else:
                self.pop -= self.POP_SPEED * ds
            if 0.5 - self.GOOD_POP_ZONE < self.pop < 0.5 + self.GOOD_POP_ZONE:
                self.tech += (1 - 0.5 + self.pop) * ds * self.TECH_SPEED
            # Yeah this fixes a bug where there's only 1 guy and he keeps rebuilding society lol
            if self.pop <= 0.001:
                self.pop = 0
            if self.pop == 0:
                self.tech = 0
        if self.tech >= 1:
            self.enlightened = True
            self.sea -= self.sea*ds*self.ENLIGHTENED_FIX_STRENGTH
            self.temp -= self.temp*ds*self.ENLIGHTENED_FIX_STRENGTH
        self.pop = np.clip(self.pop, 0, 1)
        self.tech = np.clip(self.tech, 0, 1)

    def execute_event(self, name):
        dsea, dtemp, dpop, dtech = self.EVENT_DELTA[name]
        self.sea = self.sea + dsea
        self.temp = self.temp + dtemp
        self.pop = np.clip(self.pop * dpop, 0, 1)
        self.tech = np.clip(self.tech + dtech, 0, 1)
        self.status_timer = 0

class StochasticModel(Model):
    SPEED = 0.002  # average change to parameters each milisecond
    PULL_TO_CENTER = 0.0002

    def __init__(self):
        super().__init__(
            np.random.uniform(-1.0, 1.0),
            np.random.uniform(-1.0, 1.0),
            np.random.uniform(0.0, 1.0),
            np.random.uniform(0.0, 1.0)
        )

    def random_delta(self, dt, value, off_center):
        step = np.random.uniform(-1.0, 1.0) * self.SPEED * dt
        restoration = - self.PULL_TO_CENTER * off_center * dt
        return value + step + restoration

    def tick(self, dt):
        # Randomly increase or decrease parameters, but keep them bounded
        self.sea = np.clip(self.random_delta(dt, self.sea, self.sea), -1, 1)
        self.temp = np.clip(self.random_delta(dt, self.temp, self.temp), -1, 1)
        self.pop = np.clip(self.random_delta(dt, self.pop, self.pop - 0.5), 0, 1)
        self.tech = np.clip(self.random_delta(dt, self.tech, self.tech - 0.5), 0, 1)


PlanetModel = SineModel  # Select the sine model
