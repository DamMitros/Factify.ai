'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import keycloak from './keycloak'
import { api } from '../lib/api'

type KeycloakContextType = {
  keycloak: typeof keycloak | null
  authenticated: boolean
  initialized: boolean
}

const KeycloakContext = createContext<KeycloakContextType>({
  keycloak: null,
  authenticated: false,
  initialized: false,
})

export function KeycloakProviderWrapper({ children }: { children: ReactNode }) {
  const [authenticated, setAuthenticated] = useState(false)
  const [initialized, setInitialized] = useState(false)

  useEffect(() => {
    keycloak
      .init({ onLoad: 'check-sso', pkceMethod: 'S256', checkLoginIframe: false })
      .then((auth) => {
        setAuthenticated(auth)
        setInitialized(true)
      })
      .catch((err) => {
        console.error('Keycloak init error:', err)
        setInitialized(true)
      })
  }, [])

  useEffect(() => {
    if (authenticated && keycloak?.token) {
      api.put('/user/register', {}, { requireAuth: true })
        .then(({ status }) => {
          if (status === 201) {
            console.log('Added user to database');
          } else if (status === 200) {
            console.log('User already synced with database');
          }
        })
        .catch((err) => console.error('Error syncing user', err));
    }
  }, [authenticated, keycloak?.token])

  if (!initialized) return <div>Loading auth...</div>

  return (
    <KeycloakContext.Provider value={{ keycloak, authenticated, initialized }}>
      {children}
    </KeycloakContext.Provider>
  )
}

export const useKeycloak = () => useContext(KeycloakContext)

export default KeycloakProviderWrapper