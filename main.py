# -*- coding: utf-8 -*-
"""
충남 날씨 기반 관광지 추천 서비스
실행: uvicorn main:app --reload
"""
import sys
sys.path.insert(0, ".")

from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from lib.weather import fetch_weather
from lib.recommend import match_from_api

app = FastAPI(title="충남 날씨 관광 추천")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/api/recommend")
async def recommend(
    city: str = Query(default="아산"),
    top_n: int = Query(default=6),
    user_lat: float = Query(default=None),
    user_lng: float = Query(default=None),
):
    weather = fetch_weather(city)
    result  = match_from_api(weather, city, top_n=top_n,
                              user_lat=user_lat, user_lng=user_lng)

    sky_map  = {1: "맑음", 3: "구름많음", 4: "흐림"}
    sky_text = sky_map.get(int(weather.get("sky", 1)), "알수없음")

    return {
        "city": city,
        "weather": {
            "temp":        weather["temp"],
            "precip_prob": weather["precip_prob"],
            "sky":         weather["sky"],
            "sky_text":    sky_text,
            "dust":        weather["dust"],
        },
        "scores":          result["weather"],
        "total_fetched":   result["total_fetched"],
        "recommendations": result["recommendations"],
    }
