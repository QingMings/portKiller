"""
生成一个简洁的端口图标 (app.ico)
包含多尺寸：16, 32, 48, 64, 128, 256
"""
import struct
import zlib
import os


def make_png(size):
    """用纯 Python 生成 PNG: 蓝色背景 + 白色端口符号"""
    w = h = size

    # 主色（渐变深蓝背景）
    bg_top = (30, 64, 124)
    bg_bottom = (28, 96, 180)

    def pixel(x, y):
        # 背景渐变
        t = y / max(h - 1, 1)
        r = int(bg_top[0] * (1 - t) + bg_bottom[0] * t)
        g = int(bg_top[1] * (1 - t) + bg_bottom[1] * t)
        b = int(bg_top[2] * (1 - t) + bg_bottom[2] * t)

        # 画一个端口符号: 一个圆 + 连接线
        # 使用相对坐标
        cx, cy = w / 2, h / 2
        outer_r = w * 0.38
        inner_r = w * 0.18

        dx = x - cx
        dy = y - cy
        dist = (dx * dx + dy * dy) ** 0.5

        # 圆环
        if inner_r <= dist <= outer_r:
            # 顶部有一个小缺口（端口开口）
            angle_deg = (270 - (dy / max(abs(dx) + abs(dy), 1) * 90))  # 简化: 用 y 判断
            # 简化：顶部 90 度角不开口，改为画一根向上的线
            return (255, 255, 255)

        # 内部填充（较浅）
        if dist < inner_r:
            return (180, 210, 255)

        # 向上的连接线（从圆环顶部伸出）
        if abs(x - cx) < w * 0.04 and y < cy - outer_r:
            return (255, 255, 255)

        # 顶部横线（插头）
        if y < cy - outer_r - w * 0.12 and abs(x - cx) < w * 0.15 and y > cy - outer_r - w * 0.2:
            return (255, 255, 255)

        return (r, g, b)

    # 构建 raw 数据 (加 filter byte 0 每一行)
    raw = b""
    for y in range(h):
        raw += b"\x00"
        for x in range(w):
            r, g, b = pixel(x, y)
            raw += bytes([r, g, b])

    # PNG signature
    sig = b"\x89PNG\r\n\x1a\n"

    # IHDR
    ihdr_data = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    ihdr = _chunk(b"IHDR", ihdr_data)

    # IDAT
    idat = _chunk(b"IDAT", zlib.compress(raw))

    # IEND
    iend = _chunk(b"IEND", b"")

    return sig + ihdr + idat + iend


def _chunk(chunk_type, data):
    length = struct.pack(">I", len(data))
    crc_data = chunk_type + data
    crc = struct.pack(">I", zlib.crc32(crc_data) & 0xffffffff)
    return length + crc_data + crc


def write_ico(out_path, png_sizes):
    """将多个 PNG 写入一个 ICO 文件"""
    # ICONDIR
    icon_dir = struct.pack("<HHH", 0, 1, len(png_sizes))

    # ICONDIRENTRY 列表
    entries = []
    image_datas = []
    offset = 6 + 16 * len(png_sizes)  # ICONDIR + 所有 ICONDIRENTRY 大小

    for size, png_data in png_sizes:
        entries.append(struct.pack(
            "<BBBBHHII",
            size if size < 256 else 0,  # width (0 means 256)
            size if size < 256 else 0,  # height
            0,  # color count (0 means truecolor)
            0,  # reserved
            1,  # planes
            32,  # bit count
            len(png_data),
            offset
        ))
        image_datas.append(png_data)
        offset += len(png_data)

    with open(out_path, "wb") as f:
        f.write(icon_dir)
        for entry in entries:
            f.write(entry)
        for data in image_datas:
            f.write(data)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(script_dir, "app.ico")

    sizes = [16, 32, 48, 64, 128, 256]
    png_list = [(s, make_png(s)) for s in sizes]

    write_ico(out_path, png_list)
    print(f"Icon saved: {out_path}")
    print(f"Sizes included: {sizes}")
