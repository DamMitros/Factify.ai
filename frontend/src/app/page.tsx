import Bubbles from "./components/Bubbles";
import ButtonBubbles from "./components/ButtonBubbles";
import InteractiveBubble from "./components/InteractiveBubble";
import LoginButton from "./components/LoginButton";

export default function LandingPage() {
  return (
    <div className="mainBackground">
     <LoginButton />
     <Bubbles />
     <InteractiveBubble />
     <h1>Welcome to defacto.ai</h1>
     <ButtonBubbles />
    </div>
  );
}
