"""
Generate sample images for cv-04 Edge Detection & Image Processing.
Run: pip install Pillow && python generate_samples.py
Output: 4 images — shapes, building, road, mixed scene.
"""
from PIL import Image, ImageDraw
import os

OUT = os.path.dirname(__file__)


def save(img, name):
    img.save(os.path.join(OUT, name))
    print(f"  created: {name}")


def geometric_shapes():
    img = Image.new("RGB", (500, 500), (240, 240, 240))
    d = ImageDraw.Draw(img)
    d.rectangle([40, 40, 180, 180], fill=(200, 80, 80), outline=(150, 40, 40), width=3)
    d.ellipse([220, 40, 380, 200], fill=(80, 160, 200), outline=(40, 100, 160), width=3)
    d.polygon([(420, 180), (460, 40), (500, 180)], fill=(80, 200, 100), outline=(40, 140, 60), width=3)
    d.polygon([(40, 320), (180, 240), (320, 320), (260, 460), (100, 460)], fill=(220, 180, 60), outline=(160, 120, 20), width=3)
    d.rectangle([360, 260, 480, 460], fill=(180, 80, 200), outline=(120, 40, 160), width=3)
    d.ellipse([160, 340, 300, 480], fill=(80, 200, 200), outline=(40, 140, 140), width=3)
    return img


def building():
    img = Image.new("RGB", (500, 500), (135, 180, 220))
    d = ImageDraw.Draw(img)
    # sky gradient effect
    d.rectangle([0, 300, 500, 500], fill=(100, 140, 80))
    # main building
    d.rectangle([100, 100, 400, 420], fill=(200, 190, 175), outline=(150, 140, 125), width=2)
    # roof
    d.polygon([(80, 100), (250, 30), (420, 100)], fill=(160, 80, 60), outline=(120, 50, 30), width=2)
    # windows grid
    for row in range(3):
        for col in range(4):
            wx = 120 + col * 70
            wy = 130 + row * 80
            d.rectangle([wx, wy, wx + 45, wy + 50], fill=(180, 220, 255), outline=(100, 100, 100), width=1)
    # door
    d.rectangle([210, 330, 290, 420], fill=(120, 80, 50), outline=(80, 50, 20), width=2)
    d.ellipse([282, 370, 292, 380], fill=(200, 160, 50))
    return img


def road_scene():
    img = Image.new("RGB", (600, 400), (135, 180, 220))
    d = ImageDraw.Draw(img)
    # ground
    d.rectangle([0, 250, 600, 400], fill=(100, 100, 100))
    # road markings
    for x in range(0, 600, 80):
        d.rectangle([x, 310, x + 50, 325], fill=(255, 255, 255))
    # pavement
    d.rectangle([0, 230, 600, 252], fill=(180, 170, 160))
    # buildings
    for bx, bw, bh, bc in [(20, 80, 150, (180, 170, 160)), (120, 100, 120, (160, 150, 140)),
                             (380, 90, 160, (190, 180, 170)), (490, 100, 130, (170, 160, 150))]:
        d.rectangle([bx, 250 - bh, bx + bw, 250], fill=bc, outline=(120, 110, 100), width=1)
        for wy in range(250 - bh + 15, 250 - 20, 30):
            for wx in range(bx + 10, bx + bw - 10, 20):
                d.rectangle([wx, wy, wx + 12, wy + 18], fill=(200, 230, 255))
    # traffic light
    d.rectangle([270, 160, 285, 250], fill=(60, 60, 60))
    d.ellipse([268, 162, 287, 181], fill=(255, 50, 50))
    d.ellipse([268, 185, 287, 204], fill=(255, 200, 0))
    d.ellipse([268, 208, 287, 227], fill=(50, 200, 50))
    return img


def mixed_scene():
    img = Image.new("RGB", (500, 500), (200, 220, 240))
    d = ImageDraw.Draw(img)
    # ground
    d.rectangle([0, 350, 500, 500], fill=(80, 130, 60))
    # sun
    d.ellipse([380, 30, 460, 110], fill=(255, 220, 50))
    # clouds
    for cx, cy in [(100, 60), (250, 40), (350, 80)]:
        d.ellipse([cx - 40, cy - 20, cx + 40, cy + 20], fill=(255, 255, 255))
        d.ellipse([cx - 20, cy - 35, cx + 20, cy + 10], fill=(255, 255, 255))
    # house
    d.rectangle([80, 220, 260, 360], fill=(220, 200, 170), outline=(160, 140, 110), width=2)
    d.polygon([(60, 220), (170, 130), (280, 220)], fill=(180, 80, 60), outline=(140, 50, 30), width=2)
    for wx, wy in [(100, 240), (190, 240)]:
        d.rectangle([wx, wy, wx + 45, wy + 50], fill=(180, 220, 255), outline=(100, 100, 100))
    d.rectangle([150, 290, 190, 360], fill=(120, 80, 50))
    # tree
    d.rectangle([340, 270, 360, 360], fill=(100, 70, 40))
    d.ellipse([300, 180, 400, 290], fill=(60, 160, 60))
    d.ellipse([310, 160, 390, 250], fill=(80, 180, 80))
    return img


if __name__ == "__main__":
    print("Generating cv-04 samples...")
    save(geometric_shapes(), "sample_shapes.jpg")
    save(building(), "sample_building.jpg")
    save(road_scene(), "sample_road.jpg")
    save(mixed_scene(), "sample_scene.jpg")
    print("Done — 4 images in samples/")
