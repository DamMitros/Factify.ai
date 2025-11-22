import Bubbles from "./components/Bubbles";
import ButtonBubbles from "./components/ButtonBubbles";
import InteractiveBubble from "./components/InteractiveBubble";
import LoginButton from "./components/LoginButton";
import RegisterButton from "./components/RegisterButton";


export default function LandingPage() {
  return (
    <>
    <LoginButton />
    <RegisterButton />
    <div className="buttons" >

      <InteractiveBubble />
      <ButtonBubbles />

    </div>
    <div className="mainBackground">
     <Bubbles />
    </div>
    
      <h1 className="main-page-title">Welcome to Factify.ai</h1>
      <h2 className="main-page-subtitle">Begin your journey of authenticity with us!</h2>
    
    </>
  );
}