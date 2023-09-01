"""Control all the devices to do experiment.

@author: SilentCA
@email: 2291948161@qq.com
"""


import timing_utility
import ni_devices_utilities
import numpy as np
import os
import datetime


def datetime_str():
    """Return datetime string.
    """
    return str(datetime.datetime.now())[2:-7].replace(':', '.')


# ------------- Configure experiment ---------------
repeat_time = 2        # repeat experiment for given time
timing_sequence_list = [
    (0xFF00, 1),
    (0x00FF, 1),
    (0xFF00, 1)
]
timing_rate = 5e6      # Uint: Hz
sample_time = 1        # Unit: second
sample_rate = 50e3     # Unit: Hz
# Experimental data save path
data_file_path = r'C:\Data'

timing_channel = ['/cDAQ9189-1EFE359Mod3/port0', '/cDAQ9189-1EFE359Mod4/port0']
sample_channel = ['cDAQ9189-1EFE359Mod1/ai0', 'cDAQ9189-1EFE359Mod1/ai1']
# Start trigger
sample_trigger = '/cDAQ9189-1EFE359/PFI0'

data_file_header = 'times;ai0;ai1'


# ------------- Configure devices ------------------
# configure timing
print("Configure timing device.")
timing_wave = timing_utility.generate_timing_wave(
        timing_sequence_list,
        timing_rate, n_channel=2)
timing_task = ni_devices_utilities.cfg_DO_task(
        channel=timing_channel,
        rate=timing_rate)
print("Write timing data to device.")
ni_devices_utilities.write_digital_data(timing_task, timing_wave)

# configure sample
print("Configure sample device.")
sample_task, data_buffer = ni_devices_utilities.cfg_AI_task(
        sample_time, channel=sample_channel,
        rate=sample_rate, trigger=sample_trigger
)

# ------------- Start timing loop ------------------
print("Start timing loop")
timing_task.start()


# ------------- Sample data ------------------------
for idx in range(1, repeat_time+1):
    print(f"Sampling... Total: {repeat_time}, running: {idx}.")
    sample_task.start()
    print("----> Read sampling data.")
    data = ni_devices_utilities.read_data(sample_task, data_buffer)
    sample_task.stop()

    # ------------- Save data --------------------------
    save_path = os.path.join(data_file_path, datetime_str()+'.csv')
    # Generate timeline
    data_length = int(data.size/sample_task.number_of_channels)
    times = np.linspace(start=0, stop=data_length/sample_rate, num=data_length, endpoint=False)
    # TODO: may have a good method to save.
    print("----> Save data file.")
    np.savetxt(save_path, np.vstack((times, data)).T, delimiter=';', header=data_file_header)

# ------------- Release resources ------------------
print("All work done. Good luck.")
sample_task.close()
# set final output state to low level
number_of_channels = len(timing_channel) if isinstance(timing_channel, list) else 1
timing_task.write([0]*number_of_channels, auto_start=True)
timing_task.stop()
timing_task.close()
