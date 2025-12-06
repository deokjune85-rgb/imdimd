# lead_handler.py
"""
리드 저장 모듈
"""

from datetime import datetime
from typing import Dict, Tuple, List
import streamlit as st

try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:
    gspread = None
    Credentials = None


DEFAULT_COLUMNS = [
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
    """리드 정보를 구글 시트에 저장"""

    def __init__(self):
        self.client = None
        self.sheet = None
        self.columns = DEFAULT_COLUMNS.copy()
        self._init_sheet()

    def _init_sheet(self) -> None:
        """구글 시트 초기화"""
        if gspread is None or Credentials is None:
            return

        try:
            service_info = st.secrets.get("GOOGLE_SERVICE_ACCOUNT")
            sheet_id = st.secrets.get("GOOGLE_SHEET_ID")

            if not service_info or not sheet_id:
                return

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = Credentials.from_service_account_info(service_info, scopes=scopes)
            self.client = gspread.authorize(creds)

            sh = self.client.open_by_key(sheet_id)
            self.sheet = sh.sheet1

            existing = self.sheet.row_values(1)
            if not existing:
                self.sheet.append_row(self.columns)
            else:
                self.columns = existing

        except Exception:
            self.client = None
            self.sheet = None

    def _build_row(self, data: Dict) -> List[str]:
        """딕셔너리를 시트 행으로 변환"""
        row = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for col in self.columns:
            key = col.strip()
            if key == "timestamp":
                row.append(now_str)
            else:
                value = data.get(key, "")
                if isinstance(value, (dict, list)):
                    value = str(value)
                row.append(str(value) if value is not None else "")

        return row

    def save_lead(self, data: Dict) -> Tuple[bool, str]:
        """리드 저장"""
        if self.sheet is None:
            return True, "구글 시트 미연결 상태 (데모 모드)"

        try:
            row = self._build_row(data)
            self.sheet.append_row(row)
            return True, "리드가 성공적으로 저장되었습니다."
        except Exception as e:
            return False, f"리드 저장 실패: {e}"
