"""Utilities used to generate timing sequence.

@author: SilentCA
@email: 2291948161@qq.com

Examples:
    timing sequence:
        bit1 bit2 duration
        1    0    3s
        0    1    2s
        1    0    4s

    will generate the following digital wave
    bit1: ‾‾‾__‾‾‾‾
    bit2: ___‾‾____
         0  3 5   9  uint: s
       --------- time increase ------------------->
         _: low level
         ‾: high level

    Data model example:
    timing_sequence_list_example = [
            (0b10, 3),
            (0b01, 2),
            (0b10, 4)
            ]
    with corresponding result
    timing_wave_example = [
            0b10,
            0b10,
            0b10,
            0b01,
            0b01,
            0b10,
            0b10,
            0b10,
            0b10
            ]
"""

import numpy as np
import matplotlib.pyplot as plt


def generate_timing_wave(timing_sequence_list, sample_rate, bit_num=8):
    """Generate digital wave according to timing sequence.

    Parameters
    ----------
        timing_sequence_list : list
        sample_rate : float
        bit_num : int

    Returns
    -------
        timing_wave : numpy.ndarray
            1D NumPy array containing digital wave.
    """
    dtype = np.uint8 if bit_num < 9 else np.uint16
    timing_wave = np.concatenate(
        [np.full(round(t[1] * sample_rate), t[0], dtype=dtype) for t in timing_sequence_list]
    )
    return timing_wave


def plot_timing_wave(timing_wave, sample_rate, bit_num=8):
    """Plot timing wave.

    Parameters
    ----------
        timing_wave : array
        sample_rate : float
        bit_num : int
    """
    t = np.linspace(0, len(timing_wave) / sample_rate, len(timing_wave))
    fig, axs = plt.subplots(bit_num)
    for idx, ax in enumerate(axs):
        # plot the least bit first
        ax.plot(t, np.bitwise_and(np.right_shift(timing_wave, idx), 1))
        ax.set_ylabel('Bit {}'.format(idx))
    plt.show()
