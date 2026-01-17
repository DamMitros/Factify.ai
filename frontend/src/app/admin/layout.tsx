'use client';

import { useKeycloak } from "../../auth/KeycloakProviderWrapper";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { keycloak, initialized } = useKeycloak();
  const router = useRouter();

  useEffect(() => {
    if (initialized) {
      if (!keycloak.authenticated) {
        router.push("/");
      } else if (!keycloak.hasRealmRole("admin")) {
        router.push("/"); 
      }
    }
  }, [keycloak, initialized, router]);

  if (!initialized || !keycloak.authenticated || !keycloak.hasRealmRole("admin")) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      {children}
    </div>
  );
}