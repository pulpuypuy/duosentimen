import { useState, useEffect, useRef } from 'react'
import Sidebar from '../components/Sidebar'
import styles from './PreprocessingPage.module.css'

/* ── Static data ── */
const WIZARD_STEPS = [
  { n: 1, label: 'PILIH DATASET' },
  { n: 2, label: 'KONFIGURASI' },
  { n: 3, label: 'PROSES' },
  { n: 4, label: 'SELESAI' },
]

const INITIAL_PIPELINE = [
  { id: 'cleaning',   label: 'Cleaning',          desc: 'Hapus URL, mention, hashtag',    status: 'done' },
  { id: 'casefolding',label: 'Case Folding',       desc: 'Ubah ke huruf kecil semua',      status: 'done' },
  { id: 'tokenisasi', label: 'Tokenisasi',         desc: 'Pecah kalimat jadi kata',        status: 'done' },
  { id: 'normalisasi',label: 'Normalisasi',        desc: 'Perbaiki kata tidak baku',       status: 'active' },
  { id: 'stopword',   label: 'Stopword Removal',   desc: 'Buang kata hubung/umum',         status: 'pending' },
  { id: 'stemming',   label: 'Stemming',           desc: 'Kembalikan ke kata dasar',       status: 'pending' },
]

const PREVIEW_ROWS = [
  { id: '#01', raw: '"Appnya bagus bgt tpi syg update trs :( #duolingo"', clean: 'aplikasi bagus banget tapi sayang perbarui terus', done: true },
  { id: '#02', raw: '"Gw gbsa login nih gmn min?? @duo_id"',              clean: 'saya tidak bisa masuk ini bagaimana admin',         done: true },
  { id: '#03', raw: '"MANTAPPPPP streak 100 hari 🔥🔥🔥"',               clean: 'mantap rentetan 100 hari',                          done: true },
  { id: '#04', raw: '"Knp sllu crash woyy pas mau latian"',               clean: null,                                                done: false },
]

/* ── Sub-components ── */
function StepIcon({ status }) {
  if (status === 'done') {
    return (
      <span className={`material-symbols-outlined ${styles.stepIconDone}`}
        style={{ fontVariationSettings: "'FILL' 1", fontSize: 20 }}>
        check_circle
      </span>
    )
  }
  if (status === 'active') {
    return <span className={`material-symbols-outlined ${styles.stepIconActive}`} style={{ fontSize: 20 }}>sync</span>
  }
  return <span className={styles.stepIconPending} />
}

function PreviewRow({ row, isCurrentlyProcessing }) {
  const isActive = !row.done && isCurrentlyProcessing
  return (
    <tr className={`${styles.previewRow} ${isActive ? styles.previewRowActive : ''}`}>
      <td className={`${styles.previewId} ${isActive ? styles.previewIdActive : ''}`}>{row.id}</td>
      <td className={styles.previewRaw}>{row.raw}</td>
      <td className={styles.previewClean}>
        {row.done ? (
          <span className={styles.cleanText}>{row.clean}</span>
        ) : (
          <span className={styles.normalizing}>
            <span className={`material-symbols-outlined ${styles.spinIcon}`} style={{ fontSize: 15 }}>sync</span>
            Normalizing...
          </span>
        )}
      </td>
    </tr>
  )
}

