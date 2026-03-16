import os
import subprocess
import re
from functools import lru_cache

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

# ----------------------------
# LRU-cached translator
# ----------------------------
@lru_cache(maxsize=256)
def translate(text: str, attempt: int = 0) -> str:
    """Translate a user request into a single PowerShell command.

    attempt is part of the cache key so we can ask for alternative solutions
    deterministically without overwriting the previous attempt.
    """
    extra = ""
    if attempt > 0:
        extra = (
            "\nIMPORTANT: Provide a DIFFERENT approach than previous attempts. "
            "Avoid repeating the same command."
        )

    prompt = f"{SYSTEM_PROMPT}{extra}\nUser: {text}\nAssistant:"
    response = pipe.generate(prompt, max_new_tokens=120)
    return response.strip()

# ----------------------------
# Executor – מריץ PowerShell
# ----------------------------
def run_command(cmd: str):
    """Run a PowerShell command.

    Returns (success: bool, output: str)
    """
    try:
        result = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", cmd],
            stderr=subprocess.STDOUT,
        )
        return True, result.decode(errors="ignore")
    except subprocess.CalledProcessError as e:
        return False, e.output.decode(errors="ignore")


def _looks_successful(output: str) -> bool:
    """Heuristic success detection for commands that don't raise but fail logically."""
    if not output:
        return True
    low = output.lower()
    # common PowerShell failure indicators
    failure_markers = [
        "categoryinfo",
        "fullyqualifiederrorid",
        "is not recognized",
        "cannot find path",
        "access is denied",
        "denied",
        "exception",
        "error:",
        "failed",
    ]
    return not any(m in low for m in failure_markers)


def _extract_first_ps_command(text: str) -> str:
    """Best-effort extraction: return first non-empty line, strip code fences."""
    t = text.strip()
    t = re.sub(r"^```(?:powershell|ps1|shell)?\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"```$", "", t).strip()
    # take first non-empty line
    for line in t.splitlines():
        line = line.strip()
        if line:
            return line
    return t

# ----------------------------
# Agent Loop
# ----------------------------
print("Local LLM Agent started (CPU only)")

MAX_ATTEMPTS = 4

while True:
    text = input(">> ")
    if text.lower() in ["exit", "quit"]:
        print("Exiting agent...")
        break

    last_output = ""
    success = False

    for attempt in range(MAX_ATTEMPTS):
        cmd_raw = translate(text, attempt)
        cmd = _extract_first_ps_command(cmd_raw)

        print(f"COMMAND (attempt {attempt + 1}/{MAX_ATTEMPTS}):", cmd)

        ok, output = run_command(cmd)
        last_output = output

        # If PowerShell returned non-zero -> ok will be False
        # If it returned 0 but output looks like a failure -> treat as failure
        if ok and _looks_successful(output):
            success = True
            print(output)
            break

        # Show error output and try alternative
        print(output)
        if attempt < MAX_ATTEMPTS - 1:
            print("Retrying with an alternative solution...")

    if not success:
        print("Could not complete the request after multiple attempts.")
        print("Last output:")
        print(last_output)
        print("Suggestion: rephrase the request with more details (paths, app names, desired result), or run the shown command manually and paste the exact error.")