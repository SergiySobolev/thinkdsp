import wave
import struct


class AudioFile:
    """
    Container class for an audio file.  This class allows
    for reading and writing wave files with translation of
    packed data into unpacked data for manipulation by other
    programs.
    Mostly this acts as a proxy for the wave module.  But this
    class also abstracts packing/unpacking data away from clients.
    """

    def __init__(self, filename, mode):
        """Creates a new AudioFile instance with the given filename.
           Mode should be one of 'r' (read) or 'w' (write)."""
        self.file_handle = wave.open(filename, mode)
        if mode == 'w':
            channels = 1
            sample_width = 2
            frame_rate = 44100
            self.setparams(channels,
                           sample_width,
                           frame_rate,
                           0,
                           'NONE',
                           'not compressed')

    def close(self):
        """Close the underlying file represented by this instance."""
        self.file_handle.close()

    def write(self, sample):
        """Write a sample to the underlying file.
           The sample is checked to ensure it fits in the
           size of the word the file expects."""
        sample = self.check_clip(sample)
        packed_out_data = struct.pack('h', sample)
        self.file_handle.writeframes(packed_out_data)

    def check_clip(self, sample):
        """Clip samples that are larger than the word size
           the underlying file supports.  Right now this is
           hardcoded to 16 bit signed word size."""
        if sample > 32767:
            sample = 32767
        if sample < -32768:
            sample = -32768
        return sample

    def getnframes(self):
        """Return the number of frames in the underlying file."""
        return self.file_handle.getnframes()

    def getnchannels(self):
        """Return the number of channels in the underlying file."""
        return self.file_handle.getnchannels()

    def getframerate(self):
        """Return the framerate of the udnerlying file."""
        return self.file_handle.getframerate()

    def getsampwidth(self):
        """Return the sample width of the udnerlying file."""
        return self.file_handle.getsampwidth()

    def setparams(self, nchannels, sampwidth, framerate, nframes, comptype, compname):
        """Sets parameters in the wave file header."""
        self.file_handle.setparams((nchannels,
                                    sampwidth,
                                    framerate,
                                    nframes,
                                    comptype,
                                    compname))

    def tell(self):
        """Return the current read position in the underlying file."""
        return self.file_handle.tell()

    def read(self, num_samples):
        """Read a number of samples from the underlying file.
           This returns a tuple containing the requested number of
           samples.  For multichannel files the tuple will alternate
           between each channel."""
        frame = self.file_handle.readframes(num_samples)
        frame_data = struct.unpack('%dh' % (self.getnchannels()), frame)
        return frame_data

    @staticmethod
    def write_wave_to_out_file(w, fout_name="out.wav"):
        fout = AudioFile(fout_name, 'w')
        fout.setparams(1,
                       2,
                       w.frame_rate,
                       0,
                       'NONE',
                       'not compressed')

        num_frames = len(w)
        i = 0
        while i < num_frames:
            frame_data = int(w.ys[i])
            fout.write(frame_data)
            i+=1

        fout.close()

