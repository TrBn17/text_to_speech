#!/usr/bin/env python3
"""
Automation Flow Manager for Text-to-Speech System
"""

import os
import sys
from playwright.sync_api import sync_playwright

# Add project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.dirname(current_dir)
app_dir = os.path.dirname(core_dir)
project_dir = os.path.dirname(app_dir)
automation_dir = os.path.join(app_dir, "services", "automation")

sys.path.append(app_dir)
sys.path.append(automation_dir)

# Import settings and login service
from config.settings import settings
from services.automation.login_process import perform_google_login

class NotebookLMAutomation:
    """NotebookLM automation handler for text-to-speech workflow."""
    
    def __init__(self, debug_mode=False, email=None, password=None):
        """Initialize automation handler."""
        self.debug_mode = debug_mode

        # Get credentials from settings if not provided
        self.email = email or settings.gmail.email
        self.password = password or settings.gmail.password
        self.auto_login = settings.notebooklm.auto_login

        self.profile_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default")

        # Set up static download folder
        self.static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "static")
        self.download_folder = os.path.join(self.static_folder, "audio_downloads")

        # Create folders if they don't exist
        os.makedirs(self.download_folder, exist_ok=True)

        # Log credentials status
        print(f"🔐 Login credentials loaded:")
        print(f"   Email: {self.email[:15]}..." if self.email else "   Email: Not set")
        print(f"   Password: {'*' * 8}" if self.password else "   Password: Not set")
        print(f"   Auto-login: {self.auto_login}")
        print(f"   Debug mode: {self.debug_mode}")
        
    def debug_page_state(self, page, step_name):
        """Debug helper to print current page state."""
        if not self.debug_mode:
            return
            
        try:
            print(f"\n🔍 Debug info for {step_name}:")
            print(f"   Current URL: {page.url}")
            print(f"   Page title: {page.title()}")
            
            # Count modals and dialogs
            modal_selector = 'div[role="dialog"], .mat-dialog-container'
            modal_count = page.locator(modal_selector).count()
            print(f"   Modals: {modal_count}")
            
            print(f"   Textareas: {page.locator('textarea').count()}")
            print(f"   Buttons: {page.locator('button').count()}")
            
            if self.debug_mode:
                screenshot_path = f"debug_{step_name}.png"
                page.screenshot(path=screenshot_path)
                print(f"   Screenshot: {screenshot_path}")
                
        except Exception as e:
            print(f"⚠️ Debug error: {e}")

    def handle_google_login(self, page):
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
            login_success = perform_google_login(page, self.email, self.password, self.debug_mode)

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

    def get_content(self, content_source):
        """Get content from either direct text or file."""
        print("📤 Processing content source...")
        
        # If content_source is already text (string with length > 10), use it directly
        if isinstance(content_source, str) and len(content_source.strip()) > 10:
            print(f"✅ Using direct text content ({len(content_source)} chars)")
            return content_source.strip()
        
        # Otherwise treat as file path or other source
        print(f"❌ Invalid content source (too short or not text): {content_source}")
        print(f"💡 Content must be at least 10 characters long")
        return None

    def upload_content_to_notebooklm(self, page, content):
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

            # Wait a bit more after login
            page.wait_for_timeout(2000)

            # Create new notebook
            print("📋 Creating new notebook...")
            create_btn = page.get_by_text("Create new notebook")
            create_btn.wait_for(timeout=settings.notebooklm.timeout)
            create_btn.click()
            page.wait_for_timeout(3000)
            self.debug_page_state(page, "after_create_notebook")

            # Click "Copied text"
            print("📎 Adding copied text...")
            copied_text_btn = page.get_by_text("Copied text")
            copied_text_btn.wait_for(timeout=settings.notebooklm.timeout)
            copied_text_btn.click()
            page.wait_for_timeout(3000)
            self.debug_page_state(page, "after_copied_text_click")

            # Find and fill textarea
            print("📝 Pasting content...")
            paste_area = None
            
            # Try multiple methods to find textarea
            selectors = [
                "textarea[placeholder*='Paste text here'], textarea[placeholder*='paste text']",
                "textarea:nth-child(2)",
                "textarea:visible:last-child"
            ]
            
            for selector in selectors:
                try:
                    paste_area = page.locator(selector)
                    paste_area.wait_for(timeout=3000)
                    break
                except:
                    continue
                    
            if not paste_area:
                raise Exception("Could not find paste textarea")

            # Paste content
            paste_area.click(force=True)
            page.wait_for_timeout(1000)
            paste_area.fill(content)
            page.wait_for_timeout(1500)
            print(f"Pasted {len(content)} characters")

            # Click Insert
            print("🔘 Inserting content...")
            insert_btn = page.get_by_text("Insert", exact=True)
            insert_btn.wait_for(timeout=settings.notebooklm.timeout)
            insert_btn.click(force=True)
            page.wait_for_timeout(3000)
            self.debug_page_state(page, "after_insert")
            
            print("Content uploaded successfully!")
            return True
            
        except Exception as e:
            print(f"Upload error: {e}")
            return False

    def generate_audio_overview(self, page):
        """Generate audio overview in NotebookLM."""
        try:
            print("🎵 Generating Audio Overview...")

            # Simple approach - just try to find and click Audio Overview button ONCE
            print("🔍 Looking for Audio Overview button...")

            # Most reliable selector from the UI
            audio_overview_btn = page.locator("button:has-text('Audio Overview')")

            if audio_overview_btn.count() > 0:
                print("✅ Found Audio Overview button")
                audio_overview_btn.first.wait_for(timeout=10000)
                audio_overview_btn.first.click()
                print("✅ Audio Overview clicked successfully")
            else:
                print("❌ Audio Overview button not found")
                return False

            # Wait for UI to respond
            print("⏳ Waiting for audio generation to start...")
            page.wait_for_timeout(5000)

            self.debug_page_state(page, "after_audio_overview_click")

            # Check for daily limits
            daily_limit_message = page.locator("text=You have reached your daily Audio Overview limits")
            if daily_limit_message.count() > 0:
                print("❌ Daily Audio Overview limits reached!")
                return False

            print("✅ Audio generation initiated")
            return True

        except Exception as e:
            print(f"❌ Audio generation error: {e}")
            return False

    def wait_for_audio_completion(self, page, max_wait_minutes=15):
        """Wait for audio generation to complete."""
        print("⏳ Waiting for audio generation...")
        print(f"   Maximum wait time: {max_wait_minutes} minutes")
        print("   Audio typically takes 5-15 minutes to generate")

        # MANDATORY 3-minute minimum wait before checking completion
        min_wait_time = 3 * 60  # 3 minutes
        print(f"   🕒 Minimum wait time: 3 minutes (audio needs time to start)")

        max_wait_time = max_wait_minutes * 60
        check_interval = 30  # Check every 30 seconds instead of 10
        elapsed_time = 0

        # Phase 1: Minimum wait (3 minutes) - Don't check for completion yet
        print("📝 Phase 1: Initial wait (3 minutes minimum)...")
        last_reload_time = 0
        reload_interval = 4 * 60  # 4 minutes
        print(f"⏰ Auto-reload will trigger every {reload_interval//60} minutes to prevent lag")

        while elapsed_time < min_wait_time:
            print(f"   ⏰ Initial wait... ({elapsed_time//60}:{elapsed_time%60:02d}/3:00) - Not checking completion yet")

            # Auto-reload every 4 minutes to prevent lag
            time_since_last_reload = elapsed_time - last_reload_time
            if time_since_last_reload >= reload_interval and elapsed_time > 0:
                print(f"🔄 AUTO-RELOAD TRIGGERED at {elapsed_time//60}:{elapsed_time%60:02d}")
                print(f"   Time since last reload: {time_since_last_reload//60}:{time_since_last_reload%60:02d}")
                print(f"   Reload interval: {reload_interval//60}:{reload_interval%60:02d}")

                try:
                    current_url = page.url
                    print(f"   📍 Current URL: {current_url}")

                    # Try multiple reload methods
                    print("   🔄 Method 1: Ctrl+R...")
                    page.keyboard.press("Control+r")

                    print("   ⏳ Waiting 3 seconds for initial reload response...")
                    page.wait_for_timeout(3000)

                    # Alternative method if first doesn't work
                    print("   🔄 Method 2: page.reload() as backup...")
                    try:
                        page.reload(wait_until="load", timeout=10000)
                        print("   ✅ page.reload() successful")
                    except Exception as reload_error:
                        print(f"   ⚠️ page.reload() failed: {reload_error}")

                    print("   ⏳ Final wait 5 seconds...")
                    page.wait_for_timeout(5000)

                    new_url = page.url
                    print(f"   📍 URL after reload: {new_url}")

                    last_reload_time = elapsed_time
                    print(f"✅ AUTO-RELOAD COMPLETED at {elapsed_time//60}:{elapsed_time%60:02d}")
                    print(f"   Next reload scheduled for: {(elapsed_time + reload_interval)//60}:{(elapsed_time + reload_interval)%60:02d}")

                except Exception as e:
                    print(f"❌ RELOAD ERROR: {e}")
                    print(f"   Error type: {type(e).__name__}")
                    # Still update last_reload_time to prevent spam retries
                    last_reload_time = elapsed_time
                    print("   ⚠️ Will continue without reload, next attempt in 4 minutes")

            try:
                page.wait_for_timeout(check_interval * 1000)
                elapsed_time += check_interval
            except:
                print("❌ Page unavailable during initial wait")
                return False

        print("✅ Minimum 3-minute wait completed. Now checking for audio completion...")

        # Phase 2: Active checking for completion
        while elapsed_time < max_wait_time:
            try:
                if page.is_closed():
                    print("❌ Page closed, stopping wait")
                    break

                print(f"📝 Phase 2: Checking for completion... ({elapsed_time//60}:{elapsed_time%60:02d}/{max_wait_minutes}:00)")

                # Auto-reload every 4 minutes to prevent lag
                time_since_last_reload = elapsed_time - last_reload_time
                if time_since_last_reload >= reload_interval:
                    print(f"🔄 AUTO-RELOAD TRIGGERED at {elapsed_time//60}:{elapsed_time%60:02d}")
                    print(f"   Time since last reload: {time_since_last_reload//60}:{time_since_last_reload%60:02d}")

                    try:
                        current_url = page.url
                        print(f"   📍 Current URL: {current_url}")

                        # Try multiple reload methods
                        print("   🔄 Method 1: Ctrl+R...")
                        page.keyboard.press("Control+r")

                        print("   ⏳ Waiting 3 seconds for initial reload response...")
                        page.wait_for_timeout(3000)

                        # Alternative method if first doesn't work
                        print("   🔄 Method 2: page.reload() as backup...")
                        try:
                            page.reload(wait_until="load", timeout=10000)
                            print("   ✅ page.reload() successful")
                        except Exception as reload_error:
                            print(f"   ⚠️ page.reload() failed: {reload_error}")

                        print("   ⏳ Final wait 5 seconds...")
                        page.wait_for_timeout(5000)

                        new_url = page.url
                        print(f"   📍 URL after reload: {new_url}")

                        last_reload_time = elapsed_time
                        print(f"✅ AUTO-RELOAD COMPLETED at {elapsed_time//60}:{elapsed_time%60:02d}")
                        print(f"   Next reload scheduled for: {(elapsed_time + reload_interval)//60}:{(elapsed_time + reload_interval)%60:02d}")

                    except Exception as e:
                        print(f"❌ RELOAD ERROR: {e}")
                        print(f"   Error type: {type(e).__name__}")
                        last_reload_time = elapsed_time
                        print("   ⚠️ Will continue without reload, next attempt in 4 minutes")

                # Check for generation in progress indicators first
                generating_text = page.locator(":has-text('Generating')").count() > 0
                come_back_text = page.locator(":has-text('Come back')").count() > 0
                loading_elements = page.locator("[class*='loading']").count() > 0

                generation_in_progress = generating_text or come_back_text or loading_elements

                if generation_in_progress:
                    print(f"   🔄 Still generating... ({elapsed_time//60}:{elapsed_time%60:02d} elapsed)")
                else:
                    # Look for completed audio files with more specific selectors
                    # Only check these AFTER minimum 3 minutes have passed
                    audio_completion_indicators = [
                        "button:has-text('Interactive')",  # Most reliable indicator
                        "div:has-text('Digital Fossil')",
                        "div:has-text('Deep Dive')",
                        "div:has-text('Overview')",
                        "[class*='audio-player']",
                        "[class*='generated']",
                        "div:has-text('minute')",
                        "div:has-text('hosts')"
                    ]

                    for selector in audio_completion_indicators:
                        try:
                            elements = page.locator(selector)
                            count = elements.count()
                            if count > 0:
                                # Double-check by waiting a bit more to ensure it's really there
                                page.wait_for_timeout(2000)
                                recheck_count = page.locator(selector).count()

                                if recheck_count > 0:
                                    print(f"✅ Audio completed after {elapsed_time//60}:{elapsed_time%60:02d}")
                                    print(f"   Found reliable audio indicator: {selector} (count: {recheck_count})")
                                    return True
                        except Exception as e:
                            print(f"   ⚠️ Error checking {selector}: {e}")
                            continue

                    # Final check: If no "Generating" text and we're past minimum time
                    generation_indicators = page.locator(":has-text('Generating')").count()
                    if generation_indicators == 0 and elapsed_time >= min_wait_time:
                        print(f"⚠️ Generation indicator disappeared after {elapsed_time//60}:{elapsed_time%60:02d}")
                        print("   Assuming completion - but may need manual verification")
                        # Don't return True immediately, wait a bit more to be sure

            except Exception as e:
                print(f"⚠️ Wait error: {e}")
                # Don't break on errors, continue waiting
                pass

            print(f"   ⏰ Still waiting... ({elapsed_time//60}:{elapsed_time%60:02d}/{max_wait_minutes}:00)")
            try:
                page.wait_for_timeout(check_interval * 1000)
                elapsed_time += check_interval
            except:
                print("❌ Page unavailable")
                break

        print(f"❌ Audio generation timeout after {max_wait_minutes} minutes")
        return False

    def download_audio(self, page):
        """Attempt to download generated audio using new menu approach."""
        try:
            print("🎵 Looking for generated audio to download...")

            # Wait a bit to ensure audio is fully loaded
            print("⏳ Ensuring audio is fully loaded...")
            page.wait_for_timeout(5000)

            # Click on audio file first
            audio_found = False
            audio_selectors = [
                "div:has-text('Digital Fossil')",
                "div:has-text('Deep Dive')",
                "div:has-text('hosts')",
                "[class*='audio']"
            ]

            print("🔍 Looking for audio file to select...")
            for selector in audio_selectors:
                try:
                    print(f"   Trying audio selector: {selector}")
                    audio_file = page.locator(selector).first
                    count = audio_file.count()
                    print(f"   Found {count} elements")

                    if count > 0:
                        audio_file.wait_for(timeout=5000)
                        if audio_file.is_visible():
                            audio_file.click()
                            print(f"✅ Selected audio file with: {selector}")
                            audio_found = True
                            break
                        else:
                            print(f"   Element not visible: {selector}")
                except Exception as e:
                    print(f"   ❌ Failed with {selector}: {e}")
                    continue

            if not audio_found:
                print("⚠️ No audio file found to select")

            page.wait_for_timeout(2000)

            # Click the more_vert (3-dot menu) button using specific attributes from source
            print("📋 Looking for more_vert menu button...")
            try:
                more_vert_selectors = [
                    'button[type="button"][data-mat-icon-type="font"] mat-icon:has-text("more_vert")',
                    'button.mat-icon-button[aria-label="More"] mat-icon:has-text("more_vert")',
                    'button[mattooltip="More"] mat-icon.google-symbols:has-text("more_vert")',
                    'mat-icon.mat-icon-no-color.google-symbols:has-text("more_vert")',
                    'mat-icon[data-mat-icon-type="font"]:has-text("more_vert")'
                ]

                menu_clicked = False
                for selector in more_vert_selectors:
                    try:
                        print(f"   Trying more_vert selector: {selector}")
                        more_btn = page.locator(selector)
                        count = more_btn.count()
                        print(f"   Found {count} more_vert buttons")

                        if count > 0:
                            more_btn.first.wait_for(timeout=8000)
                            if more_btn.first.is_visible():
                                more_btn.first.click()
                                print(f"✅ Clicked more_vert menu with: {selector}")
                                menu_clicked = True
                                break
                    except Exception as e:
                        print(f"   ❌ Failed more_vert with {selector}: {e}")
                        continue

                if not menu_clicked:
                    print("❌ Could not find or click more_vert menu button")
                    return False

                # Wait for menu to appear
                page.wait_for_timeout(2000)

            except Exception as e:
                print(f"❌ Error clicking more_vert menu: {e}")
                return False

            # Click Download from the menu using HTML source structure
            print("⬇️ Clicking Download from menu...")
            try:
                download_selectors = [
                    'button.mat-mdc-menu-item[role="menuitem"] span.mat-mdc-menu-item-text:has-text("Download")',
                    'button[role="menuitem"][tabindex="0"] span:has-text("Download")',
                    '.mat-mdc-menu-item.mat-focus-indicator span.mat-mdc-menu-item-text:has-text("Download")',
                    'button.mat-mdc-menu-item span:has-text("Download")',
                    'span.mat-mdc-menu-item-text:has-text("Download")'
                ]

                download_clicked = False
                for selector in download_selectors:
                    try:
                        print(f"   Trying download selector: {selector}")
                        download_btn = page.locator(selector)
                        count = download_btn.count()
                        print(f"   Found {count} Download menu items")

                        if count > 0:
                            download_btn.first.wait_for(timeout=8000)
                            if download_btn.first.is_visible():
                                download_btn.first.click()
                                print(f"✅ Clicked Download menu item with: {selector}")
                                download_clicked = True
                                break
                    except Exception as e:
                        print(f"   ❌ Failed Download with {selector}: {e}")
                        continue

                if download_clicked:
                    print("✅ Download initiated successfully")
                    page.wait_for_timeout(3000)
                    return True
                else:
                    print("❌ Could not find or click Download menu item")
                    return False

            except Exception as e:
                print(f"❌ Download error: {e}")
                return False
                    
        except Exception as e:
            print(f"Audio download error: {e}")
            return False

    def check_playwright_installation(self):
        """Check if Playwright is properly installed"""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                # Test if chromium is available
                browser_path = p.chromium.executable_path
                if browser_path and os.path.exists(browser_path):
                    print(f"Playwright Chromium found: {browser_path}")
                    return True
                else:
                    print("Playwright Chromium not found")
                    return False
        except Exception as e:
            print(f"Playwright check failed: {e}")
            return False

    def run_automation(self, content_source, max_wait_minutes=10):
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
                    # Check if Chrome profile exists
                    if not os.path.exists(self.profile_path):
                        print(f"Chrome profile not found: {self.profile_path}")
                        print("Creating default profile path...")
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
                            "--disable-features=VizDisplayCompositor"
                        ]
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
                        
                        # Wait for completion
                        audio_ready = self.wait_for_audio_completion(page, max_wait_minutes)
                        
                        # Download audio
                        download_success = self.download_audio(page)
                        
                        # Summary
                        print("\n🎉 Automation Workflow Completed!")
                        print("📊 Summary:")
                        print(f"   Content source: custom text")
                        print(f"   Content length: {len(content)} chars")
                        print(f"   Upload: SUCCESS")
                        print(f"   Audio generation: {'SUCCESS' if audio_ready else 'TIMEOUT'}")
                        print(f"   Download: {'SUCCESS' if download_success else 'PARTIAL'}")
                        
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
                        except:
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
            print(f"Error location: Content processing or setup")
            return False
            return False

def run_notebooklm_automation(content_source, debug_mode=False, max_wait_minutes=15, email=None, password=None):
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
    automation = NotebookLMAutomation(debug_mode=debug_mode, email=email, password=password)
    return automation.run_automation(content_source, max_wait_minutes)

if __name__ == "__main__":
    print("NotebookLM Automation Manager")
    print("=" * 50)
    
    print("\nDirect execution not supported")
    print("Use the API endpoint to provide custom text")
