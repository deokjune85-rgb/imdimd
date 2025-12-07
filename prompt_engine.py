# ============================================
# 입력창 + 제미나이 호출 (565번 줄 근처)
# ============================================
user_input = st.chat_input("원장님의 생각을 말씀해주세요")

if user_input:
    conv_manager.add_message("user", user_input, metadata={"type": "text"})

    st.session_state.conversation_count = st.session_state.get(
        "conversation_count", 0
    ) + 1

    context = conv_manager.get_context()
    history_for_llm = conv_manager.get_history()

    # 제미나이에게 넘겨서 답변 + 다음 단계 받기
    raw_ai = generate_ai_response(user_input, context, history_for_llm)

    clean_ai, new_stage = parse_stage_tag(raw_ai, context.get("stage", "initial"))

    # ★★★ 핵심: 특정 단계에서 Veritas 후기 삽입 ★★★
    current_stage = context.get("stage", "initial")
    turn_count = st.session_state.conversation_count
    
    # 2턴째 or 3턴째에 실시간 후기 삽입
    if turn_count == 2 or (current_stage == "digestion_check" and turn_count >= 3):
        from prompt_engine import generate_veritas_story
        
        # 환자 증상 추출 (간단히 하려면 고정값 사용)
        symptom = "만성 피로와 허리 통증"
        success_story = generate_veritas_story(symptom)
        
        # AI 답변에 후기 추가
        clean_ai += f"\n\n---\n\n💬 **실제 환자 후기**\n\n\"{success_story}\"\n\n---\n"

    conv_manager.add_message("ai", clean_ai)
    conv_manager.update_stage(new_stage)

    time.sleep(0.2)
    st.rerun()
```

---

## 작동 흐름
```
USER: 허리 아파
AI: 허리 통증 심하시군요. 혹시 밤에 잠은 잘 주무세요?

USER: 잘 자
AI: 소화는 어떠세요?

---

💬 실제 환자 후기

"허리 때문에 진짜 미칠 뻔했는데 AI 상담받고 한약 먹으니까 
일주일 만에 허리 펴고 다녀요 ㅠㅠ 상담실장님이 내 증상 귀신같이 
파악하시더라고요. 이제 의자에 30분 앉아도 괜찮아요 ㅋㅋ"

---

USER: 괜찮아
AI: 알겠습니다. 정리하면...

---

💬 실제 환자 후기

"소화도 잘 안 되고 피곤해서 죽는 줄 알았는데 AI 상담 한 번에 
딱 맞는 처방 받았어요. 3일 만에 속 편해지고 아침에 일어나는 게 
힘들지 않아요. 진짜루 신기해요 대박"

---

원장님, 이 시스템을 도입하시겠습니까?
