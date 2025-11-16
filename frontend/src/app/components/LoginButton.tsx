'use client'

import { useKeycloak } from '../../auth/KeycloakProviderWrapper'
import { useRouter } from 'next/navigation';


export default function LoginButton() {
  const router = useRouter();
  const { keycloak, authenticated, initialized } = useKeycloak()

  if (!initialized) {
    return <div>Ładowanie...</div>
  }

  const login = () => keycloak?.login()
  const logout = () => keycloak?.logout()
  const goToProfile = () => router.push('/profile');

  return (
    <div>
      {authenticated ? (
        <div>
          <p>
            {keycloak?.tokenParsed?.preferred_username || 'User'}
          </p>
          <button onClick={logout}> Wyloguj</button>
          <button onClick={goToProfile}> Twój profil</button>
        </div>
      ) : (
        <button onClick={login}>Zaloguj przez Keycloak </button>
      )}
    </div>
  )
}