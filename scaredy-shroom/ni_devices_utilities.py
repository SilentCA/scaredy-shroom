# -*- coding: utf-8 -*-
"""Control NI analog input DAQ device and digital input/output device.

@author: SilentCA
@email: 2291948161@qq.com
"""

import nidaqmx
import nidaqmx.stream_readers
import nidaqmx.stream_writers
import nidaqmx.constants

import numpy as np
import matplotlib.pyplot as plt


def cfg_AI_task(samp_time, channel='cDAQ1AIM/ai0', rate=2.5e4, trigger='/cDAQ1/PFI0'):
    """Create a NI analog input task.

    Parameters
    ----------
    samp_time : float
        Sample time.
    channel : str, list
        Analog input channel name.
    rate : float
        Sample rate.
    trigger : str
        Start trigger name.

    Returns
    -------
    task : nidaqmx.task.Task
        NI-DAQmx analog input task.
    data : numpy.ndarray
        1D NumPy array to hold samples.
    """
    # Create and configure task
    multiple_channel = False
    task = nidaqmx.Task()
    if isinstance(channel, list):
        if len(channel) > 1:
            multiple_channel = True
        for chan in channel:
            task.ai_channels.add_ai_voltage_chan(chan)
    else:
        task.ai_channels.add_ai_voltage_chan(channel)
    task.timing.samp_clk_rate = rate
    num_samples = int(samp_time * rate)
    task.timing.samp_quant_samp_per_chan = num_samples
    task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger,
                                                        trigger_edge=nidaqmx.constants.Edge.RISING)

    if multiple_channel:
        data = np.empty((len(channel), num_samples), dtype=np.float64)
    else:
        data = np.empty(num_samples, dtype=np.float64)

    return task, data


def read_data(task, data, timeout=nidaqmx.constants.WAIT_INFINITELY):
    """Read samples from task.

    Parameters
    ----------
    task : nidaqmx.task.Task
        A NI-DAQmx analog input task.
    data : numpy.ndarray
        1D NumPy array to hold the requested samples.
    timeout : float
        The amount of time in seconds to wait for samples to become available.

    Notes
    -----
    Using DAQmx Read method multiple times, such as in a loop,
    the task starts and stops repeatedly, which reduces the
    performance of the application.

    Returns
    -------
    data : numpy.ndarray
        1D NumPy array holding the samples requested.
    """
    if task.number_of_channels == 1:
        reader = nidaqmx.stream_readers.AnalogSingleChannelReader(task.in_stream)
    else:
        reader = nidaqmx.stream_readers.AnalogMultiChannelReader(task.in_stream)
    # If set `timeout` to `nidaqmx.constants.WAIT_INFINITELY`, it will wait infinitely. 
    reader.read_many_sample(data, int(data.size/task.number_of_channels), timeout=timeout)
    return data


def cfg_DO_task(channel='/cDAQ1DIOM/port0', rate=1e4):
    """Create a NI digital output task.

    Parameters
    ----------
    channel : str, list
        Digital output channel name.
    rate : float
        Sample rate.

    Returns
    -------
    task : nidaqmx.task.Task
        A NI-DAQmx digital output task.
    """
    task = nidaqmx.Task()
    if isinstance(channel, list):
        for chan in channel:
            task.do_channels.add_do_chan(chan)
    else:
        task.do_channels.add_do_chan(channel)
    task.timing.samp_clk_rate = rate
    task.timing.samp_timing_type = nidaqmx.constants.SampleTimingType.SAMPLE_CLOCK
    task.timing.samp_quant_samp_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS
    # FINITE mode may be ok
    # task.timing.samp_quant_samp_mode = nidaqmx.constants.AcquisitionType.FINITE
    # may not need
    # task.timing.samp_quant_samp_per_chan = buffer_length
    # task.out_stream.regen_mode = nidaqmx.constants.RegenerationMode.ALLOW_REGENERATION
    return task


def write_digital_data(task, data):
    """Write digital data to task.

    Parameters
    ----------
    task : nidaqmx.task.Task
        A NI-DAQmx digital output task.
    data : numpy.ndarray
        1D NumPy array containing digital wave.
    """
    if task.number_of_channels > 1:
        writer = nidaqmx.stream_writers.DigitalMultiChannelWriter(task.out_stream)
    else:
        writer = nidaqmx.stream_writers.DigitalSingleChannelWriter(task.out_stream)
    writer.write_many_sample_port_byte(data)


def cfg_task(task, rate=None):
    """Configure task.

    Parameters
    ----------
    task : nidaqmx.task.Task
        A NI-DAQmx task.
    rate : float
        Sample rate.
    """
    # Transition task to Verified state.
    task.control(nidaqmx.constants.TaskMode.TASK_ABORT)
    # Set parameters
    if rate is not None:
        task.timing.samp_clk_rate = rate


def abort_task(task):
    """Abort task, transitioning task to VERIFIED state."""
    task.control(nidaqmx.constants.TaskMode.TASK_ABORT)


def main():
    samp_time = 5
    task, data = cfg_AI_task(samp_time=samp_time, channel='cDAQ1AIM/ai0', rate=2.5e4)
    y = read_data(task, data)
    task.stop()
    task.close()
    x = np.linspace(0, samp_time, len(y))
    fig, ax = plt.subplots()
    ax.plot(x, y)
    plt.show()


if __name__ == '__main__':
    main()
