import styles from './LoginPage.module.css'
import { useState } from 'react'
import { api } from '../lib/api'
import { useNavigate } from 'react-router-dom'

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setErrorMsg('')
    try {
        const res = await api.post('/auth/login', { email: username, password })
        localStorage.setItem('token', res.data.token)
        localStorage.setItem('user', JSON.stringify(res.data.user))
        navigate('/dashboard')
    } catch (err) {
        setErrorMsg(err.message || 'Login gagal. Periksa kembali email dan password.')
    } finally {
        setIsLoading(false)
    }
  }

  return (
    <main className={styles.root}>
      {/* Ambient orbs */}
      <div className={styles.orb1} aria-hidden="true" />
      <div className={styles.orb2} aria-hidden="true" />

      <div className={styles.wrapper}>
        {/* Glow halo behind card */}
        <div className={styles.glow} aria-hidden="true" />

        {/* ── Card ── */}
        <article className={styles.card}>

          {/* Header */}
          <header className={styles.header}>
            <div className={styles.logoRing}>
              <span
                className="material-symbols-outlined"
                style={{ fontVariationSettings: "'FILL' 1", fontSize: 36, color: 'var(--color-primary-container)' }}
              >
                flutter_dash
              </span>
            </div>
            <h1 className={`${styles.appTitle} text-headline-lg`}>DuoSentimen</h1>
            <p className={`${styles.appSub} text-body-md`}>Analisis Sentimen Duolingo</p>
          </header>

          {/* Form */}
          <form className={styles.form} onSubmit={handleSubmit} noValidate>
            
            {errorMsg && (
                <div style={{ color: 'var(--color-error)', backgroundColor: 'var(--color-error-container)', padding: '12px', borderRadius: '8px', fontSize: '14px', marginBottom: '16px' }}>
                    {errorMsg}
                </div>
            )}

            {/* Username field */}
            <div className={styles.fieldGroup}>
              <span
                className={`material-symbols-outlined ${styles.fieldIcon}`}
                aria-hidden="true"
              >
                person
              </span>
              <input
                id="login-username"
                className={`${styles.input} text-body-md`}
                type="text"
                placeholder="Username / Email"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            {/* Password field */}
            <div className={styles.fieldGroup}>
              <span
                className={`material-symbols-outlined ${styles.fieldIcon}`}
                aria-hidden="true"
              >
                lock
              </span>
              <input
                id="login-password"
                className={`${styles.input} text-body-md`}
                type={showPassword ? 'text' : 'password'}
                placeholder="Password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className={styles.eyeBtn}
                aria-label={showPassword ? 'Sembunyikan password' : 'Tampilkan password'}
                onClick={() => setShowPassword((v) => !v)}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
                  {showPassword ? 'visibility_off' : 'visibility'}
                </span>
              </button>
            </div>

            {/* Submit */}
            <button
              id="login-submit"
              className={`${styles.submitBtn} text-label-bold`}
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className={styles.spinner} />
              ) : (
                <>
                  Masuk ke Dashboard
                  <span className="material-symbols-outlined" style={{ fontSize: 18, fontWeight: 700 }}>
                    arrow_forward
                  </span>
                </>
              )}
            </button>
          </form>

          {/* Footer link */}
          <footer className={styles.cardFooter}>
            <a id="forgot-password" href="#" className={`${styles.forgotLink} text-label-sm`}>
              Lupa Password?
            </a>
          </footer>
        </article>

        {/* Version badge */}
        <p className={styles.version}>v1.0.0 · DuoSentimen</p>
      </div>
    </main>
  )
}
