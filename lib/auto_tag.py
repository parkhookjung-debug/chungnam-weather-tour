# -*- coding: utf-8 -*-
"""
TourAPI 카테고리 코드 → 날씨 가중치 자동 태깅

contentTypeId: 12=관광지, 14=문화시설, 15=축제, 25=여행코스, 28=레포츠, 32=숙박, 38=쇼핑, 39=음식점
cat1: A01=자연, A02=인문/역사, A03=레저스포츠, A04=쇼핑, A05=음식, B02=숙박, C01=여행코스
"""

# cat1 기반 1차 분류
CAT1_PROFILE = {
    "A01": {  # 자연관광지 (산, 계곡, 해변, 공원)
        "category": "outdoor",
        "tags": ["자연", "산책", "힐링"],
        "weather_weights": {"sunny": 1.0, "cloudy": 0.7, "rainy": 0.1, "fine_dust_limit": "good"},
        "golden_hour_bonus": True,
    },
    "A02": {  # 인문/역사/체험
        "category": "outdoor",
        "tags": ["역사", "문화", "체험"],
        "weather_weights": {"sunny": 0.9, "cloudy": 0.8, "rainy": 0.3, "fine_dust_limit": "moderate"},
        "golden_hour_bonus": False,
    },
    "A03": {  # 레저/스포츠
        "category": "outdoor",
        "tags": ["레저", "액티비티", "스포츠"],
        "weather_weights": {"sunny": 1.0, "cloudy": 0.6, "rainy": 0.1, "fine_dust_limit": "moderate"},
        "golden_hour_bonus": False,
    },
    "A04": {  # 쇼핑
        "category": "indoor",
        "tags": ["쇼핑", "실내"],
        "weather_weights": {"sunny": 0.4, "cloudy": 0.7, "rainy": 1.0, "fine_dust_limit": "bad"},
        "golden_hour_bonus": False,
    },
    "A05": {  # 음식
        "category": "indoor",
        "tags": ["맛집", "음식", "실내"],
        "weather_weights": {"sunny": 0.5, "cloudy": 0.8, "rainy": 1.0, "fine_dust_limit": "bad"},
        "golden_hour_bonus": False,
    },
    "B02": {  # 숙박
        "category": "indoor",
        "tags": ["숙박", "실내"],
        "weather_weights": {"sunny": 0.3, "cloudy": 0.6, "rainy": 1.0, "fine_dust_limit": "bad"},
        "golden_hour_bonus": False,
    },
    "C01": {  # 여행코스
        "category": "outdoor",
        "tags": ["코스", "드라이브", "산책"],
        "weather_weights": {"sunny": 1.0, "cloudy": 0.7, "rainy": 0.2, "fine_dust_limit": "moderate"},
        "golden_hour_bonus": True,
    },
}

# contentTypeId 기반 2차 보정
CONTENT_TYPE_OVERRIDE = {
    "14": {  # 문화시설 (박물관, 미술관, 전시관)
        "category": "indoor",
        "tags": ["전시", "문화", "실내"],
        "weather_weights": {"sunny": 0.5, "cloudy": 0.8, "rainy": 1.0, "fine_dust_limit": "bad"},
        "golden_hour_bonus": False,
    },
    "15": {  # 축제/행사
        "category": "outdoor",
        "tags": ["축제", "행사", "이벤트"],
        "weather_weights": {"sunny": 1.0, "cloudy": 0.7, "rainy": 0.2, "fine_dust_limit": "moderate"},
        "golden_hour_bonus": False,
    },
    "32": {  # 숙박
        "category": "indoor",
        "tags": ["숙박"],
        "weather_weights": {"sunny": 0.3, "cloudy": 0.6, "rainy": 1.0, "fine_dust_limit": "bad"},
        "golden_hour_bonus": False,
    },
    "39": {  # 음식점
        "category": "indoor",
        "tags": ["맛집", "음식"],
        "weather_weights": {"sunny": 0.5, "cloudy": 0.8, "rainy": 1.0, "fine_dust_limit": "bad"},
        "golden_hour_bonus": False,
    },
}

