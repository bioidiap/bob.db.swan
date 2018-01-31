import scipy.io.wavfile
import subprocess
import tempfile
from os.path import split, splitext

SITE_MAPPING = {
    '1': 'NTNU',
    '2': 'UIO',
    '3': 'MPH-FRA',
    '4': 'IDIAP',
    '6': 'MPH-IND',
}

DEVICE_MAPPING = {
    'p': 'iPhone',
    't': 'iPad',
}

MODALITY_MAPPING = {
    '1': 'face',
    '2': 'voice',
    '3': 'eye',
    '4': 'finger',
}


def read_audio(video_path):
    with tempfile.NamedTemporaryFile(suffix='.wav') as f:
        cmd = ['ffmpeg', '-i', video_path, '-y', '-vn', f.name]
        subprocess.call(cmd)
        f.seek(0)
        rate, signal = scipy.io.wavfile.read(f.name)
    return rate, signal


class Client(object):
    """A base class for SWAN clients"""

    def __init__(self, site, id_in_site, gender, **kwargs):
        super(Client, self).__init__(**kwargs)
        self.institute = site
        self.id_in_site = id_in_site
        self.gender = gender

    @property
    def id(self):
        return '{}_{}'.format(self.institute, self.id_in_site)


def swan_bio_file_metadata(path):
    """Returns the metadata associated with a SWAN file recorded during the
    biometric recognition phase.

    Parameters
    ----------
    path : str
        The path of the SWAN file.

    Returns
    -------
    client : :any:`Client`
    session : str
    nrecording : str
    device : str
    modality : str
    """
    # For example:
    # path: IDIAP/session_01/iPad/00001/4_00001_m_01_01_t_2.mp4
    _, path = split(path)
    # path: 4_00001_m_01_01_t_2.mp4
    path, extension = splitext(path)
    # path: 4_00001_m_01_01_t_2
    site, identity, gender, session, nrecording, device, modality = \
        path.split('_')
    site = SITE_MAPPING[site]
    client = Client(site, identity, gender)
    device = DEVICE_MAPPING[device]
    modality = MODALITY_MAPPING[modality]
    session = int(session)
    return client, session, nrecording, device, modality
