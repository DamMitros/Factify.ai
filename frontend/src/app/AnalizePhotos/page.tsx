import React, { JSX } from "react";
import Bubbles from "../components/Bubbles";
import PhotoAnalyzer from "../components/PhotoAnalyzer";

export const metadata = {
  title: "Analize Photos",
  description: "Analyze photos to detect AI-generated images",
};

export default function Page(): JSX.Element {
  return (
    <main className="analize-text-page">
      <div className="analize-text-background" aria-hidden="true">
        <Bubbles />
      </div>
      <PhotoAnalyzer />
    </main>
  );
}
