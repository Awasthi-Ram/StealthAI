import google.generativeai as genai
import anthropic
import os
from config import load_config
import time

def process_with_ai(images=None, audio_path=None):
    config = load_config()
    backend_mode = config.get("backend_mode", "API")
    model_choice = config.get("selected_model", "Gemini 3.5 Flash")
    sys_prompt = config.get("system_prompt", "")
    
    if backend_mode == "Web":
        return process_with_gemini_web(sys_prompt, images, audio_path)
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
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        with open("stealth_error.log", "a") as f:
            f.write("Playwright not installed.\n")
        return
        
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=data_dir,
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            page = browser.new_page()
            page.goto('https://gemini.google.com/')
            try:
                page.wait_for_event('close', timeout=0)
            except Exception:
                pass
    except Exception as e:
        with open("stealth_error.log", "a") as f:
            f.write(f"Playwright error: {e}\n{traceback.format_exc()}\n")

def process_with_gemini_web(sys_prompt, images, audio_path, data_dir="./gemini_web_data"):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return "Error: Playwright is not installed. Run 'pip install playwright && playwright install chromium'."
        
    if audio_path:
        return "Error: Direct audio input is not supported in the Gemini Web backend. Use the official Gemini API."

    res_text = "Error: Did not get response from Gemini Web."
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=data_dir,
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
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
                        
                # Upload files
                file_input = page.locator('input[type="file"]')
                if file_input.count() > 0:
                    file_input.set_input_files(temp_paths)
                    page.wait_for_timeout(3000) # wait for upload
                else:
                    return "Error: Could not find file upload input on Gemini Web."

            # Send Prompt
            page.locator('rich-textarea p').fill(sys_prompt)
            page.keyboard.press("Enter")
            
            # Wait for generation to start and settle
            page.wait_for_timeout(3000)
            try:
                page.wait_for_selector('message-content', timeout=30000)
            except:
                return "Error: Timeout waiting for response from Gemini Web."
                
            last_text = ""
            for _ in range(30):
                page.wait_for_timeout(1000)
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
            browser.close()
            
    return res_text
