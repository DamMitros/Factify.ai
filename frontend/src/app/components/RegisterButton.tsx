'use client'

import { useKeycloak } from '../../auth/KeycloakProviderWrapper'

export default function RegisterButton() {
  const { keycloak, authenticated, initialized } = useKeycloak()

  if (!initialized || authenticated) {
    return null
  }

  const register = () => keycloak?.register()

  return (
    <button onClick={register}>Register</button>
  )
}
