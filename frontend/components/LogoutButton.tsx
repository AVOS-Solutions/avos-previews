"use client";

import { useRouter } from "next/navigation";
import { Button } from "./ui";

export function LogoutButton() {
  const router = useRouter();
  return (
    <Button
      variant="secondary"
      className="px-3 py-1.5 text-[0.8rem]"
      onClick={async () => {
        await fetch("/api/auth/logout", { method: "POST" });
        router.push("/login");
        router.refresh();
      }}
    >
      Abmelden
    </Button>
  );
}
