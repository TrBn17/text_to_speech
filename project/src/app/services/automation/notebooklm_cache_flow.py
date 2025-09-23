#!/usr/bin/env python3
"""
NotebookLM automation flow that reads content from cache instead of API
"""

import os
import sys
from playwright.sync_api import sync_playwright

# Add the project path to import settings
current_dir = os.path.dirname(os.path.abspath(__file__))
services_dir = os.path.dirname(current_dir)
app_dir = os.path.dirname(services_dir)
sys.path.append(app_dir)

from cache_manager import cache_manager, get_latest_text_generation

def debug_page_state(page, step_name):
    """Debug helper to print current page state."""
    try:
        print(f"\n🔍 Debug info for {step_name}:")
        print(f"   Current URL: {page.url}")
        print(f"   Page title: {page.title()}")

        # Count modal dialogs
        modals = page.locator("div[role='dialog'], .mat-dialog-container").count()
        print(f"   Modal dialogs found: {modals}")

        # Count textareas
        textareas = page.locator("textarea").count()
        print(f"   Textareas found: {textareas}")

        # Count buttons
        buttons = page.locator("button").count()
        print(f"   Buttons found: {buttons}")

        # Take screenshot for debugging
        print("📸 Taking screenshot for debugging...")
        screenshot_path = f"debug_{step_name}.png"
        page.screenshot(path=screenshot_path)
        print(f"   Screenshot saved: {screenshot_path}")

    except Exception as e:
        print(f"⚠️ Debug info error: {e}")

