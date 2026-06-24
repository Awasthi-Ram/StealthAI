import sys
import os
import traceback

def test():
    try:
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "0")
        from playwright.sync_api import sync_playwright
        print("Playwright imported successfully")
        with sync_playwright() as p:
            print("sync_playwright started")
            browser = p.chromium.launch_persistent_context(
                user_data_dir="./test_gemini_data",
                headless=True,
                channel="chrome",
                args=['--disable-blink-features=AutomationControlled']
            )
            print("Browser launched")
            browser.close()
    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()

if __name__ == "__main__":
    test()
