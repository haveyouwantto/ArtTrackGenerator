import subprocess
import os
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from tinytag import TinyTag

from drawing import resize_w, darken, draw_left, draw_multiline
from lrcparser import LrcParser
from scale import mw, mh, width, height

fps = 8

blur = ImageFilter.GaussianBlur(mw(32))
title_font = ImageFont.truetype('NotoSansSC-6.ttf',
                                mw(64),
                                layout_engine=ImageFont.LAYOUT_BASIC)
info_font = ImageFont.truetype('NotoSansSC-6.ttf',
                               mw(32),
                               layout_engine=ImageFont.LAYOUT_BASIC)
bold_font = ImageFont.truetype('NotoSansCJKsc-Bold.otf',
                               mw(32),
                               layout_engine=ImageFont.LAYOUT_BASIC)

def remove_extension(file_: str) -> str:
    return ".".join(os.path.basename(file_).split('.')[:-1])


def extract(file_: str) -> str:
    code = subprocess.call(
        'ffmpeg -hide_banner -i "%s" -an -frames:v 1 -y $temp.png' % file_,
        shell=True)
    if code == 0:
        return '$temp.png'
    else:
        return None


def draw_progress_bar(draw, dim, max_, val):
    _width = val / max_ * (dim[2] - dim[0])
    draw.rectangle((dim[0], dim[1], dim[0] + _width, dim[3]), fill='#ffffff')


def draw_info(file_, img):
    tag = TinyTag.get(file_)
    draw = ImageDraw.Draw(img)
    unit = title_font.getsize('0')[1]
    title = tag.title if tag.title is not None else remove_extension(file_)
    if title_font.getsize(title)[0] > ((img.width - img.width // 16) - img.width // 2):
        draw.text((img.width // 2, img.height // 8 + unit // 2),
                  title,
                  '#ffffff',
                  bold_font)
    else:
        draw.text((img.width // 2, img.height // 8), title, '#ffffff',
                  title_font)
    draw.text((img.width // 2, img.height // 6 + unit),
              tag.artist if tag.artist is not None else "未知艺术家", '#ffffff',
              info_font)
    draw.text((img.width // 2, img.height // 6 + unit * 2),
              tag.album if tag.album is not None else "未知专辑", '#ffffff',
              info_font)

    draw.rectangle(
        (img.width // 2 - mw(10), img.height // 3 - mh(10),
         img.width - img.width // 16 + mw(10), img.height // 3 - mh(8)),
        fill='#ffffff')


def draw_bg(cover_img) -> Image.Image:
    with Image.new("RGB", (width, height)) as img:
        cover = Image.open(cover_img)
        res = resize_w(cover, width)
        bg_cover = darken(res).filter(blur).crop(
            (0, res.height // 2 - height // 2, res.width,
             res.height // 2 + height // 2))
        img.paste(bg_cover, (0, 0))
        img.paste(resize_w(cover, mw(750)), (width // 16, height // 9))
        return img


def draw_progress(img, tag, dur):
    draw = ImageDraw.Draw(img)
    draw.text((img.width // 16, img.height - img.height // 9),
              format_time(dur), '#ffffff', info_font)
    draw_left(draw, img.width - img.width // 16, img.height - img.height // 9,
              format_time(tag.duration), '#ffffff', info_font)

    draw_progress_bar(
        draw,
        (img.width // 16, img.height - img.height // 9 - mw(5),
         img.width - img.width // 16, img.height - img.height // 9 - mw(10)),
        tag.duration, dur)

def draw_lrc(img, lrc, dur):
    draw = ImageDraw.Draw(img)
    length = img.width - img.width // 16 - img.width // 2 - mw(25)
    if lrc is None:
        draw.text((img.width // 2, img.height // 3 + mh(10)), '未发现歌词',
                  '#ffffff', info_font)
    else:
        draw_multiline(draw,
                       (img.width // 2, img.height // 3 + mh(10), length),
                       '\n'.join(lrc.get(dur)[1]), '#ffffff', info_font)


def format_time(sec):
    _min = sec // 60
    sec1 = sec % 60
    return '%02d:%02d' % (_min, sec1)


def openfile(file_: str) -> None:
    cover_img = extract(file_)
    if cover_img is None:
        cover_img = 'default.png'
    img = draw_bg(cover_img)
    draw_info(file_, img)
    tag = TinyTag.get(file_)
    lrc_name = os.path.join(os.path.dirname(file_),
                            remove_extension(file_) + '.lrc')
    has_lrc = os.path.exists(lrc_name)
    lrc = None
    if has_lrc:
        lrc = LrcParser(lrc_name)

    p = subprocess.Popen(
        'ffmpeg -hide_banner -f rawvideo -s {0:d}x{1:d} -pix_fmt rgb24 -r {2:d} -i - -i "{3}" -pix_fmt yuv420p -map '
        '0:v -map 1:a -tune stillimage -x264-params keyint={4} -preset fast -t {5} -c:a mp3 -q:a 5 -y "{6}.mp4"'
        .format(width, height, fps, file_, fps * 10, tag.duration,
                remove_extension(file_)),
        shell=True,
        stdin=subprocess.PIPE)

    dur = 0
    while True:
        try:
            new_img = img.copy()
            draw_progress(new_img, tag, dur)
            draw_lrc(new_img, lrc, dur)
            p.stdin.write(new_img.tobytes())
            dur += 1 / fps
        except BrokenPipeError:
            break


if __name__ == "__main__":
    file = sys.argv[1:]  # input('file/folder: ').replace('"', '')
    if len(file) == 0:
        print('missing input file')
        sys.exit(-1)
    for f in file:
        openfile(f)
