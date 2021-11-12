# -*- coding: utf-8 -*-

import cv2 as cv


class Fingerprint:

    @staticmethod
    def match_level(img_1: cv.numpy.ndarray,
                    img_2: cv.numpy.ndarray) -> float:

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
    def process_image(img: cv.numpy.ndarray) -> cv.numpy.ndarray:
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
