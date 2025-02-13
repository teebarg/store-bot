import os

import torch
from sentence_transformers import SentenceTransformer, util
import re
import yaml


class SimpleFAQChatbot:
    def __init__(self):
        self.faq_data = [
            {"question": "What is the name of your store?", "answer": "Our store is called E-Shop."},
            {"question": "What do you sell?", "answer": "We offer a wide range of products including electronics, clothing, home goods, and more."},
            {"question": "How can I track my order?", "answer": "You can track your order by entering your order ID in the 'Track Order' section of the app."},
            {"question": "What is your return policy?", "answer": "We accept returns within 30 days of delivery. Please ensure the product is unused and in its original packaging."},
            {"question": "How do I contact customer support?", "answer": "You can contact customer support via email at support@ecommerce.com or call us at +1-800-123-4567."},
            {"question": "Where is my order?", "answer": "You can check the status of your order by visiting the 'Track Order' section and entering your order ID."},
            {"question": "Can I cancel my order?", "answer": "Yes, you can cancel your order before it is shipped. Go to 'My Orders' and select 'Cancel Order'."},
            {"question": "How long does shipping take?", "answer": "Shipping usually takes 3-5 business days within the US. International shipping may take 7-10 business days."},
            {"question": "Do you offer international shipping?", "answer": "Yes, we offer international shipping to most countries. Shipping fees and delivery times vary by location."},
            {"question": "What payment methods do you accept?", "answer": "We accept credit cards, debit cards, PayPal, and Apple Pay."},
            {"question": "Is my payment information secure?", "answer": "Yes, we use SSL encryption to ensure your payment information is secure."},
            {"question": "How do I apply a discount code?", "answer": "You can enter your discount code during checkout in the 'Payment' section."}
        ]

        # General conversation patterns
        self.conversation_patterns = self.load_intents()

        # General responses
        self.responses = {
            "greet": "Hi! How can I help you today?",
            "goodbye": "Goodbye! Have a great day!",
            "thanks": "You're welcome! Let me know if you need anything else.",
            "check": "I'm doing well, thank you! How can I assist you today?",
            "default": "I'm here to help you with any questions about our products and services. What would you like to know?",
            "help": "I'm here to help you with any questions about our products and services. What would you like to know?",
        }

        self._initialize_models()


    def load_intents(self):
        """
        Loads the intents and examples from a YAML file and returns a dictionary
        mapping intent names to a list of example phrases.
        """
        with open(os.path.join(os.path.dirname(__file__), 'intents.yaml'), 'r') as file:
            data = yaml.safe_load(file)

        conversation_patterns = {}
        for item in data["nlu"]:
            intent = item["intent"]
            # Each example line in the block starts with "- " so split and clean up
            examples = [line.strip()[2:].strip() for line in item["examples"].split("\n") if line.strip().startswith("- ")]
            conversation_patterns[intent] = examples
        return conversation_patterns

    def normalize_text(self, text):
        """
        Lowercases the text, removes punctuation, and trims extra spaces.
        """
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()

    def _initialize_models(self):
        """Initialize models"""
        try:
            # Initialize the sentence embedding model
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

            # Pre-compute embeddings for all FAQ questions
            self.faq_questions = [faq['question'] for faq in self.faq_data]
            self.faq_embeddings = self.embedder.encode(self.faq_questions, convert_to_tensor=True)

        except Exception as e:
            print(f"Initialization error: {str(e)}")
            raise

    def is_general_conversation2(self, query):
        """Check if the query is a general conversation pattern"""
        # Normalize the query for robust matching
        norm_query = self.normalize_text(query)

        for intent, patterns in self.conversation_patterns.items():
            for pattern in patterns:
                norm_pattern = self.normalize_text(pattern)
                if norm_pattern in norm_query:
                    return self.responses[intent]

    def is_general_conversation(self, query):
        """Check if the query is a general conversation pattern"""
        for intent, patterns in self.conversation_patterns.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', query, re.IGNORECASE):
                    return self.responses[intent]

    def get_faq_answer(self, query, threshold=0.5):
        # Check for general conversation patterns first
        is_general = self.is_general_conversation(query)
        if is_general:
            return is_general

        # Compute the embedding for the query
        query_embedding = self.embedder.encode(query, convert_to_tensor=True)

        # Compute cosine similarities between query and FAQ embeddings
        cos_scores = util.cos_sim(query_embedding, self.faq_embeddings)[0]

        # Get the top result from the similarity scores
        top_result = torch.topk(cos_scores, k=1)
        score = top_result.values.item()
        idx = top_result.indices.item()

        # Return the corresponding answer if the score meets the threshold, otherwise fallback
        if score >= threshold:
            return self.faq_data[idx]['answer']
        else:
            return "Sorry, I couldn't find an answer to your question."
