# lead_handler.py
"""
IMD Sales Bot - Lead Management
리드 수집, 검증, Google Sheets 저장
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import Dict, Optional
from config import SHEET_COLUMNS

class LeadHandler:
    """리드 수집 및 저장 관리 클래스"""
    
    def __init__(self):
        """Google Sheets 클라이언트 초기화"""
        self.client = None
        self.sheet = None
        self._init_sheets_client()
    
    def _init_sheets_client(self):
        """Google Sheets API 인증 및 연결"""
        try:
            creds_dict = st.secrets["gcp_service_account"].to_dict()
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
            self.client = gspread.authorize(creds)
            
            # 시트 열기 (없으면 생성)
            sheet_name = st.secrets.get("SHEET_NAME", "IMD_Sales_Leads")
            try:
                self.sheet = self.client.open(sheet_name).sheet1
            except gspread.SpreadsheetNotFound:
                # 시트가 없으면 생성
                spreadsheet = self.client.create(sheet_name)
                self.sheet = spreadsheet.sheet1
                # 헤더 추가
                self.sheet.append_row(SHEET_COLUMNS)
                
        except Exception as e:
            st.warning(f"⚠️ Google Sheets 연결 실패: {str(e)}")
            self.client = None
            self.sheet = None
    
    def validate_lead(self, data: Dict) -> tuple[bool, Optional[str]]:
        """
        리드 데이터 검증
        
        Args:
            data: 리드 정보 딕셔너리
        
        Returns:
            (유효성, 에러메시지)
        """
        # 필수 필드 체크
        if not data.get("name"):
            return False, "성함을 입력해주세요."
        
        if not data.get("contact"):
            return False, "연락처를 입력해주세요."
        
        # 연락처 형식 검증 (간단한 체크)
        contact = data["contact"].replace("-", "").replace(" ", "")
        if not contact.isdigit() or len(contact) < 10:
            return False, "올바른 연락처를 입력해주세요. (예: 010-1234-5678)"
        
        return True, None
    
    def save_lead(self, data: Dict) -> tuple[bool, str]:
        """
        리드 정보를 Google Sheets에 저장
        
        Args:
            data: {
                'user_type': '병원' or '쇼핑몰',
                'stage': '대화 단계',
                'name': '이름',
                'contact': '연락처',
                'company': '회사명',
                'urgency': '긴급도',
                'source': '유입 경로'
            }
        
        Returns:
            (성공여부, 메시지)
        """
        # 검증
        is_valid, error_msg = self.validate_lead(data)
        if not is_valid:
            return False, error_msg
        
        # Sheets 연결 안되어있으면 로컬 저장
        if not self.sheet:
            return self._save_local_fallback(data)
        
        try:
            # 데이터 행 생성
            row = [
                datetime.now().isoformat(),
                data.get('user_type', 'Unknown'),
                data.get('stage', 'Lead Captured'),
                data.get('name', ''),
                data.get('contact', ''),
                data.get('company', ''),
                data.get('urgency', ''),
                data.get('source', 'IMD_Sales_Bot')
            ]
            
            # Sheets에 추가
            self.sheet.append_row(row)
            
            return True, "✅ 설계도 신청이 완료되었습니다!"
            
        except Exception as e:
            # 에러 발생 시 로컬 저장
            return self._save_local_fallback(data)
    
    def _save_local_fallback(self, data: Dict) -> tuple[bool, str]:
        """
        Google Sheets 실패 시 로컬 세션에 저장
        
        Args:
            data: 리드 정보
        
        Returns:
            (성공여부, 메시지)
        """
        if 'leads_backup' not in st.session_state:
            st.session_state.leads_backup = []
        
        data['timestamp'] = datetime.now().isoformat()
        st.session_state.leads_backup.append(data)
        
        return True, "✅ 설계도 신청이 완료되었습니다! (로컬 저장)"
    
    def get_recent_leads(self, limit: int = 10) -> list:
        """
        최근 리드 목록 조회 (관리자용)
        
        Args:
            limit: 조회할 개수
        
        Returns:
            리드 리스트
        """
        if not self.sheet:
            return st.session_state.get('leads_backup', [])
        
        try:
            # 최근 N개 행 가져오기
            all_values = self.sheet.get_all_values()
            recent = all_values[-limit:] if len(all_values) > limit else all_values[1:]
            return recent
        except:
            return []
    
    def format_lead_message(self, data: Dict) -> str:
        """
        저장 완료 후 사용자에게 보여줄 메시지 생성
        
        Args:
            data: 리드 정보
        
        Returns:
            포맷팅된 메시지
        """
        name = data.get('name', '고객')
        contact = data.get('contact', '')
        urgency = data.get('urgency', '검토 중')
        
        message = f"""
### 🎉 {name}님, 신청이 완료되었습니다!

**담당 아키텍트가 24시간 내로 연락드립니다.**

📞 연락처: {contact}  
⚡ 희망 시기: {urgency}

---

### 📋 다음 단계 안내

1️⃣ **24시간 내**: 담당자가 전화/카톡으로 1차 상담  
2️⃣ **48시간 내**: 맞춤 AI 설계도 + 견적서 발송  
3️⃣ **7일 내**: 무료 데모 시연 (실제 작동하는 봇 체험)

---

💡 **지금 바로 준비하세요!**
- 현재 홈페이지 URL
- 월 평균 방문자 수
- 주요 고객 문의 유형 3가지

이 정보만 있으면 설계가 2배 빨라집니다! 🚀
"""
        return message


# ============================================
# 편의 함수 (앱에서 바로 사용)
# ============================================
def save_lead_quick(name: str, contact: str, **kwargs) -> tuple[bool, str]:
    """
    빠른 리드 저장 (앱에서 직접 호출용)
    
    Args:
        name: 이름
        contact: 연락처
        **kwargs: 추가 정보
    
    Returns:
        (성공여부, 메시지)
    """
    handler = LeadHandler()
    data = {
        'name': name,
        'contact': contact,
        **kwargs
    }
    return handler.save_lead(data)
