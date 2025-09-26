#!/usr/bin/env python3

import os
import re
import sys
import time
from typing import Optional

from playwright.sync_api import sync_playwright, expect

# Add project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.dirname(current_dir)
app_dir = os.path.dirname(core_dir)
project_dir = os.path.dirname(app_dir)
automation_dir = os.path.join(app_dir, "services", "automation")

sys.path.append(app_dir)
sys.path.append(automation_dir)

# Import settings and login service
from config.settings import settings  # noqa: E402
from services.automation.login_process import perform_google_login  # noqa: E402


def _default_chrome_profile() -> str:
    """Trả về đường dẫn profile mặc định theo OS."""
    home = os.path.expanduser("~")
    if sys.platform.startswith("win"):
        return os.path.join(
            home, "AppData", "Local", "Google", "Chrome", "User Data", "Default"
        )
    else:
        # Linux
        return os.path.join(home, ".config", "google-chrome", "Default")


class NotebookLMAutomation:
    """NotebookLM automation handler for text-to-speech workflow."""

    def __init__(
        self,
        debug_mode: bool = False,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Initialize automation handler."""
        self.debug_mode = debug_mode

        # Get credentials from settings if not provided
        self.email = email or getattr(settings.gmail, "email", None)
        self.password = password or getattr(settings.gmail, "password", None)
        self.auto_login = getattr(settings.notebooklm, "auto_login", False)

        self.profile_path = _default_chrome_profile()

        # Set up static download folder
        self.static_folder = os.path.join(project_dir, "static")
        self.download_folder = os.path.join(self.static_folder, "audio_downloads")

        # Create folders if they don't exist
        os.makedirs(self.download_folder, exist_ok=True)

        # Log credentials status
        print("🔐 Login credentials loaded:")
        print(f"   Email: {self.email[:15]}..." if self.email else "   Email: Not set")
        print(f"   Password: {'*' * 8}" if self.password else "   Password: Not set")
        print(f"   Auto-login: {self.auto_login}")
        print(f"   Debug mode: {self.debug_mode}")


    def perform_reload_and_try_download(self, page, elapsed_time) -> bool:
        """Reload page and try download."""
        try:
            print("🔄 Reloading page...")
            page.reload(wait_until="load", timeout=30000)
            page.wait_for_timeout(2000)

            # Activate page
            try:
                page.locator("body").click(timeout=2000)
            except Exception:
                try:
                    page.keyboard.press("Space")
                except Exception:
                    pass  # Page activation failed, continue anyway

            # Try download
            method = "interactive" if elapsed_time < 600 else "more"
            return self.try_download_method(page, method)

        except Exception as e:
            print(f"❌ Reload error: {e}")
            return False

    def debug_page_state(self, page, step_name: str) -> None:
        """Debug helper."""
        if self.debug_mode:
            try:
                print(f"🔍 Debug {step_name}: {page.url}")
                page.screenshot(path=f"debug_{step_name}.png")
            except Exception as e:
                print(f"⚠️ Debug error: {e}")

    def handle_google_login(self, page) -> bool:
        """Handle Google login if credentials are provided."""
        if not self.auto_login:
            print("ℹ️ Auto login disabled - using existing session")
            return True

        if not self.email or not self.password:
            print("ℹ️ No login credentials found in .env - using existing session")
            return True

        try:
            print(f"🔐 Attempting Google login with {self.email}...")

            # Check if already logged in by looking for account indicators
            current_url = page.url.lower()
            if "accounts.google.com" not in current_url and "signin" not in current_url:
                print("ℹ️ Not on login page - may already be logged in")
                return True

            # Perform login
            login_success = perform_google_login(
                page, self.email, self.password, self.debug_mode
            )

            if login_success:
                print("✅ Google login successful")
                # Navigate back to NotebookLM after login
                page.goto(settings.notebooklm.navigation_url)
                page.wait_for_timeout(3000)
            else:
                print("❌ Google login failed")

            return login_success

        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def get_content(self, content_source: str) -> Optional[str]:
        """Get content from either direct text or file (hiện dùng direct text)."""
        print("📤 Processing content source...")

        if isinstance(content_source, str) and len(content_source.strip()) > 10:
            print(f"✅ Using direct text content ({len(content_source)} chars)")
            return content_source.strip()

        print(f"❌ Invalid content source (too short or not text): {content_source}")
        print("💡 Content must be at least 10 characters long")
        return None

    def upload_content_to_notebooklm(self, page, content: str) -> bool:
        """Upload content to NotebookLM."""
        try:
            # Navigate to NotebookLM
            print("🌐 Navigating to NotebookLM...")
            page.goto(settings.notebooklm.navigation_url)
            page.wait_for_timeout(3000)

            # Handle login if needed
            if not self.handle_google_login(page):
                print("❌ Login failed - cannot proceed")
                return False

            page.wait_for_timeout(2000)

            # Create new
            print("📋 Creating new...")
            # Try both English and Vietnamese
            create_selectors = [
                'text="Create new"',
                'text="Tạo mới"',
                '[aria-label="Create new"]',
                '[aria-label="Tạo mới"]'
            ]

            create_clicked = False
            for selector in create_selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.count() > 0:
                        btn.click()
                        create_clicked = True
                        print(f"✅ Clicked create button with: {selector}")
                        break
                except:
                    continue

            if not create_clicked:
                print("❌ Could not find Create new button")
                return False

            page.wait_for_timeout(2000)

            # Click "Copied text"
            print("📎 Adding copied text...")
            copied_selectors = [
                'text="Copied text"',
                'text="Văn bản đã sao chép"',
                'mat-chip:has-text("Copied text")',
                'mat-chip:has-text("Văn bản")',
                'mat-chip:has-text("văn bản")'
            ]

            copied_clicked = False
            for selector in copied_selectors:
                try:
                    chip = page.locator(selector).first
                    if chip.count() > 0:
                        chip.click()
                        copied_clicked = True
                        print(f"✅ Clicked copied text with: {selector}")
                        break
                except:
                    continue

            if not copied_clicked:
                print("❌ Could not find Copied text chip")
                return False

            page.wait_for_timeout(2000)

            # Paste content
            print(f"📝 Pasting {len(content)} chars...")
            dialog = page.get_by_role("dialog").first
            dialog.locator("textarea").first.fill(content)

            # Insert
            insert_selectors = [
                'text="Insert"',
                'text="Chèn"',
                'text="Thêm"',
                'button:has-text("Insert")',
                'button:has-text("Chèn")',
                'button:has-text("Thêm")'
            ]

            insert_clicked = False
            for selector in insert_selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.count() > 0:
                        btn.click()
                        insert_clicked = True
                        print(f"✅ Clicked insert with: {selector}")
                        break
                except:
                    continue

            if not insert_clicked:
                print("❌ Could not find Insert button")
                return False
            page.wait_for_timeout(1500)
            return True

        except Exception as e:
            print(f"❌ Upload error: {e}")
            self.debug_page_state(page, "upload_error")
            return False

    def generate_audio_overview(self, page) -> bool:
        """Generate audio overview in NotebookLM."""
        try:
            print("🎵 Generating Audio Overview...")
            print("🔍 Looking for Audio Overview button...")

            # Look for Audio Overview button (English and Vietnamese)
            audio_overview_selectors = [
                'text="Audio Overview"',
                'text="Tổng quan âm thanh"',
                'text="Bản tổng quan âm thanh"',
                'button:has-text("Audio Overview")',
                'button:has-text("Tổng quan âm thanh")',
                'button:has-text("tổng quan")',
                'span:has-text("Audio Overview")',
                'span:has-text("Tổng quan")'
            ]

            audio_overview_btn = None
            for selector in audio_overview_selectors:
                try:
                    print(f"   Trying selector: {selector}")
                    btn = page.locator(selector)
                    if btn.count() > 0:
                        # For span selector, get the parent button
                        if selector.startswith('span.'):
                            audio_overview_btn = btn.locator('xpath=ancestor::button').first
                        else:
                            audio_overview_btn = btn.first
                        print(f"✅ Found Audio Overview button with: {selector}")
                        break
                except Exception as e:
                    print(f"   ❌ Failed with {selector}: {e}")

            if audio_overview_btn and audio_overview_btn.count() > 0:
                audio_overview_btn.wait_for(timeout=10000)
                audio_overview_btn.click()
                print("✅ Audio Overview clicked successfully")
            else:
                print("❌ Audio Overview button not found")
                return False

            # Wait for UI to respond
            print("⏳ Waiting for audio generation to start...")
            page.wait_for_timeout(5000)

            self.debug_page_state(page, "after_audio_overview_click")

            # Check for daily limits (English and Vietnamese)
            daily_limit_selectors = [
                "text=You have reached your daily Audio Overview limits",
                "text=Bạn đã đạt giới hạn",
                "text=đã đạt giới hạn",
                "text=giới hạn hàng ngày"
            ]

            for selector in daily_limit_selectors:
                if page.locator(selector).count() > 0:
                    print("❌ Daily limits reached!")
                    return False

            print("✅ Audio generation initiated")
            return True

        except Exception as e:
            print(f"❌ Audio generation error: {e}")
            return False

    def wait_for_audio_completion(self, page, max_wait_minutes: int = 15) -> bool:
        """Simplified wait with reload + download retry."""
        print(f"⏳ Waiting for audio (max {max_wait_minutes} min)...")

        max_wait_time = max_wait_minutes * 60
        elapsed_time = 0
        last_reload = 0
        last_download = 0

        while elapsed_time < max_wait_time:
            # Auto-reload every 30 seconds ONLY after 3 minutes (180 seconds)
            if elapsed_time >= 180 and elapsed_time - last_reload >= 30:
                if self.perform_reload_and_try_download(page, elapsed_time):
                    return True
                last_reload = elapsed_time

            # Check if generating (English and Vietnamese)
            generating_selectors = [
                ":has-text('Generating')",
                ":has-text('Đang tạo')",
                ":has-text('Đang xử lý')",
                ":has-text('Processing')"
            ]

            is_generating = False
            for sel in generating_selectors:
                try:
                    page.locator(sel).wait_for(state="visible", timeout=100)
                    is_generating = True
                    break
                except Exception:
                    continue

            if is_generating:
                print(f"   🔄 Still generating... ({elapsed_time//60}:{elapsed_time%60:02d})")
            else:
                # Check if audio ready (English and Vietnamese)
                audio_selectors = [
                    "button:has-text('Interactive')",
                    "button:has-text('Tương tác')",
                    "div:has-text('Digital Fossil')",
                    "div:has-text('Deep Dive')",
                    "div:has-text('Hoá thạch số')",
                    "div:has-text('Đào sâu')",
                    "div:has-text('phút')",
                    "div:has-text('minute')"
                ]
                audio_found = False
                for sel in audio_selectors:
                    try:
                        page.locator(sel).wait_for(state="visible", timeout=100)
                        audio_found = True
                        break
                    except Exception:
                        continue

                # Try download after 3 minutes (180 seconds) and every 15 seconds after that
                if audio_found and elapsed_time >= 180 and elapsed_time - last_download >= 15:
                    method = "interactive" if elapsed_time < 600 else "more"  # 10 min cutoff
                    if self.try_download_method(page, method):
                        return True
                    last_download = elapsed_time

            page.wait_for_timeout(30000)  # 30 sec intervals
            elapsed_time += 30

        print(f"❌ Timeout after {max_wait_minutes} minutes")
        return False

    def find_element(self, page, selectors: list, description: str):
        """Generic element finder with multiple selectors."""
        for selector in selectors:
            try:
                candidate = page.locator(selector).first
                # Wait for element to be visible (includes attached check)
                candidate.wait_for(state="visible", timeout=10000)
                return candidate
            except Exception as e:
                print(f"   Failed selector {selector}: {e}")
                continue
        print(f"❌ Could not find {description}")
        return None

    def try_download_method(self, page, method: str) -> bool:
        """Try different download methods - Interactive or More menu."""
        page.wait_for_timeout(3000)

        if method == "interactive":
            print("👋 Trying Interactive mode...")
            # Find Interactive button using more robust locators
            interactive_selectors = [
                'button:has-text("Interactive")',
                'button:has-text("Tương tác")',
                'button[aria-label*="Interactive"]',
                'button[aria-label*="Tương tác"]',
                'button:has(mat-icon:text("waving_hand"))'
            ]
            btn = self.find_element(page, interactive_selectors, "Interactive button")
            if not btn:
                return False

            # Click Interactive button with error handling
            try:
                btn.scroll_into_view_if_needed()
                btn.click(timeout=10000)
                print("✅ Interactive button clicked")
            except Exception as e:
                print(f"❌ Failed to click Interactive button: {e}")
                # Try force click as fallback
                try:
                    btn.click(force=True)
                    print("✅ Interactive button force clicked")
                except Exception as e2:
                    print(f"❌ Force click also failed: {e2}")
                    return False

            page.wait_for_timeout(3000)

            # Find download button with better error handling
            download_selectors = [
                'a:has-text("Download")',
                'a:has-text("Tải xuống")',
                'a[aria-label*="Download"]',
                'a[aria-label*="Tải xuống"]',
                'a[href*="googleusercontent.com"][download]',
                'button:has(mat-icon:text("download"))',
                'button:has-text("Download")',
                'button:has-text("Tải xuống")'
            ]
            dl_btn = self.find_element(page, download_selectors, "Download button")
            if not dl_btn:
                return False

        else:  # More menu method
            print("📋 Trying More menu...")
            # Find artifact with better waiting
            try:
                artifact = page.locator('section, div').filter(
                    has_text=re.compile(r"(Deep Dive|Digital Fossil|hosts|Overview)", re.IGNORECASE)
                ).first
                artifact.wait_for(state="visible", timeout=10000)
            except Exception as e:
                print(f"❌ Failed to find artifact: {e}")
                return False

            # Find More button using existing helper
            more_selectors = [
                'button:has-text("More")',
                'button:has-text("Thêm")',
                'button[aria-label*="More"]',
                'button[aria-label*="Thêm"]',
                'button:has(mat-icon:text("more_vert"))'
            ]

            # Use find_element but with artifact scope
            more_btn = None
            for selector in more_selectors:
                try:
                    candidate = artifact.locator(selector).first
                    candidate.wait_for(state="visible", timeout=5000)
                    more_btn = candidate
                    break
                except Exception as e:
                    print(f"   Failed More selector {selector}: {e}")
                    continue

            if not more_btn:
                print("❌ Could not find More button")
                return False

            # Click More button with error handling
            try:
                more_btn.click(timeout=10000)
                print("✅ More button clicked")
            except Exception as e:
                print(f"❌ Failed to click More button: {e}")
                try:
                    more_btn.click(force=True)
                    print("✅ More button force clicked")
                except Exception as e2:
                    print(f"❌ Force click More button failed: {e2}")
                    return False

            page.wait_for_timeout(3000)

            # Find download menu item with better waiting
            menu_selectors = [
                'button[role="menuitem"]:has-text("Download")',
                'button[role="menuitem"]:has-text("Tải xuống")',
                '[role="menuitem"]:has-text("Download")',
                '[role="menuitem"]:has-text("Tải xuống")',
                'text="Download"',
                'text="Tải xuống"'
            ]
            dl_btn = self.find_element(page, menu_selectors, "Download menu item")
            if not dl_btn:
                return False

        # Execute download with better error handling
        try:
            with page.expect_download(timeout=20000) as dl_info:
                try:
                    dl_btn.click(timeout=10000)
                    print("✅ Download button clicked")
                except Exception as e:
                    print(f"❌ Normal click failed: {e}, trying force click")
                    dl_btn.click(force=True)
                    print("✅ Download button force clicked")

            print(f"✅ Download started: {dl_info.value.suggested_filename}")
            return True
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False

    def download_audio(self, page) -> bool:
        """Simplified download with dual strategy."""
        page.wait_for_timeout(5000)

        # Try Interactive first, then More menu
        for method in ["interactive", "more"]:
            if self.try_download_method(page, method):
                return True
        return False

    def check_playwright_installation(self) -> bool:
        """Check if Playwright is properly installed by launching a temp browser."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                browser.close()
            print("Playwright Chromium is available.")
            return True
        except Exception as e:
            print(f"Playwright check failed: {e}")
            return False

    def run_automation(self, content_source: str, max_wait_minutes: int = 10) -> bool:
        """Run complete NotebookLM automation workflow."""
        try:
            print("Starting NotebookLM Text-to-Speech Automation")
            print("=" * 60)

            # Check Playwright installation first
            if not self.check_playwright_installation():
                print("Please install Playwright browsers:")
                print("   pip install playwright")
                print("   playwright install chromium")
                return False

            # Get content
            content = self.get_content(content_source)
            if not content:
                return False

            print(f"Content preview: {content[:100]}...")
            print(f"Using Chrome profile: {self.profile_path}")

            # Show login status
            if self.auto_login and self.email:
                print(f"🔐 Auto-login enabled with: {self.email[:15]}...")
            else:
                print("🔐 Using existing browser session (no auto-login)")

            # Launch browser
            try:
                print("Launching browser...")
                with sync_playwright() as p:
                    # Ensure profile path exists
                    os.makedirs(self.profile_path, exist_ok=True)

                    browser = p.chromium.launch_persistent_context(
                        user_data_dir=self.profile_path,
                        headless=settings.notebooklm.headless,
                        downloads_path=self.download_folder,
                        args=[
                            "--disable-blink-features=AutomationControlled",
                            "--disable-infobars",
                            "--disable-extensions",
                            "--no-sandbox",
                            "--disable-dev-shm-usage",
                            "--disable-web-security",
                            "--disable-features=VizDisplayCompositor",
                        ],
                    )

                    print("Browser launched successfully")
                    page = browser.new_page()

                    try:
                        # Upload content
                        if not self.upload_content_to_notebooklm(page, content):
                            return False

                        # Generate audio
                        if not self.generate_audio_overview(page):
                            return False

                        # Wait for completion and download
                        download_success = self.wait_for_audio_completion(
                            page, max_wait_minutes
                        )

                        # If wait_for_audio_completion didn't succeed, try download one more time
                        if not download_success:
                            print("🔄 Final download attempt...")
                            download_success = self.download_audio(page)

                        # Summary
                        print("\n🎉 Automation Workflow Completed!")
                        print("📊 Summary:")
                        print("   Content source: custom text")
                        print(f"   Content length: {len(content)} chars")
                        print("   Upload: SUCCESS")
                        print("   Audio generation: SUCCESS")
                        print(
                            f"   Download: {'SUCCESS' if download_success else 'FAILED'}"
                        )

                        print("\nBrowser staying open for manual check...")
                        print(f"Audio files saved to: {self.download_folder}")
                        page.wait_for_timeout(3000)

                        return True

                    except Exception as e:
                        print(f"Automation error: {e}")
                        print(f"Error details: {type(e).__name__}: {str(e)}")
                        self.debug_page_state(page, "error_state")
                        return False

                    finally:
                        try:
                            browser.close()
                        except Exception:
                            pass

            except Exception as browser_error:
                print(f"Browser launch error: {browser_error}")
                print(f"Error type: {type(browser_error).__name__}")
                print("Possible solutions:")
                print("   1. Install Playwright browsers: playwright install chromium")
                print("   2. Check Chrome installation")
                print("   3. Run as administrator")
                return False

        except Exception as e:
            print(f"Critical error: {e}")
            print(f"Error type: {type(e).__name__}")
            print("Error location: Content processing or setup")
            return False


def run_notebooklm_automation(
    content_source: str,
    debug_mode: bool = False,
    max_wait_minutes: int = 15,
    email: Optional[str] = None,
    password: Optional[str] = None,
) -> bool:
    """
    Run NotebookLM automation workflow.

    Args:
        content_source: Text content to convert to audio
        debug_mode: Enable debug screenshots and logs (use True to debug login issues)
        max_wait_minutes: Maximum wait time for audio generation (default 15 minutes)
        email: Google account email (optional, for login)
        password: Google account password (optional, for login)

    Returns:
        bool: True if successful, False otherwise
    """
    automation = NotebookLMAutomation(
        debug_mode=debug_mode, email=email, password=password
    )
    return automation.run_automation(content_source, max_wait_minutes)


if __name__ == "__main__":
    print("NotebookLM Automation Manager")
    print("=" * 50)
    print("\nDirect execution not supported")
    print("Use the API endpoint to provide custom text")
