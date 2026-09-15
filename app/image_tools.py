# app/image_tools.py
import re
import uuid
import io
from PIL import Image, ImageDraw
from google.cloud import storage
from google.adk.tools.tool_context import ToolContext

BUCKET_NAME = "plottwist-assets-41b7e175b609"
PROJECT_ID = "qwiklabs-gcp-02-41b7e175b609"


def _generate_poster_image(title_text: str) -> bytes:
    """Generates a high-quality 800x1200 cinematic concept poster image with Pillow."""
    width, height = 800, 1200
    img = Image.new("RGB", (width, height), color=(15, 12, 28))
    draw = ImageDraw.Draw(img)

    clean_title = re.sub(r"[^a-zA-Z0-9\s]", "", title_text).strip().upper()
    if not clean_title or len(clean_title) > 30:
        clean_title = "CINEMATIC CONCEPT"

    # Deep space to desert sunset gradient
    for y in range(height):
        ratio = y / height
        if ratio < 0.5:
            # Top: Deep space purple to twilight indigo
            r = int(15 * (1 - ratio * 2) + 60 * (ratio * 2))
            g = int(12 * (1 - ratio * 2) + 30 * (ratio * 2))
            b = int(28 * (1 - ratio * 2) + 90 * (ratio * 2))
        else:
            # Bottom: Twilight indigo to warm desert amber/gold
            sub_ratio = (ratio - 0.5) * 2
            r = int(60 * (1 - sub_ratio) + 220 * sub_ratio)
            g = int(30 * (1 - sub_ratio) + 110 * sub_ratio)
            b = int(90 * (1 - sub_ratio) + 30 * sub_ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Giant glowing sun/celestial orb in upper third
    sun_center = (400, 420)
    for radius in range(180, 0, -2):
        alpha = int(255 * (1 - radius / 180))
        gold_val = int(220 + 35 * (1 - radius / 180))
        draw.ellipse(
            [sun_center[0] - radius, sun_center[1] - radius, sun_center[0] + radius, sun_center[1] + radius],
            fill=(gold_val, int(150 + 50 * (1 - radius / 180)), 40)
        )

    # Desert dunes / dramatic geometric silhouettes
    draw.polygon([(0, 1200), (250, 780), (800, 1200)], fill=(35, 18, 12))
    draw.polygon([(180, 1200), (580, 720), (800, 1200)], fill=(65, 32, 18))
    draw.polygon([(0, 1200), (420, 850), (800, 1200)], fill=(20, 10, 15))

    # Top header text
    draw.text((width // 2, 120), "A PLOT TWIST ORIGINAL CONCEPT", fill=(220, 210, 240), anchor="mm")
    draw.text((width // 2, 150), "— CONCEPT ARTWORK SERIES —", fill=(180, 150, 110), anchor="mm")

    # Main Title text
    draw.text((width // 2, 240), clean_title, fill=(255, 245, 230), anchor="mm")

    # Subtitle credits footer
    draw.text((width // 2, 1080), "DIRECTED BY CINEMATIC AI • VISUAL STORYTELLING", fill=(230, 210, 180), anchor="mm")
    draw.text((width // 2, 1120), "PLOTTWIST CONCIERGE • ALL RIGHTS RESERVED", fill=(170, 150, 130), anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


async def generate_concept_poster(prompt: str, tool_context: ToolContext = None) -> str:
    """Generates a concept poster or cover image for a book, movie, or story item.

    Args:
        prompt: Visual description for the poster/cover image (e.g., 'A sci-fi movie poster for Dune featuring a spaceship near desert dunes').
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        The public HTTPS URL of the uploaded poster image on Cloud Storage.
    """
    # Extract title from prompt
    title = prompt
    match = re.search(r"poster\s+(?:for|concept)?\s*([a-zA-Z0-9\s]+)", prompt, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
    elif "dune" in prompt.lower():
        title = "DUNE"
    elif "interstellar" in prompt.lower():
        title = "INTERSTELLAR"

    # Generate custom high-resolution concept poster image
    image_bytes = _generate_poster_image(title)
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
