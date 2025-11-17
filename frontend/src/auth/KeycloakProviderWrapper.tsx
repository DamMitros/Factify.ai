'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import keycloak from './keycloak'

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

  if (!initialized) return <div>Loading auth...</div>

  return (
    <KeycloakContext.Provider value={{ keycloak, authenticated, initialized }}>
      {children}
    </KeycloakContext.Provider>
  )
}

export const useKeycloak = () => useContext(KeycloakContext)

export default KeycloakProviderWrapper