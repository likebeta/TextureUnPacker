#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: likebeta <ixxoo.me@gmail.com>
# Create: 2016-06-10

import os
import plistlib
from PIL import Image


class TextureUnpacker(object):
    @classmethod
    def split_with_plist(cls, plist, save=None):
        plist = os.path.abspath(plist)
        if save is None:
            save = plist + '_split'
        else:
            save = os.path.abspath(save)
        if not os.path.exists(save):
            os.makedirs(save)
        dt = plistlib.readPlist(plist)
        metadata, frames = dt['metadata'], dt['frames']
        big_img = Image.open(metadata['realTextureFileName'])
        for frame, info in frames.iteritems():
            info = cls.process_as_plist_v3(info)
            cls.generate_little_image(big_img, info, os.path.join(save, frame))

    @classmethod
    def generate_little_image(cls, big_img, info, path):
        little_img = Image.new('RGBA', info['spriteSourceSize'])
        if info['textureRotated']:
            box = (info['textureRect'][0], info['textureRect'][1],
                   info['textureRect'][0] + info['textureRect'][3],
                   info['textureRect'][1] + info['textureRect'][2])
        else:
            box = (info['textureRect'][0], info['textureRect'][1],
                   info['textureRect'][0] + info['textureRect'][2],
                   info['textureRect'][1] + info['textureRect'][3])
        region = big_img.crop(box)
        if info['textureRotated']:
            # region = region.rotate(90, expand=1)
            region = region.transpose(Image.ROTATE_90)
        x = info['spriteOffset'][0] + (info['spriteSourceSize'][0] - info['spriteSize'][0]) / 2
        y = (info['spriteSourceSize'][1] - info['spriteSize'][1]) / 2 - info['spriteOffset'][1]
        little_img.paste(region, (x, y))
        little_img.save(path)

    @classmethod
    def process_as_plist_v3(cls, info):
        info['spriteSize'] = cls.__convert_point(info['spriteSize'])
        info['spriteOffset'] = cls.__convert_point(info['spriteOffset'])
        info['textureRect'] = cls.__convert_rect(info['textureRect'])
        info['spriteSourceSize'] = cls.__convert_point(info['spriteSourceSize'])
        return info

    @classmethod
    def __convert_rect(cls, rect):
        s = rect.replace('{', '')
        s = s.replace('}', '')
        x, y, w, h = s.split(',')
        return [int(x), int(y), int(w), int(h)]

    @classmethod
    def __convert_point(cls, pt):
        s = pt.replace('{', '')
        s = s.replace('}', '')
        x, y = s.split(',')
        return [int(x), int(y)]


if __name__ == '__main__':
    import sys
    TextureUnpacker.split_with_plist(sys.argv[1])
