from flask import Flask, request, jsonify, send_file
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# Load the Excel data
questions_data = pd.read_excel(r"C:\Users\valer\Downloads\Consolidated_questions_with_plaintext.xlsx")
questions_data = questions_data.dropna()  # Clean the data

# Strip whitespace from column names and data
questions_data.columns = questions_data.columns.str.strip()
questions_data['Topic'] = questions_data['Topic'].str.strip()

# Route to serve the index.html file
@app.route('/')
def home():
    return app.send_static_file('index.html')

# Route to serve questions.html
@app.route('/questions')
def questions():
    return app.send_static_file('questions.html')

# Route to get quiz topics
@app.route('/api/quizzes', methods=['GET'])
def get_quiz_topics():
    topics = questions_data['Topic'].unique().tolist()  # Extract unique quiz topics
    return jsonify({"topics": topics})

# Route to get questions for a selected topic
@app.route('/api/questions', methods=['POST'])
def get_questions():
    topic = request.json.get('topic')  # Get the selected topic from the request
    print("Received topic:", topic)  # Debugging

    # Filter questions by topic
    filtered_data = questions_data[questions_data['Topic'] == topic]
    print("Filtered data:", filtered_data)  # Debugging

    if filtered_data.empty:
        print("No data found for topic:", topic)  # Debugging
        return jsonify({"questions": []})  # Return empty list if no data

    # Convert filtered questions to JSON
    questions = filtered_data[['Question', 'Answer']].to_dict(orient='records')
    return jsonify({"questions": questions})

# Route to download selected questions as an Excel file
@app.route('/api/download', methods=['POST'])
def download_questions():
    selected_questions = request.json.get('questions')  # List of selected questions
    print("Selected questions:", selected_questions)  # Debugging

    filtered_data = questions_data[questions_data['Question'].isin(selected_questions)]
    if filtered_data.empty:
        print("No matching questions found.")  # Debugging
        return jsonify({"error": "No matching questions found!"}), 400

    # Create an in-memory bytes buffer
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_data.to_excel(writer, index=False, sheet_name='Selected Questions')

    output.seek(0)
    print("File generated successfully!")  # Debugging

    # Send the file to the client
    return send_file(
        output,
        as_attachment=True,
        download_name="selected_questions.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
