import os
import re
import random
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Rotating User-Agents list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
]

# HTML Template (Professional Design)
HTML_INDEX = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uid to Fb Information CtH</title>
    <style>
        body { background-color: #0d1117; color: #00ff41; font-family: 'Courier New', Courier, monospace; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .container { background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #00ff41; box-shadow: 0 0 20px #00ff4133; width: 90%; max-width: 500px; text-align: center; }
        h1 { color: #58a6ff; font-size: 24px; text-transform: uppercase; margin-bottom: 20px; text-shadow: 0 0 10px #58a6ff; }
        input { width: 80%; padding: 12px; border: 1px solid #30363d; background: #0d1117; color: white; border-radius: 5px; outline: none; margin-bottom: 15px; text-align: center; font-size: 16px; }
        button { background-color: #238636; color: white; border: none; padding: 12px 25px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: 0.3s; width: 80%; }
        button:hover { background-color: #2ea043; box-shadow: 0 0 10px #2ea043; }
        .result-box { margin-top: 25px; text-align: left; background: #0d1117; padding: 15px; border-radius: 8px; border: 1px solid #30363d; display: none; }
        .info-item { border-bottom: 1px solid #21262d; padding: 8px 0; font-size: 14px; }
        .info-label { color: #8b949e; font-weight: bold; }
        .credit { margin-top: 20px; font-size: 12px; color: #8b949e; }
        .credit b { color: #f85149; }
        .loader { display: none; color: #f1e05a; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Uid to Fb Information CtH</h1>
        <input type="text" id="uidInput" placeholder="Enter FB UID (e.g. 100020606404781)">
        <button onclick="scanUid()">START SCANNING</button>
        <div id="loader" class="loader">Accessing Database...</div>

        <div id="resultBox" class="result-box">
            <div class="info-item"><span class="info-label">Name:</span> <span id="resName">N/A</span></div>
            <div class="info-item"><span class="info-label">Location:</span> <span id="resLoc">N/A</span></div>
            <div class="info-item"><span class="info-label">Email:</span> <span id="resEmail">N/A</span></div>
            <div class="info-item"><span class="info-label">Phone:</span> <span id="resPhone">N/A</span></div>
        </div>

        <div class="credit">
            Developed by <b>SHADOW JOKER</b><br>
            Powered by <b>Cyber Team Help</b>
        </div>
    </div>

    <script>
        async function scanUid() {
            const uid = document.getElementById('uidInput').value;
            if(!uid) return alert("Please enter a UID!");

            document.getElementById('loader').style.display = 'block';
            document.getElementById('resultBox').style.display = 'none';

            try {
                const response = await fetch(`/api/scan?uid=${uid}`);
                const data = await response.json();
                
                document.getElementById('loader').style.display = 'none';
                document.getElementById('resultBox').style.display = 'block';

                if(data.status === "success") {
                    document.getElementById('resName').innerText = data.name || "Private/Not Found";
                    document.getElementById('resLoc').innerText = data.location || "Not Shared Publicly";
                    document.getElementById('resEmail').innerText = data.emails.length > 0 ? data.emails.join(', ') : "Protected";
                    document.getElementById('resPhone').innerText = data.phones.length > 0 ? data.phones.join(', ') : "Protected";
                } else {
                    alert("Error: " + data.message);
                }
            } catch (err) {
                alert("Connection Failed!");
                document.getElementById('loader').style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_INDEX)

@app.route('/api/scan')
def scan():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"status": "error", "message": "UID missing"}), 400

    # Rotating User Agent
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    
    # Proxy Setup (Optional: If you have a proxy list, uncomment below)
    # proxies = {"http": "http://your_proxy", "https": "http://your_proxy"}
    
    try:
        url = f"https://www.facebook.com/{uid}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Basic Scraping Logic
            name_match = re.search(r'<title>(.*?)</title>', content)
            name = name_match.group(1).replace(" | Facebook", "") if name_match else "Unknown"
            
            emails = list(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", content)))
            phones = list(set(re.findall(r"(\+8801|01)[3-9]\d{8}", content)))
            
            # Location attempt (Simple pattern)
            loc_match = re.search(r'Lives in (.*?)(?=")', content)
            location = loc_match.group(1) if loc_match else "Unknown"

            return jsonify({
                "status": "success",
                "name": name,
                "location": location,
                "emails": emails,
                "phones": phones
            })
        else:
            return jsonify({"status": "error", "message": "Access Denied by Facebook"}), 403
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))