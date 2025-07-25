"use client";

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import type { User } from '@supabase/supabase-js'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get initial session
    const getSession = async () => {
      console.log('Getting initial session...')
      const { data: { session } } = await supabase.auth.getSession()
      console.log('Initial session:', session?.user?.email || 'No session')
      setUser(session?.user ?? null)
      setLoading(false)
    }

    getSession()

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.email)
        setUser(session?.user ?? null)
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  const signUp = async (email: string, password: string) => {
    setLoading(true)
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    })
    if (!error && data.user) {
      console.log('Sign up successful, setting user:', data.user.email)
    }
    setLoading(false)
    return { data, error }
  }

  const signIn = async (email: string, password: string) => {
    setLoading(true)
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (!error && data.user) {
      console.log('Sign in successful, setting user:', data.user.email)
    } else if (error) {
      console.log('Sign in failed:', error.message)
    }
    setLoading(false)
    return { data, error }
  }

  const signOut = async () => {
    setLoading(true)
    const { error } = await supabase.auth.signOut()
    if (!error) {
      console.log('Sign out successful')
      setUser(null)
    }
    setLoading(false)
    return { error }
  }

  return {
    user,
    loading,
    signUp,
    signIn,
    signOut,
  }
}