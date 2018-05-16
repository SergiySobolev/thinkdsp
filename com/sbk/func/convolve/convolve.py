import numpy as np


def convolve(signal, impulse_response):
    signal_length = len(signal)
    impulse_response_length = len(impulse_response)
    result_length = signal_length + impulse_response_length - 1
    result = np.zeros(result_length)
    for i in range(0, signal_length):
        for j in range(0, impulse_response_length):
            result[i + j] += signal[i] * impulse_response[j]
    return result


def convolve_machine(signal, impulse_response):
    signal_length = len(signal)
    impulse_response_length = len(impulse_response)
    result_length = signal_length + impulse_response_length - 1
    result = np.zeros(result_length)
    for i in range(0, result_length):
        for j in range(0, impulse_response_length):
            cur_signal_index = i - j
            if cur_signal_index < 0 or cur_signal_index >= signal_length:
                continue
            result[i] += signal[i-j] * impulse_response[j]
    return result

