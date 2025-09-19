from flask import Flask, Response
import requests
import base64
import re

app = Flask(__name__)

LIVE_PHP_URL = "https://allinonereborn.fun/opplextv-web1/live.php?id=356533"

@app.route("/live.m3u8")
def live_playlist():
    resp = requests.get(LIVE_PHP_URL)
    if resp.status_code != 200:
        return Response("Error fetching live playlist", status=500)

    content = resp.text
    decoded_lines = []

    ts_urls = []

    # Collect all decoded .ts URLs
    for line in content.splitlines():
        match = re.search(r"file=([A-Za-z0-9+/=]+)", line)
        if match:
            encoded = match.group(1)
            missing_padding = len(encoded) % 4
            if missing_padding != 0:
                encoded += "=" * (4 - missing_padding)
            try:
                decoded_url = base64.b64decode(encoded).decode("utf-8")
                ts_urls.append(decoded_url)
            except:
                ts_urls.append(line)
        else:
            decoded_lines.append(line)

    # Serve everything except the last segment
    if ts_urls:
        ts_urls = ts_urls[:-1]

    final_playlist = "\n".join(decoded_lines + ts_urls)
    return Response(final_playlist, mimetype="application/vnd.apple.mpegurl")


# Do NOT include app.run() for Vercel
