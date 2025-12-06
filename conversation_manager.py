# conversation_manager.py
"""
대화 상태 관리 모듈
"""

import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime


class ConversationManager:
    """대화 히스토리 및 컨텍스트 관리"""
    
    def __init__(self):
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if 'user_context' not in st.session_state:
            st.session_state.user_context = {
                'selected_tongue': None,
                'stage': 'initial',
            }
    
    def add_message(self, role: str, text: str):
        """메시지 추가"""
        message = {
            'role': role,
            'text': text,
            'timestamp': datetime.now().isoformat(),
        }
        st.session_state.chat_history.append(message)
    
    def get_history(self) -> List[Dict]:
        """히스토리 반환"""
        return st.session_state.chat_history
    
    def get_context(self) -> Dict:
        """컨텍스트 반환"""
        return st.session_state.user_context.copy()
    
    def update_stage(self, new_stage: str):
        """단계 업데이트"""
        st.session_state.user_context['stage'] = new_stage
    
    def update_context(self, key: str, value):
        """컨텍스트 특정 키 업데이트"""
        st.session_state.user_context[key] = value
    
    def reset_conversation(self):
        """대화 초기화"""
        st.session_state.chat_history = []
        st.session_state.user_context = {
            'selected_tongue': None,
            'stage': 'initial',
        }
    
    def get_summary(self) -> str:
        """대화 요약"""
        context = st.session_state.user_context
        history_count = len(st.session_state.chat_history)
        
        return f"""
### 대화 요약
- 총 메시지: {history_count}개
- 선택한 혀: {context.get('selected_tongue', '미선택')}
- 현재 단계: {context.get('stage', 'initial')}
"""


def get_conversation_manager() -> ConversationManager:
    """싱글톤 인스턴스 반환"""
    if 'conv_manager' not in st.session_state:
        st.session_state.conv_manager = ConversationManager()
    return st.session_state.conv_manager
