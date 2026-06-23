import google.generativeai as genai
import anthropic
import os
from config import load_config
import time

def process_with_ai(images=None, audio_path=None):
    config = load_config()
    model_choice = config.get("selected_model", "Gemini 3.5 Flash")
    sys_prompt = config.get("system_prompt", "")
    
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
