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
  | 'reloj';

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
