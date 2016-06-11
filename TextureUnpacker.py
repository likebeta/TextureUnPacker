#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: likebeta <ixxoo.me@gmail.com>
# Create: 2016-06-10

import os
import plistlib
from PIL import Image


class Matrix(object):
    def __init__(self, src_box, clip_box, offset):
        self.src_box = src_box
        self.clip_box = clip_box
        self.offset = offset
        self.src_size = [self.src_box[2] - self.src_box[0], self.src_box[3] - self.src_box[1]]
        self.clip_size = [self.clip_box[2] - self.clip_box[0], self.clip_box[3] - self.clip_box[1]]


class TextureUnpacker(object):
    @classmethod
    def split_with_plist(cls, plist, save=None):
        plist = os.path.abspath(plist)
        if save is None:
            save = plist + '_split'
        else:
            save = os.path.abspath(save)

        dt = plistlib.readPlist(plist)
        metadata, frames = dt['metadata'], dt['frames']
        format_version = metadata['format']
        big_img = Image.open(metadata['realTextureFileName'])
        for frame, info in frames.iteritems():
            if format_version == 2:
                info = cls.parse_as_plist_v2(info)
            elif format_version == 3:
                info = cls.parse_as_plist_v3(info)
            else:
                raise Exception('not support version' + str(format_version))
            cls.generate_little_image(big_img, info, os.path.join(save, frame))

    @classmethod
    def generate_little_image(cls, big_img, info, path):
        little_img = Image.new('RGBA', info['sz'])
        region = big_img.crop(info['box'])
        if info['rotated']:
            # region = region.rotate(90, expand=1)
            region = region.transpose(Image.ROTATE_90)
        little_img.paste(region, info['xy'])
        dir_ = os.path.dirname(path)
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        little_img.save(path)

    @classmethod
    def parse_as_plist_v2(cls, info):
        """
        {
            'frame': '{{1,1},{430,635}}',
            'offset': '{2,-2}',
            'rotated': False,
            'sourceSize': '{639,639}'
        }
        """
        info['frame'] = cls.__convert_rect(info['frame'])
        info['offset'] = cls.__convert_point(info['offset'])
        info['sourceSize'] = cls.__convert_point(info['sourceSize'])

        rotated = info['rotated']
        if rotated:
            box = (info['frame'][0], info['frame'][1],
                   info['frame'][0] + info['frame'][3],
                   info['frame'][1] + info['frame'][2])
        else:
            box = (info['frame'][0], info['frame'][1],
                   info['frame'][0] + info['frame'][2],
                   info['frame'][1] + info['frame'][3])

        x = info['offset'][0] + (info['sourceSize'][0] - info['frame'][2]) / 2
        y = (info['sourceSize'][1] - info['frame'][3]) / 2 - info['offset'][1]

        return {
            'box': box,
            'rotated': rotated,
            'xy': (x, y),
            'sz': info['sourceSize']
        }

    @classmethod
    def parse_as_plist_v3(cls, info):
        """
        {
            'aliases': [],
            'spriteOffset': '{1,-1}',
            'spriteSize': '{433,637}',
            'spriteSourceSize': '{639,639}',
            'textureRect': '{{1,1},{433,637}}',
            'textureRotated': False
        }
        """
        info['spriteSize'] = cls.__convert_point(info['spriteSize'])
        info['spriteOffset'] = cls.__convert_point(info['spriteOffset'])
        info['textureRect'] = cls.__convert_rect(info['textureRect'])
        info['spriteSourceSize'] = cls.__convert_point(info['spriteSourceSize'])

        rotated = info['textureRotated']
        if rotated:
            box = (info['textureRect'][0], info['textureRect'][1],
                   info['textureRect'][0] + info['textureRect'][3],
                   info['textureRect'][1] + info['textureRect'][2])
        else:
            box = (info['textureRect'][0], info['textureRect'][1],
                   info['textureRect'][0] + info['textureRect'][2],
                   info['textureRect'][1] + info['textureRect'][3])

        x = info['spriteOffset'][0] + (info['spriteSourceSize'][0] - info['spriteSize'][0]) / 2
        y = (info['spriteSourceSize'][1] - info['spriteSize'][1]) / 2 - info['spriteOffset'][1]

        return {
            'box': box,
            'rotated': rotated,
            'xy': (x, y),
            'sz': info['spriteSourceSize']
        }

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
