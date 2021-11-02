from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import *
from tkinter import messagebox
import numpy
import os.path
import webbrowser
from skimage.color import rgb2lab, lab2rgb

message = None
root = None
MESSAGE = "gifにしたい画像ファイルをドロップしてください。"


def make_inv_img(img):
    w, h = img.size
    img = numpy.asarray(img)
    for y in range(h):
        for x in range(w):
            r, g, b = img[y, x, 0:]
            r = int(r)
            g = int(g)
            b = int(b)
            c = 255
            rate = min(255 / (c - r + 1), 255 / (c - g + 1), 255 / (c - b + 1))

            img[y, x, 0] = min((c-r) * rate, 255)
            img[y, x, 1] = min((c-g) * rate, 255)
            img[y, x, 2] = min((c-b) * rate, 255)
    img = Image.fromarray(img)
    img = ImageEnhance.Color(img).enhance(3.0)
    img = img.filter(filter=ImageFilter.GaussianBlur(radius=5))
    return img


def get_new_filename(fname, kaku):
    if os.path.exists(fname + kaku) is not True:
        return fname + kaku
    i = 1
    while True:
        path = fname + "(" + str(i) + ")" + kaku
        if os.path.exists(path) is not True:
            return path
        i += 1


def get_gray(img):
    rgb2xyz_rec709 = (
        0.412453, 0.357580, 0.180423, 0,
        0.212671, 0.715160, 0.072169, 0,  # RGB mixing weight
        0.019334, 0.119193, 0.950227, 0)

    gamma22LUT = [pow(x/255.0, 2.2)*255 for x in range(256)] * 3
    gamma045LUT = [pow(x/255.0, 1.0/2.2)*255 for x in range(256)]

    img_rgb = img.convert("RGB")  # any format to RGB
    img_rgbL = img_rgb.point(gamma22LUT)
    # RGB to L(grayscale BT.709)
    img_grayL = img_rgbL.convert("L", rgb2xyz_rec709)
    img_gray = img_grayL.point(gamma045LUT)
    return img_gray


def make_gif(path):
    try:
        img = Image.open(path)
        img = img.convert('RGB')
    except:
        messagebox.showerror(
            "Error", os.path.basename(path)+"を画像ファイルとして認識できません。")
        return

    message.set(os.path.basename(path) + "を処理しています。")
    root.update()
    images = []

    first_page = Image.new('P', img.size, 'gray')
    img_inv = make_inv_img(img).quantize(method=0, colors=253)
    gray = get_gray(img).quantize(method=0, colors=253)

    w, h = img.size
    r = 5
    second = 15
    gray2 = gray.copy()
    try:
        font = ImageFont.truetype(
            "C:/Windows/Fonts/msgothic.ttc", size=25)
    except:
        font = ImageFont.truetype(
            "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc", size=25)
    draw = ImageDraw.Draw(first_page)
    draw.ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r),
                 (0, 0, 0), "gray")
    draw.text((w / 2, h / 2 - 100), "画面が切り替わっても、中心の●を" + str(second) +
              "秒間\n目をそらさずに見続けてください。", anchor="mm", font=font, fill=(255, 0, 0),
              stroke_width=2, stroke_fill="black")

    draw = ImageDraw.Draw(img_inv)
    draw.ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r),
                 (0, 0, 0), "gray")

    draw = ImageDraw.Draw(gray)
    draw.ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r),
                 (0, 0, 0), (255, 255, 255))

    draw = ImageDraw.Draw(gray2)
    draw.ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r),
                 (0, 0, 0), (255, 255, 255))
    draw.text((0, 0), "この画像はモノクロ画像です", font=font, fill=(255, 0, 0),
              stroke_width=2, stroke_fill="black")

    images.append(first_page)
    images.append(img_inv)
    images.append(gray)
    images.append(gray2)

    fname = os.path.dirname(path) + "\\" + \
        os.path.splitext(os.path.basename(path))[0]
    path = get_new_filename(fname, ".gif")
    images[0].save(path,
                   save_all=True, append_images=images[1:], optimize=False, duration=[1, 6000, second * 1000, 4000, 4000], loop=0)
    message.set(MESSAGE)
    messagebox.showinfo("処理が完了しました", os.path.basename(path) + "として保存しました。")
    webbrowser.open(path)


def drop(event):
    path = event.data[1:-1]
    make_gif(path)


def main():
    global message, root
    # メインウィンドウの生成
    root = TkinterDnD.Tk()
    root.geometry("600x400")
    root.title("補色残像プログラム")
    root.drop_target_register(DND_FILES)
    root.dnd_bind("<<Drop>>", drop)
    # StringVarのインスタンスを格納するウィジェット変数text
    message = tk.StringVar(root)
    message.set(MESSAGE)
    # Lavelウィジェットの生成
    label = ttk.Label(root, textvariable=message,
                      font=("MSゴシック", "15", "bold"))
    # ウィジェットの配置
    label.grid(row=0, column=0, padx=10)
    root.mainloop()


main()
