import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  PieChart, Pie, Cell, Tooltip as PieTooltip, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as LineTooltip, Legend,
} from 'recharts'
import Sidebar from '../components/Sidebar'
import { api } from '../lib/api'
import styles from './DashboardPage.module.css'

/* ── Sub-components ── */
function Stars({ count }) {
  return (
    <span className={styles.stars}>
      {Array.from({ length: 5 }, (_, i) => (
        <span key={i} className={i < count ? styles.starFilled : styles.starEmpty}>★</span>
      ))}
    </span>
  )
}

function SentimentBadge({ label }) {
  if (!label) return null
  const cls = label === 'POSITIF' ? styles.badgePositif
            : label === 'NEGATIF' ? styles.badgeNegatif
            : styles.badgeNetral
  return <span className={`${styles.badge} ${cls}`}>{label}</span>
}

function StatCard({ card }) {
  return (
    <div className={styles.statCard}>
      <div className={styles.statTop}>
        <span className={styles.statLabel}>{card.label}</span>
        <span
          className="material-symbols-outlined"
          style={{ fontSize: 22, color: card.iconColor, fontVariationSettings: card.iconFill ? "'FILL' 1" : "'FILL' 0" }}
        >
          {card.icon}
        </span>
      </div>
      <p className={styles.statValue} style={{ color: card.valueColor }}>{card.value}</p>
      {card.progress != null && (
        <div className={styles.progressTrack}>
          <div className={styles.progressBar} style={{ width: `${card.progress}%`, background: card.progressColor }} />
        </div>
      )}
      {card.badge && (
        <div className={styles.statFooter}>
          <span className={styles.statBadge}>{card.badge}</span>
          <span className={styles.statBadgeText}>{card.badgeText}</span>
        </div>
      )}
    </div>
  )
}

/* Custom centre label for donut */
function DonutLabel({ cx, cy, total }) {
  return (
    <g>
      <text x={cx} y={cy - 8} textAnchor="middle" fill="var(--color-on-surface)" fontSize={26} fontWeight={700}>
        {total >= 1000 ? (total/1000).toFixed(1) + 'k' : total}
      </text>
      <text x={cx} y={cy + 14} textAnchor="middle" fill="var(--color-on-surface-variant)" fontSize={12}>Total</text>
    </g>
  )
}

const chartTooltipStyle = {
  backgroundColor: 'var(--color-surface-container-high)',
  border: '1px solid var(--color-surface-variant)',
  borderRadius: 8,
  color: 'var(--color-on-surface)',
  fontSize: 12,
}