# cat3 기반 세부 보정 (특별한 장소만)
CAT3_BONUS = {
    "A01010400": {"tags": ["등산", "산"], "golden_hour_bonus": False},           # 산
    "A01010500": {"tags": ["하천", "산책로"], "golden_hour_bonus": True},         # 하천/강
    "A01010900": {"tags": ["계곡", "물놀이"], "golden_hour_bonus": False},        # 계곡
    "A01011200": {"tags": ["해수욕장", "바다", "여름"], "golden_hour_bonus": True},# 해수욕장
    "A01011400": {"tags": ["섬", "바다"], "golden_hour_bonus": True},             # 섬
    "A01011600": {"tags": ["일출", "일몰", "사진맛집"], "golden_hour_bonus": True},# 전망대
    "A02010100": {"tags": ["성곽", "역사"], "golden_hour_bonus": True},           # 고궁/성
    "A02010200": {"tags": ["사찰", "힐링"], "golden_hour_bonus": False},          # 사찰
    "A02030200": {"tags": ["체험", "농촌"], "golden_hour_bonus": False},          # 농촌체험
    "A03021700": {"tags": ["캠핑", "야외"], "golden_hour_bonus": False},          # 캠핑장
}

# 추천 카피 템플릿
COPY_TEMPLATES = {
    ("outdoor", "sunny"):  "맑은 하늘 아래 방문하기 좋은 곳입니다.",
    ("outdoor", "cloudy"): "구름 낀 날도 나쁘지 않은 야외 명소입니다.",
    ("outdoor", "rainy"):  "비 오는 날은 피하는 게 좋습니다.",
    ("indoor", "sunny"):   "맑은 날엔 야외도 좋지만, 이곳도 추천합니다.",
    ("indoor", "cloudy"):  "날씨에 관계없이 즐길 수 있는 실내 공간입니다.",
    ("indoor", "rainy"):   "비 오는 날 가기 좋은 실내 명소입니다.",
}


def auto_tag(item: dict) -> dict:
    """
    TourAPI item 하나를 받아 날씨 태그가 붙은 destination 형식으로 변환
    """
    content_type = str(item.get("contenttypeid", "12"))
    cat1 = item.get("cat1", "A01")[:3]
    cat3 = item.get("cat3", "")

    # 1단계: cat1 기본 프로필
    profile = CAT1_PROFILE.get(cat1, CAT1_PROFILE["A01"]).copy()
    profile["weather_weights"] = profile["weather_weights"].copy()
    profile["tags"] = profile["tags"].copy()

    # 2단계: contentTypeId 보정 (문화시설, 음식점, 숙박은 실내로 강제)
    if content_type in CONTENT_TYPE_OVERRIDE:
        override = CONTENT_TYPE_OVERRIDE[content_type]
        profile["category"] = override["category"]
        profile["weather_weights"] = override["weather_weights"].copy()
        profile["tags"] = override["tags"].copy()
        profile["golden_hour_bonus"] = override["golden_hour_bonus"]

    # 3단계: cat3 세부 보정
    if cat3 in CAT3_BONUS:
        bonus = CAT3_BONUS[cat3]
        profile["tags"] = list(set(profile["tags"] + bonus.get("tags", [])))
        if "golden_hour_bonus" in bonus:
            profile["golden_hour_bonus"] = bonus["golden_hour_bonus"]

    # 카피 생성
    weather_key = "sunny"  # 기본값
    copy_text = COPY_TEMPLATES.get((profile["category"], weather_key), "방문해볼 만한 곳입니다.")

    return {
        "id":          item.get("contentid", ""),
        "name":        item.get("title", ""),
        "city":        _extract_city(item.get("addr1", "")),
        "address":     item.get("addr1", ""),
        "image":       item.get("firstimage", ""),
        "category":    profile["category"],
        "tags":        profile["tags"],
        "weather_weights":   profile["weather_weights"],
        "temp_range":        {"min": -20, "max": 40},
        "golden_hour_bonus": profile["golden_hour_bonus"],
        "copy":              copy_text,
        "coords": {
            "lat": float(item.get("mapy", 0) or 0),
            "lng": float(item.get("mapx", 0) or 0),
        },
        "source": "tourapi",
    }


def _extract_city(addr: str) -> str:
    """주소에서 시군구 추출"""
    parts = addr.replace("충청남도 ", "").split()
    return parts[0] if parts else "충남"
