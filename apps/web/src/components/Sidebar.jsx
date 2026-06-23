import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import styles from './Sidebar.module.css'

const NAV_ITEMS = [
  { id: 'dashboard',      icon: 'grid_view',       label: 'Dashboard',       path: '/dashboard' },
  { id: 'scraping',       icon: 'cloud_download',  label: 'Scraping Data',   path: '/scraping' },
  { id: 'preprocessing',  icon: 'tune',             label: 'Preprocessing',   path: '/preprocessing' },
  { id: 'training',       icon: 'model_training',  label: 'Training Model',  path: '/training' },
  { id: 'analisis',       icon: 'leaderboard',     label: 'Hasil Analisis',  path: '/analisis' },
  { id: 'prediksi',       icon: 'wifi_tethering',  label: 'Prediksi Teks',   path: '/prediksi' },
]

export default function Sidebar() {
  const [refreshing, setRefreshing] = useState(false)

  const handleRefresh = () => {
    setRefreshing(true)
    setTimeout(() => setRefreshing(false), 1800)
  }

  return (
    <aside className={styles.sidebar}>
      {/* Brand */}
      <div className={styles.brand}>
        <span className={`material-symbols-outlined ${styles.brandIcon}`}
          style={{ fontVariationSettings: "'FILL' 1" }}>flutter_dash</span>
        <div>
          <p className={styles.brandName}>LingoMetrics</p>
          <p className={styles.version}>V1.0.4-PRO</p>
        </div>
      </div>

      {/* Primary nav */}
      <nav className={styles.nav}>
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.id}
            to={item.path}
            className={({ isActive }) =>
              `${styles.navItem} ${isActive ? styles.navItemActive : ''}`
            }
          >
            <span className="material-symbols-outlined" style={{ fontSize: 20 }}>
              {item.icon}
            </span>
            <span className={styles.navLabel}>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom section */}
      <div className={styles.bottom}>
        <NavLink to="/settings" className={styles.settingsLink}>
          <span className="material-symbols-outlined" style={{ fontSize: 20 }}>settings</span>
          <span>Pengaturan</span>
        </NavLink>

        <button
          id="sidebar-refresh"
          className={`${styles.refreshBtn} ${refreshing ? styles.refreshing : ''}`}
          onClick={handleRefresh}
          disabled={refreshing}
        >
          <span
            className="material-symbols-outlined"
            style={{ fontSize: 18, display: 'inline-flex', transition: 'transform 0.3s' }}
          >
            refresh
          </span>
          {refreshing ? 'Memperbarui...' : 'Refresh Metrics'}
        </button>
      </div>
    </aside>
  )
}
