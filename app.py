from flask import Flask, request, jsonify, render_template, Response, stream_with_context
from flask_cors import CORS
import google.generativeai as genai
import os
import traceback

app = Flask(__name__)
CORS(app)

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Simplified Professional Data
STRICT_INSTRUCTIONS = """
You are Abel TOH's professional AI Assistant. 
1. Speak in the FIRST PERSON ("I", "my").
2. Use HTML for links: <a href='URL' target='_blank'>Word</a>.
3. Keep responses under 10 lines.
4. Mention the 'Schedule a Meeting' button in the header for calls.

CONTEXT:
I am an IT PMO at TCS (UniCredit). 
Previously Digital Transformation Manager at TotalEnergies (saved 25hrs/week).
MIT Certified in GenAI.
LinkedIn: https://www.linkedin.com/in/abel-gnonsoa-41613b1b7/
Calendar: https://calendar.google.com/calendar/u/0?cid=dG9oY29uc3RhbnRAZ21haWwuY29t
"""

@app.route('/')
def index():
    return render_template('index.html')

def gemini_stream_generator(user_input):
    try:
        # We use generate_content instead of start_chat for higher stability on Free Tier
        full_prompt = f"{STRICT_INSTRUCTIONS}\n\nUser Question: {user_input}"
        
        response = model.generate_content(full_prompt, stream=True)
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        print(f"STREAMING ERROR: {e}")
        yield "I'm having a quick connection hiccup. Could you try asking that again?"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("message")
    
    if not user_input:
        return jsonify({"error": "No message"}), 400

    return Response(
        stream_with_context(gemini_stream_generator(user_input)),
        content_type='text/event-stream'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
