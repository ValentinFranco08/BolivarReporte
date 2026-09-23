import type { Metadata, Viewport } from "next";
import { Archivo, Chivo_Mono } from "next/font/google";
import "./globals.css";

import { Navbar } from "@/components/layout/Navbar";
import { MobileBottomNav } from "@/components/layout/MobileBottomNav";

const archivo = Archivo({
  subsets: ["latin"],
  variable: "--font-archivo",
  weight: ["400", "500", "600", "700", "800"],
});

const chivoMono = Chivo_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: {
    default: "Bolívar Animal · Red de Búsqueda y Recuperación",
    template: "%s · Bolívar Animal",
  },
  description:
    "Red comunitaria y municipal de búsqueda, recuperación y protección animal ante extravíos y cebos tóxicos en San Carlos de Bolívar.",
  applicationName: "Bolívar Animal",
};

export const viewport: Viewport = {
  themeColor: "#faf8f5",
  colorScheme: "light",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="es"
    className={`${archivo.variable} ${chivoMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body
        className="min-h-full flex flex-col bg-lino font-sans text-corteza pb-20 md:pb-0"
        suppressHydrationWarning
      >
        <Navbar />
        <div className="flex-1 flex flex-col">
          {children}
        </div>
        <MobileBottomNav />
      </body>
    </html>
  );
}
