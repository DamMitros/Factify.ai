'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useKeycloak } from '../../auth/KeycloakProviderWrapper';
import { api } from '../../lib/api'
import AnalysisHistory from '../components/AnalysisHistory';

interface UserProfile {
  username: string;
  name: string;
  email: string;
  roles: string[];
}

export default function ProfilePage() {
  const router = useRouter();
  const { keycloak, authenticated, initialized } = useKeycloak();
  
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!initialized) return;

    if (!authenticated) {
      keycloak?.login({ redirectUri: window.location.href });
      return;
    }

    api.get<UserProfile>('/user/profile')
      .then(({ data }) => setProfile(data)) 
      .catch((err) => {
        if (err.message === 'NOT_AUTHENTICATED' || err.message === 'SESSION_EXPIRED') {
          keycloak?.login({ redirectUri: window.location.href });
        } else {
          setError(err.message);
        }
      })
      .finally(() => setLoading(false));
  }, [initialized, authenticated]);

  if (!initialized || loading) {
    return (
      <div>
        <p>Ładowanie profilu...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h1>Błąd</h1>
        <p>{error}</p>
      </div>
    );
  }

  if (!profile) return null;

  return (
    <div>
      
      <h1>Hello {profile.username}</h1>
      <button className="back-button" onClick={() => router.push('/')}> Retrun </button>

      {/* <h1>Profil użytkownika</h1>
      <div>
        <p><strong>Nazwa użytkownika:</strong> {profile.username}</p>
        <p><strong>Imię:</strong> {profile.name}</p>
        <p><strong>Email:</strong> {profile.email}</p>
        <p><strong>Role:</strong> {profile.roles.join(', ')}</p>
      </div> */}
      
      <AnalysisHistory/>

    
    </div>
  );
}
