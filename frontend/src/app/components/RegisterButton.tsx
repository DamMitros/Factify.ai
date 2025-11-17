'use client'

import { useKeycloak } from '../../auth/KeycloakProviderWrapper'

export default function RegisterButton() {
  const { keycloak, authenticated, initialized } = useKeycloak()

  if (!initialized) {
    return <div>Ładowanie...</div>
  }

  if (authenticated) {
    return null
  }

  const register = () => keycloak?.register()

  return (
    <button onClick={register}>
      Zarejestruj się przez Keycloak
    </button>
  )
}