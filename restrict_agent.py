from openvino_genai import LLMPipeline
import subprocess

pipe = LLMPipeline(r"C:\Users\user\Desktop\MCP\ov_model", device="CPU")

SYSTEM = """
You are Lab-Agent.
You help manage lab machines safely.

Allowed actions:
- ping
- ipconfig
- hostname
- dir
- docker ps
- systeminfo

Never use destructive commands.
Return only a command to execute.
"""

ALLOWLIST = [
    "ping",
    "ipconfig",
    "hostname",
    "dir",
    "docker ps",
    "systeminfo"
]


def validate(cmd):
    return any(cmd.startswith(a) for a in ALLOWLIST)


def execute(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout


while True:
    user = input("lab> ")

    prompt = SYSTEM + "\nUser: " + user
    response = pipe(prompt, max_new_tokens=80)

    cmd = response.text.strip()

    if not validate(cmd):
        print("Blocked command:", cmd)
        continue

    print("Executing:", cmd)
    print(execute(cmd))
