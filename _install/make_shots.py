# -*- coding: utf-8 -*-
"""把真实命令行输出渲染成终端风格 PNG（深色背景 + 标题栏 + 等宽字体）。"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAW = Path(r"D:\risk_project\截图\_raw")
OUT = Path(r"D:\risk_project\截图")

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\msyhl.ttc",
    r"C:\Windows\Fonts\simsun.ttc",
    r"C:\Windows\Fonts\consola.ttf",
]

W = 1500
PAD = 18
TITLE_H = 34
LINE_H = 24
FS = 15

BG = (12, 12, 12)
BAR = (32, 34, 38)
FG = (222, 226, 230)
GREEN = (126, 231, 135)
DIM = (140, 148, 158)


def load_font(size=FS):
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def text_w(draw, s, font):
    b = draw.textbbox((0, 0), s, font=font)
    return b[2] - b[0]


def wrap(draw, s, font, maxw):
    """按像素宽度折行（中文按字符切，英文按空格）。"""
    if not s.strip():
        return [""]
    if text_w(draw, s, font) <= maxw:
        return [s]
    out, cur = [], ""
    for ch in s:
        if text_w(draw, cur + ch, font) > maxw:
            out.append(cur)
            cur = "    " + ch if ch != " " else ""
        else:
            cur += ch
    out.append(cur)
    return out


def render(lines, title, dst, page_note=""):
    f = load_font()
    tmp = Image.new("RGB", (W, 10))
    d0 = ImageDraw.Draw(tmp)
    maxw = W - PAD * 2

    rows = []
    for s in lines:
        for w in wrap(d0, s, f, maxw):
            rows.append(w)

    h = TITLE_H + PAD * 2 + LINE_H * len(rows) + (26 if page_note else 0)
    img = Image.new("RGB", (W, h), BG)
    dr = ImageDraw.Draw(img)

    # 标题栏
    dr.rectangle([0, 0, W, TITLE_H], fill=BAR)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        dr.ellipse([14 + i * 22, 11, 26 + i * 22, 23], fill=c)
    dr.text((W / 2 - text_w(dr, title, f) / 2, 8), title, font=f, fill=(200, 205, 212))

    y = TITLE_H + PAD
    for s in rows:
        color = FG
        if s.startswith(("D:\\", "(venv)", "C:\\")):
            color = GREEN
        elif s.strip().startswith("=") or s.strip().startswith("---"):
            color = DIM
        dr.text((PAD, y), s, font=f, fill=color)
        y += LINE_H

    if page_note:
        dr.text((PAD, y + 6), page_note, font=load_font(13), fill=DIM)

    img.save(dst, "PNG")
    return dst, img.size


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("01_python.txt", "命令提示符 — Python 版本验证", "截图01_Python版本与虚拟环境路径.png", ""),
        ("02_venv.txt", "命令提示符 — 虚拟环境激活与依赖版本", "截图02_虚拟环境与依赖版本.png", ""),
        ("03_mysql.txt", "命令提示符 — MySQL 版本与数据库列表", "截图03_MySQL版本与数据库列表.png", ""),
        ("04_req.txt", "命令提示符 — requirements.txt 内容", "截图04_requirements依赖清单.png", ""),
    ]
    made = []
    for src, title, dst, note in jobs:
        lines = (RAW / src).read_text(encoding="utf-8", errors="replace").splitlines()
        p, size = render(lines, title, OUT / dst, note)
        made.append((p, size))
        print(f"  {p.name:46} {size[0]}×{size[1]}")

    # 运行输出：按 "=====" 小节切分，再贪心装箱，保证表格不被截断
    run = (RAW / "05_run.txt").read_text(encoding="utf-8", errors="replace").splitlines()
    sections, cur = [], []
    for ln in run:
        if ln.strip().startswith("=" * 20) and cur:
            sections.append(cur); cur = [ln]
        else:
            cur.append(ln)
    if cur:
        sections.append(cur)
    CHUNK = 38
    pages, page = [], []
    for sec in sections:
        if page and len(page) + len(sec) > CHUNK:
            pages.append(page); page = []
        if len(sec) > CHUNK:                      # 单节过长再硬切
            for i in range(0, len(sec), CHUNK):
                part = sec[i:i + CHUNK]
                (pages.append(page) if page else None)
                page = []
                pages.append(part)
            continue
        page.extend(sec)
    if page:
        pages.append(page)
    for i, chunk in enumerate(pages, 1):
        dst = OUT / f"截图05_脚本运行结果_P{i}of{len(pages)}.png"
        p, size = render(chunk, "命令提示符 — python dataset_process.py --full",
                         dst, f"第 {i} / {len(pages)} 页　共 {len(run)} 行")
        made.append((p, size))
        print(f"  {p.name:46} {size[0]}×{size[1]}")

    print(f"\n共生成 {len(made)} 张")


if __name__ == "__main__":
    main()
