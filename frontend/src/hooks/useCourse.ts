import { useState, useCallback } from 'react'
import type { NextPlace } from '@/types'

export function useCourse() {
  const [places, setPlaces] = useState<NextPlace[]>([])
  const [loading, setLoading] = useState(false)

  const fetch = useCallback(async (
    lat: number,
    lng: number,
    category: string,
  ) => {
    setLoading(true)
    setPlaces([])
    try {
      const hour = new Date().getHours()
      const res = await window.fetch(
        `/api/course?lat=${lat}&lng=${lng}&category=${encodeURIComponent(category)}&hour=${hour}`
      )
      const data = await res.json()
      setPlaces(data.next_places ?? [])
    } catch {
      setPlaces([])
    } finally {
      setLoading(false)
    }
  }, [])

  const clear = useCallback(() => setPlaces([]), [])

  return { places, loading, fetch, clear }
}
