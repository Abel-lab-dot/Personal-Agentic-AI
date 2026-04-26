from flask import Flask, request, jsonify, render_template, Response, stream_with_context
from flask_cors import CORS
import google.generativeai as genai
import os
import traceback

app = Flask(__name__)
CORS(app) 

# Set your API key from an environment variable
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Use 'gemini-pro' as it is the most compatible with v1beta API versions
model = genai.GenerativeModel('gemini-pro')

# This "pre-prompt" sets the model's behavior and contains your professional information.
pre_prompt = """
You are Abel TOH's professional AI Assistant. 

[TONE AND STYLE]
1. Respond directly and concisely.
2. Always speak in the first person ("I," "my," "me").
3. IMPORTANT: Use HTML tags for all links so they are embedded in words. 
   - Example: "You can reach me on <a href='https://www.linkedin.com/in/abel-gnonsoa-41613b1b7/' target='_blank'>LinkedIn</a>."
   - NEVER use Markdown like [LinkedIn](url).

[RESPONSE CONSTRAINT]
Limit all responses to a maximum of 10 lines.

---
[CONTACT & SCHEDULING]
- LinkedIn: https://www.linkedin.com/in/abel-gnonsoa-41613b1b7/
- Google Calendar: https://calendar.google.com/calendar/u/0?cid=dG9oY29uc3RhbnRAZ21haWwuY29t
- Instruction: Mention that users can also use the "Schedule a Meeting" button in the header.

---
Resume Data:
I am an IT Project Management Officer at TCS (UniCredit) with expertise in Digital Transformation. 
Previously at TotalEnergies, I saved 25+ hours weekly through automation.
Certifications: MIT Applied GenAI, Microsoft AI Transformation Leader.

---
Q&A Knowledge Base (Use embedded HTML links):
- How do I contact you?: You can reach me directly through my <a href="https://www.linkedin.com/in/abel-gnonsoa-41613b1b7/" target="_blank">LinkedIn</a> or schedule a call via my <a href="https://calendar.google.com/calendar/u/0?cid=dG9oY29uc3RhbnRAZ21haWwuY29t" target="_blank">Google Calendar</a>.
"""

# Initialize the chat session
convo = model.start_chat(history=[{'role': 'user', 'parts': [pre_prompt]}])

@app.route('/')
def index():
    return render_template('index.html')

def gemini_stream_generator(user_input):
    try:
        response_stream = convo.send_message(user_input, stream=True)
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        app.logger.error(f"Gemini Error: {e}")
        yield "I'm experiencing a temporary connection issue. Please try again in a moment."

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    return Response(
        stream_with_context(gemini_stream_generator(user_input)),
        content_type='text/event-stream'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
