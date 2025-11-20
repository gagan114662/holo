"""
Generate avatars for BMad-Skills specialists
"""
import cv2
import numpy as np
from pathlib import Path


def create_specialist_avatar(output_path: str, name: str, role_color: tuple, accent: tuple):
    """Create a specialist avatar with role-specific styling"""
    img = np.zeros((512, 512, 3), dtype=np.uint8)

    # Gradient background
    for y in range(512):
        ratio = y / 512
        color = tuple(int(role_color[i] * (1 - ratio * 0.4)) for i in range(3))
        img[y, :] = color

    # Face
    skin_tone = (200, 180, 160)
    cv2.ellipse(img, (256, 200), (90, 120), 0, 0, 360, skin_tone, -1)

    # Eyes
    cv2.ellipse(img, (220, 180), (16, 10), 0, 0, 360, (255, 255, 255), -1)
    cv2.circle(img, (220, 180), 7, (60, 50, 40), -1)
    cv2.circle(img, (220, 180), 3, (30, 30, 30), -1)

    cv2.ellipse(img, (292, 180), (16, 10), 0, 0, 360, (255, 255, 255), -1)
    cv2.circle(img, (292, 180), 7, (60, 50, 40), -1)
    cv2.circle(img, (292, 180), 3, (30, 30, 30), -1)

    # Eyebrows
    cv2.ellipse(img, (220, 160), (20, 5), -10, 0, 180, (50, 40, 30), 2)
    cv2.ellipse(img, (292, 160), (20, 5), 10, 0, 180, (50, 40, 30), 2)

    # Nose
    pts = np.array([[256, 185], (248, 215), (256, 220), (264, 215)], np.int32)
    cv2.polylines(img, [pts], False, (150, 130, 110), 2)

    # Smile
    cv2.ellipse(img, (256, 250), (25, 12), 0, 10, 170, (150, 100, 100), 2)

    # Hair
    hair_color = (40, 35, 30)
    cv2.ellipse(img, (256, 130), (100, 80), 0, 180, 360, hair_color, -1)

    # Professional attire with accent color
    pts = np.array([[140, 400], [190, 330], [256, 315], [322, 330], [372, 400], [372, 512], [140, 512]], np.int32)
    cv2.fillPoly(img, [pts], accent)

    # Collar
    pts = np.array([[210, 320], [256, 340], [302, 320], [285, 332], [256, 345], [227, 332]], np.int32)
    cv2.fillPoly(img, [pts], (240, 240, 240))

    # Role badge
    badge_y = 380
    cv2.rectangle(img, (180, badge_y - 15), (332, badge_y + 15), role_color, -1)
    cv2.rectangle(img, (180, badge_y - 15), (332, badge_y + 15), (255, 255, 255), 1)

    # Name
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(name, font, 0.5, 1)[0]
    text_x = (512 - text_size[0]) // 2
    cv2.putText(img, name, (text_x, badge_y + 5), font, 0.5, (255, 255, 255), 1)

    cv2.imwrite(output_path, img)
    print(f"Created: {output_path}")


def main():
    base_dir = Path(__file__).parent / "avatars" / "models"

    specialists = [
        ("analyst", "Analyst", (80, 60, 40), (120, 100, 80)),      # Brown - research
        ("planner", "Planner", (60, 80, 60), (100, 140, 100)),     # Green - organization
        ("architect", "Architect", (80, 60, 100), (130, 100, 160)), # Purple - design
        ("developer", "Dev Coach", (40, 80, 100), (80, 140, 180)), # Blue - coding
        ("tester", "QA Engineer", (100, 70, 40), (180, 120, 80)),   # Orange - testing
        ("ux_designer", "UX Designer", (100, 50, 80), (180, 100, 150)), # Pink - design
        ("security_expert", "Security", (50, 50, 80), (100, 100, 160)), # Dark blue - security
    ]

    for spec_id, name, bg_color, accent in specialists:
        spec_dir = base_dir / spec_id
        spec_dir.mkdir(parents=True, exist_ok=True)
        create_specialist_avatar(
            str(spec_dir / "portrait.png"),
            name,
            bg_color,
            accent
        )

    print("\nBMad specialist avatars created!")


if __name__ == "__main__":
    main()
