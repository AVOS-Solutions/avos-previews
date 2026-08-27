import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/session";
import { Nav } from "@/components/Nav";

export default async function AppLayout({ children }: LayoutProps<"/">) {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  return (
    <>
      <Nav userEmail={user.email} />
      <main className="mx-auto w-full max-w-[1180px] flex-1 px-4 py-6 sm:px-8 sm:py-10">{children}</main>
      <footer className="border-t border-line py-4 text-[0.8rem] text-slate">
        <div className="mx-auto w-full max-w-[1180px] px-4 sm:px-8">
          AVOS Previews · intern &amp; vertraulich · Share-Links sind einzeln steuerbar (Passwort, View-Limit, Ablauf)
        </div>
      </footer>
    </>
  );
}
