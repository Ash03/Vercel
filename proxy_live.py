from flask import Flask, Response
import requests
import re
import base64

app = Flask(__name__)

# Replace this with your PHP live URL
LIVE_PHP_URL = "https://allinonereborn.fun/opplextv-web1/live.php?id=356533"

@app.route("/live.m3u8")
def live_playlist():
    try:
        resp = requests.get(LIVE_PHP_URL)
        resp.raise_for_status()
    except Exception as e:
        return Response(f"Error fetching live playlist: {e}", status=500)

    content = resp.text
    ts_urls = []
    header_lines = []

    # Process playlist lines
    for line in content.splitlines():
        match = re.search(r"file=([A-Za-z0-9+/=]+)", line)
        if match:
            encoded = match.group(1)
            # Fix base64 padding
            missing_padding = len(encoded) % 4
            if missing_padding != 0:
                encoded += "=" * (4 - missing_padding)
            try:
                decoded_url = base64.b64decode(encoded).decode("utf-8")
                ts_urls.append(decoded_url)
            except:
                # If decoding fails, fallback to original line
                ts_urls.append(line)
        else:
            header_lines.append(line)

    # Serve all segments except the last one (1 segment behind live)
    if ts_urls:
        ts_urls = ts_urls[:-1]

    final_playlist = "\n".join(header_lines + ts_urls)

    # Return with no-cache headers for smoother live playback
    return Response(final_playlist, mimetype="application/vnd.apple.mpegurl", headers={"Cache-Control": "no-cache"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
