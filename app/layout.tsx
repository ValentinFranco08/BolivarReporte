import type { Metadata, Viewport } from "next";
import { Archivo, Chivo_Mono } from "next/font/google";
import "./globals.css";

const archivo = Archivo({
  subsets: ["latin"],
  variable: "--font-archivo",
  axes: ["wdth"],
});

const chivoMono = Chivo_Mono({
  subsets: ["latin"],
  variable: "--font-chivo-mono",
});

export const metadata: Metadata = {
  title: {
    default: "Reporte Bolívar",
    template: "%s · Reporte Bolívar",
  },
  description:
    "Sacá una foto de lo que encontraste en la calle. Nosotros lo clasificamos y el municipio lo sigue. San Carlos de Bolívar, Buenos Aires.",
  applicationName: "Reporte Bolívar",
};

export const viewport: Viewport = {
  themeColor: "#f4f1e8",
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
        className="min-h-full flex flex-col bg-papel font-sans text-grafito-900"
        suppressHydrationWarning
      >
        {/*
          impeccable:direction 63657df4
          THESIS: Bolívar ya está dibujada como una grilla de parcelas numeradas; cada
          reporte es una parcela con número en una hoja de mensura. Rechaza el portal
          municipal celeste con hero y tres tarjetas, y rechaza el dashboard oscuro de IA.
          OWN-WORLD: papel vegetal (#f4f1e8) con grilla de mensura visible, tinta
          ferroprusiato (#0b3c8c), grafito, sello sólo para marcar. Archivo + Chivo Mono
          (Omnibus-Type, Buenos Aires). Cajetín de datos, cifras de parcela monoespaciadas,
          láminas de 2px de radio; ni glass ni gradientes.
          STORY: el vecino entiende que no tiene que elegir categoría, cree que el reporte
          tiene destino porque ve estado y número, y saca una foto.
          FIRST VIEWPORT: hoja a sangre; nº de hoja y cifra de reportes arriba a la
          izquierda, grilla de parcelas de las 4 áreas a la derecha, obturador azul sólido
          del ancho del pulgar al pie, descargo legal en el borde inferior.
          FORM: hoja de mensura del IGN, candidata 6 de la lista ordenada, seed 63657df4.
          FINISH: unreviewed and undocumented is unfinished; this build ends with the
          finish review, the verdict, DESIGN.md, and every shipping raster carrying its
          provenance.
        */}
        {children}
      </body>
    </html>
  );
}
