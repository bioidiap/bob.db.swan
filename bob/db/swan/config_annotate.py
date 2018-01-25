from bob.bio.video.annotator import Wrapper
from bob.bio.face.annotator import FailSafe
from bob.bio.face.annotator.bobipfacedetect import BobIpFacedetect
from bob.bio.face.annotator.bobipflandmark import BobIpFlandmark
from bob.bio.face.annotator.bobipmtcnn import BobIpMTCNN
from .query_bio import load_frames

annotator = Wrapper(
    FailSafe([BobIpMTCNN(), BobIpFacedetect(), BobIpFlandmark()],
             ['leye', 'reye']),
    read_original_data=load_frames)
