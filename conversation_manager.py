"""
IMD Sales Bot - Conversation State Management
대화 히스토리, 컨텍스트, 사용자 의도 관리
비주얼 예진 센터 플로우 지원
"""

import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime
import re

class ConversationManager:
    """대화 상태 및 컨텍스트 관리 클래스"""
    
    def __init__(self):
        """세션 상태 초기화"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if 'user_context' not in st.session_state:
            st.session_state.user_context = {
                'user_type': 'visitor',       # 방문자 타입
                'selected_symptom': None,     # 선택한 증상/항목
                'selected_tongue': None,      # 선택한 혀/스타일
                'health_score': 0,            # 종합 점수
                'pain_point': None,           # 주요 고민
                'urgency': None,              # 긴급도
                'budget_sense': None,         # 가격 민감도
                'trust_level': 0,             # 신뢰도 (0-100)
                'stage': 'initial',           # 대화 단계
                'keywords': [],               # 언급된 키워드들
                'objections': [],             # 반박/우려 사항
            }
        
        if 'interaction_count' not in st.session_state:
            st.session_state.interaction_count = 0
    
    def add_message(self, role: str, text: str, metadata: Optional[Dict] = None):
        """
        대화 히스토리에 메시지 추가
        
        Args:
            role: 'ai' or 'user'
            text: 메시지 내용
            metadata: 추가 정보 (버튼 클릭, 의도 등)
        """
        message = {
            'role': role,
            'text': text,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        st.session_state.chat_history.append(message)
        
        # 인터랙션 카운트 증가 (신뢰도 계산용)
        if role == 'user':
            st.session_state.interaction_count += 1
            self._update_trust_level()
            self._extract_context(text, metadata)
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        대화 히스토리 조회
        
        Args:
            limit: 최근 N개만 조회 (None이면 전체)
        
        Returns:
            메시지 리스트
        """
        history = st.session_state.chat_history
        if limit:
            return history[-limit:]
        return history
    
    def get_context(self) -> Dict:
        """
        현재 대화 컨텍스트 반환 (Gemini에 전달용)
        
        Returns:
            컨텍스트 딕셔너리
        """
        return st.session_state.user_context.copy()
    
    def get_formatted_history(self, for_llm: bool = True) -> str:
        """
        LLM에 전달할 포맷의 대화 히스토리
        
        Args:
            for_llm: LLM용 포맷 여부
        
        Returns:
            포맷팅된 대화 내역
        """
        history = self.get_history(limit=10)  # 최근 10개만 (토큰 절약)
        
        if for_llm:
            formatted = []
            for msg in history:
                role_label = "고객" if msg['role'] == 'user' else "AI"
                formatted.append(f"{role_label}: {msg['text']}")
            return "\n".join(formatted)
        else:
            return history
    
    def _extract_context(self, text: str, metadata: Optional[Dict] = None):
        """
        사용자 입력에서 컨텍스트 추출 (키워드 기반 + 메타데이터)
        
        Args:
            text: 사용자 메시지
            metadata: 클릭/선택 정보
        """
        text_lower = text.lower()
        context = st.session_state.user_context
        
        # 메타데이터에서 직접 추출
        if metadata:
            if metadata.get('type') == 'symptom_select':
                context['selected_symptom'] = metadata.get('value')
            elif metadata.get('type') == 'tongue_select':
                context['selected_tongue'] = metadata.get('value')
        
        # 1. 업종 파악
        if any(word in text_lower for word in ['병원', '의원', '성형', '피부과', '한의원', '치과']):
            context['user_type'] = '병원'
        elif any(word in text_lower for word in ['쇼핑몰', '커머스', '브랜드', '판매', '온라인몰']):
            context['user_type'] = '쇼핑몰'
        
        # 2. 페인 포인트 파악
        if any(word in text_lower for word in ['전환', '구매', '예약', '상담']):
            context['pain_point'] = 'conversion'
        elif any(word in text_lower for word in ['비용', '광고비', 'roas', '마케팅']):
            context['pain_point'] = 'cost'
        elif any(word in text_lower for word in ['직원', '인력', '야근', '대응']):
            context['pain_point'] = 'manpower'
        
        # 3. 긴급도 파악
        if any(word in text_lower for word in ['급', '빨리', '즉시', '바로', '당장']):
            context['urgency'] = 'high'
        elif any(word in text_lower for word in ['천천히', '검토', '고민', '생각']):
            context['urgency'] = 'low'
        
        # 4. 가격 민감도
        if any(word in text_lower for word in ['가격', '비용', '얼마', '저렴', '비싸']):
            context['budget_sense'] = 'price_sensitive'
        
        # 5. 반박/우려 사항 기록
        if any(word in text_lower for word in ['효과', '의심', '진짜', '정말', '믿']):
            if 'skeptical' not in context['objections']:
                context['objections'].append('skeptical')
        
        if any(word in text_lower for word in ['어렵', '복잡', '힘들']):
            if 'complexity' not in context['objections']:
                context['objections'].append('complexity')
        
        # 6. 키워드 수집 (명사 위주)
        keywords = re.findall(r'[가-힣]{2,}', text)
        context['keywords'].extend([k for k in keywords if len(k) >= 2])
        context['keywords'] = list(set(context['keywords']))[-20:]  # 중복 제거, 최근 20개만
    
    def _update_trust_level(self):
        """
        대화 진행도에 따라 신뢰도 업데이트
        신뢰도 = 인터랙션 수 * 10 (최대 100)
        """
        # 사용자 메시지만 카운트 (AI 제외)
        user_messages = sum(1 for msg in st.session_state.chat_history if msg['role'] == 'user')
        
        trust = min(user_messages * 15, 100)  # 버튼 클릭도 카운트되므로 15점씩
        st.session_state.user_context['trust_level'] = trust
    
    def calculate_health_score(self) -> int:
        """
        선택한 혀 타입 기반으로 건강 점수 계산
        
        Returns:
            종합 건강 점수 (0-100)
        """
        # 단순화된 버전 - scores가 없으면 기본값 반환
        return st.session_state.user_context.get('health_score', 50)
    
    def is_ready_for_conversion(self) -> bool:
        """
        리드 전환 타이밍 판단
        """
        context = st.session_state.user_context
        stage = context.get('stage', 'initial')
        
        return stage in ['result_view', 'conversion', 'complete']
    
    def update_stage(self, new_stage: str):
        """
        대화 단계 업데이트
        
        Args:
            new_stage: 새로운 단계
            - initial: 첫 인사
            - symptom_explore: 증상 탐색
            - sleep_check: 수면 확인
            - digestion_check: 소화 확인
            - tongue_select: 혀 선택
            - diagnosis: 진단 설명
            - solution: 솔루션 제안
            - conversion: 클로징 멘트
            - complete: 견적서 제출 완료
        """
        st.session_state.user_context['stage'] = new_stage
    
    def update_context(self, key: str, value):
        """
        사용자 컨텍스트 업데이트
        
        Args:
            key: 컨텍스트 키 (예: 'selected_tongue', 'selected_symptom')
            value: 업데이트할 값
        """
        st.session_state.user_context[key] = value
    
    def reset_conversation(self):
        """대화 초기화 (처음부터 다시)"""
        st.session_state.chat_history = []
        st.session_state.user_context = {
            'user_type': 'visitor',
            'selected_symptom': None,
            'selected_tongue': None,
            'health_score': 0,
            'pain_point': None,
            'urgency': None,
            'budget_sense': None,
            'trust_level': 0,
            'stage': 'initial',
            'keywords': [],
            'objections': [],
        }
        st.session_state.interaction_count = 0
    
    def get_summary(self) -> str:
        """
        대화 요약 (관리자/디버깅용)
        
        Returns:
            요약 텍스트
        """
        context = st.session_state.user_context
        history_count = len(st.session_state.chat_history)
        
        summary = f"""
### 대화 요약
- **총 메시지**: {history_count}개
- **인터랙션**: {st.session_state.interaction_count}회
- **신뢰도**: {context['trust_level']}/100
- **선택 증상**: {context['selected_symptom'] or '미선택'}
- **선택 혀**: {context['selected_tongue'] or '미선택'}
- **건강 점수**: {context['health_score']}/100
- **현재 단계**: {context['stage']}
- **반박사항**: {', '.join(context['objections']) if context['objections'] else '없음'}
"""
        return summary


# ============================================
# 편의 함수 (전역에서 바로 사용)
# ============================================
def get_conversation_manager() -> ConversationManager:
    """ConversationManager 싱글톤 인스턴스 반환"""
    if 'conv_manager' not in st.session_state:
        st.session_state.conv_manager = ConversationManager()
    return st.session_state.conv_manager
