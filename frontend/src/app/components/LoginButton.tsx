'use client'

import { useKeycloak } from '../../auth/KeycloakProviderWrapper'
import { useEffect } from 'react';
import { api } from '../../lib/api';

export default function LoginButton() {
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
  }, [authenticated])

  if (!initialized || authenticated) {
    return null
  }

  const login = () => keycloak?.login()

  return (
    <button onClick={login}>Zaloguj</button>
  )
}
