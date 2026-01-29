import React, { JSX } from "react";
import TextAnalyzer from "../components/TextAnalyzer";
import Bubbles from "../components/Bubbles";
import { BackButton } from "../components/BackButton";

export const metadata = {
    title: "Analize Text",
};

export default function Page(): JSX.Element {
    return (
        <main className="analize-text-page">
            <BackButton />
            <div className=" analize-text-background" aria-hidden="true">
                <Bubbles />
            </div>
            <TextAnalyzer />
        </main>
    );
}
