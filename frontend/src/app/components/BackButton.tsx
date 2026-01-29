'use client';

import { useRouter } from 'next/navigation';

interface BackButtonProps {
  className?: string;
}

export function BackButton({ className = '' }: BackButtonProps) {
  const router = useRouter();

  return (
    <button
      onClick={() => router.push('/')}
      className={`fixed left-4 top-6 z-[9999] pointer-events-auto flex items-center gap-2 text-gray-400 hover:text-white transition-colors group px-4 py-2 rounded-lg hover:bg-white/5 ${className}`}
    >
      <svg
        className="w-5 h-5 group-hover:-translate-x-1 transition-transform"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M15 19l-7-7 7-7"
        />
      </svg>
      <span className="hidden sm:inline">Back</span>
    </button>
  );
}
