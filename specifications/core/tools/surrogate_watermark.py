#!/usr/bin/env python3
"""
Apply a deterministic watermark to surrogate frames based on streamId + sequence.
Usage: surrogate_watermark.py --stream cam-entrance-01 --seq 10234 --text "SYNTHETIC SURROGATE" input.jpg output.jpg
"""
import argparse, hmac, hashlib
from PIL import Image, ImageDraw, ImageFont

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stream', required=True)
    ap.add_argument('--seq', type=int, required=True)
    ap.add_argument('--text', default='SYNTHETIC SURROGATE')
    ap.add_argument('input')
    ap.add_argument('output')
    args = ap.parse_args()
    img = Image.open(args.input).convert('RGBA')
    overlay = Image.new('RGBA', img.size, (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    # deterministic color/alpha
    msg = f"{args.stream}|{args.seq}".encode()
    dig = hmac.new(b'watermark-key', msg, hashlib.sha256).digest()
    color = (200, 200, 200, 90 + (dig[0] % 80))
    text = args.text
    # position bottom-right
    w, h = img.size
    try:
        font = ImageFont.truetype('arial.ttf', int(h*0.04))
    except Exception:
        font = ImageFont.load_default()
    tw, th = draw.textsize(text, font=font)
    x, y = w - tw - 16, h - th - 12
    draw.text((x, y), text, fill=color, font=font)
    out = Image.alpha_composite(img, overlay).convert('RGB')
    out.save(args.output)

if __name__ == '__main__':
    main()
