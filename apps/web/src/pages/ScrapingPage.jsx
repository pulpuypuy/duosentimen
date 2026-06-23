import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Sidebar from '../components/Sidebar'
import { api } from '../lib/api'
import styles from './ScrapingPage.module.css'

function StatusBadge({ status }) {
  const cls = status === 'SELESAI' ? styles.badgeSelesai
            : status === 'GAGAL'   ? styles.badgeGagal
            : styles.badgePending
  return (
    <span className={`${styles.badge} ${cls}`}>
      <span className={styles.badgeDot} />
      {status}
    </span>
  )
}

export default function ScrapingPage() {
  const [targetUrl,    setTargetUrl]    = useState('com.duolingo')
  const [maxUlasan,    setMaxUlasan]    = useState('1000')
  const [filterBintang, setFilterBintang] = useState('Semua')
  const [tglMulai,     setTglMulai]     = useState('2023-01-01')
  const [tglAkhir,     setTglAkhir]     = useState('2023-12-31')
  const [activeJobId,  setActiveJobId]  = useState(null)

  const queryClient = useQueryClient()

  // Fetch total local dataset size
  const { data: statsRes } = useQuery({
    queryKey: ['scrapingStats'],
    queryFn: () => api.get('/scraping/stats')
  })
  const totalDatasetLokal = statsRes?.data?.total_dataset || 0

  // Fetch job history
  const { data: historyRes } = useQuery({
    queryKey: ['scrapingJobs'],
    queryFn: () => api.get('/scraping/jobs')
  })
  const history = historyRes?.data?.items || []

  // Poll active job status if there is one
  const { data: activeJobRes } = useQuery({
    queryKey: ['scrapingJob', activeJobId],
    queryFn: () => api.get(`/scraping/jobs/${activeJobId}`),
    enabled: !!activeJobId,
    refetchInterval: (data) => (data?.data?.status === 'RUNNING' || data?.data?.status === 'PENDING') ? 2000 : false,
    onSuccess: (res) => {
        if (res.data?.status === 'SELESAI' || res.data?.status === 'GAGAL') {
            queryClient.invalidateQueries(['scrapingJobs'])
            queryClient.invalidateQueries(['scrapingStats'])
            setActiveJobId(null)
        }
    }
  })
  const activeJob = activeJobRes?.data
  const isRunning = activeJob?.status === 'RUNNING' || activeJob?.status === 'PENDING'
  const scraped = activeJob?.reviews_scraped || 0
  const totalTarget = activeJob?.max_reviews || parseInt(maxUlasan)
  const progress = Math.min(Math.round((scraped / totalTarget) * 100), 100) || 0
  const formatNum = (n) => n.toLocaleString('id-ID')

  // Mutations
  const startMutation = useMutation({
    mutationFn: (payload) => api.post('/scraping/jobs', payload),
    onSuccess: (res) => {
        setActiveJobId(res.data.id)
        queryClient.invalidateQueries(['scrapingJobs'])
    }
  })

  const stopMutation = useMutation({
    mutationFn: (id) => api.post(`/scraping/jobs/${id}/stop`),
    onSuccess: () => queryClient.invalidateQueries(['scrapingJob', activeJobId])
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/scraping/jobs/${id}`),
    onSuccess: () => {
        queryClient.invalidateQueries(['scrapingJobs'])
        queryClient.invalidateQueries(['scrapingStats'])
    }
  })

  const handleStart = () => {
      startMutation.mutate({
          target_app_id: targetUrl,
          max_reviews: parseInt(maxUlasan),
          filter_bintang: filterBintang,
          date_from: tglMulai,
          date_to: tglAkhir
      })
  }

  const handleDelete = (id) => {
      if(window.confirm('Yakin ingin menghapus job ini?')) {
          deleteMutation.mutate(id)
      }
  }

  return (
    <div className={styles.layout}>
      <Sidebar />

      <div className={styles.main}>
        {/* Header */}
        <header className={styles.header}>
          <h1 className={styles.pageTitle}>Scraping Data</h1>
          <div className={styles.headerIcons}>
            <button id="scraping-notifications" className={styles.iconBtn} aria-label="Notifikasi">
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>notifications</span>
            </button>
            <button id="scraping-user" className={styles.iconBtn} aria-label="Profil">
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>account_circle</span>
            </button>
          </div>
        </header>

        <div className={styles.content}>
          <div className={styles.panels}>

            {/* ── LEFT PANEL ── */}
            <div className={styles.leftPanel}>

              {/* Parameter Scraping form */}
              <div className={styles.card}>
                <h2 className={styles.sectionTitle}>
                  <span className="material-symbols-outlined" style={{ fontSize: 18 }}>segment</span>
                  PARAMETER SCRAPING
                </h2>

                <div className={styles.formFields}>
                  <div className={styles.field}>
                    <label className={styles.fieldLabel}>Target URL (Google Play)</label>
                    <input
                      id="target-url"
                      className={styles.input}
                      value={targetUrl}
                      onChange={(e) => setTargetUrl(e.target.value)}
                      placeholder="com.duolingo"
                      disabled={isRunning}
                    />
                  </div>

                  <div className={styles.field}>
                    <label className={styles.fieldLabel}>Jumlah Ulasan Maksimal</label>
                    <input
                      id="max-ulasan"
                      className={styles.input}
                      type="number"
                      value={maxUlasan}
                      onChange={(e) => setMaxUlasan(e.target.value)}
                      disabled={isRunning}
                    />
                  </div>

                  <div className={styles.field}>
                    <label className={styles.fieldLabel}>Filter Bintang</label>
                    <div className={styles.selectWrap}>
                      <select
                        id="filter-bintang"
                        className={styles.select}
                        value={filterBintang}
                        onChange={(e) => setFilterBintang(e.target.value)}
                        disabled={isRunning}
                      >
                        <option value="Semua">Semua Bintang (1-5)</option>
                        <option value="Bintang 1-2">Bintang 1-2</option>
                        <option value="Bintang 3">Bintang 3</option>
                        <option value="Bintang 4-5">Bintang 4-5</option>
                      </select>
                      <span className="material-symbols-outlined" style={{ fontSize: 18 }}>expand_more</span>
                    </div>
                  </div>

                  <div className={styles.dateRow}>
                    <div className={styles.field}>
                      <label className={styles.fieldLabel}>Tanggal Mulai</label>
                      <input
                        type="date"
                        id="tgl-mulai"
                        className={styles.input}
                        value={tglMulai}
                        onChange={(e) => setTglMulai(e.target.value)}
                        disabled={isRunning}
                      />
                    </div>
                    <div className={styles.field}>
                      <label className={styles.fieldLabel}>Tanggal Akhir</label>
                      <input
                        type="date"
                        id="tgl-akhir"
                        className={styles.input}
                        value={tglAkhir}
                        onChange={(e) => setTglAkhir(e.target.value)}
                        disabled={isRunning}
                      />
                    </div>
                  </div>
                </div>

                <button
                  id="mulai-scraping"
                  className={styles.startBtn}
                  onClick={handleStart}
                  disabled={isRunning || startMutation.isLoading}
                >
                  <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
                    {isRunning ? 'hourglass_top' : 'play_arrow'}
                  </span>
                  {isRunning ? 'SEDANG BERJALAN...' : 'MULAI SCRAPING'}
                </button>
              </div>

              {/* Total Dataset */}
              <div className={styles.datasetCard}>
                <div>
                  <p className={styles.datasetLabel}>TOTAL DATASET LOKAL</p>
                  <p className={styles.datasetValue}>{formatNum(totalDatasetLokal)}</p>
                </div>
                <span
                  className="material-symbols-outlined"
                  style={{ fontSize: 36, color: 'var(--color-primary-container)', fontVariationSettings: "'FILL' 1" }}
                >
                  layers
                </span>
              </div>
            </div>

            {/* ── RIGHT PANEL ── */}
            <div className={styles.rightPanel}>

              {/* Live status card */}
              <div className={`${styles.card} ${styles.statusCard}`}>
                <div className={styles.statusHeader}>
                  <div className={styles.statusInfo}>
                    <div className={styles.statusRunning}>
                      {isRunning && <span className={styles.greenPulse} />}
                      <span className={styles.statusTitle}>
                        {isRunning ? 'Scraping Berjalan' : (activeJob?.status === 'GAGAL' ? 'Scraping Gagal' : 'Menunggu / Selesai')}
                      </span>
                    </div>
                    <p className={styles.statusSub}>
                      {activeJob?.error_message || 'Mengambil data dari Google Play Store'}
                    </p>
                  </div>
                  <button
                    id="stop-scraping"
                    className={`${styles.stopBtn} ${!isRunning ? styles.stopDisabled : ''}`}
                    onClick={() => stopMutation.mutate(activeJobId)}
                    disabled={!isRunning}
                  >
                    <span className={styles.stopSquare} />
                    STOP
                  </button>
                </div>

                {/* Progress */}
                <div className={styles.progressSection}>
                  <div className={styles.progressMeta}>
                    <span className={styles.progressPct}>{progress}%</span>
                    <span className={styles.progressCount}>
                      {formatNum(scraped)} / {formatNum(totalTarget)} ulasan
                    </span>
                  </div>
                  <div className={styles.progressTrack}>
                    <div
                      className={styles.progressBar}
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>

              </div>

              {/* Riwayat Scraping */}
              <div className={styles.card}>
                <div className={styles.historyHeader}>
                  <div className={styles.historyTitle}>
                    <span className="material-symbols-outlined" style={{ fontSize: 16 }}>history</span>
                    RIWAYAT SCRAPING
                  </div>
                  <button className={styles.filterIconBtn} aria-label="Filter">
                    <span className="material-symbols-outlined" style={{ fontSize: 18 }}>filter_list</span>
                  </button>
                </div>

                <div className={styles.tableWrap}>
                  <table className={styles.table}>
                    <thead>
                      <tr>
                        <th>TANGGAL</th>
                        <th>JUMLAH<br/>ULASAN</th>
                        <th>FILTER</th>
                        <th>STATUS</th>
                        <th>AKSI</th>
                      </tr>
                    </thead>
                    <tbody>
                      {history.map((row) => (
                        <tr key={row.id}>
                          <td className={styles.dateCell} style={{ whiteSpace: 'pre-line' }}>{row.created_at?.split('T').join('\n')}</td>
                          <td className={styles.countCell}>{row.reviews_scraped} / {row.max_reviews}</td>
                          <td>{row.filter_bintang}</td>
                          <td><StatusBadge status={row.status} /></td>
                          <td>
                            <div className={styles.actionBtns}>
                              <button className={styles.actionBtnDanger} aria-label="Hapus" onClick={() => handleDelete(row.id)}>
                                <span className="material-symbols-outlined" style={{ fontSize: 17 }}>delete</span>
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
  )
}
