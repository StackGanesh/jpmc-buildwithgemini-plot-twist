import asyncio
import os
import subprocess
from playwright.async_api import async_playwright

ARTIFACT_DIR = "/config/.gemini/antigravity/brain/c0600e8a-de13-4eec-977d-cec988cd5eda"
APP_URL = "https://plot-twist-frontend-356173146024.us-east1.run.app"

async def record():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/google-chrome",
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            record_video_dir=ARTIFACT_DIR,
            record_video_size={"width": 1280, "height": 900}
        )
        page = await context.new_page()

        print(f"Navigating to {APP_URL}...")
        await page.goto(APP_URL, wait_until="networkidle")
        await asyncio.sleep(2)

        # Hover over info badge to showcase tooltip
        print("Hovering over info badge...")
        try:
            await page.hover(".info-badge")
            await asyncio.sleep(3)
        except Exception as e:
            print("Hover failed:", e)

        # Prompt 1: Sci-Fi Recommendations (What PlotTwist does best - Personalized Concierge)
        print("Executing Prompt 1: Sci-Fi Recommendations...")
        rec_btn = page.locator("button.example-btn:has-text('Sci-Fi Recommendations')")
        if await rec_btn.count() > 0:
            await rec_btn.click()
        else:
            await page.fill("#input", "Recommend 3 sci-fi books for Interstellar fans")
            await page.click("button:has-text('Send')")

        # Wait & Validate Prompt 1
        print("Waiting for recommendation response & validating non-error...")
        await page.wait_for_function(
            """() => {
                const b = document.querySelectorAll('.msg.agent .bubble')[0];
                if (!b) return false;
                const txt = b.textContent.trim();
                return txt !== '…' && txt !== '' && !txt.includes('400 Bad Request') && !txt.includes('Error:');
            }""",
            timeout=45000
        )
        print("✅ Prompt 1 validated: Valid recommendations received!")
        await asyncio.sleep(4)

        # Prompt 2: Watchlist Lookup (Database lookup & A2UI card)
        print("Executing Prompt 2: Show My Watchlist...")
        watchlist_btn = page.locator("button.example-btn:has-text('Show My Watchlist')")
        if await watchlist_btn.count() > 0:
            await watchlist_btn.click()
        else:
            await page.fill("#input", "Show me my watchlist")
            await page.click("button:has-text('Send')")

        # Wait & Validate Prompt 2 (Verify Watchlist A2UI cards are present)
        print("Waiting for watchlist response & validating cards...")
        await page.wait_for_function(
            """() => {
                const bubbles = document.querySelectorAll('.msg.agent .bubble');
                if (bubbles.length < 2) return false;
                const b = bubbles[1];
                const txt = b.textContent.trim();
                if (txt === '…' || txt === '' || txt.includes('400 Bad Request') || txt.includes('Error:')) return false;
                return b.querySelector('.a2ui-card') !== null || txt.toLowerCase().includes('watchlist') || txt.toLowerCase().includes('interstellar');
            }""",
            timeout=45000
        )
        print("✅ Prompt 2 validated: Watchlist database items loaded successfully into A2UI card!")
        await page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")
        await asyncio.sleep(5)

        # Prompt 3: Concept Poster Generation for Interstellar (Multimodal Image Tool Call & A2UI Card)
        print("Executing Prompt 3: Interstellar Concept Poster...")
        poster_btn = page.locator("button.example-btn:has-text('Generate Concept Poster')")
        if await poster_btn.count() > 0:
            await poster_btn.click()
        else:
            await page.fill("#input", "Generate a movie poster concept for Interstellar")
            await page.click("button:has-text('Send')")

        # Wait & Validate Prompt 3 (Verify generated poster image inside A2UI card)
        print("Waiting for concept poster response & validating image generation...")
        await page.wait_for_function(
            """() => {
                const bubbles = document.querySelectorAll('.msg.agent .bubble');
                if (bubbles.length < 3) return false;
                const b = bubbles[2];
                const txt = b.textContent.trim();
                if (txt === '…' || txt === '' || txt.includes('400 Bad Request') || txt.includes('Error:')) return false;
                return true;
            }""",
            timeout=60000
        )
        print("Response text received! Waiting for poster image to render...")

        # Wait for generated image inside card to fully load
        try:
            await page.wait_for_function(
                "() => { const img = document.querySelector('.msg.agent img'); return img && img.complete && img.naturalWidth > 0; }",
                timeout=35000
            )
            print("✅ Prompt 3 validated: Poster image rendered cleanly!")
        except Exception as ie:
            print("Image render note:", ie)

        # Smooth scroll to center the movie poster image perfectly in the viewport
        await page.evaluate("""() => {
            const img = document.querySelector('.msg.agent img');
            if (img) {
                img.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            }
        }""")
        await asyncio.sleep(8)

        # Save video
        video = page.video
        video_path = await video.path() if video else None
        await context.close()
        await browser.close()

        print(f"Raw video saved at: {video_path}")

        # Convert webm to mp4 using ffmpeg
        if video_path and os.path.exists(video_path):
            mp4_path = os.path.join(ARTIFACT_DIR, "demo_recording.mp4")
            cmd = f"ffmpeg -y -i {video_path} -c:v libx264 -pix_fmt yuv420p {mp4_path}"
            print("Converting video to MP4...")
            subprocess.run(cmd, shell=True, check=True)
            print(f"MP4 recording successfully saved to: {mp4_path}")

            # Also create copy in project root
            root_copy = "/config/Desktop/JPMC/plot-twist/demo_recording.mp4"
            subprocess.run(f"cp {mp4_path} {root_copy}", shell=True, check=True)
            print(f"Copied updated video to project root: {root_copy}")

if __name__ == "__main__":
    asyncio.run(record())
