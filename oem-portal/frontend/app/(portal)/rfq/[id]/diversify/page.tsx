"use client"
import { useEffect } from "react"
import { useParams, useRouter } from "next/navigation"

export default function DiversifyPage() {
  const params = useParams()
  const router = useRouter()
  useEffect(() => { router.replace(`/rfq/${params.id}`) }, [params.id, router])
  return null
}
