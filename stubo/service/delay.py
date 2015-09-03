"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import random


class Delay(object):
    @staticmethod
    def parse_args(policy):
        delay = None
        delay_type = policy.get('delay_type')
        if delay_type == 'fixed':
            delay = FixedDelay(int(policy['milliseconds']))
        elif delay_type == 'normalvariate':
            delay = NormalVariateDelay(int(policy['mean']),
                                       int(policy['stddev']))

        elif delay_type == 'weighted':
            delays = []
            for delay in policy['delays'].split(':'):
                delay_values = delay.split(',')
                delay_type = delay_values[0]
                delay_args = delay_values[1:-1]
                weight = int(delay_values[-1])
                if delay_type == 'fixed':
                    delays.append((FixedDelay(int(delay_args[0])), weight))
                elif delay_type == 'normalvariate':
                    delays.append((NormalVariateDelay(int(delay_args[0]),
                                                      int(delay_args[1])),
                                   weight))
            delay = WeightedDelay(delays)
        return delay

    def calculate(self):
        pass


class FixedDelay(Delay):
    def __init__(self, millisecs):
        self.millisecs = millisecs

    def calculate(self):
        return float(self.millisecs)


class NormalVariateDelay(Delay):
    def __init__(self, mean, stddev):
        self.mean = mean
        self.stddev = stddev

    def calculate(self):
        # normal distribution, but set minimum at zero
        return max(0.0, random.normalvariate(self.mean, self.stddev))


class WeightedDelay(Delay):
    def __init__(self, delays):
        self.delays = []
        for delay, pcent in delays:
            self.delays.extend([delay] * pcent)

    def calculate(self):
        delay = random.choice(self.delays)
        return delay.calculate()