/* ── Page ── */
export default function PreprocessingPage() {
  const [progress, setProgress]   = useState(65)
  const [pipeline, setPipeline]   = useState(INITIAL_PIPELINE)
  const [rows, setRows]           = useState(PREVIEW_ROWS)
  const [running, setRunning]     = useState(true)
  const [liveDiff, setLiveDiff]   = useState(false)
  const timerRef                  = useRef(null)

  useEffect(() => {
    if (!running) return
    timerRef.current = setInterval(() => {
      setProgress((p) => {
        const next = p + 0.4
        if (next >= 100) {
          clearInterval(timerRef.current)
          setRunning(false)
          // Complete normalisasi → activate stopword
          setPipeline((prev) => prev.map((s) =>
            s.id === 'normalisasi' ? { ...s, status: 'done' }
          : s.id === 'stopword'   ? { ...s, status: 'active' }
          : s
          ))
          // Mark row #04 done
          setRows((prev) => prev.map((r) =>
            r.id === '#04' ? { ...r, done: true, clean: 'kenapa selalu crash saat mau latihan' } : r
          ))
          return 100
        }
        return next
      })
    }, 80)
    return () => clearInterval(timerRef.current)
  }, [running])

  const handleStop = () => {
    clearInterval(timerRef.current)
    setRunning(false)
  }

  const activeIdx = WIZARD_STEPS.findIndex((s) => s.n === 3)

  return (
    <div className={styles.layout}>
      <Sidebar />

      <div className={styles.main}>
        {/* Header */}
        <header className={styles.header}>
          <h1 className={styles.pageTitle}>Preprocessing Data</h1>
          <div className={styles.headerIcons}>
            <button className={styles.iconBtn} aria-label="Notifikasi">
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>notifications</span>
            </button>
            <button className={styles.iconBtn} aria-label="Profil">
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>account_circle</span>
            </button>
          </div>
        </header>

        <div className={styles.content}>
          {/* ── Wizard Stepper ── */}
          <div className={styles.stepper}>
            {WIZARD_STEPS.map((step, i) => {
              const state = step.n < 3 ? 'past' : step.n === 3 ? 'active' : 'future'
              return (
                <div key={step.n} className={styles.stepItem}>
                  {i > 0 && <div className={`${styles.stepLine} ${state !== 'future' ? styles.stepLineDone : ''}`} />}
                  <div className={`${styles.stepCircle} ${styles[`stepCircle_${state}`]}`}>
                    {step.n}
                  </div>
                  <p className={`${styles.stepLabel} ${state === 'active' ? styles.stepLabelActive : ''}`}>
                    {step.label}
                  </p>
                </div>
              )
            })}
          </div>

          {/* ── Main panels ── */}
          <div className={styles.panels}>
            {/* LEFT: Pipeline Steps */}
            <div className={styles.leftPanel}>
              <div className={styles.card}>
                <h2 className={styles.panelTitle}>
                  <span className="material-symbols-outlined" style={{ fontSize: 18 }}>account_tree</span>
                  Pipeline Steps
                </h2>
                <div className={styles.pipelineList}>
                  {pipeline.map((step) => (
                    <div
                      key={step.id}
                      className={`${styles.pipelineItem} ${step.status === 'active' ? styles.pipelineItemActive : ''}`}
                    >
                      <StepIcon status={step.status} />
                      <div className={styles.pipelineText}>
                        <p className={`${styles.pipelineName} ${step.status === 'pending' ? styles.pipelineNamePending : ''}`}>
                          {step.label}
                        </p>
                        <p className={styles.pipelineDesc}>{step.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Progress footer */}
                <div className={styles.progressSection}>
                  <div className={styles.progressMeta}>
                    <span className={styles.progressLabel}>Progress: {Math.round(progress)}%</span>
                    <span className={styles.processingText}>{running ? 'Processing...' : 'Selesai'}</span>
                  </div>
                  <div className={styles.progressTrack}>
                    <div className={styles.progressBar} style={{ width: `${progress}%` }} />
                  </div>
                </div>
              </div>
            </div>

            {/* RIGHT: Preview + Distribution */}
            <div className={styles.rightPanel}>
              {/* Preview Transformasi */}
              <div className={styles.card}>
                <div className={styles.previewHeader}>
                  <h2 className={styles.previewTitle}>
                    <span className="material-symbols-outlined" style={{ fontSize: 18, fontVariationSettings: "'FILL' 1" }}>description</span>
                    Preview Transformasi
                  </h2>
                  <button
                    id="live-diff-btn"
                    className={`${styles.diffBtn} ${liveDiff ? styles.diffBtnActive : ''}`}
                    onClick={() => setLiveDiff((v) => !v)}
                  >
                    LIVE DIFF VIEW
                  </button>
                </div>

                <div className={styles.tableWrap}>
                  <table className={styles.previewTable}>
                    <thead>
                      <tr>
                        <th style={{ width: 46 }}>ID</th>
                        <th>Raw Text (Before)</th>
                        <th>Cleaned Text (After)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((row) => (
                        <PreviewRow key={row.id} row={row} isCurrentlyProcessing={running} />
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Distribution card */}
              <div className={styles.distCard}>
                <div className={styles.distIcon}>
                  <span className="material-symbols-outlined"
                    style={{ fontSize: 24, color: 'var(--color-primary-container)', fontVariationSettings: "'FILL' 1" }}>
                    bar_chart
                  </span>
                </div>
                <div className={styles.distInfo}>
                  <p className={styles.distTitle}>Estimasi Distribusi Label (Post-Clean)</p>
                  <div className={styles.distLegend}>
                    <span className={styles.distItem}><span className={styles.dotGreen} /> Positif (60%)</span>
                    <span className={styles.distItem}><span className={styles.dotRed} /> Negatif (25%)</span>
                    <span className={styles.distItem}><span className={styles.dotGray} /> Netral (15%)</span>
                  </div>
                </div>
                <button id="stop-process" className={styles.stopProcessBtn} onClick={handleStop} disabled={!running}>
                  Stop Process
                  <span className="material-symbols-outlined" style={{ fontSize: 16 }}>radio_button_checked</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
