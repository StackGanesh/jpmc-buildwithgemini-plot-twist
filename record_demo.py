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

        # Step 2: The Generation & Climax - Wait for full agent completion
        print("Waiting up to 120s for Agent Generation (Title 'Neon Horizon', Outline, Poster Image)...")
        await page.wait_for_function(
            """() => {
                const b = document.querySelectorAll('.msg.agent .bubble')[0];
                if (!b) return false;
                const txt = b.textContent.trim();
                return txt !== '…' && txt !== '' && (txt.includes('Neon Horizon') || txt.includes('Chapter'));
            }""",
            timeout=120000
        )
        print("✅ Generation in progress: Neon Horizon streaming...")

        # Step 3: Wait for Concept Poster image to render
        print("Waiting for Concept Poster image...")
        try:
            await page.wait_for_function(
                """() => {
                    const img = document.querySelector('.msg.agent img');
                    return img && img.complete && img.naturalWidth > 0;
                }""",
                timeout=90000
            )
            print("✅ Climax Validated: Custom Concept Poster rendered on screen!")
        except Exception as e:
            print("Poster render note:", e)

        await asyncio.sleep(3)

        # Position viewport so that the top of the message bubble (Book Title "Neon Horizon") AND poster card are fully visible
        print("Positioning viewport to ensure book title and poster card are both visible...")
        await page.evaluate("""() => {
            const agentMsg = document.querySelector('.msg.agent');
            if (agentMsg) {
                agentMsg.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }""")
        
        # Hold viewport for 15 full seconds in video
        print("Holding view on complete book concept & poster card for 15s...")
        await asyncio.sleep(15)

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
