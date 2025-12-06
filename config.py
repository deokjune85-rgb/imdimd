# config.py
"""
IMD Strategic Consulting - Configuration
"""

# ============================================
# 앱 기본 설정
# ============================================
APP_TITLE = "IMD Strategic Consulting"
APP_ICON = "💼"
LAYOUT = "centered"

# ============================================
# 디자인 컬러
# ============================================
COLOR_PRIMARY = "#111827"
COLOR_BG = "#FFFFFF"
COLOR_TEXT = "#111827"
COLOR_AI_BUBBLE = "#F9FAFB"
COLOR_USER_BUBBLE = "#E5E7EB"
COLOR_BORDER = "#E5E7EB"

# ============================================
# 혀 진단 데이터
# ============================================
TONGUE_TYPES = {
    '담백설': {
        'emoji': '⚪',
        'name': '담백설 (淡白舌)',
        'visual': '핏기 없고 하얀 혀',
        'analysis': '혀가 창백하고 핏기가 없습니다. 이는 기혈(氣血) 부족의 대표적인 신호입니다.',
    },
    '황태설': {
        'emoji': '🟡',
        'name': '황태설 (黃苔舌)',
        'visual': '누런 태가 두껍게',
        'analysis': '혀에 누런 태(황태)가 두껍게 껴 있습니다. 이는 열독(熱毒)이 체내에 쌓인 신호입니다.',
    },
    '치흔설': {
        'emoji': '🦷',
        'name': '치흔설 (齒痕舌)',
        'visual': '가장자리에 이빨 자국',
        'analysis': '혀 가장자리가 울퉁불퉁하죠? 혀가 부어서 이빨에 눌린 자국입니다. 몸이 물 먹은 솜처럼 퉁퉁 불어 순환이 막혔다는 명백한 증거입니다.',
    },
    '자색설': {
        'emoji': '🟣',
        'name': '자색설 (紫色舌)',
        'visual': '검붉거나 자주색',
        'analysis': '혀가 검붉은 자주색을 띠고 있습니다. 이는 어혈(瘀血), 즉 혈액순환 장애의 적신호입니다.',
    }
}

# ============================================
# 구글 시트 컬럼
# ============================================
SHEET_COLUMNS = [
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

# ============================================
# Gemini 설정
# ============================================
GEMINI_MODEL = "gemini-2.0-flash-exp"
GEMINI_TEMPERATURE = 0.6
GEMINI_MAX_TOKENS = 1024
