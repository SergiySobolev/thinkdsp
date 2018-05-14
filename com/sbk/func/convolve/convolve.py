import numpy as np


def convolve(signal, impulse_response):
    signal_length = len(signal)
    impulse_response_length = len(impulse_response)
    result_length = signal_length + impulse_response_length + 1
    result = np.zeros(result_length)
    return result
