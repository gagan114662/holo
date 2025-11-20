"""
Generate high-quality avatar portraits for production use
Uses OpenCV to create realistic placeholder avatars
"""
import cv2
import numpy as np
from pathlib import Path


def create_professional_avatar(output_path: str, name: str, primary_color: tuple, secondary_color: tuple):
    """
    Create a professional-looking avatar placeholder

    Args:
        output_path: Where to save the image
        name: Character name for label
        primary_color: Main color (BGR)
        secondary_color: Accent color (BGR)
    """
    # Create 512x512 image
    img = np.zeros((512, 512, 3), dtype=np.uint8)

    # Gradient background
    for y in range(512):
        ratio = y / 512
        color = tuple(int(primary_color[i] * (1 - ratio * 0.3)) for i in range(3))
        img[y, :] = color

    # Head (oval)
    center = (256, 200)
    axes = (100, 130)
    head_color = tuple(int(c * 1.3) for c in secondary_color)
    head_color = tuple(min(255, c) for c in head_color)
    cv2.ellipse(img, center, axes, 0, 0, 360, head_color, -1)

    # Face features
    skin_tone = (200, 180, 160)  # Light skin tone BGR
    cv2.ellipse(img, center, (95, 125), 0, 0, 360, skin_tone, -1)

    # Eyes
    eye_white = (255, 255, 255)
    eye_iris = (80, 60, 40)
    eye_pupil = (30, 30, 30)

    # Left eye
    cv2.ellipse(img, (220, 180), (18, 12), 0, 0, 360, eye_white, -1)
    cv2.circle(img, (220, 180), 8, eye_iris, -1)
    cv2.circle(img, (220, 180), 4, eye_pupil, -1)
    cv2.circle(img, (217, 177), 2, (255, 255, 255), -1)  # Highlight

    # Right eye
    cv2.ellipse(img, (292, 180), (18, 12), 0, 0, 360, eye_white, -1)
    cv2.circle(img, (292, 180), 8, eye_iris, -1)
    cv2.circle(img, (292, 180), 4, eye_pupil, -1)
    cv2.circle(img, (289, 177), 2, (255, 255, 255), -1)  # Highlight

    # Eyebrows
    cv2.ellipse(img, (220, 158), (22, 6), -10, 0, 180, (60, 40, 30), 2)
    cv2.ellipse(img, (292, 158), (22, 6), 10, 0, 180, (60, 40, 30), 2)

    # Nose
    pts = np.array([[256, 190], [248, 220], [256, 225], [264, 220]], np.int32)
    cv2.polylines(img, [pts], False, (150, 130, 110), 2)

    # Mouth (smile)
    cv2.ellipse(img, (256, 255), (30, 15), 0, 0, 180, (150, 100, 100), 2)
    cv2.ellipse(img, (256, 252), (25, 8), 0, 10, 170, (180, 140, 140), -1)

    # Body/shoulders
    pts = np.array([[130, 400], [180, 330], [256, 320], [332, 330], [382, 400], [382, 512], [130, 512]], np.int32)
    cv2.fillPoly(img, [pts], secondary_color)

    # Collar
    pts = np.array([[200, 320], [256, 350], [312, 320], [290, 340], [256, 360], [222, 340]], np.int32)
    cv2.fillPoly(img, [pts], (240, 240, 240))

    # Hair
    hair_color = (40, 30, 20)
    cv2.ellipse(img, (256, 140), (110, 90), 0, 180, 360, hair_color, -1)
    cv2.ellipse(img, (180, 160), (40, 60), 20, 180, 360, hair_color, -1)
    cv2.ellipse(img, (332, 160), (40, 60), -20, 180, 360, hair_color, -1)

    # Add subtle shadow
    overlay = img.copy()
    cv2.ellipse(overlay, (256, 320), (60, 20), 0, 0, 360, (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.1, img, 0.9, 0, img)

    # Name label with nice styling
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(name, font, 0.8, 2)[0]
    text_x = (512 - text_size[0]) // 2
    text_y = 480

    # Text background
    cv2.rectangle(img, (text_x - 10, text_y - 25), (text_x + text_size[0] + 10, text_y + 10), (0, 0, 0), -1)
    cv2.rectangle(img, (text_x - 10, text_y - 25), (text_x + text_size[0] + 10, text_y + 10), secondary_color, 2)

    # Text
    cv2.putText(img, name, (text_x, text_y), font, 0.8, (255, 255, 255), 2)

    # Save
    cv2.imwrite(output_path, img)
    print(f"Created: {output_path}")


def create_einstein_avatar(output_path: str):
    """Create Einstein-style avatar with distinctive features"""
    img = np.zeros((512, 512, 3), dtype=np.uint8)

    # Dark academic background
    for y in range(512):
        ratio = y / 512
        img[y, :] = (int(40 + ratio * 20), int(30 + ratio * 15), int(20 + ratio * 10))

    # Head
    skin_tone = (190, 170, 150)
    cv2.ellipse(img, (256, 200), (95, 125), 0, 0, 360, skin_tone, -1)

    # Wild white hair (Einstein's signature)
    hair_color = (220, 220, 220)
    for i in range(20):
        angle = i * 18
        x = int(256 + 100 * np.cos(np.radians(angle)))
        y = int(150 + 60 * np.sin(np.radians(angle)))
        cv2.ellipse(img, (x, y), (30, 50), angle, 0, 360, hair_color, -1)

    # Eyes (wise, thoughtful)
    cv2.ellipse(img, (220, 185), (16, 10), 0, 0, 360, (255, 255, 255), -1)
    cv2.circle(img, (220, 185), 6, (60, 50, 40), -1)
    cv2.ellipse(img, (292, 185), (16, 10), 0, 0, 360, (255, 255, 255), -1)
    cv2.circle(img, (292, 185), 6, (60, 50, 40), -1)

    # Bushy eyebrows
    cv2.ellipse(img, (220, 165), (25, 10), -5, 0, 180, (200, 200, 200), -1)
    cv2.ellipse(img, (292, 165), (25, 10), 5, 0, 180, (200, 200, 200), -1)

    # Mustache
    cv2.ellipse(img, (256, 235), (35, 15), 0, 0, 180, (180, 180, 180), -1)

    # Nose
    pts = np.array([[256, 195], [245, 225], [256, 230], [267, 225]], np.int32)
    cv2.polylines(img, [pts], False, (140, 120, 100), 2)

    # Slight smile
    cv2.ellipse(img, (256, 260), (25, 12), 0, 10, 170, (140, 100, 100), 2)

    # Body (suit)
    pts = np.array([[140, 400], [190, 330], [256, 315], [322, 330], [372, 400], [372, 512], [140, 512]], np.int32)
    cv2.fillPoly(img, [pts], (50, 50, 60))

    # White shirt collar
    pts = np.array([[210, 320], [256, 345], [302, 320], [285, 335], [256, 350], [227, 335]], np.int32)
    cv2.fillPoly(img, [pts], (240, 240, 240))

    # Tie
    pts = np.array([[246, 350], [256, 400], [266, 350]], np.int32)
    cv2.fillPoly(img, [pts], (40, 40, 120))

    # Label
    font = cv2.FONT_HERSHEY_SIMPLEX
    name = "Einstein"
    text_size = cv2.getTextSize(name, font, 0.8, 2)[0]
    text_x = (512 - text_size[0]) // 2
    cv2.rectangle(img, (text_x - 10, 455), (text_x + text_size[0] + 10, 490), (0, 0, 0), -1)
    cv2.putText(img, name, (text_x, 480), font, 0.8, (255, 255, 255), 2)

    cv2.imwrite(output_path, img)
    print(f"Created: {output_path}")


def main():
    base_dir = Path(__file__).parent / "avatars" / "models"

    # Teacher - friendly blue theme
    teacher_dir = base_dir / "teacher"
    teacher_dir.mkdir(parents=True, exist_ok=True)
    create_professional_avatar(
        str(teacher_dir / "portrait.png"),
        "Teacher",
        (120, 80, 60),    # Dark blue-brown background
        (180, 120, 80)    # Blue accent
    )

    # Einstein
    einstein_dir = base_dir / "einstein"
    einstein_dir.mkdir(parents=True, exist_ok=True)
    create_einstein_avatar(str(einstein_dir / "portrait.png"))

    # Curie - purple/science theme
    curie_dir = base_dir / "curie"
    curie_dir.mkdir(parents=True, exist_ok=True)
    create_professional_avatar(
        str(curie_dir / "portrait.png"),
        "M. Curie",
        (100, 60, 80),    # Purple-ish background
        (180, 100, 140)   # Purple accent
    )

    # Lovelace - green/computing theme
    lovelace_dir = base_dir / "lovelace"
    lovelace_dir.mkdir(parents=True, exist_ok=True)
    create_professional_avatar(
        str(lovelace_dir / "portrait.png"),
        "Lovelace",
        (60, 80, 60),     # Green-ish background
        (100, 160, 100)   # Green accent
    )

    print("\nProduction avatars created!")
    print("For best results, replace with real photos.")


if __name__ == "__main__":
    main()
