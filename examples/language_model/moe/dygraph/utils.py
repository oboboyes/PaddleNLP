# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import time

import paddle

_GLOBAL_TIMERS = None


def _ensure_var_is_not_initialized(var, name):
    """Make sure the input variable is not None."""
    assert var is None, '{} is not initialized.'.format(name)


def _ensure_var_is_initialized(var, name):
    """Make sure the input variable is not None."""
    assert var is not None, '{} is not initialized.'.format(name)


def get_timers():
    _ensure_var_is_initialized(_GLOBAL_TIMERS, 'timers')
    return _GLOBAL_TIMERS


def set_timers():
    """Initialize timers."""
    global _GLOBAL_TIMERS
    _ensure_var_is_not_initialized(_GLOBAL_TIMERS, 'timers')
    _GLOBAL_TIMERS = Timers()


class _Timer:
    """Timer."""

    def __init__(self, name):
        self.name = name
        self.elapsed_ = 0.0
        self.started_ = False
        self.start_time = time.time()

    def start(self):
        """Start the timer."""
        assert not self.started_, 'timer has already started'
        paddle.device.cuda.synchronize()
        self.start_time = time.time()
        self.started_ = True

    def stop(self):
        """Stop the timers."""
        assert self.started_, 'timer is not started.'
        paddle.device.cuda.synchronize()
        self.elapsed_ += time.time() - self.start_time
        self.started_ = False

    def reset(self):
        """Reset timer."""
        self.elapsed_ = 0.0
        self.started_ = False

    def elapsed(self, reset=True):
        """Calculate the elapsed time."""
        started_ = self.started_
        # If the timing in progress, end it first.
        if self.started_:
            self.stop()
        # Get the elapsed time.
        elapsed_ = self.elapsed_
        # Reset the elapsed time
        if reset:
            self.reset()
        # If timing was in progress, set it back.
        if started_:
            self.start()
        return elapsed_


class Timers:
    """Group of timers."""

    def __init__(self):
        self.timers = {}

    def __call__(self, name):
        if name not in self.timers:
            self.timers[name] = _Timer(name)
        return self.timers[name]

    def write(self, names, writer, iteration, normalizer=1.0, reset=False):
        """Write timers to a tensorboard writer"""
        assert normalizer > 0.0
        for name in names:
            value = self.timers[name].elapsed(reset=reset) / normalizer
            writer.add_scalar(name + '-time', value, iteration)

    def log(self, names, normalizer=1.0, reset=True):
        """Log a group of timers."""
        assert normalizer > 0.0
        string = 'time (ms)'
        for name in names:
            elapsed_time = self.timers[name].elapsed(
                reset=reset) * 1000.0 / normalizer
            string += ' | {}: {:.2f}'.format(name, elapsed_time)

        if paddle.distributed.get_rank() == (
                paddle.distributed.get_world_size() - 1):
            print(string, flush=True)
        else:
            print(string, flush=True)
