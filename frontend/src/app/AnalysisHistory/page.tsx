import React, { JSX } from "react";
import TextAnalyzer from "../components/TextAnalyzer";
import Bubbles from "../components/Bubbles";
import AnalysisHistory from "../components/AnalysisHistory";

export const metadata = {
    title: "Analize Text",
};

export default function Page(): JSX.Element {
    return (
        <>
            <div className="opacity-100 blur-xl  fixed">
                <Bubbles />
                
            </div>
            <AnalysisHistory />
        </>
            
       
    );
}
