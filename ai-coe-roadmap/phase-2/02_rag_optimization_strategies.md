# 02. RAG 정확도 최적화 전략 (Advanced RAG)

RAG 시스템을 만들었더니 엉뚱한 문서를 가져오거나, 답변이 부정확하다면 다음 기술들을 적용해야 합니다. AI CoE 수준에서는 단순 구현을 넘어 **정확도(Accuracy)**를 높이는 튜닝 기술이 핵심입니다.

## 1. Chunking Strategy (청킹 전략)

문서를 어떻게 자르느냐에 따라 검색 성능이 천차만별입니다.

### 왜 자르는가?
LLM의 문맥 창(Context Window)은 한계가 있고, 너무 긴 내용을 넣으면 "Needle in a Haystack(건초더미에서 바늘 찾기)" 현상으로 인해 정작 중요한 정보를 놓칠 수 있습니다.

### 주요 전략
1. **Fixed-size Chunking**: 단순히 글자 수(예: 500자)로 자릅니다. 가장 쉽지만 문장이 중간에 잘려 의미가 훼손될 수 있습니다.
2. **Recursive Character Chunking**: 문단(줄바꿈) -> 문장(마침표) -> 단어(공백) 순서로 의미 단위를 지키며 자릅니다. (가장 추천되는 기본 방식)
3. **Semantic Chunking**: 의미가 급격히 변하는 지점을 AI로 파악해서 자릅니다. 비용이 들지만 정확도가 높습니다.

## 2. Hybrid Search (하이브리드 검색)

벡터 검색(Vector Search)이 만능은 아닙니다. 고유명사나 정확한 모델명 검색엔 약할 수 있습니다.

- **Vector Search**: "화면이 안 나올 때 어떻게 해?" (의미 기반)
- **Keyword Search (BM25)**: "Error-Code-404" (정확한 키워드 매칭)

**Solution**: 두 검색 결과를 가져와서 가중치를 두어 합칩니다 (Weighted Sum).
> 결과 = (Vector Score * 0.7) + (Keyword Score * 0.3)

## 3. Reranking (리랭킹) ⭐ *Accuracy 끝판왕*

Vector Search는 속도가 빠르지만 정확도가 약간 떨어질 수 있습니다(Bi-Encoder 방식).
정확도를 극대화하기 위해 **2단계 검색**을 수행합니다.

1. **Retrieval (1차 검색)**: Vector DB에서 빠르게 후보 문서 50개를 가져옵니다.
2. **Reranking (2차 정렬)**: **Cross-Encoder**라는 더 정밀한 모델을 사용해, 50개 문서와 사용자 질문을 하나하나 꼼꼼히 비교하여 순위를 다시 매깁니다.
3. **Top-K Selection**: 다시 정렬된 순서에서 상위 3~5개만 뽑아서 LLM에게 줍니다.

## 4. Metadata Filtering

"모든 문서"에서 찾지 말고, 범위를 좁힙니다.
예: "2024년 뷰티 트렌드 알려줘"
-> Vector Search만 하면 2020년 자료가 나올 수도 있습니다.
-> **Metadata Filter 적용**: `year == 2024` 조건으로 먼저 필터링한 후 검색합니다.

---

## 💡 실무 팁: "Garbage In, Garbage Out"
아무리 좋은 RAG 기술을 써도, 원본 데이터(PDF, 매뉴얼)가 엉망이면 AI도 답변을 못 합니다.
데이터를 적재하기 전에 **전처리(표 정리, 오타 수정, 무의미한 헤더/푸터 제거)**하는 것이 엔지니어링의 80%입니다.