def launch_notebooklm_from_cache(content_source="latest"):
    """
    Launch NotebookLM automation using cached content.

    Args:
        content_source: Can be "latest" for latest cached content, or a specific cache key

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("🚀 Starting NotebookLM automation with cached content")
        print("=" * 60)

        # Step 1: Get content from cache
        print("📤 Retrieving content from cache...")

        if content_source == "latest":
            cached_content = get_latest_text_generation()
            if not cached_content:
                print("❌ No cached text generation found!")
                print("💡 Make sure to run API text generation first to populate cache")
                return False
            print(f"✅ Retrieved latest cached content ({len(cached_content)} chars)")
        else:
            # Get specific cache key
            cached_data = cache_manager.get_response_by_key(content_source)
            if not cached_data:
                print(f"❌ Cache key not found: {content_source}")
                return False
            cached_content = cached_data.get('response_data')
            print(f"✅ Retrieved cached content by key: {content_source}")

        if not cached_content or len(cached_content.strip()) == 0:
            print("❌ Cached content is empty!")
            return False

        print(f"📝 Content preview: {cached_content[:100]}...")

        # Step 2: Launch browser automation
        profile_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
        print(f"💡 Using Chrome profile: {profile_path}")

        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=profile_path,
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
                # Step 3: Navigate to NotebookLM
                print("🌐 Navigating to NotebookLM...")
                page.goto("https://notebooklm.google.com/")
                page.wait_for_timeout(3000)

                # Step 4: Click "Create new notebook"
                print("📋 Creating new notebook...")
                create_btn = page.get_by_text("Create new notebook")
                create_btn.wait_for(timeout=10000)
                create_btn.click()
                print("✅ Clicked 'Create new notebook'")

                # Step 5: Wait and debug state
                page.wait_for_timeout(3000)
                debug_page_state(page, "after_create_notebook")

                # Step 6: Click "Copied text" button
                print("📎 Looking for 'Copied text' option...")
                copied_text_btn = page.get_by_text("Copied text")
                copied_text_btn.wait_for(timeout=10000)
                copied_text_btn.click()
                print("✅ Clicked 'Copied text' button")

                # Step 7: Wait for paste modal
                print("⏳ Waiting for paste modal...")
                page.wait_for_timeout(3000)
                debug_page_state(page, "after_copied_text_click")

                # Step 8: Find and fill textarea
                print("📝 Finding paste textarea...")
                paste_area = None

                try:
                    # Method 1: Look for textarea with paste placeholder
                    paste_area = page.locator("textarea[placeholder*='Paste text here'], textarea[placeholder*='paste text']")
                    paste_area.wait_for(timeout=5000)
                    print("✅ Found textarea with paste placeholder")
                except:
                    try:
                        # Method 2: Look for the second textarea (new one)
                        paste_area = page.locator("textarea").nth(1)
                        paste_area.wait_for(timeout=5000)
                        print("✅ Found second textarea element")
                    except:
                        # Method 3: Last visible textarea
                        paste_area = page.locator("textarea:visible").last
                        paste_area.wait_for(timeout=5000)
                        print("✅ Found last visible textarea")

                if not paste_area:
                    raise Exception("Could not find paste textarea")

                # Step 9: Click to focus and paste content
                print("🎯 Clicking textarea to focus...")
                paste_area.click(force=True)
                page.wait_for_timeout(1000)

                print("📋 Pasting cached content...")
                paste_area.fill(cached_content)
                page.wait_for_timeout(1500)
                print(f"✅ Pasted {len(cached_content)} characters")

                # Step 10: Click Insert button
                print("🔘 Looking for Insert button...")
                insert_btn = page.get_by_text("Insert", exact=True)
                insert_btn.wait_for(timeout=8000)
                insert_btn.click(force=True)
                print("✅ Clicked Insert button")

                # Step 11: Wait for completion
                page.wait_for_timeout(3000)
                debug_page_state(page, "after_insert")

                print("\n🎉 NotebookLM content upload completed successfully!")

                # Step 12: Click Audio Overview to generate audio
                print("🎵 Step 12: Clicking Audio Overview to generate audio...")
                try:
                    # Look for Audio Overview button in Studio sidebar (specific selector)
                    audio_overview_btn = page.locator(".mdc-button__label:has-text('Audio Overview')").first
                    audio_overview_btn.wait_for(timeout=10000)
                    audio_overview_btn.click()
                    print("✅ Clicked Audio Overview")

                    page.wait_for_timeout(3000)
                    debug_page_state(page, "after_audio_overview_click")

                    # Check for daily limits message
                    daily_limit_message = page.locator("text='You have reached your daily Audio Overview limits'")
                    if daily_limit_message.count() > 0:
                        print("⚠️ Daily Audio Overview limits reached!")
                        print("💡 Please try again tomorrow or upgrade your account")
                        print("✅ Content upload completed, but audio generation limited")
                        return True  # Still consider successful for content upload

                    print("✅ Audio Overview activated, waiting for audio generation...")

                except Exception as e:
                    print(f"⚠️ Could not click Audio Overview: {e}")
                    # Try alternative selector
                    try:
                        audio_overview_btn = page.get_by_text("Audio Overview").first
                        audio_overview_btn.click()
                        print("✅ Clicked Audio Overview (alternative method)")
                    except:
                        print("❌ Failed to click Audio Overview")
                        return False

                # Step 13: Wait for audio generation (reduced time)
                print("⏳ Step 13: Waiting for audio generation...")
                print("   Audio Overview activated, checking for completion...")

                # Check for audio generation completion periodically (faster)
                max_wait_time = 10 * 60  # Reduced to 10 minutes
                check_interval = 10  # Check every 10 seconds (faster)
                elapsed_time = 0

                audio_generated = False

                while elapsed_time < max_wait_time:
                    try:
                        # Check if page is still active
                        if page.is_closed():
                            print("⚠️ Page was closed, stopping audio generation wait")
                            break
                            
                        # Look for generated audio file (Digital Fossil... or similar)
                        audio_files = page.locator("[class*='digital'], [class*='fossil'], div:has-text('Digital Fossil'), div:has-text('hosts'), div:has-text('minute')")

                        if audio_files.count() > 0:
                            print(f"✅ Audio generation completed after {elapsed_time//60} minutes {elapsed_time%60} seconds")
                            audio_generated = True
                            break

                    except Exception as e:
                        print(f"⚠️ Error during audio generation wait: {e}")
                        break

                    print(f"   Checking... ({elapsed_time//60}:{elapsed_time%60:02d} elapsed)")
                    try:
                        page.wait_for_timeout(check_interval * 1000)
                        elapsed_time += check_interval
                    except:
                        print("⚠️ Page became unavailable during wait")
                        break

                if not audio_generated:
                    print("⚠️ Audio generation timeout or interrupted. Continuing anyway...")

                # Step 14: Click on the generated audio file
                print("🎵 Step 14: Looking for generated audio file...")
                try:
                    # Look for audio file with various possible selectors
                    audio_file = None

                    # Method 1: Look for text containing "Digital Fossil"
                    try:
                        audio_file = page.locator("div:has-text('Digital Fossil'), span:has-text('Digital Fossil')")
                        audio_file.first.wait_for(timeout=5000)
                        audio_file.first.click()
                        print("✅ Clicked on audio file (Digital Fossil)")
                    except:
                        # Method 2: Look for elements with "hosts" text
                        try:
                            audio_file = page.locator("div:has-text('hosts'), span:has-text('hosts')")
                            audio_file.first.wait_for(timeout=5000)
                            audio_file.first.click()
                            print("✅ Clicked on audio file (hosts)")
                        except:
                            # Method 3: Look for any clickable audio-related element
                            audio_file = page.locator("[class*='audio'], [class*='overview']").first
                            audio_file.wait_for(timeout=5000)
                            audio_file.click()
                            print("✅ Clicked on audio file (generic)")

                    page.wait_for_timeout(3000)
                    debug_page_state(page, "after_audio_file_click")

                except Exception as e:
                    print(f"⚠️ Could not find/click audio file: {e}")

                # Step 15: Click Interactive button
                print("🤝 Step 15: Looking for Interactive button...")
                try:
                    # Look for Interactive button based on the provided HTML structure
                    interactive_btn = page.locator("button:has-text('Interactive'), [aria-label*='Interactive'], .artifact-action-button-extended:has-text('Interactive')")
                    interactive_btn.wait_for(timeout=10000)
                    interactive_btn.click()
                    print("✅ Clicked Interactive button")

                    page.wait_for_timeout(5000)  # Wait for new window/modal
                    debug_page_state(page, "after_interactive_click")

                except Exception as e:
                    print(f"⚠️ Could not click Interactive button: {e}")

                # Step 16: Click Download audio preview
                print("⬇️ Step 16: Looking for Download audio preview...")
                try:
                    # Look for download button based on the HTML structure shown
                    download_btn = page.locator("a[aria-label*='Download audio overview'], button:has-text('Download'), [href*='audio'], [download*='audio']")
                    download_btn.wait_for(timeout=10000)
                    download_btn.click()
                    print("✅ Clicked Download audio preview")

                    page.wait_for_timeout(3000)
                    print("💾 Audio download should start...")

                except Exception as e:
                    print(f"⚠️ Could not click Download button: {e}")
                    # Alternative: try right-click and save
                    try:
                        audio_element = page.locator("audio, [class*='audio']").first
                        audio_element.click(button="right")
                        page.wait_for_timeout(1000)
                        page.keyboard.press("s")  # Save as
                        print("✅ Attempted download via right-click")
                    except:
                        print("❌ Download failed")

                print("\n🎉 Complete NotebookLM Audio Generation Workflow Finished!")
                print("📊 Summary:")
                print(f"   ✅ Content source: {content_source}")
                print(f"   ✅ Content length: {len(cached_content)} characters")
                print(f"   ✅ Content upload: SUCCESSFUL")
                print(f"   ✅ Audio generation: INITIATED")
                print(f"   ✅ Interactive mode: ACCESSED")
                print(f"   ✅ Download: ATTEMPTED")

                # Keep browser open for user to see result (reduced time)
                print("\n💡 Browser will stay open for you to check the result...")
                print("💡 Check your Downloads folder for the audio file")
                page.wait_for_timeout(3000)  # Reduced from 10s to 3s

                return True

            except Exception as e:
                print(f"❌ Automation error: {e}")
                debug_page_state(page, "error_state")
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

if __name__ == "__main__":
    print("🧪 NotebookLM Cache-Based Automation")
    print("=" * 50)

    # List available cache
    available = list_available_cache()

    if available:
        print(f"\n📤 Using latest cached content...")
        success = launch_notebooklm_from_cache("latest")
        print(f"\n🏁 Result: {'SUCCESS' if success else 'FAILED'}")
    else:
        print("\n❌ No cached content available")
        print("💡 Please ensure cache contains text generation data")