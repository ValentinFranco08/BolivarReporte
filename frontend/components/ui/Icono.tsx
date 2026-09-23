/**
 * Iconografía dibujada del mundo de la hoja de mensura: trazo de 1.5, esquinas
 * a escuadra, sin relleno. Reemplaza los emojis que hacían de iconos
 * (📍 🤖 ⚙️ ✅ ❌ ⚠️ 🗺 📋 ✏️), que cada sistema operativo dibuja distinto y
 * los lectores de pantalla leen en voz alta.
 */

export type NombreIcono =
  | 'camara'
  | 'chincheta'
  | 'plano'
  | 'hoja'
  | 'visto'
  | 'cruz'
  | 'atencion'
  | 'lapiz'
  | 'flecha-izquierda'
  | 'flecha-derecha'
  | 'lupa'
  | 'regla'
  | 'compas'
  | 'salir'
  | 'mas'
  | 'filtro'
  | 'reloj'
  | 'telefono'
  | 'escudo'
  | 'impresora'
  | 'pata'
  | 'mira'
  | 'qr'
  | 'credencial'
  | 'corazon'
  | 'campana'
  | 'compartir';

const TRAZOS: Record<NombreIcono, React.ReactNode> = {
  camara: (
    <>
      <path d="M3 8.5A1.5 1.5 0 0 1 4.5 7h2.2a1.5 1.5 0 0 0 1.25-.67l.9-1.35A1.5 1.5 0 0 1 10.1 4h3.8a1.5 1.5 0 0 1 1.25.98l.9 1.35A1.5 1.5 0 0 0 17.3 7h2.2A1.5 1.5 0 0 1 21 8.5v9A1.5 1.5 0 0 1 19.5 19h-15A1.5 1.5 0 0 1 3 17.5v-9Z" />
      <circle cx="12" cy="13" r="3.5" />
    </>
  ),
  chincheta: (
    <>
      <path d="M12 21s6-5.686 6-10a6 6 0 1 0-12 0c0 4.314 6 10 6 10Z" />
      <circle cx="12" cy="11" r="2.25" />
    </>
  ),
  plano: (
    <>
      <path d="M3 6.5 9.5 4l5 2.5L21 4v13.5L14.5 20l-5-2.5L3 20V6.5Z" />
      <path d="M9.5 4v13.5M14.5 6.5V20" />
    </>
  ),
  hoja: (
    <>
      <path d="M5 3.5h9L19 8v12.5H5V3.5Z" />
      <path d="M13.5 3.5V8H19" />
      <path d="M8 12.5h8M8 16h5" />
    </>
  ),
  visto: <path d="M5 12.5l4.5 4.5L19 7.5" />,
  cruz: <path d="M6 6l12 12M18 6L6 18" />,
  atencion: (
    <>
      <path d="M12 4.5 21 19.5H3L12 4.5Z" />
      <path d="M12 10v4" />
      <path d="M12 16.75h.01" />
    </>
  ),
  lapiz: (
    <>
      <path d="M4 20h4l11-11a2.5 2.5 0 0 0-3.5-3.5L4.5 16.5 4 20Z" />
      <path d="M14.5 6.5 17.5 9.5" />
    </>
  ),
  'flecha-izquierda': <path d="M19 12H5m0 0 6-6m-6 6 6 6" />,
  'flecha-derecha': <path d="M5 12h14m0 0-6-6m6 6-6 6" />,
  lupa: (
    <>
      <circle cx="11" cy="11" r="6.5" />
      <path d="M16 16l4.5 4.5" />
    </>
  ),
  regla: (
    <>
      <path d="M3.5 15.5 15.5 3.5l5 5-12 12-5-5Z" />
      <path d="M7 12l2 2M10 9l2 2M13 6l2 2" />
    </>
  ),
  compas: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 12 15.5 8.5M12 12l-2.5 5" />
    </>
  ),
  salir: (
    <>
      <path d="M15 4.5H6.5v15H15" />
      <path d="M12 12h8.5m0 0-3-3m3 3-3 3" />
    </>
  ),
  mas: <path d="M12 5.5v13M5.5 12h13" />,
  filtro: <path d="M4 6h16l-6.5 7.5V20l-3-2v-4.5L4 6Z" />,
  reloj: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7.5V12l3 2" />
    </>
  ),
  telefono: (
    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92Z" />
  ),
  escudo: (
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" />
  ),
  impresora: (
    <>
      <path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
      <path d="M6 14h12v8H6z" />
    </>
  ),
  pata: (
    <>
      <circle cx="12" cy="14" r="3.5" />
      <circle cx="8" cy="8.5" r="1.8" />
      <circle cx="16" cy="8.5" r="1.8" />
      <circle cx="5" cy="11.5" r="1.5" />
      <circle cx="19" cy="11.5" r="1.5" />
    </>
  ),
  mira: (
    <>
      <circle cx="12" cy="12" r="8" />
      <line x1="12" y1="2" x2="12" y2="6" />
      <line x1="12" y1="18" x2="12" y2="22" />
      <line x1="2" y1="12" x2="6" y2="12" />
      <line x1="18" y1="12" x2="22" y2="12" />
    </>
  ),
  qr: (
    <>
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="3" height="3" />
      <rect x="18" y="14" width="3" height="3" />
      <rect x="14" y="18" width="3" height="3" />
      <rect x="18" y="18" width="3" height="3" />
    </>
  ),
  credencial: (
    <>
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <circle cx="9" cy="11" r="2.5" />
      <path d="M14 9h4M14 13h3M6 17c0-1.5 1.5-2.5 3-2.5s3 1 3 2.5" />
    </>
  ),
  corazon: (
    <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
  ),
  campana: (
    <>
      <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
      <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
    </>
  ),
  compartir: (
    <>
      <circle cx="18" cy="5" r="3" />
      <circle cx="6" cy="12" r="3" />
      <circle cx="18" cy="19" r="3" />
      <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
      <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
    </>
  ),
};

interface IconoProps extends React.SVGProps<SVGSVGElement> {
  nombre: NombreIcono;
  /** Texto para lectores de pantalla. Sin esto el icono queda oculto. */
  titulo?: string;
}

export function Icono({ nombre, titulo, className, ...resto }: IconoProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="square"
      strokeLinejoin="miter"
      aria-hidden={titulo ? undefined : true}
      role={titulo ? 'img' : undefined}
      className={className}
      {...resto}
    >
      {titulo ? <title>{titulo}</title> : null}
      {TRAZOS[nombre]}
    </svg>
  );
}
