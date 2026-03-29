#!/usr/bin/env python3
import argparse, base64, json, os, sys, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-2.5-flash-image"
TELEGRAM_API = "https://api.telegram.org/bot{token}/sendPhoto"

def generate_image(prompt, model, aspect_ratio, api_key):
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "modalities": ["image", "text"]}
    if aspect_ratio != "1:1":
        payload["image_config"] = {"aspect_ratio": aspect_ratio}
    req = urllib.request.Request(API_URL, data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode())
    images = result.get("choices", [])[0].get("message", {}).get("images", [])
    if not images:
        sys.exit("Error: No image returned")
    img_url = images[0]["image_url"]["url"]
    b64 = img_url.split(",", 1)[1]
    return base64.b64decode(b64)

def send_telegram(image_bytes, caption, token, chat_id):
    import io, http.client, uuid
    boundary = uuid.uuid4().hex
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="chat_id"\r\n\r\n')
    body.extend(str(chat_id).encode())
    body.extend(b"\r\n")

    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="caption"\r\n\r\n')
    body.extend(caption.encode())
    body.extend(b"\r\n")

    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="photo"; filename="image.png"\r\n')
    body.extend(b"Content-Type: image/png\r\n\r\n")
    body.extend(image_bytes)
    body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode())
    req = urllib.request.Request(
        TELEGRAM_API.format(token=token),
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", required=True)
    p.add_argument("--output")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--aspect-ratio", default="1:1")
    p.add_argument("--telegram-send", action="store_true", help="Send image to Telegram")
    p.add_argument("--chat-id", help="Telegram chat ID")
    args = p.parse_args()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        sys.exit("Error: OPENROUTER_API_KEY not set")

    print(f"Generating image with {args.model}...", file=sys.stderr)
    img = generate_image(args.prompt, args.model, args.aspect_ratio, api_key)

    out_path = Path(args.output) if args.output else Path(os.getenv("OPENCLAW_WORKSPACE", str(Path.home() / ".openclaw" / "workspace"))) / "images" / "generated" / f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(img)
    print(str(out_path.resolve()))

    if args.telegram_send:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = args.chat_id or os.getenv("TELEGRAM_CHAT_ID")
        if token and chat_id:
            try:
                send_telegram(img, args.prompt[:200], token, chat_id)
                print("Telegram: sent", file=sys.stderr)
            except Exception as e:
                print(f"Telegram send failed: {e}", file=sys.stderr)
        else:
            print("Telegram: TELEGRAM_BOT_TOKEN or chat_id missing, skipped", file=sys.stderr)

if __name__ == "__main__":
    main()
