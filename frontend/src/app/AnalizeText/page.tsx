import React, { JSX } from "react";
import TextAnalyzer from "../components/TextAnalyzer";
import Bubbles from "../components/Bubbles";

export const metadata = {
    title: "Analize Text",
};

export default function Page(): JSX.Element {
    return (
        <main className="analize-text-page">
            <div className="mainBackground analize-text-background" aria-hidden="true">
                <Bubbles />
            </div>
            <TextAnalyzer />
        </main>
    );
}