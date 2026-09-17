import asyncio
import os
import subprocess
from playwright.async_api import async_playwright

ARTIFACT_DIR = "/config/.gemini/antigravity/brain/c0600e8a-de13-4eec-977d-cec988cd5eda"
APP_URL = "https://plot-twist-frontend-356173146024.us-east1.run.app"

HOOK_PROMPT = "I love the philosophical depth of Interstellar but want the gritty noir detective vibe of Blade Runner. Give me a brand new book concept."

async def record():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/google-chrome",
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 960},
            record_video_dir=ARTIFACT_DIR,
            record_video_size={"width": 1280, "height": 960}
        )
        page = await context.new_page()

        print(f"Navigating to {APP_URL}...")
        await page.goto(APP_URL, wait_until="networkidle")
        await asyncio.sleep(2)

        # Hover over info badge to showcase tooltip
        print("Hovering over info badge...")
        try:
            await page.hover(".info-badge")
            await asyncio.sleep(2)
        except Exception as e:
            print("Hover failed:", e)

        # Step 1: The Hook - Typing the hyper-specific prompt
        print(f"Executing Hook Prompt: '{HOOK_PROMPT}'...")
        await page.click("#input")
        await page.type("#input", HOOK_PROMPT, delay=35)
        await asyncio.sleep(1)
        await page.click("button:has-text('Send')")

        # Step 2: The Generation - Wait for Card 1 (Title 'Neon Horizon', Outline, Profiles)
        print("Waiting for Card 1 (Book Concept Title 'Neon Horizon')...")
        try:
            await page.wait_for_function(
                """() => {
                    const agentMsgs = document.querySelectorAll('.msg.agent .bubble');
                    if (agentMsgs.length === 0) return false;
                    const txt = agentMsgs[0].textContent.trim();
                    return txt.includes('Neon Horizon') && (txt.includes('Chapter') || txt.includes('Outline'));
                }""",
                timeout=120000
            )
            print("✅ Card 1 Validated: Title, 3-Chapter Outline, and Character Profiles generated!")
        except Exception as e:
            raise AssertionError(f"❌ Card 1 Validation Failed! Formatted text or outline missing: {e}")

        # Step 3: The Climax - Wait for Card 2 (Concept Poster Art image)
        print("Waiting for Card 2 (Concept Poster Art)...")
        try:
            await page.wait_for_function(
                """() => {
                    const posterImgs = document.querySelectorAll('.poster-card img, .msg.agent img');
                    for (const img of posterImgs) {
                        if (img && img.complete && img.naturalWidth > 0 && img.src.startsWith('http')) {
                            return true;
                        }
                    }
                    return false;
                }""",
                timeout=120000
            )
            print("✅ Card 2 Validated: High-Res Concept Poster Art rendered as a separate card!")
        except Exception as e:
            raise AssertionError(f"❌ Card 2 Validation Failed! Poster image was not generated or loaded: {e}")

        await asyncio.sleep(2)

        # Viewport showcase:
        # First, scroll to Card 1 (Book Concept)
        print("Scrolling to Card 1 (Book Concept Title, Outline, Character Profiles)...")
        await page.evaluate("""() => {
            const agentMsgs = document.querySelectorAll('.msg.agent');
            if (agentMsgs.length > 0) {
                agentMsgs[0].scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }""")
        await asyncio.sleep(6)

        # Second, scroll to Card 2 (Concept Poster Art)
        print("Scrolling to Card 2 (Concept Poster Art)...")
        await page.evaluate("""() => {
            const agentMsgs = document.querySelectorAll('.msg.agent');
            if (agentMsgs.length > 1) {
                agentMsgs[1].scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else if (agentMsgs.length > 0) {
                agentMsgs[0].scrollIntoView({ behavior: 'smooth', block: 'end' });
            }
        }""")
        await asyncio.sleep(10)

        # Save video
        video = page.video
        video_path = await video.path() if video else None
        await context.close()
        await browser.close()

        print(f"Raw video saved at: {video_path}")

        if video_path and os.path.exists(video_path):
            mp4_path = os.path.join(ARTIFACT_DIR, "demo_recording.mp4")
            cmd = f"ffmpeg -y -i {video_path} -c:v libx264 -pix_fmt yuv420p {mp4_path}"
            print("Converting video to MP4...")
            subprocess.run(cmd, shell=True, check=True)
            print(f"MP4 recording successfully saved to: {mp4_path}")

            root_copy = "/config/Desktop/JPMC/plot-twist/demo_recording.mp4"
            subprocess.run(f"cp {mp4_path} {root_copy}", shell=True, check=True)
            print(f"Copied updated video to project root: {root_copy}")

if __name__ == "__main__":
    asyncio.run(record())
