# 03. LLM 연결과 프롬프트 패턴

검색된 문서 조각(Context)을 LLM에게 어떻게 줘야 할까요? 이것이 **Connecting** 입니다.

## The "Context Injection" Pattern

가장 표준적인 RAG 프롬프트 구조입니다.

```text
너는 [회사의 지식을 기반으로 답변하는 AI 비서]야.
아래 제공된 [Context]를 바탕으로 사용자의 [Question]에 답변해.

### 규칙
1. [Context]에 없는 내용은 절대 지어내지 마.
2. [Context]로 충분하지 않으면 "정보가 부족하여 알 수 없습니다"라고 답해.
3. 답변은 친절하고 전문적인 어조로 작성해.

### Context (검색된 자료)
---
{retrieved_chunk_1}
---
{retrieved_chunk_2}
---
{retrieved_chunk_3}
---

### Question (사용자 질문)
{user_query}

### Answer
```

## Hallucination 방지 (Grounding)

RAG의 가장 큰 적은 '환각'입니다. 검색된 내용에 없는데도 아는 척 답변하는 것을 막아야 합니다.

1. **"지식의 출처를 밝혀라"**:
   - "답변할 때, Context의 어느 부분을 참고했는지 인용(Citation)해줘." 라고 지시합니다.
   - 예: "제품 보증 기간은 1년입니다 (참고: 서비스운영안 4페이지)."

2. **"Strict Mode"**:
   - 프롬프트에 "네가 가진 사전 지식(Pre-trained Knowledge)을 사용하지 말고, 오직 Context만 믿어."라고 강하게 제약을 겁니다.

## Conversation History (대화 문맥 유지)

사용자가 "그거 얼마야?"라고 물었을 때, 이전 질문이 "아이폰 15"였다는 것을 알아야 합니다.
RAG 시스템을 구축할 때 Query를 Vector DB에 던지기 전에 **Standalone Query(독립된 질문)**로 변환하는 과정이 필요합니다.

- **대화 이력**:
  - User: "아이폰 15 기능 알려줘."
  - AI: (답변...)
  - User: "가격은?"
- **검색 쿼리 변환**:
  - "가격은?" -> (LLM에게 변환 요청) -> **"아이폰 15의 가격은 얼마인가요?"** -> Vector DB 검색
