#!/usr/bin/env python

'''
Simple "Square Detector" program.
Loads several images sequentially and tries to find squares in each image.
'''

# Python 2/3 compatibility
from __future__ import print_function
import sys
import numpy as np
import cv2 as cv

PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range


def angle_cos(p0, p1, p2):
    d1, d2 = (p0 - p1).astype('float'), (p2 - p1).astype('float')
    return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1) * np.dot(d2, d2)))


def find_squares(img):
    img = cv.GaussianBlur(img, (5, 5), 0)
    squares = []
    for gray in cv.split(img):
        for thrs in xrange(0, 255, 26):
            if thrs == 0:
                bin = cv.Canny(gray, 0, 50, apertureSize=5)
                bin = cv.dilate(bin, None)
            else:
                _retval, bin = cv.threshold(gray, thrs, 255, cv.THRESH_BINARY)
            contours, _hierarchy = cv.findContours(bin, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv.arcLength(cnt, True)
                cnt = cv.approxPolyDP(cnt, 0.02 * cnt_len, True)
                if len(cnt) == 4 and cv.contourArea(cnt) > 100 and cv.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    # max_cos = np.max([angle_cos(cnt[i], cnt[(i + 1) % 4], cnt[(i + 2) % 4]) for i in xrange(4)])
                    # if max_cos < 0.1:
                    squares.append(cnt)
    return squares


def main():
    from glob import glob
    for fn in glob('data/test/*.png'):
        i = fn.split('/')[-1]
        print(i)
        img = cv.imread(fn)
        squares = find_squares(img)
        # print(len(squares[0]))
        for s in squares:
            print(s[0][0])
            cv.rectangle(img, (s[0][0], s[0][1]), (s[2][0], s[2][1]), (0, 0, 255), 2)
        # cv.imshow('squares', img)
        cv.imwrite(f'data/simple-squares/{i}', img)

        # ch = cv.waitKey()
        # if ch == 27:
        #     break

    print('Done')


if __name__ == '__main__':
    print(__doc__)
    main()
    cv.destroyAllWindows()
