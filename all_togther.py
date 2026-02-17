import os
import subprocess

# כופה שימוש ב-CPU בלבד
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# ----------------------------
# Interpreter עם OpenVINO LLM
# ----------------------------
from openvino_genai import LLMPipeline

# מודל OpenVINO חייב להיות בתיקייה ov_model
pipe = LLMPipeline(r"C:\Users\user\Desktop\MCP\ov_model", device="CPU")  # CPU בלבד כדי למנוע DLL errors



SYSTEM_PROMPT = """
You are a Windows automation agent.

Translate user requests into ONE PowerShell command.

Rules:
- Return ONLY the command
- No explanation
- Prefer PowerShell
"""

def translate(text):
    prompt = f"{SYSTEM_PROMPT}\nUser: {text}\nAssistant:"
    response = pipe.generate(prompt, max_new_tokens=80)
    return response.strip()

# ----------------------------
# Executor – מריץ PowerShell
# ----------------------------
def run_command(cmd):
    try:
        result = subprocess.check_output(
            ["powershell", "-Command", cmd],
            stderr=subprocess.STDOUT
        )
        return result.decode(errors="ignore")
    except subprocess.CalledProcessError as e:
        return e.output.decode(errors="ignore")

# ----------------------------
# Agent Loop
# ----------------------------
print("Local LLM Agent started (CPU only)")

while True:
    text = input(">> ")
    if text.lower() in ["exit", "quit"]:
        print("Exiting agent...")
        break

    cmd = translate(text)
    print("COMMAND:", cmd)

    output = run_command(cmd)
    print(output)
