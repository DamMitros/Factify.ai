'use client'

import { useKeycloak } from '../../auth/KeycloakProviderWrapper'

export default function LoginButton() {
  const { keycloak, authenticated, initialized } = useKeycloak()

  if (!initialized) {
    return <div>Ładowanie...</div>
  }

  const login = () => keycloak?.login()
  const logout = () => keycloak?.logout()

  return (
    <div>
      {authenticated ? (
        <div>
          <p>
            {keycloak?.tokenParsed?.preferred_username || 'User'}
          </p>
          <button onClick={logout}> Wyloguj</button>
        </div>
      ) : (
        <button onClick={login}>Zaloguj przez Keycloak </button>
      )}
    </div>
  )
}