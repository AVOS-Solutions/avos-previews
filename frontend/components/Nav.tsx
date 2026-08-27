import Link from "next/link";
import { BrandMark, BrandWord } from "./BrandMark";
import { LogoutButton } from "./LogoutButton";

export function Nav({ userEmail }: { userEmail: string }) {
  return (
    <header className="sticky top-0 z-50 border-b border-line bg-[rgba(236,238,231,0.88)] backdrop-blur-[10px]">
      <div className="mx-auto flex h-[76px] w-full max-w-[1180px] items-center justify-between px-4 sm:px-8">
        <Link href="/dashboard" className="flex items-center gap-2.5 text-ink no-underline">
          <BrandMark />
          <BrandWord />
        </Link>
        <div className="flex items-center gap-4">
          <span className="mono hidden text-[0.8rem] text-slate sm:inline">{userEmail}</span>
          <LogoutButton />
        </div>
      </div>
    </header>
  );
}
