import { MapPin, Star, Clock, ChevronRight } from 'lucide-react'
import type { NextPlace } from '@/types'

interface Props {
  places: NextPlace[]
  loading: boolean
  onClose: () => void
}

const TYPE_LABEL: Record<string, string> = {
  restaurant:        '식당',
  korean_restaurant: '한식',
  chinese_restaurant:'중식',
  cafe:              '카페',
  coffee_shop:       '카페',
  bakery:            '베이커리',
}

function getTypeLabel(types: string[]): string {
  for (const t of types) {
    if (TYPE_LABEL[t]) return TYPE_LABEL[t]
  }
  return '식당'
}

export default function CoursePanel({ places, loading, onClose }: Props) {
  const hour = new Date().getHours()
  const label =
    hour >= 11 && hour <= 14 ? '근처 점심 맛집' :
    hour > 14 && hour <= 17  ? '근처 카페' :
    hour > 17                ? '근처 저녁 맛집' : '근처 카페'

  return (
    <div className="mt-2 mb-4 rounded-2xl border border-primary/20 bg-primary/5 overflow-hidden">
      {/* 헤더 */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-primary/10">
        <div className="flex items-center gap-2">
          <ChevronRight className="w-4 h-4 text-primary" />
          <span className="text-sm font-bold text-primary">다음 코스 — {label}</span>
        </div>
        <button
          onClick={onClose}
          className="text-xs text-muted-foreground hover:text-foreground"
        >
          닫기
        </button>
      </div>

      {/* 내용 */}
      <div className="px-4 py-3 flex flex-col gap-3">
        {loading ? (
          <div className="flex flex-col gap-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-16 rounded-xl bg-muted animate-pulse" />
            ))}
          </div>
        ) : places.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">
            근처 장소를 찾지 못했습니다.
          </p>
        ) : (
          places.map((p, i) => (
            <NextPlaceCard key={i} place={p} />
          ))
        )}
      </div>
    </div>
  )
}

function NextPlaceCard({ place: p }: { place: NextPlace }) {
  const typeLabel = getTypeLabel(p.types)

  return (
    <div className="flex gap-3 bg-white rounded-xl overflow-hidden shadow-sm border border-border/40">
      {/* 썸네일 */}
      <div className="flex-shrink-0 w-20 h-20">
        {p.photo_url ? (
          <img
            src={p.photo_url}
            alt={p.name}
            loading="lazy"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full bg-muted flex items-center justify-center text-2xl">
            🍽️
          </div>
        )}
      </div>

      {/* 정보 */}
      <div className="flex-1 py-2.5 pr-3 min-w-0">
        <div className="flex items-start justify-between gap-1 mb-1">
          <div>
            <span className="text-[10px] bg-primary/10 text-primary px-1.5 py-0.5 rounded-full mr-1">
              {typeLabel}
            </span>
            <span className="text-[13px] font-bold">{p.name}</span>
          </div>
          {p.open_now !== null && (
            <span className={`flex-shrink-0 text-[10px] font-semibold flex items-center gap-0.5 ${
              p.open_now ? 'text-emerald-600' : 'text-rose-500'
            }`}>
              <Clock className="w-2.5 h-2.5" />
              {p.open_now ? '영업중' : '영업종료'}
            </span>
          )}
        </div>

        <div className="flex items-center gap-1 mb-1">
          <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
          <span className="text-xs font-bold">{p.rating.toFixed(1)}</span>
          <span className="text-[11px] text-muted-foreground">
            ({p.review_count.toLocaleString()}개)
          </span>
        </div>

        <div className="flex items-center gap-1 text-[11px] text-muted-foreground">
          <MapPin className="w-3 h-3 flex-shrink-0" />
          <span className="line-clamp-1">{p.address}</span>
        </div>
      </div>
    </div>
  )
}
