"""
Simple CUDA profiler for pytorch, as an alternative to autograd's
I made this for three reasons:
 - I actually know what this does
 - Everyone on the top duck results says to do this and barely mention the autograd profiler
 - I could not find a clear analysis in autograd's favor.

https://discuss.pytorch.org/t/training-gets-slow-down-by-each-batch-slowly/4460
https://discuss.pytorch.org/t/how-to-measure-time-in-pytorch/26964
https://github.com/Paxoo/PyTorch-Best_Practices/wiki/Correct-Way-To-Measure-Time
https://pytorch.org/docs/stable/autograd.html#torch.autograd.profiler.profile

There are two ways to use this:
use the SimpleCudaProfiler context directly (i.e. use the with statement),
or make one SimpleCudaProfilerFactory object and produce contexts with its .profile method.

The second way is a little more cumbersome, but it allows for easily putting it to sleep
and disabling all profiling simply by passing True or False upon factory initialization.
(Note: enabling/disabling the factory only affects whether the new profilers it produces
 from then on will be functioning or null. It has no effects on already produced profilers.
 The intended use case is to have a cli option or a config file decide whether the factory
 will be initialized as enabled or disabled, and have it stay that way for the whole run.)

(Note: the SimpleCudaProfiler automatically uses Python's default logging to store the results.
 You may want to customize this part based on your needs.)
"""

import torch
import contextlib
import logging

# the only reason why there is this extra class is to make it possible to enable/disable by modifying one line in the source code
class SimpleCudaProfilerFactory:
    def __init__(self, enabled):
        self.enabled = enabled
    
    def profiler(self, log_header=""):
        if self.enabled:
            return SimpleCudaProfiler(log_header=log_header)
        else:
            return contextlib.nullcontext()



# you may use this directly, but the factory is much easier to disable altogether
class SimpleCudaProfiler:
    def __init__(self, log_header=""):
        self.log_header = log_header
        self.start_event = torch.cuda.Event(enable_timing=True)
        self.end_event = torch.cuda.Event(enable_timing=True)
        self.elapsed = None

    def __enter__(self):
        # fire start cuda event
        self.start_event.record()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # fire end cuda event
        self.end_event.record()
        # wait for everything to finish running (since cuda is asynchronous)
        torch.cuda.synchronize()
        # save elapsed time b/w events
        self.elapsed = self.start_event.elapsed_time(self.end_event)
        # autolog for my personal ease of use
        # (profiler instances were not intended to be saved and referenced when I first wrote them)
        # (if you have different needs, customize this part!)
        logger = logging.getLogger(__name__)
        logger.info(self.log_header + "  CUDA time: " + str(self.elapsed))
        return False
