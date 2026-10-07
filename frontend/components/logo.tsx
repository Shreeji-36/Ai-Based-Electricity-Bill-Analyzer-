export default function Logo({ size = 40 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none" aria-label="Logo">
      <rect width="48" height="48" rx="12" fill="#14b8a6" />
      <path d="M27 8 14 27h9l-2 13 13-19h-9l2-13Z" fill="#042f2e" />
    </svg>
  );
}