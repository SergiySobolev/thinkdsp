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
        a = flipped_sub_signal(signal, i, impulse_response_length)
        b = a * impulse_response
        result[i] = np.sum(b)
    return result

def flipped_sub_signal(signal, index, length):
    if index < length:
        r = signal[0:index+1]
        flipped_r = np.flip(r, axis=0)
        zeros_to_add = length - index - 1
        padded_r = np.pad(flipped_r, (0, zeros_to_add), 'constant')
        return padded_r
    elif index > len(signal) - 1:
        zeros_to_add = index - len(signal) + 1
        r = signal[index - length + 1:]
        padded_r = np.pad(r, (0, zeros_to_add), 'constant')
        flipped_r = np.flip(padded_r, axis=0)
        return flipped_r
    else:
        return np.flip(signal[index-length + 1:index+1], axis=0)
