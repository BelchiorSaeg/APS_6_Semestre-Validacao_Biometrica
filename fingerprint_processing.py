# -*- coding: utf-8 -*-

import cv2 as cv
import os
from numpy import ndarray

_TEMP_FILENAME = ".#TEMP_FILE.png"


class Fingerprint:

    @staticmethod
    def match_level(img_1: bytes,
                    img_2: bytes) -> float:

        img_1 = Fingerprint.bytes_to_ndarray(img_1)
        img_2 = Fingerprint.bytes_to_ndarray(img_2)

        sift = cv.SIFT_create()

        keypoints_1, descriptors_1 = sift.detectAndCompute(img_1, None)
        keypoints_2, descriptors_2 = sift.detectAndCompute(img_2, None)

        matches = cv.FlannBasedMatcher(dict(algorithm=1, tress=10),
                                       dict()).knnMatch(descriptors_1,
                                                        descriptors_2,
                                                        k=2)

        match_points = []

        for p, q in matches:
            if p.distance < 0.1 * q.distance:
                match_points.append(p)

        keypoints = 0

        if len(keypoints_1) <= len(keypoints_2):
            keypoints = len(keypoints_1)

        else:
            keypoints = len(keypoints_2)

        return len(match_points) / keypoints

    @staticmethod
    def process_image(img: bytes) -> bytes:
        return img

    @staticmethod
    def display_matches():
        pass

    @staticmethod
    def hard_compare(img: cv.numpy.ndarray, targets: list) -> list:
        match = []

        for target_img in targets:
            match.append(Fingerprint.match_level(img, target_img))

        return match

    @staticmethod
    def bytes_to_ndarray(bin_file: bytes) -> ndarray:
        with open(_TEMP_FILENAME, 'wb') as file:
            file.write(bin_file)

        array = cv.imread(_TEMP_FILENAME)

        os.remove(_TEMP_FILENAME)

        return array

    @staticmethod
    def ndarray_to_bytes(array: ndarray) -> bytes:
        cv.imwrite(_TEMP_FILENAME, array)

        with open(_TEMP_FILENAME, 'rb') as file:
            bin_file = file.read()

        os.remove(_TEMP_FILENAME)

        return bin_file
