import dill
import google.generativeai as genai
import markdown
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline

data = pd.read_csv("data.csv")

# Load the pre-trained model
with open("model/model.pkl", "rb") as f:
    model = dill.load(f)

class Model:
    __transformer_embedding = None
    __transformer = None
    __data = None
    __classifier = None
    
    def __init__(self, data):
        self.__data = data
        self.__classifier = pipeline("sentiment-analysis")
        self.__transformer= SentenceTransformer('all-MiniLM-L6-v2')
        self.__transformer_embedding = self.__transformer.encode(data['Context']).tolist()

    def __get_sentimet(self,text):
        result = self.__classifier(text)[0]
        return result['label'].lower()
    def __get_response_transformer(self, user_input):
        user_embedding = self.__transformer.encode([user_input.lower()])
        similarities = cosine_similarity(user_embedding, self.__transformer_embedding).flatten()
        user_sentiment = self.__get_sentimet(user_input)
        sentiment_similarities = self.__data['Sentiment'].apply(lambda x: 1 if x == user_sentiment else 0)

        similarities = similarities * sentiment_similarities
        top_indices = similarities.argsort()[-5:][::-1] 
        max_index = similarities.argmax()

        if similarities[max_index] > 0.70:
            return self.__data.iloc[max_index]['Response']
        else:
            possible_questions = self.__data.iloc[top_indices]['Context'].to_list()
            return  "Sorry, I don't understand. Can you please rephrase your question? " "Or try one of the following questions:<br><ul>" + "".join(f"<li>{question}</li>" for question in possible_questions) + "</ul>"

    def get_response(self,user_input):
        response = self.__get_response_transformer(user_input)
        return response


genai.configure(api_key="AIzaSyDKScvOItxiUhjkv08vJz4htrPnUcqXQaM")
generative_ai = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
CORS(app)

chat_dictionary = {}


@app.route("/<id>", methods=["POST"])
def chat(id):
    user_input = request.json.get("message", "")
    mode = request.json.get("mode", "python")  # Default ke model Python
    if not user_input:
        return jsonify({"response": "Please provide a message!"}), 400

    if id not in chat_dictionary:
        chat_dictionary[id] = {"history": []}
    client_history = chat_dictionary.get(id)["history"]

    response = ""
    if mode == "python":
        response = model.get_response(user_input)
    elif mode == "genai":
        user_input = f"You are a mental health specialist, you only answer questions about mental health and stress management. {user_input}"
        response = (
            generative_ai.start_chat(history=client_history)
            .send_message(user_input)
            .text
        )
    else:
        return jsonify({"response": "Invalid mode selected!"}), 400

    client_history.append({"role": "user", "parts": user_input})
    client_history.append({"role": "model", "parts": response})
    print(client_history)

    return jsonify({"response": markdown.markdown(response)})


if __name__ == "__main__":
    app.run(debug=False)
