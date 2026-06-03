from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "VERSION-RAJIB-TEST"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "WEBHOOK-ACTIVE"
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
