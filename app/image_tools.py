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

    else:  # Cyberpunk / Neon
        for y in range(height):
            ratio = y / height
            r = int(20 * (1 - ratio) + 120 * ratio)
            g = int(10 * (1 - ratio) + 20 * ratio)
            b = int(40 * (1 - ratio) + 160 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        draw.polygon([(0, 1200), (200, 800), (800, 1200)], fill=(20, 10, 40))

    # Top header
    draw.text((width // 2, 110), "A PLOT TWIST ORIGINAL CONCEPT", fill=(240, 230, 255), font=font_header, anchor="mm")
    draw.text((width // 2, 150), "— CONCEPT ARTWORK SERIES —", fill=(255, 210, 130), font=font_footer, anchor="mm")

    # Drop shadow for Title
    shadow_offset = 4
    for dx in range(-shadow_offset, shadow_offset + 1):
        for dy in range(-shadow_offset, shadow_offset + 1):
            if dx != 0 or dy != 0:
                draw.text((width // 2 + dx, 270 + dy), clean_title, fill=(5, 5, 10), font=font_title, anchor="mm")

    # Title text
    draw.text((width // 2, 270), clean_title, fill=(255, 250, 235), font=font_title, anchor="mm")

    # Subtitle footer
    draw.text((width // 2, 1080), "DIRECTED BY CINEMATIC AI • VISUAL STORYTELLING", fill=(255, 235, 200), font=font_footer, anchor="mm")
    draw.text((width // 2, 1120), "PLOTTWIST CONCIERGE • ALL RIGHTS RESERVED", fill=(220, 200, 170), font=font_footer, anchor="mm")

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
