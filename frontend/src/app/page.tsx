import Bubbles from "./components/Bubbles";
import ButtonBubbles from "./components/ButtonBubbles";
import InteractiveBubble from "./components/InteractiveBubble";
import LoginButton from "./components/LoginButton";
import RegisterButton from "./components/RegisterButton";

export default function LandingPage() {
  return (
    <div className="mainBackground">
     <LoginButton />
     <RegisterButton />
     <Bubbles />
     <InteractiveBubble />
     <h1>Welcome to Factify.ai</h1>
     <ButtonBubbles />
    </div>
  );
}