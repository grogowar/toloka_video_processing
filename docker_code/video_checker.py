import pyFSDK
from pyfsdk_bind import numpy_to_pyfsdk


class VideoChecker:

    def __init__(self):
        path_fsdk = "/home/researcher/SDK_data"
        profile = "toloka_processing_profile"
        device_idx = 0
        init = pyFSDK.configuration.init_fsdk()
        fsdk_profile = pyFSDK.configuration.FSDKProfile(path_fsdk, profile)
        self.face_tracker = pyFSDK.tracking.MultiTracker(fsdk_profile, device_idx=device_idx)

    def check(self, video):
        return video.read()[-20:]