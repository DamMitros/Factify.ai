import Bubbles from "./components/Bubbles";
import InteractiveBubble from "./components/InteractiveBubble";

export default function LandingPage() {
  return (
    <div className="mainBackground">
     <Bubbles />
     <InteractiveBubble />
     <h1>Welcome to Factify.ai</h1>
    </div>
  );
}
