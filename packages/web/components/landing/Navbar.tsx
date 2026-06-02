import Link from "next/link";
import { auth } from "@clerk/nextjs/server";
import { NavbarClient } from "./NavbarClient";

export async function Navbar() {
  const { userId } = await auth();
  return <NavbarClient isSignedIn={!!userId} />;
}
