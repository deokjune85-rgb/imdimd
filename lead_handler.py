# lead_handler.py
"""
IMD Sales / Medical Bot - Lead Handler
구글 시트에 리드(문의/견적 요청) 저장하는 모듈
- 증상, 혀 타입, 건강 점수 저장 지원
"""

from datetime import datetime
from typing import Dict, Tuple, List, Optional

import streamlit as st

try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:
    gspread = None
    Credentials = None  # type: ignore


# 기본 컬럼 정의
DEFAULT_SHEET_COLUMNS: List[str] = [
    "timestamp",
    "name",
    "contact",
    "symptom",
    "tongue_type",
    "health_score",
    "preferred_date",
    "chat_summary",
    "source",
    "type",
]


class LeadHandler:
    """리드(예약/견적 신청) 정보를 구글 시트에 저장하는 클래스"""

    def __init__(self):
        self.client = None
        self.sheet = None
        self.columns = DEFAULT_SHEET_COLUMNS.copy()
        self._init_sheet()

    # --------------------------------------------------
    # 1) 구글 시트 초기화
    # --------------------------------------------------
    def _init_sheet(self) -> None:
        """구글 시트 클라이언트 및 워크시트 초기화 (실패해도 앱은 계속 동작)"""
        # gspread 자체가 없는 경우
        if gspread is None or Credentials is None:
            # 개발/테스트 환경에서 시트 없이도 앱이 돌도록만 한다
            return

        # 시크릿에서 서비스 계정/시트 ID 가져오기
        try:
            service_info = (
                st.secrets.get("GOOGLE_SERVICE_ACCOUNT")
                or st.secrets.get("gcp_service_account")
                or st.secrets.get("gspread_service_account")
            )
            sheet_id = (
                st.secrets.get("GOOGLE_SHEET_ID")
                or st.secrets.get("LEAD_SHEET_ID")
                or st.secrets.get("SPREADSHEET_ID")
            )

            if not service_info or not sheet_id:
                # 시트 미연결 상태 (하지만 앱은 죽지 않게)
                return

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = Credentials.from_service_account_info(service_info, scopes=scopes)
            self.client = gspread.authorize(creds)

            # 기본: 첫 번째 워크시트 사용
            sh = self.client.open_by_key(sheet_id)
            self.sheet = sh.sheet1

            # 헤더가 비어 있으면 기본 컬럼 헤더 세팅
            existing = self.sheet.row_values(1)
            if not existing:
                self.sheet.append_row(self.columns)
            else:
                # 이미 헤더가 있으면 그걸 기준으로 사용
                self.columns = existing

        except Exception as e:
            try:
                st.error(f"⚠️ 구글 시트 초기화 실패: {e}")
            except Exception:
                pass
            self.client = None
            self.sheet = None

    # --------------------------------------------------
    # 2) 내부 유틸: 한 줄 데이터 만들기
    # --------------------------------------------------
    def _build_row(self, data: Dict) -> List[str]:
        """
        입력 딕셔너리를 현재 시트 컬럼 순서에 맞춰 한 줄 리스트로 변환
        """
        row: List[str] = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for col in self.columns:
            key = col.strip()
            if key == "timestamp":
                row.append(now_str)
            else:
                value = data.get(key, "")
                # dict/list면 문자열로 캐스팅
                if isinstance(value, (dict, list)):
                    value = str(value)
                row.append(str(value) if value is not None else "")

        return row

    # --------------------------------------------------
    # 3) 외부에서 호출: 리드 저장
    # --------------------------------------------------
    def save_lead(self, data: Dict) -> Tuple[bool, str]:
        """
        리드를 구글 시트에 저장
        Args:
            data: {
                'name': ...,
                'contact': ...,
                'symptom': ...,  # 선택한 증상
                'tongue_type': ...,  # 선택한 혀 타입
                'health_score': ...,  # 건강 점수
                'preferred_date': ...,
                'chat_summary': ...,
                'source': ...,
                'type': ...
            }

        Returns:
            (성공여부, 메시지)
        """
        # 시트 미연결 상태
        if self.sheet is None:
            # 개발 / 데모 환경에서는 그냥 성공으로 처리
            return True, "구글 시트 미연결 상태 (데모 모드로 처리했습니다)."

        try:
            row = self._build_row(data)
            self.sheet.append_row(row)
            return True, "리드가 성공적으로 저장되었습니다."
        except Exception as e:
            return False, f"리드 저장 실패: {e}"
