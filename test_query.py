import sys
from ai_client import process_with_gemini_web

if __name__ == "__main__":
    print("Testing process_with_gemini_web...")
    res = process_with_gemini_web("What is 2+2? reply with just the number.", None, None)
    print("Result:", res)
