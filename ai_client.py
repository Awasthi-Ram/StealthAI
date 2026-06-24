import google.generativeai as genai
import anthropic
import os
from config import load_config
import time

def process_with_ai(images=None, audio_path=None, progress_cb=None):
    if progress_cb is None: progress_cb = lambda v, m: None
    config = load_config()
    backend_mode = config.get("backend_mode", "API")
    model_choice = config.get("selected_model", "Gemini 3.5 Flash")
    sys_prompt = config.get("system_prompt", "")
    
    if backend_mode == "Web":
        return process_with_gemini_web(sys_prompt, images, audio_path, progress_cb=progress_cb)
    else:
        if "Gemini" in model_choice:
            return process_with_gemini(config.get("gemini_api_key", ""), model_choice, sys_prompt, images, audio_path)
        elif "Claude" in model_choice:
            return process_with_claude(config.get("claude_api_key", ""), sys_prompt, images, audio_path)
        else:
            return "Invalid model selected."

def process_with_gemini(api_key, model_choice, sys_prompt, images, audio_path):
    if not api_key:
        return "Error: Gemini API Key is missing."
    
    genai.configure(api_key=api_key)
    
    # Map friendly name to actual model name
    model_name = "gemini-3.5-flash"
    if "Pro" in model_choice:
        model_name = "gemini-3.5-pro"
        
    model = genai.GenerativeModel(model_name)
    
    contents = [sys_prompt]
    
    if images:
        if isinstance(images, list):
            contents.extend(images)
        else:
            contents.append(images)
        
    uploaded_audio = None
    if audio_path:
        try:
            uploaded_audio = genai.upload_file(audio_path)
            contents.append(uploaded_audio)
        except Exception as e:
            return f"Error uploading audio to Gemini: {e}"
            
    try:
        response = model.generate_content(contents)
        res_text = response.text
    except Exception as e:
        res_text = f"Gemini Error: {e}"
        
    if uploaded_audio:
        try:
            uploaded_audio.delete()
        except:
            pass
            
    return res_text

def process_with_claude(api_key, sys_prompt, images, audio_path):
    if not api_key:
        return "Error: Claude API Key is missing."
        
    if audio_path:
        return "Error: Audio input is not currently supported with Claude in this tool. Please use Gemini for audio."
        
    client = anthropic.Anthropic(api_key=api_key)
    
    content = []
    
    if images:
        if not isinstance(images, list):
            images = [images]
            
        import io
        import base64
        
        for img in images:
            # Convert PIL Image to base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": img_str,
                }
            })
        
    content.append({
        "type": "text",
        "text": sys_prompt
    })
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": content}
            ]
        )
        return response.content[0].text
    except Exception as e:
        return f"Claude Error: {e}"

def login_gemini_web(data_dir="./gemini_web_data"):
    import traceback
    import os
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "0")
    
    lock_path = os.path.join(data_dir, "SingletonLock")
    if os.path.exists(lock_path):
        try:
            os.remove(lock_path)
        except OSError:
            pass
            
    try:
        import subprocess
        subprocess.run(
            ['powershell', '-Command', f"Get-CimInstance Win32_Process -Filter \\\"Name = 'msedge.exe' OR Name = 'chrome.exe'\\\" | Where-Object {{ $_.CommandLine -like '*{os.path.basename(data_dir)}*' }} | Stop-Process -Force"],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
    except Exception:
        pass
            
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        with open("stealth_error.log", "a") as f:
            f.write("Playwright not installed.\n")
        return
        
    try:
        with sync_playwright() as p:
            browser = None
            try:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=data_dir,
                    headless=False,
                    channel="chrome",
                    args=['--disable-blink-features=AutomationControlled']
                )
            except Exception:
                try:
                    browser = p.chromium.launch_persistent_context(
                        user_data_dir=data_dir,
                        headless=False,
                        channel="msedge",
                        args=['--disable-blink-features=AutomationControlled']
                    )
                except Exception:
                    pass
                    
            if not browser:
                raise Exception("Failed to launch browser. Ensure no other instance is using the profile.")
                
            page = browser.new_page()
            page.goto('https://gemini.google.com/')
            try:
                page.wait_for_event('close', timeout=0)
            except Exception:
                pass
    except Exception as e:
        with open("stealth_error.log", "a") as f:
            f.write(f"Playwright error: {e}\n{traceback.format_exc()}\n")

