#!/usr/bin/env python

from bob.bio.spear.database import AudioBioFile
from bob.bio.video.database import VideoBioFile
from bob.bio.video.utils import FrameSelector
import bob.bio.base
import numpy
import scipy.io.wavfile
import subprocess
import tempfile
import bob.io.base
import bob.io.video
import numpy as np


def read_audio(video_path):
    with tempfile.NamedTemporaryFile(suffix='.wav') as f:
        cmd = ['ffmpeg', '-i', video_path, '-y', '-vn', f.name]
        subprocess.call(cmd)
        f.seek(0)
        rate, signal = scipy.io.wavfile.read(f.name)
    return rate, signal


class SwanAudioBioFile(AudioBioFile):
    """SwanAudioBioFile are video files actually"""

    def load(self, directory=None, extension='.mp4'):
        extension = extension or '.mp4'
        if extension == '.mp4':
            video_path = self.make_path(directory, extension)
            rate, audio = read_audio(video_path)
            return rate, numpy.cast['float'](audio)
        else:
            return super(SwanAudioBioFile, self).load(directory, extension)


class SwanVideoBioFile(VideoBioFile):
    """SwanVideoBioFile are video files actually"""

    def load(self, directory=None, extension='.mp4', frame_selector=FrameSelector()):
        extension = extension or '.mp4'
        if extension == '.mp4':
            video_path = self.make_path(directory, extension)
            video = bob.io.base.load(video_path)
            # rotate the video since SWAN videos are not upright!
            video = np.swapaxes(video, -2, -1)
            return frame_selector(video)
        else:
            return super(SwanVideoBioFile, self).load(
                directory, extension, frame_selector)


class Database(bob.bio.base.database.FileListBioDatabase):
    """Wrapper class for the SWAN database for speaker recognition
    (http://www.idiap.ch/dataset/swan). This class defines a simple protocol
    for training, dev and and by splitting the audio files of the database in
    three main parts.
    """

    def __init__(self, original_directory=None, original_extension=None,
                 bio_file_class=SwanAudioBioFile):
        # call base class constructor
        from pkg_resources import resource_filename
        folder = resource_filename(__name__, 'lists')
        super(Database, self).__init__(
            folder, 'swan', bio_file_class=bio_file_class,
            original_directory=original_directory,
            original_extension=original_extension)
