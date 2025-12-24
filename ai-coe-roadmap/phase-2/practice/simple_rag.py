import os

def load_knowledge_base(file_path):
    """
    Load the text file and split it into chunks based on sections.
    Assumes sections are separated by double newlines or headers.
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

def retrieve(query, chunks):
    """
    Simple keyword-based retrieval.
    Returns the top 3 most relevant chunks.
    """
    query_tokens = set(query.split())
    
    scores = []
    for chunk in chunks:
        score = sum(1 for token in query_tokens if token in chunk)
        scores.append((score, chunk))
    
    scores.sort(key=lambda x: x[0], reverse=True)
    
    relevant_chunks = [chunk for score, chunk in scores[:3] if score > 0]
    
    if not relevant_chunks and chunks:
        return []
        
    return relevant_chunks

def generate_prompt(query, context_chunks):
    """
    Constructs the prompt using the Context Injection pattern.
    """
    context_text = "\n---\n".join(context_chunks)
    
    prompt = f"""
너는 [회사의 지식을 기반으로 답변하는 AI 비서]야.
아래 제공된 [Context]를 바탕으로 사용자의 [Question]에 답변해.

### 규칙
1. [Context]에 없는 내용은 절대 지어내지 마.
2. [Context]로 충분하지 않으면 "정보가 부족하여 알 수 없습니다"라고 답해.
3. 답변은 친절하고 전문적인 어조로 작성해.

### Context (검색된 자료)
---
{context_text}
---

### Question (사용자 질문)
{query}

### Answer
"""
    return prompt

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    knowledge_file = os.path.join(current_dir, "company_knowledge.txt")
    
    print("Loading knowledge base...")
    chunks = load_knowledge_base(knowledge_file)
    print(f"Loaded {len(chunks)} chunks.")
    
    print("\nStarting Chat Session (Type 'exit' to quit)")
    while True:
        user_query = input("\nQ: ").strip()
        if user_query.lower() == 'exit':
            break
        
        if not user_query:
            continue
            
        print(f"\nSearching for match for: '{user_query}'...")
        relevant_chunks = retrieve(user_query, chunks)
        
        if not relevant_chunks:
            print("No relevant information found in knowledge base.")
            continue
            
        print(f"Found {len(relevant_chunks)} relevant chunks.")
        
        prompt = generate_prompt(user_query, relevant_chunks)
        
        print("\n" + "="*50)
        print("[Generated Prompt for LLM]")
        print("="*50)
        print(prompt)
        print("="*50)
        print("\n(This prompt would be sent to the LLM API to get the final answer.)")

if __name__ == "__main__":
    main()
