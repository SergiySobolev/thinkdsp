from com.sbk.wave.amplify.audiofile import AudioFile


def transform(data, scale_factor):
    sample = int(data * scale_factor)
    return sample


def do_amplification(in_file, out_file, amplification_factor):
    fin = AudioFile(in_file, 'r')
    fout = AudioFile(out_file, 'w')
    fout.setparams(fin.getnchannels(),
                   fin.getsampwidth(),
                   fin.getframerate(),
                   0,
                   'NONE',
                   'not compressed')

    num_frames = fin.getnframes()
    while fin.tell() < num_frames:
        frame_data = fin.read(1)
        for data in frame_data:
            out_frame = transform(int(data * amplification_factor))
            fout.write(out_frame)

    fout.close()
    fin.close()