def process_with_gemini_web(sys_prompt, images, audio_path, data_dir="./gemini_web_data", progress_cb=None):
    if progress_cb is None: progress_cb = lambda v, m: None
    import os
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "0")
    
    lock_path = os.path.join(data_dir, "SingletonLock")
    if os.path.exists(lock_path):
        try:
            os.remove(lock_path)
        except OSError:
            pass
            
    try:
        import subprocess
        subprocess.run(
            ['powershell', '-Command', f"Get-CimInstance Win32_Process -Filter \\\"Name = 'msedge.exe' OR Name = 'chrome.exe'\\\" | Where-Object {{ $_.CommandLine -like '*{os.path.basename(data_dir)}*' }} | Stop-Process -Force"],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
    except Exception:
        pass
            
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return "Error: Playwright is not installed. Run 'pip install playwright && playwright install chromium'."
        
    if audio_path:
        return "Error: Direct audio input is not supported in the Gemini Web backend. Use the official Gemini API."

    res_text = "Error: Did not get response from Gemini Web."
    progress_cb(10, "Initializing Playwright Engine...")
    with sync_playwright() as p:
        browser = None
        try:
            try:
                progress_cb(20, "Launching Chrome...")
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=data_dir,
                    headless=True,
                    channel="chrome",
                    args=['--disable-blink-features=AutomationControlled']
                )
            except Exception:
                progress_cb(20, "Launching Edge Fallback...")
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=data_dir,
                    headless=True,
                    channel="msedge",
                    args=['--disable-blink-features=AutomationControlled']
                )
            progress_cb(40, "Opening Gemini Web...")
            page = browser.new_page()
            page.goto('https://gemini.google.com/')
            
            # Check for Sign In
            page.wait_for_timeout(2000)
            if page.locator("text=Sign in").count() > 0:
                browser.close()
                return "Error: You are not logged in to Gemini. Please use 'Web Login' in settings."
                
            # Try to find the input box
            try:
                page.wait_for_selector('rich-textarea p', timeout=15000)
            except:
                browser.close()
                return "Error: Could not find input box on Gemini Web."
                
            temp_paths = []
            if images:
                import tempfile
                import os
                for img in images:
                    if not isinstance(img, str):
                        fd, path = tempfile.mkstemp(suffix=".png")
                        os.close(fd)
                        img.save(path)
                        temp_paths.append(path)
                    else:
                        temp_paths.append(img)
                        
                # Upload files via programmatic paste (most reliable for Gemini Web)
                progress_cb(50, "Uploading images...")
                uploaded = False
                
                import base64
                
                # Strategy 1: Programmatic paste via DataTransfer API
                # This simulates Ctrl+V with the image data - works regardless of UI structure
                try:
                    for tp in temp_paths:
                        with open(tp, 'rb') as f:
                            img_b64 = base64.b64encode(f.read()).decode('utf-8')
                        
                        # Focus the input area first
                        textarea = page.locator('rich-textarea p')
                        if textarea.count() > 0:
                            textarea.first.click()
                            page.wait_for_timeout(300)
                        
                        result = page.evaluate('''(b64Data) => {
                            return new Promise((resolve) => {
                                try {
                                    // Decode base64 to binary
                                    const binaryStr = atob(b64Data);
                                    const bytes = new Uint8Array(binaryStr.length);
                                    for (let i = 0; i < binaryStr.length; i++) {
                                        bytes[i] = binaryStr.charCodeAt(i);
                                    }
                                    const blob = new Blob([bytes], { type: 'image/png' });
                                    const file = new File([blob], 'screenshot.png', { type: 'image/png' });
                                    
                                    // Create DataTransfer with the file
                                    const dt = new DataTransfer();
                                    dt.items.add(file);
                                    
                                    // Find the best target element for paste
                                    let target = document.querySelector('rich-textarea') 
                                        || document.querySelector('[contenteditable="true"]')
                                        || document.querySelector('textarea')
                                        || document.activeElement;
                                    
                                    // Dispatch paste event
                                    const pasteEvent = new ClipboardEvent('paste', {
                                        bubbles: true,
                                        cancelable: true,
                                        clipboardData: dt
                                    });
                                    target.dispatchEvent(pasteEvent);
                                    
                                    // Also try drop event as fallback
                                    const dropEvent = new DragEvent('drop', {
                                        bubbles: true,
                                        cancelable: true,
                                        dataTransfer: dt
                                    });
                                    target.dispatchEvent(dropEvent);
                                    
                                    resolve(true);
                                } catch(e) {
                                    resolve(false);
                                }
                            });
                        }''', img_b64)
                        
                        if result:
                            uploaded = True
                            page.wait_for_timeout(2000)
                except Exception:
                    pass
                
                # Strategy 2: File chooser interception
                if not uploaded:
                    try:
                        # Try to find and click any upload-related button
                        attach_selectors = [
                            'button[aria-label*="pload"]',
                            'button[aria-label*="ttach"]',
                            'button[aria-label*="file"]',
                            'button[aria-label*="File"]',
                            'button[aria-label*="mage"]',
                            '[data-tooltip*="pload"]',
                            '[data-tooltip*="mage"]',
                        ]
                        for sel in attach_selectors:
                            btn = page.locator(sel)
                            if btn.count() > 0:
                                # Use file chooser interception
                                with page.expect_file_chooser(timeout=5000) as fc_info:
                                    btn.first.click()
                                file_chooser = fc_info.value
                                file_chooser.set_files(temp_paths)
                                uploaded = True
                                page.wait_for_timeout(2000)
                                break
                    except Exception:
                        pass
                
                # Strategy 3: Direct input[type=file] as last CSS attempt
                if not uploaded:
                    try:
                        file_input = page.locator('input[type="file"]')
                        if file_input.count() > 0:
                            file_input.first.set_input_files(temp_paths)
                            uploaded = True
                            page.wait_for_timeout(2000)
                    except Exception:
                        pass
                
                if not uploaded:
                    progress_cb(55, "Image upload failed, sending text-only...")
                
                page.wait_for_timeout(1000)

            # Send Prompt
            page.locator('rich-textarea p').fill(sys_prompt)
            page.keyboard.press("Enter")
            
            # Wait for generation to start and settle
            page.wait_for_timeout(1000)
            try:
                page.wait_for_selector('message-content', timeout=30000)
            except:
                return "Error: Timeout waiting for response from Gemini Web."
                
            last_text = ""
            for _ in range(40):
                page.wait_for_timeout(500)
                msgs = page.query_selector_all('message-content')
                if not msgs: continue
                current_text = msgs[-1].inner_text()
                if current_text and current_text == last_text:
                    break
                last_text = current_text
                
            res_text = last_text

            if images:
                import os
                for p in temp_paths:
                    try:
                        os.remove(p)
                    except: pass
                    
        except Exception as e:
            res_text = f"Gemini Web Error: {e}"
        finally:
            if browser:
                browser.close()
            
    return res_text
