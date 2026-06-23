import { useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts'
import Sidebar from '../components/Sidebar'
import styles from './HasilAnalisisPage.module.css'

/* ── Data ── */
const TREND = [
  { week: 'Week 1', positif: 30, negatif: 70 },
  { week: 'Week 2', positif: 45, negatif: 55 },
  { week: 'Week 3', positif: 60, negatif: 48 },
  { week: 'Week 4', positif: 52, negatif: 55 },
  { week: 'Week 5', positif: 72, negatif: 35 },
  { week: 'Week 6', positif: 88, negatif: 25 },
]

const VERSION_BARS = [
  { label: 'v1.0.0', pct: 45, active: false },
  { label: 'v1.0.1', pct: 52, active: false },
  { label: 'v1.0.2', pct: 38, active: false },
  { label: 'v1.0.3', pct: 75, active: false },
  { label: 'v1.0.4-P', pct: 88, active: true },
]

const WORDS_POS = [
  { w: 'Bagus',    sz: 26, op: 1.0 }, { w: 'Membantu', sz: 19, op: 0.8 },
  { w: 'Cepat',   sz: 22, op: 0.9 }, { w: 'Mudah',    sz: 13, op: 0.6 },
  { w: 'Keren',   sz: 34, op: 1.0 }, { w: 'Lengkap',  sz: 15, op: 0.7 },
  { w: 'Suka',    sz: 13, op: 0.5 }, { w: 'Akurat',   sz: 22, op: 0.8 },
  { w: 'Praktis', sz: 11, op: 0.4 },
]
const WORDS_NEG = [
  { w: 'Error',  sz: 26, op: 1.0 }, { w: 'Lambat', sz: 13, op: 0.6 },
  { w: 'Bug',    sz: 22, op: 0.9 }, { w: 'Keluar', sz: 19, op: 0.8 },
  { w: 'Crash',  sz: 34, op: 1.0 }, { w: 'Susah',  sz: 11, op: 0.4 },
  { w: 'Gagal',  sz: 15, op: 0.7 }, { w: 'Berat',  sz: 22, op: 0.8 },
]

const TABLE_ROWS = [
  { date: '2023-10-24', uid: 'usr_8x92j', text: 'Aplikasi ini sangat membantu saya dalam belajar bahasa baru. Fiturnya lengkap.', ver: 'v1.0.4', sentiment: 'POSITIVE' },
  { date: '2023-10-24', uid: 'usr_2m4nq', text: 'Sering crash saat buka menu pengaturan. Tolong diperbaiki secepatnya!',          ver: 'v1.0.3', sentiment: 'NEGATIVE' },
  { date: '2023-10-23', uid: 'usr_k9p1l', text: 'Lumayan, tapi UI nya agak membingungkan untuk pengguna baru.',                    ver: 'v1.0.4', sentiment: 'NEUTRAL'  },
  { date: '2023-10-23', uid: 'usr_7b5vt', text: 'Keren banget prediksinya akurat, mempermudah kerjaan analisis data saya.',         ver: 'v1.0.4', sentiment: 'POSITIVE' },
]

/* ── Sub-components ── */
function SentimentBadge({ s }) {
  const cls = s === 'POSITIVE' ? styles.badgePos : s === 'NEGATIVE' ? styles.badgeNeg : styles.badgeNeu
  return <span className={`${styles.badge} ${cls}`}>{s}</span>
}

const chartStyle = {
  backgroundColor: 'var(--color-surface-container-high)',
  border: '1px solid var(--color-surface-variant)',
  borderRadius: 8,
  color: 'var(--color-on-surface)',
  fontSize: 11,
}

/* ── Page ── */
export default function HasilAnalisisPage() {
  const [search, setSearch] = useState('')
  const [timeFilter, setTimeFilter]    = useState('Last 30 Days')
  const [versionFilter, setVFilter]    = useState('All Versions')

  const filtered = TABLE_ROWS.filter((r) =>
    r.text.toLowerCase().includes(search.toLowerCase()) ||
    r.uid.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className={styles.layout}>
      <Sidebar />

      <div className={styles.main}>
        {/* ── Page Header ── */}
        <div className={styles.pageHeader}>
          <div>
            <h1 className={styles.pageTitle}>Hasil Analisis</h1>
            <p className={styles.pageSub}>Detailed analysis and data exploration of sentiment trends.</p>
          </div>
          <div className={styles.filters}>
            <div className={styles.filterChip}>
              <span className="material-symbols-outlined" style={{ fontSize: 15 }}>calendar_today</span>
              <select className={styles.filterSelect} value={timeFilter} onChange={(e) => setTimeFilter(e.target.value)}>
                <option>Last 30 Days</option>
                <option>Last 90 Days</option>
                <option>This Year</option>
              </select>
            </div>
            <div className={styles.filterChip}>
              <span className="material-symbols-outlined" style={{ fontSize: 15 }}>app_settings_alt</span>
              <select className={styles.filterSelect} value={versionFilter} onChange={(e) => setVFilter(e.target.value)}>
                <option>All Versions</option>
                <option>v1.0.4-PRO</option>
                <option>v1.0.3</option>
              </select>
            </div>
            <button className={styles.filterBtn}>
              <span className="material-symbols-outlined" style={{ fontSize: 15 }}>filter_list</span>
              More Filters
            </button>
          </div>
        </div>

        {/* ── Content grid ── */}
        <div className={styles.grid}>

          {/* 1. Overall Sentiment Donut */}
          <div className={`${styles.card} ${styles.donutCard}`}>
            <div className={styles.cardHead}>
              <span className={styles.cardLabel}>OVERALL SENTIMENT</span>
              <span className="material-symbols-outlined" style={{ fontSize: 18, color: 'var(--color-on-surface-variant)' }}>donut_large</span>
            </div>
            <div className={styles.donutWrap}>
              <div className={styles.donut}>
                <div className={styles.donutCenter}>
                  <span className={styles.donutPct}>65%</span>
                  <span className={styles.donutLbl}>Positive</span>
                </div>
              </div>
            </div>
            <div className={styles.donutLegend}>
              <div className={styles.legendItem}>
                <span className={styles.dotGreen} />
                <span className={styles.legendLabel}>Pos</span>
                <span className={styles.legendVal}>12.4k</span>
              </div>
              <div className={styles.legendItem}>
                <span className={styles.dotAmber} />
                <span className={styles.legendLabel}>Neu</span>
                <span className={styles.legendVal}>3.8k</span>
              </div>
              <div className={styles.legendItem}>
                <span className={styles.dotRed} />
                <span className={styles.legendLabel}>Neg</span>
                <span className={styles.legendVal}>2.8k</span>
              </div>
            </div>
          </div>

          {/* 2. Sentiment Trend Line Chart */}
          <div className={`${styles.card} ${styles.trendCard}`}>
            <div className={styles.cardHead}>
              <span className={styles.cardLabel}>SENTIMENT TREND</span>
              <span className="material-symbols-outlined" style={{ fontSize: 18, color: 'var(--color-on-surface-variant)' }}>show_chart</span>
            </div>
            <div className={styles.chartWrap}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={TREND} margin={{ top: 6, right: 8, left: -28, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(139,143,168,0.12)" vertical={false} />
                  <XAxis dataKey="week" tick={{ fill: 'var(--color-on-surface-variant)', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: 'var(--color-on-surface-variant)', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={chartStyle} />
                  <Line type="monotone" dataKey="positif" name="Positif" stroke="#58cc02" strokeWidth={2.5} dot={false} />
                  <Line type="monotone" dataKey="negatif" name="Negatif" stroke="#ff4b4b" strokeWidth={2} dot={false} strokeDasharray="4 3" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* 3. Positive Rate by Version Bar Chart */}
          <div className={`${styles.card} ${styles.barCard}`}>
            <div className={styles.cardHead}>
              <span className={styles.cardLabel}>POSITIVE SENTIMENT RATE BY VERSION</span>
              <span className="material-symbols-outlined" style={{ fontSize: 18, color: 'var(--color-on-surface-variant)' }}>bar_chart</span>
            </div>
            <div className={styles.barChart}>
              {VERSION_BARS.map((b) => (
                <div key={b.label} className={styles.barCol}>
                  <div className={styles.barTrack}>
                    <div
                      className={`${styles.barFill} ${b.active ? styles.barFillActive : ''}`}
                      style={{ height: `${b.pct}%` }}
                    />
                  </div>
                  <span className={`${styles.barLabel} ${b.active ? styles.barLabelActive : ''}`}>{b.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* 4. Word Clouds */}
          <div className={styles.wordCloudsRow}>
            {/* Positive */}
            <div className={styles.card}>
              <div className={styles.cardHead}>
                <span className={`${styles.cardLabel} ${styles.cardLabelGreen}`}>
                  <span className="material-symbols-outlined" style={{ fontSize: 14, fontVariationSettings: "'FILL' 1" }}>thumb_up</span>
                  TOP POSITIVE TERMS
                </span>
              </div>
              <div className={styles.wordCloud}>
                {WORDS_POS.map((w) => (
                  <span key={w.w} className={styles.wordPos} style={{ fontSize: w.sz, opacity: w.op }}>{w.w}</span>
                ))}
              </div>
            </div>
            {/* Negative */}
            <div className={styles.card}>
              <div className={styles.cardHead}>
                <span className={`${styles.cardLabel} ${styles.cardLabelRed}`}>
                  <span className="material-symbols-outlined" style={{ fontSize: 14, fontVariationSettings: "'FILL' 1" }}>thumb_down</span>
                  TOP NEGATIVE TERMS
                </span>
              </div>
              <div className={styles.wordCloud}>
                {WORDS_NEG.map((w) => (
                  <span key={w.w} className={styles.wordNeg} style={{ fontSize: w.sz, opacity: w.op }}>{w.w}</span>
                ))}
              </div>
            </div>
          </div>

          {/* 5. Raw Dataset Explorer */}
          <div className={`${styles.card} ${styles.tableCard}`}>
            <div className={styles.tableHead}>
              <span className={styles.cardLabel}>RAW DATASET EXPLORER</span>
              <div className={styles.tableControls}>
                <div className={styles.searchWrap}>
                  <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--color-on-surface-variant)' }}>search</span>
                  <input
                    id="review-search"
                    className={styles.searchInput}
                    type="text"
                    placeholder="Search reviews..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>
                <button className={styles.exportBtn}>
                  <span className="material-symbols-outlined" style={{ fontSize: 15 }}>download</span>
                  Export
                </button>
              </div>
            </div>

            <div className={styles.tableWrap}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>DATE</th>
                    <th>USER ID</th>
                    <th>REVIEW TEXT</th>
                    <th>VER</th>
                    <th>SENTIMENT</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((row, i) => (
                    <tr key={i}>
                      <td className={styles.tdMuted}>{row.date}</td>
                      <td className={styles.tdMono}>{row.uid}</td>
                      <td className={styles.tdText}>{row.text}</td>
                      <td className={styles.tdMuted}>{row.ver}</td>
                      <td><SentimentBadge s={row.sentiment} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination footer */}
            <div className={styles.tableFooter}>
              <span className={styles.footerInfo}>Showing 1 to {filtered.length} of 19,042 entries</span>
              <div className={styles.pagination}>
                <button className={styles.pgBtn} aria-label="Previous">
                  <span className="material-symbols-outlined" style={{ fontSize: 17 }}>chevron_left</span>
                </button>
                {[1, 2, 3].map((n) => (
                  <button key={n} className={`${styles.pgBtn} ${n === 1 ? styles.pgBtnActive : ''}`}>{n}</button>
                ))}
                <span className={styles.pgEllipsis}>...</span>
                <button className={styles.pgBtn} aria-label="Next">
                  <span className="material-symbols-outlined" style={{ fontSize: 17 }}>chevron_right</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
