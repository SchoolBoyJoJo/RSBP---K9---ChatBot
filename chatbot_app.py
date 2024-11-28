
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
pd.set_option('display.max_colwidth', None)
import gensim.downloader as api
from transformers import pipeline
import dill

data = pd.read_csv('data.csv')

class Model:
    __tfidf_embedding = None
    __tfidf = None
    __transformer_embedding = None
    __transformer = None
    __gensim_embedding= None
    __gensim_model = None
    __data = None
    __classifier = None
    
    def __init__(self, data):
        self.__data = data
        self.__classifier = pipeline("sentiment-analysis")
        self.__tfidf = TfidfVectorizer(ngram_range=(1,2), stop_words='english')
        self.__tfidf_embedding  = self.__tfidf.fit_transform(data['Context'])
        self.__transformer=SentenceTransformer('all-MiniLM-L6-v2')
        self.__transformer_embedding = self.__transformer.encode(data['Context']).tolist()
        self.__gensim_model = api.load('word2vec-google-news-300')
        self.__gensim_embedding = np.array(data['Context'].apply(lambda x: self.__get_sentence_embedding_gensim(x)).tolist())

    def __get_sentimet(self,text):
        result = self.__classifier(text)[0]
        return result['label'].lower()

    def __get_sentence_embedding_gensim(self,sentence):
        words = [word for word in sentence.lower().split() if word in self.__gensim_model]
        if not words:
            return np.zeros(self.__gensim_model.vector_size)
        return np.mean([self.__gensim_model[word] for word in words], axis=0)
    
    def __get_response_gensim(self,user_input):
        user_embedding = self.__get_sentence_embedding_gensim(user_input)
        
        similarities = cosine_similarity(user_embedding.reshape(1,-1), self.__gensim_embedding).flatten()
        
        user_sentiment = self.__get_sentimet(user_input)  # Replace with your sentiment function
        sentiment_similarities = self.__data['Sentiment'].apply(lambda x: 1 if x == user_sentiment else 0)
        
        combined_similarities = similarities * sentiment_similarities
        max_index = combined_similarities.argmax()
        max_score = combined_similarities.max()

        if max_score > 0.85:
            return self.__data.iloc[max_index]['Response'], max_score
        else:
            return "I'm sorry, I don't understand that. Can you rephrase?", max_score
        
    def __get_response_transformer(self,user_input):
        user_embedding = self.__transformer.encode([user_input.lower()])
        similarities = cosine_similarity(user_embedding,self.__transformer_embedding).flatten()
        user_sentiment = self.__get_sentimet(user_input)
        sentiment_similarities = self.__data['Sentiment'].apply(lambda x:1 if x == user_sentiment else 0)

        similarities = similarities * sentiment_similarities

        max_index = similarities.argmax()
        max_score = similarities.max()
        
        if similarities[max_index] > 0.5:
            return self.__data.iloc[max_index]['Response'], max_score
        else:
            return "I'm sorry, I don't understand that. Can you rephrase?", max_score

        
    def __get_response_tfidf(self,user_input):
        user_tfidf = self.__tfidf.fit(data['Context']).transform([user_input])
        tfidf_similarities = cosine_similarity(user_tfidf, self.__tfidf_embedding).flatten()
        user_sentiment = self.__get_sentimet(user_input)
        sentiment_similarities = self.__data['Sentiment'].apply(lambda x:2 if x == user_sentiment else 0)

        combine_similarities = tfidf_similarities * sentiment_similarities

        max_index = combine_similarities.argmax()
        max_score = combine_similarities.max()
        
        if combine_similarities[max_index] > 0.5:
            return self.__data.iloc[max_index]['Response'],max_score
        else:
            return "I'm sorry, I don't understand that. Can you rephrase?", max_score

    def get_response(self,user_input):
        model1, _ = self.__get_response_tfidf(user_input)
        model2, score2 = self.__get_response_transformer(user_input)
        model3, score3 = self.__get_response_gensim(user_input)
        if score2 > 0.6:
            return model2
        elif score3 > 0.85:
            return model3
        else:
            return model1
    

# Load the pre-trained model
with open('custom_model3.pkl', 'rb') as f:
    model = dill.load(f)

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    if not user_input:
        return jsonify({'response': 'Please provide a message!'}), 400

    response = model.get_response(user_input)
    return jsonify({'response': response})

    # # Respons dummy sementara
    # response = f"Echo: {user_input}"
    # return jsonify({'response': response})


if __name__ == '__main__':
    app.run(debug=True)
