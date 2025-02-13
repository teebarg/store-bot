# # First, ensure you have the correct packages installed:
# # pip install --upgrade pip
# # pip install faiss-cpu numpy sentence-transformers transformers torch

# import os
# os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Prevent tokenizer warnings

# import faiss
# import numpy as np
# import torch
# from sentence_transformers import SentenceTransformer
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# import gc  # For garbage collection

# class FAQChatbot:
#     def __init__(self):
#         self.faq_data = [
#             {
#                 "question": "What is your return policy?",
#                 "answer": "Our return policy allows returns within 30 days of purchase with a receipt."
#             },
#             {
#                 "question": "How can I track my order?",
#                 "answer": "You can track your order via the tracking link sent to your email after purchase."
#             },
#             {
#                 "question": "Do you offer international shipping?",
#                 "answer": "Yes, we offer international shipping to select countries; shipping costs may vary."
#             },
#             {
#                 "question": "How do I reset my password?",
#                 "answer": "You can reset your password by clicking the 'Forgot Password' link on the login page."
#             },
#             {
#                 "question": "How can I buy the phones?",
#                 "answer": "At MyTechStore, you can buy the phones directly from our website. Simply visit our Phones category, select your desired model, add it to your cart, and complete the checkout process."
#             }
#         ]

#         # Initialize models with proper error handling
#         self._initialize_models()

#     def _initialize_models(self):
#         """Initialize models with proper error handling"""
#         try:
#             # Load embedding model
#             self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

#             # Compute and store FAQ embeddings
#             faq_texts = [item["question"] for item in self.faq_data]
#             self.faq_embeddings = self.embedder.encode(
#                 faq_texts,
#                 convert_to_tensor=False,
#                 show_progress_bar=False
#             )
#             self.faq_embeddings = np.ascontiguousarray(  # Ensure memory alignment
#                 self.faq_embeddings.astype(np.float32)
#             )

#             # Initialize FAISS index with proper memory alignment
#             self.dimension = self.faq_embeddings.shape[1]
#             self.index = faiss.IndexFlatL2(self.dimension)
#             self.index.add(self.faq_embeddings)

#             # Load tokenizer and model
#             self.tokenizer = AutoTokenizer.from_pretrained(
#                 "google/flan-t5-base",
#                 use_fast=True
#             )
#             self.gen_model = AutoModelForSeq2SeqLM.from_pretrained(
#                 "google/flan-t5-base"
#             ).cpu()

#             # Force garbage collection
#             gc.collect()
#             torch.cuda.empty_cache() if torch.cuda.is_available() else None

#         except Exception as e:
#             print(f"Initialization error: {str(e)}")
#             raise

#     def retrieve_faq_context(self, query, k=2):
#         """Retrieve similar FAQ entries"""
#         try:
#             # Encode query with proper memory handling
#             query_embedding = self.embedder.encode(
#                 [query],
#                 convert_to_tensor=False,
#                 show_progress_bar=False
#             )
#             query_embedding = np.ascontiguousarray(
#                 query_embedding.astype(np.float32)
#             )

#             # Search index
#             distances, indices = self.index.search(query_embedding, k)

#             # Collect results
#             retrieved = []
#             for idx in indices[0]:
#                 faq = self.faq_data[idx]
#                 retrieved.append(f"Q: {faq['question']}\nA: {faq['answer']}")

#             return "\n\n".join(retrieved)

#         except Exception as e:
#             print(f"Retrieval error: {str(e)}")
#             return ""

#     def generate_answer(self, query):
#         """Generate final answer"""
#         try:
#             # Get context
#             context = self.retrieve_faq_context(query, k=2)
#             prompt = (
#                 "Below are some frequently asked questions and their answers from MyTechStore:\n"
#                 f"{context}\n\n"
#                 "Based on the above, answer the following question in a way that is tailored to MyTechStore:\n"
#                 f"{query}"
#             )

#             # Generate answer with proper memory handling
#             with torch.no_grad():
#                 inputs = self.tokenizer(
#                     prompt,
#                     return_tensors="pt",
#                     truncation=True,
#                     max_length=512
#                 )

#                 outputs = self.gen_model.generate(
#                     **inputs,
#                     max_new_tokens=100,
#                     num_beams=4,
#                     length_penalty=2.0,
#                     early_stopping=True
#                 )

#                 answer = self.tokenizer.decode(
#                     outputs[0],
#                     skip_special_tokens=True
#                 )

#             # Clean up
#             del inputs, outputs
#             gc.collect()
#             torch.cuda.empty_cache() if torch.cuda.is_available() else None

#             return answer

#         except Exception as e:
#             print(f"Generation error: {str(e)}")
#             return "I apologize, but I encountered an error generating the response."

#     def __del__(self):
#         """Cleanup when the object is destroyed"""
#         try:
#             del self.embedder
#             del self.gen_model
#             del self.tokenizer
#             del self.index
#             gc.collect()
#             torch.cuda.empty_cache() if torch.cuda.is_available() else None
#         except:
#             pass

# def main():
#     try:
#         # Initialize chatbot
#         print("Initializing chatbot...")
#         chatbot = FAQChatbot()

#         # Test query
#         print("\nProcessing query...")
#         user_query = "How can I buy the phones?"
#         final_answer = chatbot.generate_answer(user_query)
#         print("\nFinal Answer:")
#         print(final_answer)

