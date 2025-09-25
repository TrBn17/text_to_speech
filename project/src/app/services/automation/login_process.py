#!/usr/bin/env python3
"""
Google Account Login Process for NotebookLM Automation
"""

import os
import time
from playwright.sync_api import TimeoutError

class GoogleLoginService:
    """Handle Google account login process for NotebookLM automation."""

    def __init__(self, debug_mode=False):
        """Initialize login service."""
        self.debug_mode = debug_mode

    def debug_login_state(self, page, step_name):
        """Debug helper for login process."""
        if not self.debug_mode:
            return

        try:
            print(f"\n🔍 Login Debug - {step_name}:")
            print(f"   URL: {page.url}")
            print(f"   Title: {page.title()}")

            # Check for common login elements
            email_input = page.locator('input[type="email"]').count()
            password_input = page.locator('input[type="password"]').count()
            buttons = page.locator('button').count()

            print(f"   Email inputs: {email_input}")
            print(f"   Password inputs: {password_input}")
            print(f"   Buttons: {buttons}")

            if self.debug_mode:
                screenshot_path = f"login_debug_{step_name}.png"
                page.screenshot(path=screenshot_path)
                print(f"   Screenshot: {screenshot_path}")

        except Exception as e:
            print(f"⚠️ Login debug error: {e}")

    def click_use_another_account(self, page):
        """Click 'Use another account' button if present."""
        try:
            print("🔄 Looking for 'Use another account' option...")

            # Debug: Show page content to understand structure
            if self.debug_mode:
                print("📱 Checking for riDSKb elements...")
                riDSKb_elements = page.locator(".riDSKb").count()
                print(f"   Found {riDSKb_elements} elements with class 'riDSKb'")

                if riDSKb_elements > 0:
                    for i in range(riDSKb_elements):
                        text = page.locator(".riDSKb").nth(i).text_content()
                        print(f"   riDSKb[{i}]: '{text}'")

            # Try multiple selectors for 'Use another account'
            selectors = [
                ".riDSKb:has-text('Use another account')",
                "div.riDSKb:has-text('Use another account')",
                ".riDSKb",
                "#yDmH0d > c-wiz > main > div.UXFQgc > div > div > div > form > span > section > div > div > div > div > ul > li:nth-child(2) > div > div > div.riDSKb",
                "div:has-text('Use another account')",
                "button:has-text('Use another account')",
                "[data-identifier='UseAnotherAccount']"
            ]

            # Try all selectors
            for selector in selectors:
                try:
                    print(f"🔍 Trying selector: {selector}")
                    btn = page.locator(selector)
                    count = btn.count()
                    print(f"   Found {count} elements")

                    if count > 0:
                        # Check text content before clicking
                        text = btn.first.text_content() or ""
                        print(f"   Element text: '{text}'")

                        # Only click if element contains relevant text or is .riDSKb
                        if ("another" in text.lower() and "account" in text.lower()) or selector == ".riDSKb":
                            btn.first.click(force=True)
                            print(f"✅ Clicked 'Use another account' using: {selector}")
                            page.wait_for_timeout(3000)  # Wait longer for page transition

                            # Verify we moved to a different page/state
                            current_url = page.url
                            print(f"   Current URL after click: {current_url}")

                            return True
                        else:
                            print(f"   ⏭️ Skipped - text doesn't match: '{text}'")

                except Exception as e:
                    print(f"   ❌ Failed with {selector}: {e}")
                    continue

            # Final attempt: Click any .riDSKb element that might be the right one
            try:
                riDSKb_elements = page.locator(".riDSKb")
                for i in range(riDSKb_elements.count()):
                    element = riDSKb_elements.nth(i)
                    text = element.text_content() or ""
                    if "another" in text.lower() or "account" in text.lower():
                        element.click()
                        print(f"✅ Clicked riDSKb element with matching text: '{text}'")
                        page.wait_for_timeout(2000)
                        return True
            except Exception as e:
                print(f"⚠️ Final attempt failed: {e}")

            print("ℹ️ 'Use another account' button not found - proceeding")
            return True

        except Exception as e:
            print(f"⚠️ Error clicking 'Use another account': {e}")
            return True  # Continue anyway

    def enter_email(self, page, email):
        """Enter email address."""
        try:
            print("📧 Entering email address...")

            # Try multiple selectors for email input
            email_selectors = [
                'input[type="email"]#identifierId',
                'input[type="email"].whsOnd.zHQkBf#identifierId',
                'input[name="identifier"]',
                'input#identifierId',
                'input[type="email"]',
                'input[aria-label*="Email"]',
                'input[placeholder*="email"]'
            ]

            email_input = None
            for selector in email_selectors:
                try:
                    print(f"🔍 Trying email selector: {selector}")
                    input_elem = page.locator(selector)
                    count = input_elem.count()
                    print(f"   Found {count} email input elements")

                    if count > 0:
                        input_elem.first.wait_for(timeout=5000)
                        email_input = input_elem.first
                        print(f"✅ Found email input with: {selector}")
                        break
                except Exception as e:
                    print(f"   ❌ Failed with {selector}: {e}")
                    continue

            if not email_input:
                print("❌ No email input field found with any selector")
                self.debug_login_state(page, "email_input_not_found")
                return False

            # Clear and enter email
            print("✍️ Filling email...")
            email_input.click()
            page.wait_for_timeout(500)
            email_input.clear()
            page.wait_for_timeout(500)
            email_input.fill(email)
            page.wait_for_timeout(1000)

            print(f"✅ Email entered: {email}")
            self.debug_login_state(page, "after_email_input")
            return True

        except Exception as e:
            print(f"❌ Error entering email: {e}")
            self.debug_login_state(page, "email_error")
            return False

    def click_next_after_email(self, page):
        """Click Next button after entering email."""
        try:
            print("➡️ Clicking Next after email...")

            # Try multiple selectors for Next button
            next_selectors = [
                "#identifierNext > div > button",
                "#identifierNext button",
                "button:has-text('Next')",
                "[data-primary-action-label='Next'] button",
                "button[type='submit']",
                ".VfPpkd-LgbsSe:has-text('Next')"
            ]

            next_btn = None
            for selector in next_selectors:
                try:
                    print(f"🔍 Trying Next selector: {selector}")
                    btn_elem = page.locator(selector)
                    count = btn_elem.count()
                    print(f"   Found {count} Next button elements")

                    if count > 0:
                        btn_elem.first.wait_for(timeout=5000)
                        next_btn = btn_elem.first
                        print(f"✅ Found Next button with: {selector}")
                        break
                except Exception as e:
                    print(f"   ❌ Failed with {selector}: {e}")
                    continue

            if not next_btn:
                print("❌ No Next button found with any selector")
                self.debug_login_state(page, "next_button_not_found")
                return False

            # Click the button
            print("🖱️ Clicking Next button...")
            next_btn.click()
            print("✅ Next button clicked")
            page.wait_for_timeout(4000)  # Wait longer for password page
            self.debug_login_state(page, "after_email_next")
            return True

        except Exception as e:
            print(f"❌ Error clicking Next after email: {e}")
            self.debug_login_state(page, "next_error")
            return False

    def enter_password(self, page, password):
        """Enter password."""
        try:
            print("🔐 Entering password...")

            # Wait for password input field
            password_input = page.locator('input[type="password"].whsOnd.zHQkBf[name="Passwd"]')
            password_input.wait_for(timeout=10000)

            # Clear and enter password
            password_input.click()
            password_input.clear()
            password_input.fill(password)
            page.wait_for_timeout(1000)

            print("✅ Password entered")
            self.debug_login_state(page, "after_password_input")
            return True

        except TimeoutError:
            print("❌ Password input field not found")
            return False
        except Exception as e:
            print(f"❌ Error entering password: {e}")
            return False

    def click_next_after_password(self, page):
        """Click Next button after entering password."""
        try:
            print("➡️ Clicking Next after password...")

            # Use the specific selector provided
            next_btn = page.locator("#passwordNext > div > button")
            next_btn.wait_for(timeout=8000)
            next_btn.click()

            print("✅ Password Next button clicked")
            page.wait_for_timeout(5000)  # Wait longer for login to complete
            self.debug_login_state(page, "after_password_next")
            return True

        except TimeoutError:
            print("❌ Next button not found after password")
            return False
        except Exception as e:
            print(f"❌ Error clicking Next after password: {e}")
            return False

    def wait_for_login_completion(self, page, max_wait_seconds=30):
        """Wait for login to complete."""
        print("⏳ Waiting for login completion...")

        start_time = time.time()

        while time.time() - start_time < max_wait_seconds:
            try:
                current_url = page.url

                # Check if we're redirected to a success page or main Google page
                if any(indicator in current_url.lower() for indicator in [
                    'accounts.google.com/signin/oauth',
                    'accounts.google.com/b/0/oauth',
                    'myaccount.google.com',
                    'accounts.google.com/ManageAccount'
                ]):
                    print("✅ Login appears successful - redirected")
                    return True

                # Check if we're no longer on login page
                if 'signin' not in current_url.lower() and 'login' not in current_url.lower():
                    print("✅ Login completed - left login pages")
                    return True

                page.wait_for_timeout(2000)

            except Exception as e:
                print(f"⚠️ Error checking login status: {e}")
                break

        print("⚠️ Login completion timeout")
        return False

    def handle_two_factor_auth(self, page):
        """Handle two-factor authentication if required."""
        try:
            print("🔐 Checking for 2FA requirements...")

            # Look for 2FA prompts
            two_fa_selectors = [
                "div:has-text('2-Step Verification')",
                "div:has-text('Verify it\\'s you')",
                "div:has-text('Get a verification code')",
                "input[aria-label*='verification']",
                "input[placeholder*='code']"
            ]

            for selector in two_fa_selectors:
                if page.locator(selector).count() > 0:
                    print("⚠️ 2FA required - manual intervention needed")
                    print("Please complete 2FA manually in the browser")

                    # Wait for user to complete 2FA
                    print("Waiting 120 seconds for manual 2FA completion...")
                    page.wait_for_timeout(120000)
                    return True

            print("ℹ️ No 2FA detected")
            return True

        except Exception as e:
            print(f"⚠️ Error handling 2FA: {e}")
            return True

    def login_to_google(self, page, email, password):
        """Complete Google login process."""
        try:
            print("🔐 Starting Google login process...")
            print("=" * 50)

            # Step 1: Handle "Use another account" if present
            if not self.click_use_another_account(page):
                print("❌ Failed to handle account selection")
                return False

            # Step 2: Enter email
            if not self.enter_email(page, email):
                print("❌ Failed to enter email")
                return False

            # Step 3: Click Next after email
            if not self.click_next_after_email(page):
                print("❌ Failed to proceed after email")
                return False

            # Step 4: Enter password
            if not self.enter_password(page, password):
                print("❌ Failed to enter password")
                return False

            # Step 5: Click Next after password
            if not self.click_next_after_password(page):
                print("❌ Failed to proceed after password")
                return False

            # Step 6: Handle 2FA if needed
            if not self.handle_two_factor_auth(page):
                print("❌ Failed to handle 2FA")
                return False

            # Step 7: Wait for login completion
            if not self.wait_for_login_completion(page):
                print("❌ Login did not complete in time")
                return False

            print("✅ Google login completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Login process error: {e}")
            return False

def perform_google_login(page, email, password, debug_mode=False):
    """
    Perform Google login with provided credentials.

    Args:
        page: Playwright page object
        email: Google account email
        password: Google account password
        debug_mode: Enable debug screenshots and logging

    Returns:
        bool: True if login successful, False otherwise
    """
    login_service = GoogleLoginService(debug_mode=debug_mode)
    return login_service.login_to_google(page, email, password)