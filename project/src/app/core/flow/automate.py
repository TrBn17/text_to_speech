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

from cache_manager import cache_manager, get_latest_text_generation

class NotebookLMAutomation:
    """NotebookLM automation handler for text-to-speech workflow."""
    
    def __init__(self, debug_mode=False):
        """Initialize automation handler."""
        self.debug_mode = debug_mode
        self.profile_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
        
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

    def get_cached_content(self, content_source="latest"):
        """Retrieve content from cache."""
        print("📤 Retrieving content from cache...")
        
        if content_source == "latest":
            cached_content = get_latest_text_generation()
            if not cached_content:
                print("❌ No cached text generation found!")
                return None
            print(f"✅ Retrieved latest cached content ({len(cached_content)} chars)")
        else:
            cached_data = cache_manager.get_response_by_key(content_source)
            if not cached_data:
                print(f"❌ Cache key not found: {content_source}")
                return None
            cached_content = cached_data.get('response_data')
            print(f"✅ Retrieved cached content by key: {content_source}")

        if not cached_content or len(cached_content.strip()) == 0:
            print("❌ Cached content is empty!")
            return None
            
        return cached_content

    def upload_content_to_notebooklm(self, page, content):
        """Upload content to NotebookLM."""
        try:
            # Navigate to NotebookLM
            print("🌐 Navigating to NotebookLM...")
            page.goto("https://notebooklm.google.com/")
            page.wait_for_timeout(3000)

            # Create new notebook
            print("📋 Creating new notebook...")
            create_btn = page.get_by_text("Create new notebook")
            create_btn.wait_for(timeout=10000)
            create_btn.click()
            page.wait_for_timeout(3000)
            self.debug_page_state(page, "after_create_notebook")

            # Click "Copied text"
            print("📎 Adding copied text...")
            copied_text_btn = page.get_by_text("Copied text")
            copied_text_btn.wait_for(timeout=10000)
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
            print(f"✅ Pasted {len(content)} characters")

            # Click Insert
            print("🔘 Inserting content...")
            insert_btn = page.get_by_text("Insert", exact=True)
            insert_btn.wait_for(timeout=8000)
            insert_btn.click(force=True)
            page.wait_for_timeout(3000)
            self.debug_page_state(page, "after_insert")
            
            print("✅ Content uploaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False

    def generate_audio_overview(self, page):
        """Generate audio overview in NotebookLM."""
        try:
            print("🎵 Generating Audio Overview...")
            
            # Click Audio Overview in sidebar
            audio_overview_btn = page.locator(".mdc-button__label:has-text('Audio Overview')").first
            audio_overview_btn.wait_for(timeout=10000)
            audio_overview_btn.click()
            print("✅ Audio Overview activated")
            
            page.wait_for_timeout(3000)
            self.debug_page_state(page, "after_audio_overview_click")

            # Check for daily limits
            daily_limit_message = page.locator("text='You have reached your daily Audio Overview limits'")
            if daily_limit_message.count() > 0:
                print("⚠️ Daily Audio Overview limits reached!")
                return True  # Still successful for upload

            print("✅ Audio generation started...")
            return True
            
        except Exception as e:
            print(f"⚠️ Audio generation error: {e}")
            # Try alternative method
            try:
                audio_btn = page.get_by_text("Audio Overview").first
                audio_btn.click()
                print("✅ Audio Overview activated (alternative method)")
                return True
            except:
                print("❌ Failed to activate Audio Overview")
                return False

    def wait_for_audio_completion(self, page, max_wait_minutes=10):
        """Wait for audio generation to complete."""
        print("⏳ Waiting for audio generation...")
        print(f"   Maximum wait time: {max_wait_minutes} minutes")
        
        max_wait_time = max_wait_minutes * 60
        check_interval = 10
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            try:
                if page.is_closed():
                    print("⚠️ Page closed, stopping wait")
                    break
                    
                # Look for generated audio files
                audio_files = page.locator(
                    "[class*='digital'], [class*='fossil'], "
                    "div:has-text('Digital Fossil'), div:has-text('hosts'), "
                    "div:has-text('minute')"
                )
                
                if audio_files.count() > 0:
                    print(f"✅ Audio completed after {elapsed_time//60}:{elapsed_time%60:02d}")
                    return True
                    
            except Exception as e:
                print(f"⚠️ Wait error: {e}")
                break
                
            print(f"   Checking... ({elapsed_time//60}:{elapsed_time%60:02d} elapsed)")
            try:
                page.wait_for_timeout(check_interval * 1000)
                elapsed_time += check_interval
            except:
                print("⚠️ Page unavailable")
                break
                
        print("⚠️ Audio generation timeout")
        return False

    def download_audio(self, page):
        """Attempt to download generated audio."""
        try:
            print("🎵 Looking for generated audio...")
            
            # Click on audio file
            audio_selectors = [
                "div:has-text('Digital Fossil'), span:has-text('Digital Fossil')",
                "div:has-text('hosts'), span:has-text('hosts')",
                "[class*='audio'], [class*='overview']"
            ]
            
            for selector in audio_selectors:
                try:
                    audio_file = page.locator(selector).first
                    audio_file.wait_for(timeout=3000)
                    audio_file.click()
                    print("✅ Clicked audio file")
                    break
                except:
                    continue
            
            page.wait_for_timeout(3000)
            
            # Click Interactive button
            print("🤝 Accessing Interactive mode...")
            try:
                interactive_btn = page.locator(
                    "button:has-text('Interactive'), "
                    "[aria-label*='Interactive'], "
                    ".artifact-action-button-extended:has-text('Interactive')"
                )
                interactive_btn.wait_for(timeout=8000)
                interactive_btn.click()
                print("✅ Interactive mode activated")
                page.wait_for_timeout(3000)
            except Exception as e:
                print(f"⚠️ Interactive mode error: {e}")

            # Download audio
            print("⬇️ Downloading audio...")
            try:
                download_btn = page.locator(
                    "a[aria-label*='Download audio overview'], "
                    "button:has-text('Download'), "
                    "[href*='audio'], [download*='audio']"
                )
                download_btn.wait_for(timeout=8000)
                download_btn.click()
                print("✅ Download initiated")
                page.wait_for_timeout(3000)
                return True
            except Exception as e:
                print(f"⚠️ Download error: {e}")
                # Try right-click method
                try:
                    audio_element = page.locator("audio, [class*='audio']").first
                    audio_element.click(button="right")
                    page.wait_for_timeout(1000)
                    page.keyboard.press("s")
                    print("✅ Download attempted via right-click")
                    return True
                except:
                    print("❌ Download failed")
                    return False
                    
        except Exception as e:
            print(f"❌ Audio download error: {e}")
            return False

    def run_automation(self, content_source="latest", max_wait_minutes=10):
        """Run complete NotebookLM automation workflow."""
        try:
            print("🚀 Starting NotebookLM Text-to-Speech Automation")
            print("=" * 60)
            
            # Get cached content
            cached_content = self.get_cached_content(content_source)
            if not cached_content:
                return False
                
            print(f"📝 Content preview: {cached_content[:100]}...")
            print(f"💡 Using Chrome profile: {self.profile_path}")
            
            # Launch browser
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self.profile_path,
                    headless=False,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-infobars",
                        "--disable-extensions",
                        "--no-sandbox",
                        "--disable-dev-shm-usage"
                    ]
                )
                
                page = browser.new_page()
                
                try:
                    # Upload content
                    if not self.upload_content_to_notebooklm(page, cached_content):
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
                    print(f"   ✅ Content source: {content_source}")
                    print(f"   ✅ Content length: {len(cached_content)} chars")
                    print(f"   ✅ Upload: SUCCESS")
                    print(f"   ✅ Audio generation: {'SUCCESS' if audio_ready else 'TIMEOUT'}")
                    print(f"   ✅ Download: {'SUCCESS' if download_success else 'PARTIAL'}")
                    
                    print("\n💡 Browser staying open for manual check...")
                    print("💡 Check Downloads folder for audio file")
                    page.wait_for_timeout(3000)
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ Automation error: {e}")
                    self.debug_page_state(page, "error_state")
                    return False
                    
                finally:
                    browser.close()
                    
        except Exception as e:
            print(f"❌ Critical error: {e}")
            return False

def list_available_cache():
    """List all available cached content."""
    print("📋 Available cached content:")
    responses = cache_manager.list_cached_responses('text_generation')
    
    if not responses:
        print("   No cached content found")
        print("💡 Please ensure cache contains text generation data")
        return []
    
    return responses

def run_notebooklm_automation(content_source="latest", debug_mode=False, max_wait_minutes=10):
    """
    Run NotebookLM automation workflow.
    
    Args:
        content_source: "latest" or specific cache key
        debug_mode: Enable debug screenshots and logs
        max_wait_minutes: Maximum wait time for audio generation
        
    Returns:
        bool: True if successful, False otherwise
    """
    automation = NotebookLMAutomation(debug_mode=debug_mode)
    return automation.run_automation(content_source, max_wait_minutes)

if __name__ == "__main__":
    print("🎯 NotebookLM Automation Manager")
    print("=" * 50)
    
    # List available cache
    available = list_available_cache()
    
    if available:
        print("\n📤 Running automation with latest cached content...")
        success = run_notebooklm_automation("latest", debug_mode=True)
        print(f"\n🏁 Result: {'SUCCESS' if success else 'FAILED'}")
    else:
        print("\n❌ No cached content available")
        print("💡 Please ensure cache contains text generation data")
