import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# 1. Define a tailored FAQ dataset for your store (replace "MyTechStore" with your store name)
faq_data = [
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
    },
]

# 2. Load an embedding model to compute FAQ embeddings
embedder = SentenceTransformer('all-MiniLM-L6-v2')
faq_texts = [item["question"] for item in faq_data]
faq_embeddings = embedder.encode(faq_texts, convert_to_tensor=False)
faq_embeddings = np.array(faq_embeddings).astype("float32")

# 3. Build a FAISS index for fast similarity search (using L2 distance)
dimension = faq_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(faq_embeddings)

# 4. Load a free generative model (Flan-T5) to synthesize a final answer
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
gen_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")


def retrieve_faq_context(query, k=2):
    """
    Compute the embedding for the query, retrieve top-k similar FAQ entries,
    and return them as a formatted text block.
    """
    query_embedding = embedder.encode([query], convert_to_tensor=False)
    query_embedding = np.array(query_embedding).astype("float32")
    distances, indices = index.search(query_embedding, k)
    retrieved = []
    for idx in indices[0]:
        faq = faq_data[idx]
        retrieved.append(f"Q: {faq['question']}\nA: {faq['answer']}")
    return "\n\n".join(retrieved)


def generate_answer(query):
    """
    Retrieve FAQ context and generate a tailored final answer using a generative model.
    """
    context = retrieve_faq_context(query, k=2)
    prompt = (
        "Below are some frequently asked questions and their answers from MyTechStore:\n"
        f"{context}\n\n"
        "Based on the above, answer the following question in a way that is tailored to MyTechStore:\n"
        f"{query}"
    )
    inputs = tokenizer(prompt, return_tensors="pt",
                       truncation=True, max_length=512)
    outputs = gen_model.generate(**inputs, max_new_tokens=100)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer

# Example usage:
# if __name__ == "__main__":
#     # User query
#     user_query = "How can i buy the phones?"
#     final_answer = generate_answer(user_query)
#     print("Final Answer:")
#     print(final_answer)