/* ── Page ── */
export default function DashboardPage() {
  const [timeFilter, setTimeFilter] = useState('Semua Waktu')

  // Fetch summary stats
  const { data: summaryRes } = useQuery({
    queryKey: ['summary'],
    queryFn: () => api.get('/analysis/summary')
  })
  const summary = summaryRes?.data || {}

  // Fetch distribution
  const { data: distRes } = useQuery({
    queryKey: ['distribution'],
    queryFn: () => api.get('/analysis/distribution')
  })
  const distribution = distRes?.data || []
  const distTotal = distribution.reduce((sum, d) => sum + d.count, 0)
  
  // map db labels to UI colors
  const distData = distribution.map(d => ({
      name: d.label === 'POSITIF' ? 'Positif' : d.label === 'NEGATIF' ? 'Negatif' : 'Netral',
      value: d.count,
      pct: d.pct,
      color: d.label === 'POSITIF' ? '#58cc02' : d.label === 'NEGATIF' ? '#ff6b6b' : '#4a5568'
  }))

  // Fetch trends
  const { data: trendsRes } = useQuery({
    queryKey: ['trends'],
    queryFn: () => api.get('/analysis/trends?period=monthly')
  })
  const trends = (trendsRes?.data || []).map(t => ({
      month: t.period_key, // e.g. "2023-10"
      positif: t.positif,
      negatif: t.negatif,
      netral: t.netral
  }))

  // Fetch recent reviews
  const { data: reviewsRes } = useQuery({
    queryKey: ['reviews', 1],
    queryFn: () => api.get('/analysis/reviews?page=1&per_page=10')
  })
  const reviews = reviewsRes?.data?.items || []

  // Prepare stat cards
  const STAT_CARDS = [
    {
      label: 'TOTAL ULASAN',
      value: summary.total_reviews?.toLocaleString() || '0',
      icon: 'chat_bubble_outline',
      iconColor: 'var(--color-on-surface-variant)',
      valueColor: 'var(--color-on-surface)',
      badge: '',
      badgeText: '',
    },
    {
      label: 'POSITIF',
      value: `${summary.positif_pct || 0}%`,
      icon: 'sentiment_satisfied',
      iconColor: '#58cc02',
      iconFill: true,
      valueColor: '#58cc02',
      progress: summary.positif_pct || 0,
      progressColor: '#58cc02',
    },
    {
      label: 'NEGATIF',
      value: `${summary.negatif_pct || 0}%`,
      icon: 'sentiment_dissatisfied',
      iconColor: '#ff6b6b',
      iconFill: true,
      valueColor: '#ff6b6b',
      progress: summary.negatif_pct || 0,
      progressColor: '#ff6b6b',
    },
    {
      label: 'AKURASI MODEL',
      value: summary.model_accuracy != null ? `${summary.model_accuracy}%` : 'N/A',
      icon: 'gps_fixed',
      iconColor: 'var(--color-secondary-container)',
      valueColor: 'var(--color-secondary-container)',
      badge: summary.model_version || '-',
      badgeText: 'versi aktif',
    },
  ]

  return (
    <div className={styles.layout}>
      <Sidebar />

      <div className={styles.main}>
        {/* ── Header ── */}
        <header className={styles.header}>
          <h1 className={styles.pageTitle}>Dashboard</h1>
          <div className={styles.headerActions}>
            <button id="time-filter" className={styles.filterBtn}>
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>calendar_month</span>
              {timeFilter}
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>expand_more</span>
            </button>
            <button id="export-pdf" className={styles.exportBtn}>
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>download</span>
              Export PDF
            </button>
            <button id="notifications" className={styles.iconBtn} aria-label="Notifikasi">
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>notifications</span>
            </button>
            <button id="user-profile" className={styles.iconBtn} aria-label="Profil">
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>account_circle</span>
            </button>
          </div>
        </header>

        <div className={styles.content}>
          {/* ── Stat Cards ── */}
          <section className={styles.statsGrid} aria-label="Statistik utama">
            {STAT_CARDS.map((c) => <StatCard key={c.label} card={c} />)}
          </section>

          {/* ── Charts row ── */}
          <section className={styles.chartsRow} aria-label="Grafik sentimen">
            {/* Donut */}
            <div className={styles.card}>
              <p className={styles.cardTitle}>DISTRIBUSI SENTIMEN</p>
              <div className={styles.donutWrap}>
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={distData}
                      cx="50%"
                      cy="50%"
                      innerRadius={72}
                      outerRadius={100}
                      dataKey="value"
                      cornerRadius={6}
                      labelLine={false}
                      label={<DonutLabel total={distTotal} />}
                    >
                      {distData.map((d) => (
                        <Cell key={d.name} fill={d.color} stroke="none" />
                      ))}
                    </Pie>
                    <PieTooltip
                      contentStyle={chartTooltipStyle}
                      formatter={(v, name, props) => [`${props.payload.pct}% (${v})`, name]}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className={styles.legendRow}>
                {distData.map((d) => (
                  <span key={d.name} className={styles.legendItem}>
                    <span className={styles.legendDot} style={{ background: d.color }} />
                    {d.name}
                  </span>
                ))}
              </div>
            </div>

            {/* Line chart */}
            <div className={styles.card} style={{ flex: 1 }}>
              <p className={styles.cardTitle}>TREN SENTIMEN PER BULAN</p>
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={trends} margin={{ top: 8, right: 16, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-surface-variant)" vertical={false} />
                  <XAxis
                    dataKey="month"
                    tick={{ fill: 'var(--color-on-surface-variant)', fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: 'var(--color-on-surface-variant)', fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <LineTooltip contentStyle={chartTooltipStyle} />
                  <Legend
                    iconType="circle"
                    iconSize={8}
                    wrapperStyle={{ fontSize: 12, color: 'var(--color-on-surface-variant)', paddingTop: 8 }}
                    formatter={(value) => value.charAt(0).toUpperCase() + value.slice(1)}
                  />
                  <Line type="monotone" dataKey="positif" name="Positif" stroke="#58cc02" strokeWidth={2.5} dot={false} />
                  <Line type="monotone" dataKey="negatif" name="Negatif" stroke="#ff6b6b" strokeWidth={2.5} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </section>

          {/* ── Recent Reviews ── */}
          <section className={styles.card} aria-label="Ulasan terbaru">
            <div className={styles.tableHeader}>
              <p className={styles.cardTitle}>10 ULASAN TERBARU</p>
              <a href="/analisis" className={styles.lihatSemua}>Lihat Semua</a>
            </div>
            <div className={styles.tableWrap}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>RATING</th>
                    <th>TEKS ULASAN</th>
                    <th>SENTIMEN</th>
                    <th>TANGGAL</th>
                  </tr>
                </thead>
                <tbody>
                  {reviews.length === 0 ? (
                      <tr><td colSpan="4" style={{textAlign: 'center', padding: '24px'}}>Belum ada ulasan. Silakan scraping data terlebih dahulu.</td></tr>
                  ) : reviews.map((r) => (
                    <tr key={r.id}>
                      <td><Stars count={r.rating || 0} /></td>
                      <td className={styles.reviewText}>{r.raw_text}</td>
                      <td><SentimentBadge label={r.sentiment_label} /></td>
                      <td className={styles.dateCell}>{r.review_date || r.created_at?.split('T')[0]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
