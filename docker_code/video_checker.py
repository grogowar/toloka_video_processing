import cv2
import numpy as np
from s3fd_detector import S3FDDetector, Mode
import os
import shutil
import settings
import datetime


class MyError(Exception):
    def __init__(self, message):
        self.message = message


class VideoChecker:
    tmp_dir = '/dev/shm'
    frames_with_face_count = 0
    frames_without_face_count = 0
    log = ''

    def __init__(self):
        self.detector = S3FDDetector(model_path="s3fd_convert.pth", mode=Mode.GPU)
        self.face_probability = settings.face_probability_percentage / 100
        self.face_area_ratio = settings.face_area_percentage / 100
        self.frames_with_face_ratio = settings.frames_with_face_percentage / 100

    def check(self, video):
        result = ''
        self.frames_with_face_count = 0
        self.frames_without_face_count = 0
        self.__create_tmp_file(video)
        try:
            self.__get_video()
            self.__get_video_area()
            self.__get_fps()
            while True:
                if not self.__get_next_frame():
                    break
                self.__get_boxes()
                self.__filter_boxes()
                self.__single_face_check()
                self.__save_frame_info()
            self.__duration_check()
        except MyError as error:
            result = error.message
        finally:
            self.__delete_tmp_files()
        if settings.debug:
            return self.log + '\n' + result
        else:
            return result

    def __log(self, message):
        time = datetime.datetime.now().strftime("%H:%M:%S")
        self.log += '%s: %s\n' % (time, message)

    def __create_tmp_file(self, video):
        ext = self.__get_extension(video.filename)
        self.tmp_file_path = os.path.join(self.tmp_dir, '1%s' % ext)
        video.save(self.tmp_file_path)

    def __get_extension(self, file_name):
        return os.path.splitext(file_name)[1]

    def __get_video(self):
        self.video_source = cv2.VideoCapture(self.tmp_file_path)
        if not self.video_source.isOpened():
            raise MyError("Не удалось открыть видео.")

    def __get_video_area(self):
        video_width = self.video_source.get(cv2.CAP_PROP_FRAME_WIDTH)
        video_height = self.video_source.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.video_area = video_width * video_height

    def __get_fps(self):
        self.fps = self.video_source.get(cv2.CAP_PROP_FPS)

    def __get_next_frame(self):
        ret, self.frame = self.video_source.read()
        return ret

    def __get_boxes(self):
        imgs = [self.frame]
        self.__log('before getting boxes')
        boxes_batch = self.detector.detect(imgs)
        self.boxes = boxes_batch[0]
        self.__log('after getting boxes, boxes: %s' % self.boxes)

    def __filter_boxes(self):
        i = len(self.boxes)
        while i > 0:
            i -= 1
            box = self.boxes[i]
            box_area = box[2] * box[3]
            if box[4] < self.face_probability or box_area/self.video_area < self.face_area_ratio:
                self.boxes.pop(i)

    def __single_face_check(self):
        if len(self.boxes) > 1:
            raise MyError("На видео присутствует более одного лица.")

    def __save_frame_info(self):
        if len(self.boxes) == 1:
            self.frames_with_face_count += 1
        else:
            self.frames_without_face_count += 1

    def __duration_check(self):
        frames_count = self.frames_with_face_count + self.frames_without_face_count
        self.__log('frames_count: %s, self.frames_with_face_count: %s, self.frames_without_face_count: %s, '
                   'self.frames_with_face_count/frames_count: %s, self.frames_with_face_ratio: %s, '
                   'self.fps: %s'
                   % (frames_count, self.frames_with_face_count, self.frames_without_face_count,
                      self.frames_with_face_count/frames_count, self.frames_with_face_ratio, self.fps))
        if self.frames_with_face_count/frames_count < self.frames_with_face_ratio:
            raise MyError("На видео меньше %d%% кадров с лицами" % settings.frames_with_face_percentage)
        duration_with_faces = self.frames_with_face_count / self.fps
        self.__log('duration_with_faces: %s' % duration_with_faces)
        if duration_with_faces < settings.min_seconds_with_face:
            raise MyError("На видео суммарная длительность кадров с лицами < %d секунд."
                          % settings.min_seconds_with_face)
        if duration_with_faces > settings.max_seconds_with_face:
            raise MyError("На видео суммарная длительность кадров с лицами > %d секунд."
                          % settings.max_seconds_with_face)

    def __delete_tmp_files(self):
        for dir_or_file in os.listdir(self.tmp_dir):
            path = os.path.join(self.tmp_dir, dir_or_file)
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
