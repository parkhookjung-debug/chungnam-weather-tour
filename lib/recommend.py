# -*- coding: utf-8 -*-
"""
통합 추천 파이프라인
weather → scoring → tourapi fetch → auto_tag → distance → matching → result
"""
import os
import requests
from dotenv import load_dotenv
from lib.scoring import calc_weather_score
from lib.auto_tag import auto_tag
from lib.distance import calc_distance_score, get_user_coords

load_dotenv()

TOUR_API_KEY = os.getenv("TOUR_API_KEY")
BASE_URL = "https://apis.data.go.kr/B551011/KorService2"

SIGUNGU_CODES = {
    "공주": 1, "금산": 2, "논산": 3, "당진": 4,
    "보령": 5, "부여": 6, "서산": 7, "서천": 8,
    "아산": 9, "예산": 11, "천안": 12, "청양": 13,
    "태안": 14, "홍성": 15,
}


def fetch_and_tag(city: str, num: int = 50) -> list:
    """TourAPI에서 관광지 가져와서 자동 태깅"""
    sigungu = SIGUNGU_CODES.get(city)
    if sigungu is None:
        raise ValueError(f"지원하지 않는 도시: {city}")

    params = {
        "serviceKey":  TOUR_API_KEY,
        "numOfRows":   num,
        "pageNo":      1,
        "MobileOS":    "ETC",
        "MobileApp":   "ChungnamTour",
        "_type":       "json",
        "areaCode":    34,
        "sigunguCode": sigungu,
        "arrange":     "C",  # 수정일 순 (최신 데이터 우선)
    }

    r = requests.get(f"{BASE_URL}/areaBasedList2", params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    if data["response"]["header"]["resultCode"] != "0000":
        return []

    body = data["response"]["body"]["items"]
    if not body:
        return []

    items = body["item"]
    # 숙박·쇼핑 제외 (관광 서비스에 불필요)
    items = [it for it in items if str(it.get("contenttypeid")) not in ("32", "38")]

    return [auto_tag(it) for it in items]


def match_from_api(weather: dict, city: str, top_n: int = 5,
                   user_lat: float = None, user_lng: float = None) -> dict:
    """
    실시간 날씨 + TourAPI 데이터 + 거리 가중치로 추천 결과 반환

    가중치 비율:
        날씨 점수  60%
        거리 점수  40%
    """
    scores = calc_weather_score(weather)
    destinations = fetch_and_tag(city)

    # 사용자 위치 (미입력 시 도시 중심 좌표 사용)
    if user_lat is None or user_lng is None:
        user_lat, user_lng = get_user_coords(city)

    WEATHER_WEIGHT  = 0.6
    DISTANCE_WEIGHT = 0.4

    results = []
    for dest in destinations:
        w = dest["weather_weights"]

        # Hard Filter
        if scores["is_raining"] and dest["category"] == "outdoor":
            continue
        if scores["is_dust_bad"] and w.get("fine_dust_limit") == "good":
            continue

        # 날씨 점수
        if dest["category"] == "outdoor":
            weather_score = scores["outdoor"] * w["sunny"]
        else:
            weather_score = scores["indoor"] * w["rainy"]

        golden_bonus = 0.3 if (dest.get("golden_hour_bonus") and scores["is_golden_hour"]) else 0.0
        weather_score = min(weather_score + golden_bonus, 1.0)

        # 거리 점수
        lat = dest["coords"]["lat"]
        lng = dest["coords"]["lng"]
        dist_score, dist_km = calc_distance_score(lat, lng, user_lat, user_lng)

        # 최종 점수
        total = round(weather_score * WEATHER_WEIGHT + dist_score * DISTANCE_WEIGHT, 3)

        results.append({
            **dest,
            "score":          total,
            "weather_score":  round(weather_score, 3),
            "distance_score": dist_score,
            "distance_km":    dist_km,
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    return {
        "city":            city,
        "user_coords":     {"lat": user_lat, "lng": user_lng},
        "weather":         scores,
        "total_fetched":   len(destinations),
        "recommendations": results[:top_n],
    }
