export function BrandMark() {
  return (
    /* AVOS product mark — briefcase tile matching avos-erp's Nav (zero ids so copies can't collide). */
    <svg width="26" height="26" viewBox="0 0 24 24" aria-hidden="true" className="shrink-0">
      <rect x="3.5" y="3.5" width="17" height="17" rx="2.5" fill="#161225" />
      <path
        d="M4.23 4.23A2.5 2.5 0 0 1 6 3.5H18A2.5 2.5 0 0 1 20.5 6V18A2.5 2.5 0 0 1 19.77 19.77Z"
        fill="#e0a437"
        opacity="0.22"
      />
      <g fill="none" stroke="#e0a437" strokeWidth="1.25" strokeLinecap="round" strokeLinejoin="round">
        <rect x="7.1" y="10.1" width="9.8" height="6.2" rx="1.2" />
        <path d="M10.2 10.1v-0.8a1.4 1.4 0 0 1 1.4-1.4h0.8a1.4 1.4 0 0 1 1.4 1.4v0.8" />
        <path d="M11.2 12.9h1.6" stroke="#f4c04d" strokeWidth="0.75" />
      </g>
    </svg>
  );
}

export function BrandWord() {
  return (
    <span className="mono text-[0.95rem] font-medium tracking-[0.06em]">
      AVOS <span className="text-slate font-normal">PREVIEWS</span>
    </span>
  );
}
