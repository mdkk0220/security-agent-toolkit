from flask import Flask, request

app = Flask(__name__)


@app.route("/alert", methods=["POST"])
def alert():
    data = request.get_json()
    print("[알림 받음]", data["text"])
    return {"ok": True}


app.run(port=5001)
