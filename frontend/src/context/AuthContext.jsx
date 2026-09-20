import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authService } from '../services/api'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('feeassist_user')
      return savedUser ? JSON.parse(savedUser) : null
    } catch {
      return null
    }
  })
  const [token, setToken] = useState(() => localStorage.getItem('feeassist_token'))
  const [loading, setLoading] = useState(true)

  // Validate or fetch fresh user profile on initial load
  const loadUser = useCallback(async () => {
    const savedToken = localStorage.getItem('feeassist_token')
    if (!savedToken) {
      setUser(null)
      setLoading(false)
      return
    }

    try {
      const res = await authService.getMe()
      setUser(res.data)
      localStorage.setItem('feeassist_user', JSON.stringify(res.data))
    } catch (err) {
      console.warn('Session expired or invalid token:', err)
      localStorage.removeItem('feeassist_token')
      localStorage.removeItem('feeassist_user')
      setUser(null)
      setToken(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadUser()
  }, [loadUser])

  const login = async (email, password) => {
    const res = await authService.login({ email, password })
    const { access_token } = res.data
    localStorage.setItem('feeassist_token', access_token)
    setToken(access_token)

    // Fetch user profile immediately
    const meRes = await authService.getMe()
    const userData = meRes.data
    localStorage.setItem('feeassist_user', JSON.stringify(userData))
    setUser(userData)
    return userData
  }

  const register = async (userData) => {
    const res = await authService.register(userData)
    return res.data
  }

  const logout = () => {
    localStorage.removeItem('feeassist_token')
    localStorage.removeItem('feeassist_user')
    setToken(null)
    setUser(null)
  }

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token && !!user,
    login,
    register,
    logout,
    refreshUser: loadUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
