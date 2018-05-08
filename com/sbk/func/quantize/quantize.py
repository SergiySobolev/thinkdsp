from com.sbk.func.normalize.normalize import normalize

import warnings

def quantize(ys, bound, dtype):
    """Maps the waveform to quanta.

    ys: wave array
    bound: maximum amplitude
    dtype: numpy data type of the result

    returns: quantized signal
    """
    if max(ys) > 1 or min(ys) < -1:
        warnings.warn('Warning: normalizing before quantizing.')
        ys = normalize(ys)

    zs = (ys * bound).astype(dtype)
    return zs