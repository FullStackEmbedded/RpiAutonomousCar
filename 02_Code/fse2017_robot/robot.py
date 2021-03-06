#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of FSE 2017.
#
# FSE 2017 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FSE 2017 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FSE 2017.  If not, see <http://www.gnu.org/licenses/>.

"""Robot interface combining ultrasonic, LED and motor drivers."""

import time

from drivers.infrared import InfraredSensor
from drivers.led import LED
from drivers.motor_driver import MotorDriver
from drivers.ultrasonic_ranger import UltrasonicRanger, UltrasonicTimeoutError


class Robot(object):

    """The robot used for FSE 2017."""

    _time_for_circle_turn = 3

    def __init__(self, duty_cycle=20):
        """duty_cycle is percent of maximum speed."""
        self.ultrasonic = UltrasonicRanger()
        self.led = LED()
        self.infrared = InfraredSensor()
        self.motor = MotorDriver()
        self.duty_cycle = duty_cycle

    def set_drive_mode(self, direction):
        """Drive forwards if direction > 0, otherwise backwards."""
        if direction > 0:
            self.motor.forward(self.duty_cycle)
        elif direction < 0:
            self.motor.reverse(self.duty_cycle)

    def drive(self, seconds):
        """
        Drive for a given duration.

        seconds is signed - positive for driving forwards, negative for
        backwards.
        """
        if seconds > 0:
            self.set_drive_mode(1)
        elif seconds < 0:
            self.set_drive_mode(-1)
        time.sleep(abs(seconds))
        self.motor.stop()

    def turn(self, degrees):
        """
        Turn a number of degrees.

        Positive is clockwise, negative is counterclockwise.
        """
        turn_time = self._time_for_circle_turn * (degrees / 360.0)
        if degrees > 0:
            self.motor.right(self.duty_cycle)
        elif degrees < 0:
            self.motor.left(self.duty_cycle)
        time.sleep(abs(turn_time))
        self.motor.stop()

    def drive_curve(self, seconds, angle):
        """Drive for a time while turning."""
        increment = 1
        if angle < 0:
            increment = -1
        for degree in range(0, int(round(angle)), increment):
            self.drive(float(seconds) / abs(angle))
            self.turn(increment)

    @property
    def obstacle(self):
        """Return distance to nearest obstacle in cm or None."""
        try:
            distance = self.ultrasonic.average_distance
        except UltrasonicTimeoutError:
            distance = None
        return distance

    def __enter__(self):
        return self

    def __exit__(self, *args):
        """Release internally used resources."""
        self.ultrasonic.__exit__()
        self.led.__exit__()
        self.infrared.__exit__()
        self.motor.__exit__()

