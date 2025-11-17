import React, { JSX } from "react";

export const metadata = {
  title: "AnalizePhotos",
  description: "Placeholder page for the AnalizePhotos route",
};

export default function Page(): JSX.Element {
  return (
    <main style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
      <section style={{ maxWidth: 800, width: "100%" }}>
        <h1 style={{ margin: 0, fontSize: 28, fontWeight: 600 }}>AnalizePhotos</h1>
        <p style={{ marginTop: 12, color: "#6b7280" }}>
        </p>
      </section>
    </main>
  );
}