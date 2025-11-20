"""
Generate placeholder avatar images for demo/testing
Run: python generate_demo_avatars.py
"""
import os
from pathlib import Path

def create_placeholder_avatar(output_path: str, name: str, color: tuple):
    """Create a simple placeholder avatar image"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("PIL not installed, creating minimal placeholder")
        # Create a minimal PPM file (no dependencies)
        create_ppm_placeholder(output_path, name, color)
        return

    # Create image
    size = (512, 512)
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)

    # Draw circle for head
    head_color = tuple(min(c + 40, 255) for c in color)
    draw.ellipse([128, 64, 384, 320], fill=head_color)

    # Draw body
    draw.ellipse([96, 280, 416, 520], fill=head_color)

    # Draw eyes
    eye_color = (50, 50, 50)
    draw.ellipse([190, 150, 230, 190], fill=eye_color)
    draw.ellipse([282, 150, 322, 190], fill=eye_color)

    # Draw mouth (smile)
    draw.arc([200, 200, 312, 280], 0, 180, fill=eye_color, width=3)

    # Add name
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()

    # Text with background
    text_bbox = draw.textbbox((0, 0), name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (size[0] - text_width) // 2
    text_y = 440

    draw.rectangle([text_x - 10, text_y - 5, text_x + text_width + 10, text_y + 35], fill=(0, 0, 0, 180))
    draw.text((text_x, text_y), name, fill=(255, 255, 255), font=font)

    # Save
    img.save(output_path, 'PNG')
    print(f"Created: {output_path}")


def create_ppm_placeholder(output_path: str, name: str, color: tuple):
    """Create a minimal PPM placeholder (no PIL needed)"""
    width, height = 512, 512

    # Create pixel data
    pixels = []
    for y in range(height):
        row = []
        for x in range(width):
            # Simple gradient background
            r = color[0]
            g = color[1]
            b = color[2]

            # Draw a simple circle for the head
            cx, cy = 256, 192
            dx, dy = x - cx, y - cy
            if dx*dx + dy*dy < 120*120:
                r = min(color[0] + 40, 255)
                g = min(color[1] + 40, 255)
                b = min(color[2] + 40, 255)

            row.append((r, g, b))
        pixels.append(row)

    # Write PPM file
    ppm_path = output_path.replace('.png', '.ppm')
    with open(ppm_path, 'wb') as f:
        f.write(f"P6\n{width} {height}\n255\n".encode())
        for row in pixels:
            for r, g, b in row:
                f.write(bytes([r, g, b]))

    print(f"Created: {ppm_path}")
    print(f"  (Convert to PNG with: convert {ppm_path} {output_path})")


def main():
    base_dir = Path(__file__).parent / "avatars" / "models"

    avatars = [
        ("teacher", "Teacher", (70, 130, 180)),    # Steel blue
        ("einstein", "Einstein", (139, 90, 43)),   # Brown
        ("curie", "M. Curie", (147, 112, 219)),    # Purple
        ("lovelace", "Lovelace", (60, 179, 113)),  # Green
    ]

    for avatar_id, name, color in avatars:
        avatar_dir = base_dir / avatar_id
        avatar_dir.mkdir(parents=True, exist_ok=True)

        output_path = str(avatar_dir / "portrait.png")
        create_placeholder_avatar(output_path, name, color)

    print("\nDemo avatars created!")
    print("Replace with real portraits for production use.")


if __name__ == "__main__":
    main()
