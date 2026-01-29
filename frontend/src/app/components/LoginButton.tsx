'use client'

import { useKeycloak } from '../../auth/KeycloakProviderWrapper'

export default function LoginButton() {
  const { keycloak, authenticated, initialized } = useKeycloak()

  if (!initialized || authenticated) {
    return null
  }

  const login = () => keycloak?.login()

  return (
    <button onClick={login}>Log in</button>
  )
}
