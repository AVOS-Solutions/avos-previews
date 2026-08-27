import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, SelectHTMLAttributes } from "react";

export function cx(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(" ");
}

export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <div className={cx("rounded-lg border border-line bg-white/60 p-4 shadow-sm sm:p-6", className)}>
      {children}
    </div>
  );
}

type ButtonVariant = "primary" | "secondary" | "danger";

const buttonBase =
  "inline-flex items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50";
const buttonVariants: Record<ButtonVariant, string> = {
  primary: "bg-ink text-paper hover:bg-signal-dim",
  secondary: "bg-transparent text-ink border border-line hover:bg-paper-dim",
  danger: "bg-brass text-paper hover:opacity-90",
};

export function Button({
  variant = "primary",
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: ButtonVariant }) {
  return <button className={cx(buttonBase, buttonVariants[variant], className)} {...props} />;
}

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cx(
        "w-full rounded-md border border-line bg-white px-3 py-2 text-sm text-ink placeholder:text-slate focus:border-signal focus:outline-none",
        className,
      )}
      {...props}
    />
  );
}

export function Select({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={cx(
        "w-full rounded-md border border-line bg-white px-3 py-2 text-sm text-ink focus:border-signal focus:outline-none",
        className,
      )}
      {...props}
    />
  );
}

export function Label({ htmlFor, children }: { htmlFor?: string; children: ReactNode }) {
  return (
    <label htmlFor={htmlFor} className="eyebrow mb-1.5 block">
      {children}
    </label>
  );
}

export function PageHeader({
  eyebrow,
  title,
  action,
}: {
  eyebrow: string;
  title: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1 className="text-2xl">{title}</h1>
      </div>
      {action}
    </div>
  );
}

const badgeStyles: Record<string, string> = {
  aktiv: "bg-signal/20 text-signal-dim",
  abgelaufen: "bg-slate/15 text-slate",
  aufgebraucht: "bg-brass/15 text-brass",
  widerrufen: "bg-brass/15 text-brass",
  offen: "bg-slate/15 text-slate",
  passwort: "bg-ink/10 text-ink",
};

export function Badge({ kind, children }: { kind: string; children: ReactNode }) {
  return (
    <span
      className={cx(
        "mono inline-flex items-center whitespace-nowrap rounded-full px-2.5 py-0.5 text-[0.72rem] tracking-[0.04em]",
        badgeStyles[kind] ?? "bg-slate/15 text-slate",
      )}
    >
      {children}
    </span>
  );
}
