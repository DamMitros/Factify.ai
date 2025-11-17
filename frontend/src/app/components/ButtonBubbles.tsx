"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const bubbles = [
  { id: 1, label: "Analyze text" },
  { id: 2, label: "Analyze photos" },
  { id: 3, label: "" },
];

const randomShadow = () => {
  const blur = 3 + Math.random() * 6;
  const spread = 3 + Math.random() * 6;
  return `0 0 ${blur}px ${spread}px #fff`;
};

const buildOverrides = () =>
  bubbles.map((_, idx) => {
    const shadowDirection = Math.random() > 0.5 ? "normal" : "reverse";
    const shadowDelay = `${(Math.random() * 2).toFixed(2)}s`;
    const morphDelay = `${(Math.random() * 3).toFixed(2)}s`;
    const morphDuration = `${(5 + Math.random() * 4).toFixed(2)}s`;

    return {
      animationDirection: `${shadowDirection}, normal`,
      animationDelay: `${shadowDelay}, ${morphDelay}`,
      animationDuration: `5s, ${morphDuration}`,
      boxShadow: idx < 3 ? randomShadow() : undefined,
    };
  });

export default function ButtonBubbles() {
  const router = useRouter();
  const [animationOverrides, setAnimationOverrides] = useState(() =>
    bubbles.map(() => ({
      animationDirection: "normal, normal",
      animationDelay: "0s, 0s",
      animationDuration: "5s, 6s",
    }))
  );

  useEffect(() => {
    setAnimationOverrides(buildOverrides());
  }, []);

  const routes = ["/AnalizeText", "/AnalizePhotos", null];

  const handleClick = (index: number) => {
    const route = routes[index];
    if (route) router.push(route);
  };

  return (
    <>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        style={{ position: "fixed", width: 0, height: 0 }}
      >
        <defs>
          <filter id="goo">
            <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
            <feColorMatrix
              in="blur"
              mode="matrix"
              values="1 0 0 0 0  0 1 0 0 0  0 0 2 0 0  0 0 0 18 -10"
              result="goo"
            />
            <feBlend in="SourceGraphic" in2="goo" />
          </filter>
        </defs>
      </svg>
      <div className="buttonBubbles">
        {bubbles.map((bubble, index) => (
          <button
            key={bubble.id}
            className={`buttonBubble bubbleButton buttonBubble${index + 1}`}
            style={animationOverrides[index]}
            onClick={() => handleClick(index)}
            type="button"
          >
            {bubble.label}
          </button>
        ))}
      </div>
    </>
  );
}