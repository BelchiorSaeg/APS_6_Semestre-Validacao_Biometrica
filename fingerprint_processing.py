# -*- coding: utf-8 -*-

import cv2 as cv
import os
import numpy as np


class Fingerprint:
    """
    | > Processamento e validacao de digitais.
    """
    _TEMP_FILENAME = ".#TEMP_FILE.png"

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
        img = Fingerprint.bytes_to_ndarray(img)

        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        img = img[935:2636, 547:1723]

        kernel = np.ones((5, 5), np.uint8)
        img = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)
        img = cv.morphologyEx(img, cv.MORPH_OPEN, kernel)

        img = cv.adaptiveThreshold(img, 255,
                                   cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv.THRESH_BINARY, 145, 1)

        img = Fingerprint.ndarray_to_bytes(img)

        return img

    @staticmethod
    def bytes_to_ndarray(bin_file: bytes) -> np.ndarray:
        with open(Fingerprint._TEMP_FILENAME, 'wb') as file:
            file.write(bin_file)

        array = cv.imread(Fingerprint._TEMP_FILENAME)

        os.remove(Fingerprint._TEMP_FILENAME)

        return array

    @staticmethod
    def ndarray_to_bytes(array: np.ndarray) -> bytes:
        cv.imwrite(Fingerprint._TEMP_FILENAME, array)

        with open(Fingerprint._TEMP_FILENAME, 'rb') as file:
            bin_file = file.read()

        os.remove(Fingerprint._TEMP_FILENAME)

        return bin_file
