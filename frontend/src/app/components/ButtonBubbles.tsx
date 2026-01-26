"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const bubbles = [
	{ id: 1, label: "Analyze text" },
	{ id: 2, label: "Analyze photos" },
	{ id: 3, label: "Community" },
];

// const randomShadow = () => {
//   const blur = 3 + Math.random() * 6;
//   const spread = 3 + Math.random() * 6;
//   return `0 0 ${blur}px ${spread}px #fff`;
// };

// const buildOverrides = () =>
//   bubbles.map((_, idx) => {
//     const shadowDirection = Math.random() > 0.5 ? "normal" : "reverse";
//     const shadowDelay = `${(Math.random() * 2).toFixed(2)}s`;
//     const morphDelay = `${(Math.random() * 3).toFixed(2)}s`;
//     const morphDuration = `${(5 + Math.random() * 4).toFixed(2)}s`;

//     return {
//       animationDirection: `${shadowDirection}, normal`,
//       animationDelay: `${shadowDelay}, ${morphDelay}`,
//       animationDuration: `5s, ${morphDuration}`,
//       boxShadow: idx < 3 ? randomShadow() : undefined,
//     };
//   });

export default function ButtonBubbles() {
	const router = useRouter();
	const routes = ["/AnalizeText", "/AnalizePhotos", "/Community"];
	const [activeButtons, setActiveButtons] = useState<Set<number>>(new Set());

	const handleClick = (index: number) => {
		const route = routes[index];
		if (route) router.push(route);
	};

	const handleMouseEnter = (index: number) => {
		setActiveButtons(prev => new Set(prev).add(index));
	};

	useEffect(() => {
		if (activeButtons.size > 0) {
			const timers = Array.from(activeButtons).map(buttonIndex =>
				setTimeout(() => {
					setActiveButtons(prev => {
						const newSet = new Set(prev);
						newSet.delete(buttonIndex);
						return newSet;
					});
				}, 600)
			);
			return () => timers.forEach(timer => clearTimeout(timer));
		}
	}, [activeButtons]);

	return (
		<>
			<div className="buttonBubbles ">
				{bubbles.map((bubble, index) => (
					<button
						key={bubble.id}
						className={`buttonBubble ${activeButtons.has(index) ? "animate-shine" : ""}`}
						onClick={() => handleClick(index)}
						onMouseEnter={() => handleMouseEnter(index)}
						type="button"
					>
						<div className="glass-filter" />
						<div className="glass-overlay" />
						<div className="glass-specular" />
						<span className="buttonBubble-content">{bubble.label}</span>
						
					</button>
				))}
			</div>
		</>
	);
}
