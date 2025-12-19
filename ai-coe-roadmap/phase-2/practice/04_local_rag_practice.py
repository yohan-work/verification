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
    from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader
except ImportError as e:
    print(f"라이브러리가 설치되지 않았습니다. (Error: {e})")
    print("터미널에 다음을 입력하세요:")
    print("pip install langchain-community langchain-huggingface chromadb sentence-transformers pypdf")
    exit()

def load_document(file_path):
    """파일 확장자에 따라 적절한 로더를 선택하여 문서를 로드합니다."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        print(f" PDF 파일을 로드합니다: {file_path}")
        loader = PyPDFLoader(file_path)
        return loader.load()
    elif ext == '.csv':
        print(f" CSV 파일을 로드합니다: {file_path}")
        loader = CSVLoader(file_path)
        return loader.load()
    elif ext == '.txt':
        print(f" 텍스트 파일을 로드합니다: {file_path}")
        loader = TextLoader(file_path, encoding='utf-8')
        return loader.load()
    else:
        print(f" 지원하지 않는 파일 형식입니다: {ext}")
        return []

def main():
    print("1. 로컬 임베딩 모델 로딩 중... (최초 실행 시 다운로드에 시간이 걸립니다)")
    # 한국어 처리에 강력한 오픈소스 모델 사용 (HuggingFace)
    embedding_model = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask"
    )
    print("모델 로딩 완료!")

    # ---------------------------------------------------------
    # 2. 문서 로딩 (Document Loading)
    # ---------------------------------------------------------
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 기본값은 company_knowledge.txt, 하지만 사용자가 다른 파일을 지정할 수 있게 함
    print(f"\n 현재 폴더({current_dir})에 있는 파일을 로드할 수 있습니다.")
    target_filename = input("로드할 파일명을 입력하세요 (엔터 치면 'company_knowledge.txt' 사용): ").strip()
    
    if not target_filename:
        target_filename = "company_knowledge.txt"
        
    file_path = os.path.join(current_dir, target_filename)
    
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return

    docs = load_document(file_path)
    
    if not docs:
        print("문서 로드에 실패했거나 내용이 없습니다.")
        return
        
    print(f"✅ 총 {len(docs)}개의 페이지(또는 청크)를 로드했습니다.")

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
        query = input("궁금한 점을 물어보세요 (종료하려면 'exit' 입력): ")
        
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
