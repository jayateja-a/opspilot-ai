import type { SVGProps } from "react";
type Props = SVGProps<SVGSVGElement> & { size?: number };
export const Activity = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M3 12h4l3-8 4 16 3-8h4" />
  </svg>
);
export const ArrowRight = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M5 12h14 M12 5l7 7-7 7" />
  </svg>
);
export const BookOpen = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M12 5c-4-3-8-2-10-1v15c4-2 7-2 10 0 3-2 6-2 10 0V4c-2-1-6-2-10 1v14" />
  </svg>
);
export const Check = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M5 12l4 4L19 6" />
  </svg>
);
export const ChevronRight = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M9 5l7 7-7 7" />
  </svg>
);
export const CircleDot = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M21 12a9 9 0 1 1-18 0 9 9 0 1 1 18 0 M14 12a2 2 0 1 1-4 0 2 2 0 1 1 4 0" />
  </svg>
);
export const ClipboardCheck = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M8 4H5v17h14V4h-3 M8 2h8v5H8V2 M8 13l3 3 5-5" />
  </svg>
);
export const Cpu = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M7 7h10v10H7V7 M3 8h4 M3 16h4 M17 8h4 M17 16h4 M8 3v4 M16 3v4 M8 17v4 M16 17v4" />
  </svg>
);
export const LoaderCircle = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M21 12a9 9 0 1 1-9-9" />
  </svg>
);
export const Play = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M7 4l14 8-14 8V4" />
  </svg>
);
export const Plus = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M12 5v14 M5 12h14" />
  </svg>
);
export const Radar = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M20 12a8 8 0 1 1-8-8 M16 12a4 4 0 1 1-4-4 M12 12l8-8" />
  </svg>
);
export const ShieldCheck = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M12 2l9 4v6c0 5-9 10-9 10S3 17 3 12V6l9-4 M8 12l3 3 5-6" />
  </svg>
);
export const Terminal = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M4 7l5 5-5 5 M12 17h8" />
  </svg>
);
export const X = ({ size = 20, ...props }: Props) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M6 6l12 12 M6 18L18 6" />
  </svg>
);
