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

            # Try download using more menu only
            return self.try_download_method(page, "more")

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
                print("Google login successful")
                # Navigate back to NotebookLM after login
                page.goto(settings.notebooklm.navigation_url)
                page.wait_for_timeout(3000)
            else:
                print("Google login failed")

            return login_success

        except Exception as e:
            print(f"Login error: {e}")
            return False

    def get_content(self, content_source: str) -> Optional[str]:
        """Get content from either direct text or file (hiện dùng direct text)."""
        print("📤 Processing content source...")

        if isinstance(content_source, str) and len(content_source.strip()) > 10:
            print(f"Using direct text content ({len(content_source)} chars)")
            return content_source.strip()

        print(f"Invalid content source (too short or not text): {content_source}")
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
                print("Login failed - cannot proceed")
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
                        print(f"Clicked create button with: {selector}")
                        break
                except:
                    continue

            if not create_clicked:
                print("Could not find Create new button")
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
                        print(f"Clicked copied text with: {selector}")
                        break
                except:
                    continue

            if not copied_clicked:
                print("Could not find Copied text chip")
                return False

            page.wait_for_timeout(2000)

            # Paste content
            print(f"Pasting {len(content)} chars...")
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
                        print(f"Clicked insert with: {selector}")
                        break
                except:
                    continue

            if not insert_clicked:
                print("Could not find Insert button")
                return False
            page.wait_for_timeout(1500)
            return True

        except Exception as e:
            print(f"Upload error: {e}")
            self.debug_page_state(page, "upload_error")
            return False

    def generate_audio_overview(self, page) -> bool:
        """Generate audio overview in NotebookLM."""
        try:
            print("🎵 Generating Audio Overview...")
            print("🔍 Looking for Audio Overview button...")

            # Look for Audio Overview button using best practices
            audio_overview_btn = None

            # Method 1: get_by_role for buttons
            try:
                audio_overview_btn = page.get_by_role("button", name="Audio Overview")
                expect(audio_overview_btn).to_be_visible(timeout=5000)
                print("Found Audio Overview with get_by_role")
            except Exception:
                try:
                    audio_overview_btn = page.get_by_role("button", name="Tổng quan âm thanh")
                    expect(audio_overview_btn).to_be_visible(timeout=3000)
                    print("Found Audio Overview with get_by_role (Vietnamese)")
                except Exception as e:
                    print(f"   get_by_role failed: {e}")
                    audio_overview_btn = None

            # Method 2: get_by_text
            if not audio_overview_btn:
                try:
                    audio_overview_btn = page.get_by_text("Audio Overview", exact=False)
                    expect(audio_overview_btn).to_be_visible(timeout=3000)
                    print("Found Audio Overview with get_by_text")
                except Exception:
                    try:
                        audio_overview_btn = page.get_by_text("Tổng quan âm thanh", exact=False)
                        expect(audio_overview_btn).to_be_visible(timeout=3000)
                        print("Found Audio Overview with get_by_text (Vietnamese)")
                    except Exception as e:
                        print(f"   get_by_text failed: {e}")
                        audio_overview_btn = None

            # Method 3: Fallback with locators
            if not audio_overview_btn:
                selectors = [
                    'button:has-text("Audio Overview")',
                    'button:has-text("Tổng quan âm thanh")',
                    'button:has-text("tổng quan")'
                ]
                for selector in selectors:
                    try:
                        audio_overview_btn = page.locator(selector).first
                        expect(audio_overview_btn).to_be_visible(timeout=2000)
                        print(f"Found Audio Overview with: {selector}")
                        break
                    except Exception:
                        continue
                else:
                    audio_overview_btn = None

            if not audio_overview_btn:
                print("Audio Overview button not found")
                return False

            # Click Audio Overview button
            try:
                expect(audio_overview_btn).to_be_enabled(timeout=5000)
                audio_overview_btn.click()
                print("✅ Audio Overview clicked successfully")
            except Exception as e:
                print(f"❌ Failed to click Audio Overview: {e}")
                return False

            # Wait for UI to respond
            print("⏳ Waiting for audio generation to start...")
            page.wait_for_timeout(5000)

            self.debug_page_state(page, "after_audio_overview_click")

            # Check for daily limits using best practices
            limit_messages = [
                "You have reached your daily Audio Overview limits",
                "Bạn đã đạt giới hạn",
                "đã đạt giới hạn",
                "giới hạn hàng ngày"
            ]

            for message in limit_messages:
                try:
                    limit_text = page.get_by_text(message, exact=False)
                    expect(limit_text).to_be_visible(timeout=1000)
                    print("❌ Daily limits reached!")
                    return False
                except Exception:
                    continue

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
            # Auto-reload every 60 seconds ONLY after 5 minutes (300 seconds)
            if elapsed_time >= 300 and elapsed_time - last_reload >= 60:
                if self.perform_reload_and_try_download(page, elapsed_time):
                    return True
                last_reload = elapsed_time

            # Check if generating using better approach
            is_generating = False
            generating_messages = [
                "Generating",
                "Đang tạo",
                "Đang xử lý",
                "Processing"
            ]

            for message in generating_messages:
                try:
                    generating_text = page.get_by_text(message, exact=False)
                    expect(generating_text).to_be_visible(timeout=100)
                    is_generating = True
                    break
                except Exception:
                    continue

            if is_generating:
                print(f"   🔄 Still generating... ({elapsed_time//60}:{elapsed_time%60:02d})")
            else:
                # Check if audio ready using better approach
                audio_found = False

                # Check for duration indicators
                duration_indicators = ["phút", "minute", "min"]
                for indicator in duration_indicators:
                    try:
                        duration_text = page.get_by_text(indicator, exact=False)
                        expect(duration_text).to_be_visible(timeout=100)
                        audio_found = True
                        break
                    except Exception:
                        continue

                # Check for More button as audio ready indicator
                if not audio_found:
                    try:
                        more_btn = page.get_by_text("More", exact=False)
                        expect(more_btn).to_be_visible(timeout=100)
                        audio_found = True
                    except Exception:
                        try:
                            more_btn = page.get_by_text("Thêm", exact=False)
                            expect(more_btn).to_be_visible(timeout=100)
                            audio_found = True
                        except Exception:
                            pass

                # Check for artifact elements
                if not audio_found:
                    try:
                        artifact = page.locator("artifact-library-item").first
                        expect(artifact).to_be_visible(timeout=100)
                        audio_found = True
                    except Exception:
                        pass

                # Try download when audio ready and after minimum wait time
                if audio_found and elapsed_time >= 120:  # Wait at least 2 minutes
                    if self.try_download_method(page, "more"):
                        return True
                    # If download failed, wait longer before next attempt
                    page.wait_for_timeout(30000)  # Wait 30 more seconds
                    elapsed_time += 30

            page.wait_for_timeout(30000)  # 30 sec intervals
            elapsed_time += 30

        print(f"❌ Timeout after {max_wait_minutes} minutes")
        return False

    def find_element_with_expect(self, page, selectors: list, description: str):
        """Find element using Playwright best practices with expect()."""
        for selector in selectors:
            try:
                candidate = page.locator(selector).first
                expect(candidate).to_be_visible(timeout=5000)
                return candidate
            except Exception as e:
                print(f"   Failed selector {selector}: {e}")
                continue
        print(f"❌ Could not find {description}")
        return None

    def try_download_method(self, page, method: str) -> bool:
        """Try More menu download method."""
        page.wait_for_timeout(3000)

        print("📋 Trying More menu...")

        # Use the working XPath that was found
        try:
            more_btn = page.locator("//artifact-library-item//button[contains(@aria-label, 'More')]")
            expect(more_btn).to_be_visible(timeout=10000)
            print("✅ Found More button")
        except Exception as e:
            print(f"❌ Could not find More button: {e}")
            return False

        # Wait for More button to be enabled (audio generation complete)
        print("   Waiting for More button to be enabled...")
        try:
            expect(more_btn).to_be_enabled(timeout=30000)  # Wait up to 30 seconds
            more_btn.click()
            print("✅ More button clicked")
        except Exception as e:
            print(f"❌ More button not enabled within timeout: {e}")
            return False

        page.wait_for_timeout(3000)

        # Find download menu item using best practices
        print("   Looking for Download menu item...")
        dl_btn = None

        # Method 1: get_by_role for menu items
        try:
            dl_btn = page.get_by_role("menuitem", name="Download")
            expect(dl_btn).to_be_visible(timeout=5000)
            print("✅ Found Download with get_by_role")
        except Exception:
            try:
                dl_btn = page.get_by_role("menuitem", name="Tải xuống")
                expect(dl_btn).to_be_visible(timeout=3000)
                print("✅ Found Download with get_by_role (Vietnamese)")
            except Exception as e:
                print(f"   get_by_role for menuitem failed: {e}")
                dl_btn = None

        # Method 2: get_by_text for download text
        if not dl_btn:
            try:
                dl_btn = page.get_by_text("Download", exact=False)
                expect(dl_btn).to_be_visible(timeout=3000)
                print("✅ Found Download with get_by_text")
            except Exception:
                try:
                    dl_btn = page.get_by_text("Tải xuống", exact=False)
                    expect(dl_btn).to_be_visible(timeout=3000)
                    print("✅ Found Download with get_by_text (Vietnamese)")
                except Exception as e:
                    print(f"   get_by_text failed: {e}")
                    dl_btn = None

        # Method 3: Fallback with locators
        if not dl_btn:
            selectors = [
                '[role="menuitem"]:has-text("Download")',
                '[role="menuitem"]:has-text("Tải xuống")'
            ]
            for selector in selectors:
                try:
                    dl_btn = page.locator(selector).first
                    expect(dl_btn).to_be_visible(timeout=2000)
                    print(f"✅ Found Download with: {selector}")
                    break
                except Exception:
                    continue
            else:
                dl_btn = None

        if not dl_btn:
            print("❌ Could not find Download menu item")
            return False

        # Execute download using best practices
        try:
            expect(dl_btn).to_be_enabled(timeout=5000)
            with page.expect_download(timeout=30000) as dl_info:
                dl_btn.click()
                print("✅ Download button clicked")

            download = dl_info.value
            suggested_filename = download.suggested_filename
            print(f"✅ Download started: {suggested_filename}")

            # Wait for download to complete and save to our folder
            download_path = os.path.join(self.download_folder, suggested_filename)
            download.save_as(download_path)
            print(f"✅ Download saved to: {download_path}")

            return True
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False

    def download_audio(self, page) -> bool:
        """Simplified download with dual strategy."""
        page.wait_for_timeout(5000)

        # Only try More menu method
        return self.try_download_method(page, "more")

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
                print(f"Download folder: {self.download_folder}")

                # Ensure both profile and download folders exist
                os.makedirs(self.profile_path, exist_ok=True)
                os.makedirs(self.download_folder, exist_ok=True)

                with sync_playwright() as p:
                    # Use persistent context to keep login state
                    # downloads_path + --download-default-directory ensures correct download location
                    browser = p.chromium.launch_persistent_context(
                        user_data_dir=self.profile_path,
                        headless=settings.notebooklm.headless,
                        downloads_path=self.download_folder,
                        args=[
                            f"--download-default-directory={self.download_folder}",
                            "--disable-blink-features=AutomationControlled",
                            "--disable-infobars",
                            "--disable-extensions",
                            "--no-sandbox",
                            "--disable-dev-shm-usage",
                            "--disable-web-security",
                            "--disable-features=VizDisplayCompositor",
                            "--disable-prompt-on-repost",
                            "--disable-background-downloads",
                            "--disable-backgrounding-occluded-windows"
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
