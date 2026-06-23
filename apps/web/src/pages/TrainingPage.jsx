import { useState } from 'react'
import Sidebar from '../components/Sidebar'
import styles from './TrainingPage.module.css'

/* ── Static data ── */
const METRICS = [
  { label: 'Accuracy',  value: '89.4%', color: 'green',  icon: 'check_circle',    badge: '+2.1%', badgeType: 'up',   sub: 'vs last run' },
  { label: 'Precision', value: '87.2%', color: 'neutral', icon: 'target',          badge: '0.0%',  badgeType: 'flat', sub: '' },
  { label: 'Recall',    value: '88.1%', color: 'neutral', icon: 'keyboard_return', badge: '+0.5%', badgeType: 'up',   sub: '' },
  { label: 'F1-Score',  value: '87.6%', color: 'amber',  icon: 'balance',         badge: null,    badgeType: null,   sub: 'Harmonic mean' },
]

const HISTORY = [
  { version: 'v1.4.0', active: true,  accuracy: '89.4%', accuracyColor: true,  date: 'Today, 14:30',   canDeploy: false },
  { version: 'v1.3.2', active: false, accuracy: '87.3%', accuracyColor: false, date: 'Oct 24, 09:15',  canDeploy: true },
  { version: 'v1.3.1', active: false, accuracy: '86.8%', accuracyColor: false, date: 'Oct 20, 16:45',  canDeploy: true },
  { version: 'v1.2.0', active: false, accuracy: '82.1%', accuracyColor: false, date: 'Sep 15, 11:20',  canDeploy: true },
]

/* ── Sub-components ── */
function MetricCard({ m }) {
  return (
    <div className={`${styles.metricCard} ${m.color === 'green' ? styles.metricCardGreen : ''}`}>
      <div className={styles.metricTop}>
        <span className={styles.metricLabel}>{m.label}</span>
        <span
          className="material-symbols-outlined"
          style={{
            fontSize: 20,
            color: m.color === 'green' ? 'var(--color-primary-container)'
                 : m.color === 'amber' ? 'var(--color-secondary-container)'
                 : 'var(--color-on-surface-variant)',
            fontVariationSettings: m.color === 'green' ? "'FILL' 1" : "'FILL' 0",
          }}
        >
          {m.icon}
        </span>
      </div>
      <p className={`${styles.metricValue} ${
        m.color === 'green' ? styles.metricValueGreen
      : m.color === 'amber' ? styles.metricValueAmber
      : styles.metricValueNeutral}`}>
        {m.value}
      </p>
      <div className={styles.metricFooter}>
        {m.badge && (
          <span className={`${styles.metricBadge} ${
            m.badgeType === 'up'   ? styles.metricBadgeUp
          : m.badgeType === 'flat' ? styles.metricBadgeFlat
          : ''}`}>
            <span className="material-symbols-outlined" style={{ fontSize: 10 }}>
              {m.badgeType === 'up' ? 'trending_up' : 'trending_flat'}
            </span>
            {m.badge}
          </span>
        )}
        {m.sub && <span className={styles.metricSub}>{m.sub}</span>}
      </div>
    </div>
  )
}

