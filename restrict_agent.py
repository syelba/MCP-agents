from flask import Flask, request, abort
from openvino_genai import LLMPipeline
import subprocess

AUTHORIZED_IP = "10.0.0.50"

pipe = LLMPipeline(r"C:\Users\user\Desktop\MCP\ov_model", device="CPU")

app = Flask(__name__)

ALLOWLIST = [
    "ping",
    "hostname",
    "ipconfig",
    "docker ps",
    "systeminfo"
]


def validate(cmd):
    return any(cmd.startswith(a) for a in ALLOWLIST)


def execute(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout


@app.before_request
def restrict_ip():
    if request.remote_addr != AUTHORIZED_IP:
        abort(403)


@app.route("/run", methods=["POST"])
def run():
    data = request.json
    prompt = data["prompt"]

    response = pipe(prompt, max_new_tokens=80)
    cmd = response.text.strip()

    if not validate(cmd):
        return {"error": "blocked command", "cmd": cmd}

    output = execute(cmd)
    return {"cmd": cmd, "output": output}


app.run(host="0.0.0.0", port=8080)
