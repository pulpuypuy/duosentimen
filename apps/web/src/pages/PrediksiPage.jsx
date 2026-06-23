import { useState, useRef } from 'react'
import Sidebar from '../components/Sidebar'
import styles from './PrediksiPage.module.css'

/* ── Naive preprocessing simulation ── */
const STOP_WORDS = new Set(['ini', 'itu', 'yang', 'dan', 'di', 'ke', 'dari', 'dengan', 'untuk', 'saat', 'mau', 'lagi', 'saya', 'aku', 'kamu', 'nya'])
const STEM_MAP   = { 'membantu': 'bantu', 'belajar': 'ajar', 'menggunakan': 'guna', 'diperbaiki': 'perbaiki', 'memperbaiki': 'perbaiki', 'memproses': 'proses', 'melatih': 'latih', 'latihan': 'latih', 'submit': 'submit', 'bikin': 'bikin', 'males': 'males', 'segera': 'segera', 'sering': 'sering' }

function preprocess(text) {
  return text
    .toLowerCase()
    .replace(/@\w+/g, '')
    .replace(/#\w+/g, '')
    .replace(/[!?.,"'():;]/g, '')
    .split(/\s+/)
    .filter((w) => w && !STOP_WORDS.has(w))
    .map((w) => STEM_MAP[w] || w)
    .join(' ')
}

/* ── Naive sentiment classifier ── */
const NEG_WORDS = ['error', 'crash', 'bug', 'lambat', 'gagal', 'males', 'susah', 'berat', 'buruk', 'jelek', 'parah', 'kecewa', 'tolong', 'perbaiki', 'keluar', 'lelet']
const POS_WORDS = ['bagus', 'bantu', 'keren', 'suka', 'mantap', 'akurat', 'cepat', 'mudah', 'lengkap', 'senang', 'puas', 'berhasil', 'lancar', 'hebat']

function classify(processed) {
  const words = processed.split(' ')
  let negScore = 0, posScore = 0
  words.forEach((w) => {
    if (NEG_WORDS.includes(w)) negScore++
    if (POS_WORDS.includes(w)) posScore++
  })
  if (negScore > posScore) {
    const conf = Math.min(99, 70 + negScore * 8 - posScore * 3)
    return { label: 'NEGATIF', conf, pos: Math.max(1, 100 - conf - 5), neu: Math.max(1, 5) }
  }
  if (posScore > negScore) {
    const conf = Math.min(99, 70 + posScore * 8 - negScore * 3)
    return { label: 'POSITIF', conf, neg: Math.max(1, 100 - conf - 5), neu: Math.max(1, 5) }
  }
  return { label: 'NETRAL', conf: 67, pos: 18, neg: 15 }
}

/* ── Initial state ── */
const INIT_TEXT = 'Aplikasi ini sering error saat mau submit latihan, bikin males belajar lagi. Tolong segera diperbaiki bugnya!'
const INIT_RESULT = { label: 'NEGATIF', conf: 89.4, pos: 8.2, neu: 2.4 }
const INIT_HISTORY = [
  { text: 'Aplikasi ini sering error saat mau submit...', label: 'NEGATIF', conf: 89.4 },
  { text: 'Sangat suka dengan update terbaru, UI-nya jadi lebih bersih.', label: 'POSITIF', conf: 94.1 },
  { text: 'Saya menggunakan aplikasi ini setiap hari untuk belajar Spanyol.', label: 'NETRAL',  conf: 67.8 },
]

/* ── Helpers ── */
function sentimentColor(label) {
  if (label === 'NEGATIF') return '#ff4b4b'
  if (label === 'POSITIF') return '#58cc02'
  return 'var(--color-surface-variant)'
}
function sentimentBg(label) {
  if (label === 'NEGATIF') return 'color-mix(in srgb, #ff4b4b 15%, transparent)'
  if (label === 'POSITIF') return 'color-mix(in srgb, #58cc02 15%, transparent)'
  return 'color-mix(in srgb, var(--color-surface-variant) 40%, transparent)'
}
function sentimentBorder(label) {
  if (label === 'NEGATIF') return 'color-mix(in srgb, #ff4b4b 30%, transparent)'
  if (label === 'POSITIF') return 'color-mix(in srgb, #58cc02 30%, transparent)'
  return 'var(--color-surface-variant)'
}

/* ── Bar component ── */
function ScoreBar({ label, pct, color }) {
  return (
    <div className={styles.scoreBar}>
      <div className={styles.scoreBarTop}>
        <span className={styles.scoreBarLabel}>{label}</span>
        <span className={styles.scoreBarPct}>{pct.toFixed(1)}%</span>
      </div>
      <div className={styles.scoreTrack}>
        <div className={styles.scoreFill} style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  )
}

/* ── Page ── */
export default function PrediksiPage() {
  const [inputText, setInputText] = useState(INIT_TEXT)
  const [result,    setResult]    = useState(INIT_RESULT)
  const [history,   setHistory]   = useState(INIT_HISTORY)
  const [loading,   setLoading]   = useState(false)
  const [processed, setProcessed] = useState(preprocess(INIT_TEXT))

  const handlePredict = () => {
    if (!inputText.trim()) return
    setLoading(true)
    // Simulate async model call
    setTimeout(() => {
      const proc = preprocess(inputText)
      setProcessed(proc)
      const res  = classify(proc)
      const neg  = res.label === 'NEGATIF' ? res.conf : (res.neg ?? Math.round((100 - res.conf) * 0.6))
      const pos  = res.label === 'POSITIF' ? res.conf : (res.pos ?? Math.round((100 - res.conf) * 0.3))
      const neu  = Math.max(0.5, 100 - neg - pos)
      const finalRes = { label: res.label, conf: res.conf, neg, pos, neu }
      setResult(finalRes)
      setHistory((prev) => [
        { text: inputText.slice(0, 52) + (inputText.length > 52 ? '...' : ''), label: res.label, conf: res.conf },
        ...prev.slice(0, 4),
      ])
      setLoading(false)
    }, 1200)
  }

  const confGlowColor = result.label === 'NEGATIF' ? 'rgba(255,75,75,0.1)'
                      : result.label === 'POSITIF' ? 'rgba(88,204,2,0.1)'
                      : 'rgba(139,143,168,0.1)'

  return (
    <div className={styles.layout}>
      <Sidebar />

      <div className={styles.main}>
        {/* ── Header ── */}
        <header className={styles.header}>
          <h1 className={styles.pageTitle}>Prediksi Sentimen</h1>
          <div className={styles.headerIcons}>
            <button className={styles.iconBtn} aria-label="Notifikasi">
              <span className="material-symbols-outlined" style={{ fontSize: 22 }}>notifications</span>
            </button>
            <button className={styles.iconBtn} aria-label="Profil">
              <span className="material-symbols-outlined" style={{ fontSize: 22 }}>account_circle</span>
            </button>
          </div>
        </header>

        {/* ── Canvas ── */}
        <div className={styles.canvas}>
          <div className={styles.grid}>

            {/* ── LEFT COLUMN ── */}
            <div className={styles.leftCol}>
              {/* Input Teks */}
              <section className={styles.card}>
                <h2 className={styles.cardTitle}>
                  <span className="material-symbols-outlined" style={{ fontSize: 22, color: 'var(--color-primary)' }}>edit_note</span>
                  Input Teks
                </h2>
                <p className={styles.cardDesc}>
                  Masukkan ulasan atau teks yang ingin dianalisis sentimennya. Model akan memproses dan memprediksi kecenderungannya.
                </p>
                <textarea
                  id="prediction-input"
                  className={styles.textarea}
                  rows={6}
                  placeholder="Masukkan teks ulasan... (contoh: Aplikasi ini sangat membantu belajar bahasa dengan mudah)"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                />
                <div className={styles.inputActions}>
                  <span className={styles.charCount}>{inputText.length} karakter</span>
                  <button
                    id="predict-btn"
                    className={`${styles.predictBtn} ${loading ? styles.predictBtnLoading : ''}`}
                    onClick={handlePredict}
                    disabled={loading || !inputText.trim()}
                  >
                    {loading ? (
                      <>
                        <span className={styles.predictSpinner} />
                        Memproses...
                      </>
                    ) : (
                      <>
                        <span className="material-symbols-outlined" style={{ fontSize: 18, fontVariationSettings: "'FILL' 1" }}>auto_awesome</span>
                        Prediksi Sekarang
                      </>
                    )}
                  </button>
                </div>
              </section>

              {/* Preprocessing Preview */}
              <section className={styles.card}>
                <h3 className={styles.previewTitle}>
                  <span className="material-symbols-outlined" style={{ fontSize: 16 }}>cleaning_services</span>
                  HASIL PREPROCESSING (PREVIEW)
                </h3>
                <div className={styles.codeBlock}>
                  <span className={styles.codeComment}>#</span>{' '}
                  {processed || <span style={{ opacity: 0.4 }}>— teks akan muncul setelah prediksi —</span>}
                </div>
              </section>
            </div>

            {/* ── RIGHT COLUMN ── */}
            <div className={styles.rightCol}>
              {/* Hasil Analisis */}
              <section className={styles.card} style={{ position: 'relative', overflow: 'hidden' }}>
                {/* Decorative glow */}
                <div style={{
                  position: 'absolute', top: 0, right: 0,
                  width: 128, height: 128,
                  background: confGlowColor,
                  borderRadius: '50%', filter: 'blur(40px)',
                  marginTop: -32, marginRight: -32,
                  pointerEvents: 'none', transition: 'background 0.4s',
                }} />
                <h2 className={styles.resultTitle}>Hasil Analisis</h2>

                {/* Label + confidence */}
                <div className={styles.resultTop}>
                  <div className={styles.resultLabel} style={{
                    background: sentimentBg(result.label),
                    border: `1px solid ${sentimentBorder(result.label)}`,
                    color: sentimentColor(result.label),
                  }}>
                    {result.label}
                  </div>
                  <div className={styles.confidenceBlock}>
                    <span className={styles.confidenceHead}>CONFIDENCE SCORE</span>
                    <span className={styles.confidenceVal}>{result.conf.toFixed(1)}%</span>
                  </div>
                </div>

                {/* Score bars */}
                <div className={styles.scoreBars}>
                  <ScoreBar label="Negatif" pct={result.neg ?? (result.label === 'NEGATIF' ? result.conf : 8)}  color="#ff4b4b" />
                  <ScoreBar label="Positif" pct={result.pos ?? (result.label === 'POSITIF' ? result.conf : 8)}  color="#58cc02" />
                  <ScoreBar label="Netral"  pct={result.neu ?? 2.4} color="var(--color-surface-variant)" />
                </div>
              </section>

              {/* Riwayat Prediksi */}
              <section className={`${styles.card} ${styles.historyCard}`}>
                <h3 className={styles.historyTitle}>
                  <span className="material-symbols-outlined" style={{ fontSize: 16 }}>history</span>
                  RIWAYAT PREDIKSI
                </h3>
                <div className={styles.historyList}>
                  {history.map((h, i) => (
                    <div
                      key={i}
                      className={styles.historyItem}
                      onClick={() => setInputText(h.text.replace('...', ''))}
                    >
                      <span className={styles.historyDot} style={{ background: sentimentColor(h.label) }} />
                      <div className={styles.historyText}>
                        <p className={styles.historySnippet}>{h.text}</p>
                        <span className={styles.historyMeta}>{h.label} • {h.conf.toFixed(1)}%</span>
                      </div>
                    </div>
                  ))}
                  {history.length === 0 && (
                    <p className={styles.historyEmpty}>Belum ada riwayat prediksi.</p>
                  )}
                </div>
              </section>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
