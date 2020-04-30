import pyFSDK
from pyfsdk_bind import numpy_to_pyfsdk
import cv2
import os
import shutil
from statistics import mean


class MyError(Exception):
    def __init__(self, message):
        self.message = message


class VideoChecker:
    tmp_dir = '/dev/shm'

    def __init__(self):
        path_fsdk = "/home/researcher/SDK_data"
        profile = "toloka_processing_profile"
        device_idx = 0
        init = pyFSDK.configuration.init_fsdk()
        fsdk_profile = pyFSDK.configuration.FSDKProfile(path_fsdk, profile)
        self.face_tracker = pyFSDK.tracking.MultiTracker(fsdk_profile, device_idx=device_idx)

    def check(self, video):
        result = ''
        self.__create_tmp_file(video)
        try:
            self.__get_tracks_and_dimentions()
            self.__has_faces_check()
            self.__single_face_check()
            self.__big_face_check()
        except MyError as error:
            result = error.message
        finally:
            self.__delete_tmp_files()
        return result

    def __create_tmp_file(self, video):
        ext = self.__get_extension(video.filename)
        self.tmp_file_path = os.path.join(self.tmp_dir, '1%s' % ext)
        video.save(self.tmp_file_path)

    def __get_extension(self, file_name):
        return os.path.splitext(file_name)[1]

    def __get_tracks_and_dimentions(self):
        video_source = cv2.VideoCapture(self.tmp_file_path)
        if not video_source.isOpened():
            raise MyError("Не удалось открыть видео.")
        self.video_width = video_source.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.video_height = video_source.get(cv2.CAP_PROP_FRAME_HEIGHT)
        prev_timestamp_ms = 0
        tracks_tmp = {}
        self.tracks = []
        while True:
            ret, frame = video_source.read()
            if not ret:
                break
            timestamp_ms = video_source.get(cv2.CAP_PROP_POS_MSEC)
            fsdk_image = numpy_to_pyfsdk(frame, pyFSDK.core_types.ColorType.BGR)
            fsdk_track = self.face_tracker.process_next_frame(fsdk_image, int(timestamp_ms - prev_timestamp_ms))
            prev_timestamp_ms = timestamp_ms
            for track_id, image_bbox, confidence in fsdk_track:
                w = image_bbox[2]
                h = image_bbox[3]
                if track_id in tracks_tmp:
                    tracks_tmp[track_id]['widths'].append(w)
                    tracks_tmp[track_id]['heights'].append(h)
                    tracks_tmp[track_id]['end'] = timestamp_ms / 1000
                else:
                    tracks_tmp[track_id] = {
                        'widths': [w],
                        'heights': [h],
                        'begin': timestamp_ms / 1000,
                        'end': timestamp_ms / 1000
                    }
        for track_id in tracks_tmp:
            self.tracks.append({
                'average_width': mean(tracks_tmp[track_id]['widths']),
                'average_height': mean(tracks_tmp[track_id]['heights']),
                'begin': tracks_tmp[track_id]['begin'],
                'end': tracks_tmp[track_id]['end']
            })

    def __has_faces_check(self):
        for track in self.tracks:
            if track['end'] - track['begin'] > 5:
                return
        raise MyError("На видео отсутствует лицо либо оно перекрыто/пропадает.")

    def __single_face_check(self):
        length = len(self.tracks)
        for i in range(length):
            track1 = self.tracks[i]
            for j in range(i+1, length):
                track2 = self.tracks[j]
                if min(track1['end'], track2['end']) - max(track1['begin'], track2['begin']) > 2:
                    raise MyError("На видео присутствует более одного лица.")

    def __big_face_check(self):
        longest_track = self.tracks[0]
        longest_track_length = longest_track['end'] - longest_track['begin']
        for i in range(1, len(self.tracks)):
            track = self.tracks[i]
            track_length = track['end'] - track['begin']
            if track_length > longest_track_length:
                longest_track = track
                longest_track_length = track_length
        video_area = self.video_width * self.video_height
        longest_track_area = longest_track['average_width']*longest_track['average_height']
        if longest_track_area/video_area < 0.15:
            raise MyError("Присутствующее в кадре лицо слишком маленькое.")

    def __delete_tmp_files(self):
        for dir_or_file in os.listdir(self.tmp_dir):
            path = os.path.join(self.tmp_dir, dir_or_file)
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
