from PIL import Image, ImageEnhance

from scale import mh


def resize_w(img: Image.Image, target_w: int) -> Image.Image:
    ratio = img.width / img.height
    return img.resize((target_w, int(target_w / ratio)))


def darken(img: Image.Image) -> Image.Image:
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(0.5)


def draw_center(draw, cx, cy, string, color, font):
    sizex, sizey = font.getsize(string)
    draw.text((cx - sizex / 2, cy - sizey / 2), string, color, font)


def draw_left(draw, cx, cy, string, color, font):
    sizex, sizey = font.getsize(string)
    draw.text((cx - sizex, cy), string, color, font)


last_string = ''
last_arr = []
def draw_multiline(draw, dim, string, color, font):
    global last_string
    global last_arr
    if string == last_string:
        draw.multiline_text((dim[0], dim[1]), ''.join(last_arr), color, font, spacing=mh(10))
    else:
        i = 1
        j = 0
        inserted = 0
        arr = list(string)
        while i < len(string):
            line_break = False
            last_space = -1
            sizex, sizey = font.getsize(string[j:i])
            while sizex < dim[2] and i < len(string):
                if string[i] == '\n':
                    line_break = True
                    i += 1
                    break
                elif string[i] == ' ':
                    last_space = i
                i += 1
                sizex, sizey = font.getsize(string[j:i])
            if not line_break:
                if last_space > 0 and sizex > dim[2]:
                    i = last_space + 1
                    j = i
                    arr.insert(last_space+inserted, '\n')
                    inserted+=1
                else:
                    j = i
                    arr.insert(i +inserted, '\n')
                    inserted+=1
            elif line_break:
                j = i
        last_string = string
        last_arr = arr
        draw.multiline_text((dim[0], dim[1]), ''.join(arr), color, font, spacing=mh(10))
