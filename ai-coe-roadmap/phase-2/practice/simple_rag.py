import os
import requests
import numpy as np
from sentence_transformers import SentenceTransformer

# Settings
LLM_API_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3"  # Changing to available model

def load_knowledge_base(file_path):
    """
    Load the text file and split it into chunks based on sections.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    chunks = []
    current_chunk = []
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
        else:
            current_chunk.append(line)
    
    if current_chunk:
        chunks.append("\n".join(current_chunk))
        
    return chunks

def get_embeddings(texts, model):
    """
    Convert a list of texts into vectors (embeddings).
    """
    embeddings = model.encode(texts)
    return embeddings

def retrieve(query, chunk_embeddings, chunks, model, top_k=3):
    """
    Semantic search using Cosine Similarity.
    """
    # 1. Embed the query
    query_embedding = model.encode([query])[0]
    
    # 2. Calculate Cosine Similarity
    # (A . B) / (|A| * |B|)
    # Since sentence_transformers embeddings are often normalized, |A| and |B| are approx 1.
    # So we can just do dot product.
    scores = np.dot(chunk_embeddings, query_embedding)
    
    # 3. Sort and get top_k
    # argsort returns indices of sorted array (ascending), so we take last top_k and reverse
    top_indices = np.argsort(scores)[-top_k:][::-1]
    
    relevant_chunks = []
    for idx in top_indices:
        # Filter out low relevance if needed (e.g., score > 0.3)
        if scores[idx] > 0.3:
            relevant_chunks.append(chunks[idx])
            
    return relevant_chunks

def generate_answer(query, context_chunks):
    """
    Call Ollama API to generate answer.
    """
    if not context_chunks:
        return "죄송합니다. 관련 정보를 찾을 수 없습니다."

    context_text = "\n---\n".join(context_chunks)
    
    prompt = f"""
너는 [회사의 지식을 기반으로 답변하는 AI 비서]야.
아래 제공된 [Context]를 바탕으로 사용자의 [Question]에 답변해.

### 규칙
1. [Context]에 없는 내용은 절대 지어내지 마.
2. [Context]로 충분하지 않으면 "정보가 부족하여 알 수 없습니다"라고 답해.
3. 답변은 친절하고 전문적인 어조로 작성해.
4. 한국어로 답변해.

### Context
{context_text}

### Question
{query}

### Answer
"""
    
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(LLM_API_URL, json=payload)
        response.raise_for_status()
        return response.json().get('response', 'Error: No response field')
    except Exception as e:
        return f"Error calling LLM: {str(e)}"

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    knowledge_file = os.path.join(current_dir, "company_knowledge.txt")
    
    print("Loading knowledge base...")
    chunks = load_knowledge_base(knowledge_file)
    print(f"Loaded {len(chunks)} chunks.")
    
    print("Loading Embedding Model (skt/kogpt2-base-v2 is NOT for embedding, using a multilingual one)...")
    # Using a good multilingual model or Korean specific one
    model_name = "jhgan/ko-sroberta-multitask" 
    print(f"Downloading/Loading model: {model_name}...")
    model = SentenceTransformer(model_name)
    
    print("Creating Embeddings for Knowledge Base...")
    chunk_embeddings = get_embeddings(chunks, model)
    print("Embeddings ready.")
    
    print("\nStarting Chat Session (Type 'exit' to quit)")
    while True:
        user_query = input("\nQ: ").strip()
        if user_query.lower() == 'exit':
            break
        
        if not user_query:
            continue
            
        print(f"\nSearching for match for: '{user_query}'...")
        relevant_chunks = retrieve(user_query, chunk_embeddings, chunks, model)
        
        if not relevant_chunks:
            print("No relevant information found in knowledge base (Score too low).")
            continue
            
        print(f"Found {len(relevant_chunks)} relevant chunks.")
        # Optional: Print retrieved chunks for debugging
        # for i, chunk in enumerate(relevant_chunks):
        #     print(f"--- Chunk {i+1} ---\n{chunk[:100]}...\n")
        
        print("Generating answer with LLM...")
        answer = generate_answer(user_query, relevant_chunks)
        
        print("\nA: " + answer)

if __name__ == "__main__":
    main()
