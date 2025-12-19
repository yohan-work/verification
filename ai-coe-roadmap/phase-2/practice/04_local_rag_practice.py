import os

# ==========================================
# [Phase 2 실습] 로컬 RAG 구현하기
# ==========================================
#
# "문서 임베딩 -> 저장 -> 검색" 과정을 수행합니다.
#
# [필수 설치 라이브러리]
# 터미널에서 아래 명령어를 실행해주세요:
# pip install langchain-community langchain-huggingface chromadb sentence-transformers
#
# ==========================================

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_core.documents import Document
except ImportError as e:
    print(f"라이브러리가 설치되지 않았습니다. (Error: {e})")
    print("터미널에 다음을 입력하세요:")
    print("pip install langchain-community langchain-huggingface chromadb sentence-transformers")
    exit()

def main():
    print("1. 로컬 임베딩 모델 로딩 중... (최초 실행 시 다운로드에 시간이 걸립니다)")
    # 한국어 처리에 강력한 오픈소스 모델 사용 (HuggingFace)
    # CPU에서도 무리 없이 돌아가는 경량 모델입니다.
    embedding_model = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask"
    )
    print("모델 로딩 완료!")

    # ---------------------------------------------------------
    # 2. 가상의 사내 데이터 준비 (Document Loading)
    # company_knowledge.txt 파일에서 데이터를 읽어옵니다.
    # ---------------------------------------------------------
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "company_knowledge.txt")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            full_text = f.read()
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return

    # 간단하게 줄바꿈 단위로 문서를 나눕니다. (빈 줄 제외)
    # RecursiveCharacterTextSplitter :: v2
    raw_documents = [line.strip() for line in full_text.split('\n') if line.strip()]
    
    # LangChain Document 형식으로 변환
    docs = [Document(page_content=text) for text in raw_documents]
    print(f"문서 {len(docs)}개를 준비했습니다.")

    # ---------------------------------------------------------
    # 3. Vector DB 생성 및 저장 (Indexing)
    # ---------------------------------------------------------
    # ChromaDB를 사용하여 메모리에 벡터 저장소를 만듭니다.
    print("Vector DB에 데이터를 저장(Indexing) 중...")
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        collection_name="company_knowledge"
    )
    print("저장 완료!")

    # ---------------------------------------------------------
    # 4. 검색 테스트 (Retrieval)
    # ---------------------------------------------------------
    while True:
        print("\n" + "="*50)
        query = input("🔍 궁금한 점을 물어보세요 (종료하려면 'exit' 입력): ")
        
        if query.lower() == 'exit':
            break
            
        print(f"'{query}' 관련 정보를 검색합니다...")
        
        # 유사도 검색 (Similarity Search)
        # k=2 : 가장 유사한 문서 2개만 가져오기
        results = vector_store.similarity_search(query, k=2)
        
        if not results:
            print("관련 정보를 찾지 못했습니다.")
            continue
            
        print("\n[검색 결과]")
        for i, doc in enumerate(results):
            print(f"{i+1}. {doc.page_content}")
            
        print("\n[Tip] 위 검색 결과를 LLM 프롬프트에 넣으면 답변이 완성됩니다.")

if __name__ == "__main__":
    main()
