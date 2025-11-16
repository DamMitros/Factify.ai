'use client'

import { useKeycloak } from '../../auth/KeycloakProviderWrapper'
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { api } from '../../lib/api';

export default function LoginButton() {
  const router = useRouter();
  const { keycloak, authenticated, initialized } = useKeycloak()

  useEffect(() => {
    if (authenticated && keycloak?.token) {
      api.put('/user/register', {}, { requireAuth: true })
      .then(({ status, data }) => {
        if (status === 201) {
          console.log('Added user to database');
        } else if (status === 200) {
          console.log('User already synced with database');
        }
      })
      .catch((err) => console.error('Error syncing user', err));
    }
  }, [authenticated])//usunelam keycloak.token - itak sie wysylaja 2 requesty ale chyba drugi jest opozniony bo sie nie dubluja userzy w bazie, tylko ze nw czy to nie bedzie pwodowalo bugow

  if (!initialized) {
    return <div>Ładowanie...</div>
  }

  const login = () => keycloak?.login()
  const logout = () => keycloak?.logout({ redirectUri: "http://localhost:3000" }) //wymuszenie na glowna nie dziala ale jak to bedzie na navigation to nie powinno byc problemu
  const goToProfile = () => router.push('/profile');

  return (
    <div>
      {authenticated ? (
        <div>
          <p>
            Hejkaaa {keycloak?.tokenParsed?.preferred_username || 'User'}!
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