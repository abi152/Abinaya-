from flask import Flask, render_template, request, jsonify, session
import json
import re

app = Flask(__name__)
app.secret_key = "simple-demo-secret"

with open("faq.json", "r", encoding="utf-8") as f:
    FAQS = json.load(f)

def words(text):
    return set(re.findall(r"[a-zA-Z0-9]+", text.lower()))

def retrieve_answer(question):
    q_words = words(question)
    best_score = 0
    best_answer = None

    for item in FAQS:
        item_words = words(item["question"] + " " + item["answer"])
        score = len(q_words & item_words)

        if score > best_score:
            best_score = score
            best_answer = item["answer"]

    return best_answer if best_score > 0 else None

def office_tool():
    return "College office timing: 9:00 AM to 5:00 PM, Monday to Friday."

def agent(question):
    q = question.strip()
    low = q.lower()

    match = re.search(r"my name is ([a-zA-Z ]+)", q, re.I)
    if match:
        name = match.group(1).strip().title()
        session["student_name"] = name
        return f"Nice to meet you, {name}! I will remember your name during this session."

    if "what is my name" in low or "do you know my name" in low:
        name = session.get("student_name")
        return f"Your name is {name}." if name else "You have not told me your name yet."

    if "office" in low and ("time" in low or "timing" in low or "open" in low):
        return office_tool()

    answer = retrieve_answer(q)
    if answer:
        return answer

    return ("Sorry, I do not have that information in my college "
            "knowledge base. Please check with the college office.")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("message", "")

    if not question.strip():
        return jsonify({"answer": "Please type a question."})

    return jsonify({"answer": agent(question)})

if __name__ == "__main__":
    app.run(debug=True)
