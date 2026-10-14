// Ícones de traço simples (herdam a cor do texto) no lugar de emoji.
const base = {
  width: 20, height: 20, viewBox: "0 0 24 24", fill: "none",
  stroke: "currentColor", strokeWidth: 2, strokeLinecap: "round", strokeLinejoin: "round",
  "aria-hidden": true,
};

export function RunIcon(props) {
  return (
    <svg {...base} {...props}>
      <circle cx="14" cy="4.5" r="1.8" />
      <path d="M8 21l3-6 3 2v5" />
      <path d="M6 12l3-4h5l3 4 3 1" />
      <path d="M11 15l1-7" />
    </svg>
  );
}

export function StrengthIcon(props) {
  return (
    <svg {...base} {...props}>
      <path d="M6.5 6.5v11M17.5 6.5v11M3.5 9v6M20.5 9v6M6.5 12h11" />
    </svg>
  );
}

export function RideIcon(props) {
  return (
    <svg {...base} {...props}>
      <circle cx="5.5" cy="16.5" r="3.5" />
      <circle cx="18.5" cy="16.5" r="3.5" />
      <path d="M5.5 16.5l4-7h6l3 7M9.5 9.5l3 7h-7M14 6h3" />
    </svg>
  );
}

export function ShieldIcon(props) {
  return (
    <svg {...base} {...props}>
      <path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6l7-3z" />
    </svg>
  );
}

export function RefreshIcon(props) {
  return (
    <svg {...base} {...props}>
      <path d="M20 11a8 8 0 0 0-14.5-4.5L4 8M4 4v4h4" />
      <path d="M4 13a8 8 0 0 0 14.5 4.5L20 16M20 20v-4h-4" />
    </svg>
  );
}