/* ── Page ── */
export default function TrainingPage() {
  const [algorithm,  setAlgorithm]  = useState('nb')
  const [features,   setFeatures]   = useState('tfidf')
  const [ngramMin,   setNgramMin]   = useState(1)
  const [ngramMax,   setNgramMax]   = useState(2)
  const [splitRatio, setSplitRatio] = useState(80)
  const [training,   setTraining]   = useState(false)
  const [searchVal,  setSearchVal]  = useState('')

  const handleTrain = () => {
    setTraining(true)
    setTimeout(() => setTraining(false), 3000)
  }

  return (
    <div className={styles.layout}>
      <Sidebar />

      <div className={styles.main}>
        {/* ── Header ── */}
        <header className={styles.header}>
          <div className={styles.breadcrumb}>
            <span className={styles.breadcrumbBrand}>LingoAnalytics</span>
            <span className={styles.breadcrumbSep}>/</span>
            <span className={styles.breadcrumbPage}>Training Model</span>
          </div>
          <div className={styles.headerRight}>
            <div className={styles.searchWrap}>
              <span className="material-symbols-outlined" style={{ fontSize: 17, color: 'var(--color-on-surface-variant)' }}>search</span>
              <input
                id="metrics-search"
                className={styles.searchInput}
                type="text"
                placeholder="Search metrics..."
                value={searchVal}
                onChange={(e) => setSearchVal(e.target.value)}
              />
            </div>
            <button className={styles.iconBtn} aria-label="Notifikasi">
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>notifications</span>
            </button>
            <button className={styles.iconBtn} aria-label="Profil">
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>account_circle</span>
            </button>
          </div>
        </header>

        {/* ── Scrollable content ── */}
        <div className={styles.content}>
          {/* Page title row */}
          <div className={styles.pageTitleRow}>
            <div>
              <h1 className={styles.pageTitle}>Model Pipeline Setup</h1>
              <p className={styles.pageSubtitle}>Configure hyperparameters and evaluate text classification models.</p>
            </div>
            <div className={styles.engineBadge}>
              <span className={styles.enginePulse}><span className={styles.enginePulseInner} /></span>
              <span className={styles.engineLabel}>Engine Ready</span>
            </div>
          </div>

          {/* ── Bento Grid ── */}
          <div className={styles.grid}>

            {/* LEFT: Configuration */}
            <div className={styles.configPanel}>
              <div className={styles.configHeader}>
                <span className="material-symbols-outlined" style={{ color: 'var(--color-primary-container)', fontSize: 20 }}>tune</span>
                <h2 className={styles.configTitle}>Configuration</h2>
              </div>

              <div className={styles.configForm}>
                {/* Algorithm */}
                <div className={styles.field}>
                  <label className={styles.fieldLabel}>Algorithm</label>
                  <div className={styles.selectWrap}>
                    <select id="algo-select" className={styles.select} value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}>
                      <option value="nb">Naïve Bayes</option>
                      <option value="svm">Support Vector Machine</option>
                      <option value="lr">Logistic Regression</option>
                      <option value="rf">Random Forest</option>
                    </select>
                    <span className="material-symbols-outlined" style={{ fontSize: 18 }}>expand_more</span>
                  </div>
                </div>

                {/* Feature Extraction */}
                <div className={styles.field}>
                  <label className={styles.fieldLabel}>Feature Extraction</label>
                  <div className={styles.selectWrap}>
                    <select id="feature-select" className={styles.select} value={features} onChange={(e) => setFeatures(e.target.value)}>
                      <option value="tfidf">TF-IDF Vectorizer</option>
                      <option value="bow">Bag of Words</option>
                      <option value="w2v">Word2Vec (Pre-trained)</option>
                    </select>
                    <span className="material-symbols-outlined" style={{ fontSize: 18 }}>expand_more</span>
                  </div>
                </div>

                {/* N-Gram */}
                <div className={styles.field}>
                  <label className={styles.fieldLabel}>N-Gram Range</label>
                  <div className={styles.ngramRow}>
                    <div className={styles.ngramField}>
                      <span className={styles.ngramPrefix}>Min</span>
                      <input
                        id="ngram-min"
                        className={`${styles.input} ${styles.inputPrefixed}`}
                        type="number" min={1} max={3}
                        value={ngramMin}
                        onChange={(e) => setNgramMin(+e.target.value)}
                      />
                    </div>
                    <div className={styles.ngramField}>
                      <span className={styles.ngramPrefix}>Max</span>
                      <input
                        id="ngram-max"
                        className={`${styles.input} ${styles.inputPrefixed}`}
                        type="number" min={1} max={4}
                        value={ngramMax}
                        onChange={(e) => setNgramMax(+e.target.value)}
                      />
                    </div>
                  </div>
                </div>

                {/* Split Ratio */}
                <div className={styles.field}>
                  <div className={styles.sliderHeader}>
                    <label className={styles.fieldLabel}>Train/Test Split</label>
                    <span className={styles.sliderValue}>{splitRatio} / {100 - splitRatio}</span>
                  </div>
                  <input
                    id="split-slider"
                    className={styles.slider}
                    type="range" min={50} max={90}
                    value={splitRatio}
                    onChange={(e) => setSplitRatio(+e.target.value)}
                  />
                  <div className={styles.sliderTicks}>
                    <span>50%</span><span>90%</span>
                  </div>
                </div>

                {/* Train button */}
                <button
                  id="mulai-training"
                  className={`${styles.trainBtn} ${training ? styles.trainBtnLoading : ''}`}
                  onClick={handleTrain}
                  disabled={training}
                >
                  {training ? (
                    <>
                      <span className={styles.trainSpinner} />
                      Training...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined" style={{ fontSize: 18, fontVariationSettings: "'FILL' 1" }}>play_arrow</span>
                      Mulai Training
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* RIGHT COLUMN */}
            <div className={styles.rightCol}>

              {/* Metric cards row */}
              <div className={styles.metricsRow}>
                {METRICS.map((m) => <MetricCard key={m.label} m={m} />)}
              </div>

              {/* Bottom row: confusion matrix + history */}
              <div className={styles.bottomRow}>

                {/* Confusion Matrix */}
                <div className={styles.card}>
                  <h3 className={styles.cardTitle}>Confusion Matrix</h3>
                  <p className={styles.cardSub}>Test set predictions breakdown.</p>

                  <div className={styles.matrixWrap}>
                    {/* Y axis */}
                    <div className={styles.matrixYLabel}>
                      <span>ACTUAL</span>
                    </div>

                    <div className={styles.matrixBody}>
                      {/* X axis labels */}
                      <div className={styles.matrixXLabel}>PREDICTED</div>

                      <div className={styles.matrixColLabels}>
                        <span>Pos</span><span>Neg</span>
                      </div>

                      <div className={styles.matrixRowLabelAndGrid}>
                        <div className={styles.matrixRowLabels}>
                          <span>Pos</span><span>Neg</span>
                        </div>
                        <div className={styles.matrixGrid}>
                          <div className={`${styles.matrixCell} ${styles.cellTP}`}>
                            <span className={styles.cellNum}>1,245</span>
                            <span className={styles.cellLbl}>TP</span>
                          </div>
                          <div className={`${styles.matrixCell} ${styles.cellFN}`}>
                            <span className={styles.cellNum}>182</span>
                            <span className={styles.cellLbl}>FN</span>
                          </div>
                          <div className={`${styles.matrixCell} ${styles.cellFP}`}>
                            <span className={styles.cellNum}>210</span>
                            <span className={styles.cellLbl}>FP</span>
                          </div>
                          <div className={`${styles.matrixCell} ${styles.cellTN}`}>
                            <span className={styles.cellNum}>3,190</span>
                            <span className={styles.cellLbl}>TN</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Training History */}
                <div className={styles.historyCard}>
                  <div className={styles.historyHeader}>
                    <h3 className={styles.cardTitle}>Training History</h3>
                    <button className={styles.viewAllBtn}>
                      View All
                      <span className="material-symbols-outlined" style={{ fontSize: 16 }}>arrow_forward</span>
                    </button>
                  </div>

                  <div className={styles.tableWrap}>
                    <table className={styles.table}>
                      <thead>
                        <tr>
                          <th>VERSION</th>
                          <th>ACCURACY</th>
                          <th>DATE</th>
                          <th className={styles.thRight}>ACTIONS</th>
                        </tr>
                      </thead>
                      <tbody>
                        {HISTORY.map((row) => (
                          <tr key={row.version}>
                            <td>
                              <div className={styles.versionCell}>
                                <span className={styles.versionName}>{row.version}</span>
                                {row.active && <span className={styles.activeBadge}>Active</span>}
                              </div>
                            </td>
                            <td className={row.accuracyColor ? styles.accuracyGreen : styles.accuracyMuted}>{row.accuracy}</td>
                            <td className={styles.dateMuted}>{row.date}</td>
                            <td>
                              <div className={styles.actionBtns}>
                                {row.canDeploy && (
                                  <button className={styles.actionBtn} title="Deploy">
                                    <span className="material-symbols-outlined" style={{ fontSize: 18 }}>rocket_launch</span>
                                  </button>
                                )}
                                <button className={styles.actionBtn} title="Download">
                                  <span className="material-symbols-outlined" style={{ fontSize: 18 }}>download</span>
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
