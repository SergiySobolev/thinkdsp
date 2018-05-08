import subprocess


def play_wave(filename='sound.wav', player='aplay'):
    """Plays a wave file.

    filename: string
    player: string name of executable that plays wav files
    """
    cmd = '%s %s' % (player, filename)
    popen = subprocess.Popen(cmd, shell=True)
    popen.communicate()