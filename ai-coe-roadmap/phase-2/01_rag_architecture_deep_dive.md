# 01. RAG (검색 증강 생성) 아키텍처 심층 분석

## 왜 RAG인가?
LLM은 "학습된 시점"까지만 정보를 알고 있으며, "우리 회사의 비공개 데이터"는 전혀 모릅니다.
데이터를 LLM에게 새로 학습(Fine-tuning)시키는 것은 비용이 매우 비싸고, 데이터가 바뀔 때마다 다시 학습해야 하는 치명적인 단점이 있습니다.
**RAG (Retrieval-Augmented Generation)**는 **"시험 볼 때 오픈북(Open Book)을 허용하는 것"**과 같습니다. LLM이 모르는 내용을 외부 도서관(Vector DB)에서 찾아보고(Retrieval), 그 내용을 참고해서 답변(Generation)하게 만드는 기술입니다.

---

## 핵심 파이프라인 (Pipeline)

### 1. 전처리 및 적재 (Ingestion)
사용자가 질문하기 전에 미리 해워야 하는 작업입니다.
1. **Load**: PDF, Word, 웹페이지 등에서 텍스트를 추출합니다.
2. **Chunk**: 텍스트를 적절한 크기(예: 300~500자)로 자릅니다. (매우 중요)
3. **Embed**: 잘린 텍스트를 AI가 이해할 수 있는 **숫자 벡터**로 변환합니다.
4. **Store**: 벡터를 **Vector DB**에 저장합니다.

### 2. 검색 및 생성 (Retrieval & Generation)
사용자가 질문을 했을 때 일어나는 과정입니다.
1. **Query Embedding**: 사용자의 질문(Query)을 같은 방식으로 숫자 벡터로 변환합니다.
2. **Similarity Search**: Vector DB에서 질문 벡터와 가장 거리가 가까운(유사한) 텍스트 조각들을 찾습니다.
3. **Prompting**: 찾은 조각(Context)들을 프롬프트에 끼워넣습니다.
   > "다음 내용을 참고해서 질문에 답해줘: [검색된 내용]"
4. **Generation**: LLM이 완성된 프롬프트를 보고 답변을 생성합니다.

---

## Deep Dive: Vector & Embedding

### 임베딩(Embedding)이란?
사람의 언어를 컴퓨터가 계산할 수 있는 **좌표(숫자 배열)**로 바꾸는 것입니다.
단순히 단어를 숫자로 바꾸는 게 아니라, **"의미(Semantics)"**를 숫자로 표현합니다.

- **기존 키워드 검색**: "맛있는 사과" 검색 -> "맛있는", "사과" 단어가 포함된 문서를 찾음.
- **벡터 검색 (Semantic Search)**: "맛있는 사과" 검색 -> "달콤한 과일", "아삭한 부사" 등 **단어는 다르지만 의미가 비슷한** 문서를 찾음.

### Vector DB
일반적인 DB(SQL)는 정확히 일치하는 값을 찾는 데 특화되어 있지만, Vector DB는 **"비슷한(Similar)"** 값을 찾는 데 특화되어 있습니다.
- **주요 알고리즘**: Cosine Similarity(코사인 유사도), Euclidean Distance(유클리드 거리)
- **대표적인 도구**:
    - **Open Source (Local)**: ChromaDB, FAISS, Milvus
    - **Cloud (Managed)**: Pinecone, Weaviate

---

![RAG Flow](https://mermaid.ink/img/pako:eNpVkMtqwzAQRX9FzKpF_AAfC6F0001l0013jS0_EmtG0kiWjSHk3ys7LaQggXPvPcxoZgZtTIIPBtsK94oWigm8V7QgW8YKLy_PjzzP0yXPP8gq52dC8j-fF-Q4O19Q-M4Lcl_XG_J5fCa73Y5sNhtyMpl0YwV9Mh6f9C_oT19Bf4I-GI_P-hf0p6-gP0EfjMcX_Qv601fQn6APxuOb_gX96SvoT9AH4_Fd_4L-9BX0J-iD8fiuf0F_-gr6E_TBeHw_qJ8K2lW0oExZSquK1vQz2jBqtLaM0doyagzWljFaW0aNwRr7h-f7BwYdM3U?type=png)
*(Mermaid 다이어그램이 렌더링되지 않을 수 있으니 개념적으로 이해해 주세요: User Query -> Embedding -> Vector Search -> Context Injection -> LLM Answer)*
