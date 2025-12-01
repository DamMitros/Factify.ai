'use client';

import React, { useEffect, useRef } from 'react';

export default function InteractiveBubble() {
  const bubbleRef = useRef<HTMLDivElement | null>(null);

  const curX = useRef(0);
  const curY = useRef(0);
  const tgX = useRef(0);
  const tgY = useRef(0);
  const rafId = useRef<number | null>(null);

  useEffect(() => {
    const el = bubbleRef.current;
    if (!el) return;

    curX.current = window.innerWidth / 2;
    curY.current = window.innerHeight / 2;
    tgX.current = curX.current;
    tgY.current = curY.current;

    function animate() {
      curX.current += (tgX.current - curX.current) ; 
      curY.current += (tgY.current - curY.current) ;

      if (el) {
        el.style.left = `${Math.round(curX.current)}px`;
        el.style.top = `${Math.round(curY.current)}px`;
      }

      rafId.current = requestAnimationFrame(animate);
    }

    function onMouseMove(e: MouseEvent) {
      tgX.current = e.clientX;
      tgY.current = e.clientY;
    }

    function onTouchMove(e: TouchEvent) {
      if (e.touches.length > 0) {
        tgX.current = e.touches[0].clientX;
        tgY.current = e.touches[0].clientY;
      }
    }

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('touchmove', onTouchMove, { passive: true });

    rafId.current = requestAnimationFrame(animate);

    return () => {
      if (rafId.current !== null) cancelAnimationFrame(rafId.current);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('touchmove', onTouchMove);
    };
  }, []);

  return (
    <div className="interactiveBubbleContainer">
      <div ref={bubbleRef} className="interactiveBubble" />
    </div>
  );
}
