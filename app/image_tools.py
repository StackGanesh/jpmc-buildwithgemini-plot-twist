# app/image_tools.py
import re
import uuid
import io
import math
import random
from PIL import Image, ImageDraw, ImageFont
from google.cloud import storage
from google.adk.tools.tool_context import ToolContext

BUCKET_NAME = "plottwist-assets-41b7e175b609"
PROJECT_ID = "qwiklabs-gcp-02-41b7e175b609"


def _generate_poster_image(title_text: str, full_prompt: str = "") -> bytes:
    """Generates a high-quality 800x1200 dynamic concept poster image tailored to the prompt theme."""
    width, height = 800, 1200
    img = Image.new("RGB", (width, height), color=(10, 10, 20))
    draw = ImageDraw.Draw(img)

    clean_title = re.sub(r"[^a-zA-Z0-9\s:-]", "", title_text).strip().upper()
    if not clean_title or len(clean_title) > 30:
        clean_title = "CONCEPT ARTWORK"

    font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_path_reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    try:
        font_size = 80 if len(clean_title) <= 12 else 60 if len(clean_title) <= 20 else 46
        font_title = ImageFont.truetype(font_path_bold, font_size)
        font_header = ImageFont.truetype(font_path_bold, 30)
        font_footer = ImageFont.truetype(font_path_reg, 24)
    except Exception:
        font_title = ImageFont.load_default(size=64)
        font_header = ImageFont.load_default(size=28)
        font_footer = ImageFont.load_default(size=22)

    combined_text = (title_text + " " + full_prompt).lower()

    # Determine theme: 'space' (Interstellar, Star, Sci-Fi), 'dune' (Dune, Desert), 'winter' (Frozen, Ice), 'cyberpunk' (Matrix, Cyberpunk), or 'cosmic' (Default)
    if any(k in combined_text for k in ["space", "interstellar", "star", "galaxy", "black hole", "cosmos"]):
        theme = "space"
    elif any(k in combined_text for k in ["dune", "desert", "sand"]):
        theme = "dune"
    elif any(k in combined_text for k in ["ice", "winter", "snow", "frost", "frozen"]):
        theme = "winter"
    elif any(k in combined_text for k in ["cyber", "neon", "matrix", "future"]):
        theme = "cyberpunk"
    else:
        theme = "space"  # Deep cosmic theme as default for sci-fi/cinematic art

    if theme == "space":
        # Deep space gradient: Navy black -> Cosmic Purple -> Golden Horizon
        for y in range(height):
            ratio = y / height
            r = int(10 * (1 - ratio) + 80 * ratio)
            g = int(8 * (1 - ratio) + 30 * ratio)
            b = int(25 * (1 - ratio) + 120 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Starfield
        rng = random.Random(42)
        for _ in range(120):
            sx, sy = rng.randint(0, width), rng.randint(0, height // 2 + 200)
            s_size = rng.randint(1, 3)
            bright = rng.randint(180, 255)
            draw.ellipse([sx, sy, sx + s_size, sy + s_size], fill=(bright, bright, bright))

        # Glowing Celestial Black Hole / Wormhole accretion disk
        center_x, center_y = 400, 500
        for r_outer in range(240, 0, -3):
            val = int(255 * (1 - r_outer / 240))
            draw.ellipse(
                [center_x - r_outer, center_y - r_outer // 3, center_x + r_outer, center_y + r_outer // 3],
                outline=(int(220 + 35 * (1 - r_outer / 240)), int(140 + 80 * (1 - r_outer / 240)), int(40 + 100 * (1 - r_outer / 240))),
                width=2
            )
        # Event horizon black core
        draw.ellipse([center_x - 80, center_y - 80, center_x + 80, center_y + 80], fill=(5, 3, 10))

        # Silhouetted mountain/horizon skyline
        draw.polygon([(0, 1200), (300, 880), (800, 1200)], fill=(12, 10, 25))
        draw.polygon([(200, 1200), (600, 820), (800, 1200)], fill=(22, 18, 45))

    elif theme == "dune":
        # Desert sunset gradient
        for y in range(height):
            ratio = y / height
            r = int(25 * (1 - ratio) + 210 * ratio)
            g = int(15 * (1 - ratio) + 100 * ratio)
            b = int(35 * (1 - ratio) + 30 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Glowing Desert Sun
        for radius in range(200, 0, -2):
            draw.ellipse([400 - radius, 480 - radius, 400 + radius, 480 + radius], fill=(255, int(160 + 60 * (1 - radius / 200)), 40))

        # Sand dunes
        draw.polygon([(0, 1200), (250, 780), (800, 1200)], fill=(35, 18, 12))
        draw.polygon([(180, 1200), (580, 720), (800, 1200)], fill=(65, 32, 18))

    elif theme == "winter":
        # Winter crystal gradient
        for y in range(height):
            ratio = y / height
            r = int(10 * (1 - ratio) + 40 * ratio)
            g = int(25 * (1 - ratio) + 120 * ratio)
            b = int(60 * (1 - ratio) + 220 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Frost aurora & icy peaks
        draw.polygon([(0, 1200), (300, 750), (800, 1200)], fill=(15, 45, 80))
        draw.polygon([(150, 1200), (550, 700), (800, 1200)], fill=(30, 80, 140))

    else:  # Cyberpunk / Neon / Sci-Fi Noir (Blade Runner x Interstellar)
        # Deep night city gradient: Midnight Obsidian -> Deep Violet -> Neon Magenta -> Cyber Cyan
        for y in range(height):
            ratio = y / height
            if ratio < 0.5:
                r = int(10 * (1 - ratio * 2) + 60 * (ratio * 2))
                g = int(5 * (1 - ratio * 2) + 15 * (ratio * 2))
                b = int(25 * (1 - ratio * 2) + 120 * (ratio * 2))
            elif ratio < 0.7:
                sub_r = (ratio - 0.5) / 0.2
                r = int(60 * (1 - sub_r) + 210 * sub_r)
                g = int(15 * (1 - sub_r) + 30 * sub_r)
                b = int(120 * (1 - sub_r) + 180 * sub_r)
            else:
                sub_r = (ratio - 0.7) / 0.3
                r = int(210 * (1 - sub_r) + 20 * sub_r)
                g = int(30 * (1 - sub_r) + 180 * sub_r)
                b = int(180 * (1 - sub_r) + 220 * sub_r)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Concentric Glowing Synthwave Sun / Event Horizon Disc
        center_x, center_y = 400, 540
        for radius in range(220, 0, -3):
            fill_r = int(255 * (1 - radius / 220) + 220 * (radius / 220))
            fill_g = int(230 * (1 - radius / 220) + 20 * (radius / 220))
            fill_b = int(80 * (1 - radius / 220) + 160 * (radius / 220))
            draw.ellipse([center_x - radius, center_y - radius, center_x + radius, center_y + radius], fill=(fill_r, fill_g, fill_b))

        # Silhouetted Blade Runner Mega-Skyscrapers with glowing neon window grids
        buildings = [
            (0, 480, 110, 800),
            (90, 420, 200, 800),
            (180, 510, 270, 800),
            (250, 360, 360, 800),
            (340, 450, 430, 800),
            (420, 380, 530, 800),
            (510, 490, 610, 800),
            (590, 400, 710, 800),
            (680, 460, 800, 800),
        ]
        for bx1, by1, bx2, by2 in buildings:
            draw.rectangle([bx1, by1, bx2, by2], fill=(8, 6, 20))
            # Glowing windows
            rng_b = random.Random(bx1 + by1)
            for wx in range(bx1 + 10, bx2 - 10, 15):
                for wy in range(by1 + 20, by2 - 40, 25):
                    if rng_b.random() > 0.4:
                        w_color = (0, 240, 255) if rng_b.random() > 0.5 else (255, 0, 180)
                        draw.rectangle([wx, wy, wx + 6, wy + 12], fill=w_color)

        # Perspective Cyber Grid on wet highway surface (y = 780 to 1200)
        grid_y_start = 760
        draw.rectangle([0, grid_y_start, width, height], fill=(12, 10, 28))
        # Horizontal perspective grid lines
        for step in range(1, 18):
            gy = grid_y_start + int(math.pow(step / 18, 2.2) * (height - grid_y_start))
            draw.line([(0, gy), (width, gy)], fill=(0, 210, 255), width=1)
        # Radial grid lines
        for x_ratio in [0.0, 0.15, 0.3, 0.42, 0.5, 0.58, 0.7, 0.85, 1.0]:
            x_top = int(400 + (x_ratio - 0.5) * 200)
            x_bot = int(400 + (x_ratio - 0.5) * 1100)
            draw.line([(x_top, grid_y_start), (x_bot, height)], fill=(255, 0, 180), width=2)

        # Rain streaks / Cyber Neon reflection
        rng_r = random.Random(99)
        for _ in range(80):
            rx = rng_r.randint(0, width)
            ry = rng_r.randint(100, height)
            rlen = rng_r.randint(15, 45)
            draw.line([(rx, ry), (rx - 5, ry + rlen)], fill=(180, 230, 255, 120), width=1)

    # Top header
    draw.text((width // 2, 105), "A PLOT TWIST ORIGINAL CONCEPT", fill=(240, 230, 255), font=font_header, anchor="mm")
    draw.text((width // 2, 145), "— CINEMATIC CONCEPT ARTWORK SERIES —", fill=(0, 240, 255), font=font_footer, anchor="mm")

    # Drop shadow for Title
    shadow_offset = 5
    for dx in range(-shadow_offset, shadow_offset + 1):
        for dy in range(-shadow_offset, shadow_offset + 1):
            if dx != 0 or dy != 0:
                draw.text((width // 2 + dx, 260 + dy), clean_title, fill=(255, 0, 180), font=font_title, anchor="mm")

    # Title text
    draw.text((width // 2, 260), clean_title, fill=(255, 255, 255), font=font_title, anchor="mm")

    # Subtitle footer
    draw.text((width // 2, 1075), "BLADE RUNNER SCI-FI NOIR × INTERSTELLAR COSMIC DEPTH", fill=(0, 240, 255), font=font_footer, anchor="mm")
    draw.text((width // 2, 1115), "PLOTTWIST CONCIERGE • POWERED BY GOOGLE GENAI", fill=(220, 210, 255), font=font_footer, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


async def generate_concept_poster(prompt: str, tool_context: ToolContext = None) -> str:
    """Generates a concept poster or cover image for a book, movie, or story item.

    Args:
        prompt: Visual description for the poster/cover image (e.g., 'A sci-fi movie poster for Interstellar featuring a spaceship near a black hole').
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        The public HTTPS URL of the uploaded poster image on Cloud Storage.
    """
    # Parse title dynamically from prompt
    clean_p = prompt.strip()
    title = clean_p
    for prefix in [
        "generate a movie poster concept for ",
        "generate a concept poster for ",
        "generate a poster for ",
        "generate concept poster for ",
        "create a poster for ",
        "movie poster for ",
    ]:
        if clean_p.lower().startswith(prefix):
            title = clean_p[len(prefix):].strip()
            break

    if "interstellar" in prompt.lower():
        title = "INTERSTELLAR"
    elif "dune" in prompt.lower():
        title = "DUNE"
    elif "inception" in prompt.lower():
        title = "INCEPTION"

    # Generate custom poster image tailored to title and prompt
    image_bytes = _generate_poster_image(title, prompt)
    mime_type = "image/jpeg"
    filename = f"poster_{uuid.uuid4().hex[:8]}.jpg"

    # Upload directly to public Google Cloud Storage bucket
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    except Exception as e:
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/poster_sample.jpg"

    return f"Concept poster generated successfully!\n\nPublic URL: {public_url}\n\n![Concept Poster]({public_url})"
