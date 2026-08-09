import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hendrickson — AI-Driven QA Agent Harness",
  description: "Autonomous multi-agent QA and Testing Harness for modern software engineering teams.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background antialiased">
        {children}
      </body>
    </html>
  );
}