#     except Exception as e:
#         print(f"Main execution error: {str(e)}")

# if __name__ == "__main__":
#     main()


# Required packages:
# pip install numpy sentence-transformers transformers torch

import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import gc

class SimpleFAQChatbot:
    def __init__(self):
        # General conversation patterns
        self.conversation_patterns = {
            "greeting": ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"],
            "goodbye": ["bye", "goodbye", "see you", "farewell", "good night"],
            "thanks": ["thank", "thanks", "appreciate", "grateful"],
        }

        # General responses
        self.responses = {
            "greeting": "Hi! How can I help you today?",
            "goodbye": "Goodbye! Have a great day!",
            "thanks": "You're welcome! Let me know if you need anything else.",
            "default": "I'm here to help you with any questions about our products and services. What would you like to know?"
        }
        self.faq_data = [
            {
                "question": "What is your return policy?",
                "answer": "Our return policy allows returns within 30 days of purchase with a receipt."
            },
            {
                "question": "How can I track my order?",
                "answer": "You can track your order via the tracking link sent to your email after purchase."
            },
            {
                "question": "Do you offer international shipping?",
                "answer": "Yes, we offer international shipping to select countries; shipping costs may vary."
            },
            {
                "question": "How do I reset my password?",
                "answer": "You can reset your password by clicking the 'Forgot Password' link on the login page."
            },
            {
                "question": "How can I buy the phones?",
                "answer": "At MyTechStore, you can buy the phones directly from our website. Simply visit our Phones category, select your desired model, add it to your cart, and complete the checkout process."
            }
        ]

        self._initialize_models()

    def _initialize_models(self):
        """Initialize models"""
        try:
            print("Loading embedding model...")
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

            print("Computing FAQ embeddings...")
            faq_texts = [item["question"] for item in self.faq_data]
            self.faq_embeddings = self.embedder.encode(
                faq_texts,
                convert_to_tensor=True,
                show_progress_bar=False
            )

            print("Loading language model...")
            self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
            self.gen_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base").cpu()

            gc.collect()
            torch.cuda.empty_cache() if torch.cuda.is_available() else None

        except Exception as e:
            print(f"Initialization error: {str(e)}")
            raise

    def is_general_conversation(self, query):
        """Check if the query is a general conversation pattern"""
        query_lower = query.lower()

        for pattern_type, patterns in self.conversation_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return True, pattern_type
        return False, None

    def cosine_similarity(self, a, b):
        """Compute cosine similarity between two vectors"""
        return torch.nn.functional.cosine_similarity(a, b, dim=1)

    def retrieve_faq_context(self, query, k=2):
        """Retrieve similar FAQ entries using cosine similarity"""
        try:
            query_embedding = self.embedder.encode(
                query,
                convert_to_tensor=True,
                show_progress_bar=False
            )

            similarities = self.cosine_similarity(
                query_embedding.unsqueeze(0),
                self.faq_embeddings
            )

            top_k_indices = torch.topk(similarities, k=k).indices.tolist()
            retrieved_faqs = [self.faq_data[idx] for idx in top_k_indices]

            # Check if the best match has high enough similarity
            max_similarity = torch.max(similarities).item()
            if max_similarity < 0.5:  # Threshold for FAQ matching
                return "", []

            context = "\n\n".join([f"Q: {faq['question']}\nA: {faq['answer']}" for faq in retrieved_faqs])
            return context, retrieved_faqs

        except Exception as e:
            print(f"Retrieval error: {str(e)}")
            return "", []

    def generate_answer(self, query):
        """Generate final answer"""
        try:
            # Check for general conversation patterns first
            is_general, conv_type = self.is_general_conversation(query)
            if is_general:
                print(f"Detected general conversation: {conv_type}")
                return self.responses.get(conv_type, self.responses["default"]), []

            # If not a general conversation, proceed with FAQ matching
            context, relevant_faqs = self.retrieve_faq_context(query, k=2)

            # If no relevant FAQs found, return default response
            if not context:
                return self.responses["default"], []

            prompt = (
                "Below are some frequently asked questions and their answers from MyTechStore:\n"
                f"{context}\n\n"
                "Based on the above, answer the following question in a way that is tailored to MyTechStore:\n"
                f"{query}"
            )

            with torch.no_grad():
                inputs = self.tokenizer(
                    prompt,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512
                )

                outputs = self.gen_model.generate(
                    **inputs,
                    max_new_tokens=100,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True
                )

                answer = self.tokenizer.decode(
                    outputs[0],
                    skip_special_tokens=True
                )

            del inputs, outputs
            gc.collect()
            torch.cuda.empty_cache() if torch.cuda.is_available() else None

            return answer, relevant_faqs

        except Exception as e:
            print(f"Generation error: {str(e)}")
            return "I apologize, but I encountered an error generating the response.", []

    def __del__(self):
        """Cleanup"""
        try:
            del self.embedder
            del self.gen_model
            del self.tokenizer
            gc.collect()
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
        except:
            pass

def main():
    try:
        print("Initializing chatbot...")
        chatbot = SimpleFAQChatbot()

        print("\nProcessing query...")
        user_query = "Do you ship internationally?"
        final_answer, relevant_faqs = chatbot.generate_answer(user_query)
        print("\nFinal Answer:")
        print(final_answer)
        print(relevant_faqs)

    except Exception as e:
        print(f"Main execution error: {str(e)}")

if __name__ == "__main__":
    main()