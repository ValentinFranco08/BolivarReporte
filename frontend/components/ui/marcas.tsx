/**
 * Marcas del cajetín: estado, prioridad, área y número de parcela.
 *
 * El estado nunca se codifica sólo en color. Cada marca lleva palabra y, en
 * prioridad, una escala de trazos que se cuenta. Así se lee a pleno sol, en
 * escala de grises y con daltonismo.
 */

import type { Area, Estado, Prioridad } from '@/lib/taxonomy';
import { ESTADO_LABEL, PRIORIDAD_LABEL } from '@/lib/taxonomy';

// ─── Estado ───────────────────────────────────────────────────────────────────

const ESTILO_ESTADO: Record<Estado, string> = {
  reportado: 'border-grafito-400 bg-papel-alto text-grafito-600',
  clasificado: 'border-tinta-300 bg-tinta-50 text-tinta-700',
  pendiente: 'border-margen-600/40 bg-margen-100 text-margen-600',
  en_proceso: 'border-tinta-600 bg-tinta-100 text-tinta-800',
  resuelto: 'border-visto-600/40 bg-visto-100 text-visto-700',
  rechazado: 'border-grafito-400 bg-papel-hondo text-grafito-600',
  duplicado: 'border-grafito-200 bg-papel-hondo text-grafito-600',
  requiere_informacion: 'border-sello-500/40 bg-sello-100 text-sello-700',
};

export function MarcaEstado({ estado }: { estado: Estado }) {
  return (
    <span
      className={`inline-flex items-center rounded-hoja border px-2 py-0.5 font-mono text-[0.6875rem] uppercase tracking-[0.08em] ${
        ESTILO_ESTADO[estado] ?? ESTILO_ESTADO.reportado
      }`}
    >
      {ESTADO_LABEL[estado] ?? estado}
    </span>
  );
}

// ─── Prioridad ────────────────────────────────────────────────────────────────

const TRAZOS_PRIORIDAD: Record<Prioridad, number> = {
  baja: 1,
  media: 2,
  alta: 3,
  critica: 4,
};

const COLOR_PRIORIDAD: Record<Prioridad, string> = {
  baja: 'bg-grafito-400',
  media: 'bg-tinta-500',
  alta: 'bg-margen-600',
  critica: 'bg-sello-500',
};

/**
 * Prioridad como escala de trazos de mensura: se cuenta, no se interpreta.
 * Cuatro trazos llenos es crítica.
 */
export function MarcaPrioridad({
  prioridad,
  conTexto = true,
}: {
  prioridad: Prioridad;
  conTexto?: boolean;
}) {
  const llenos = TRAZOS_PRIORIDAD[prioridad] ?? 2;
  const color = COLOR_PRIORIDAD[prioridad] ?? COLOR_PRIORIDAD.media;

  return (
    <span className="inline-flex items-center gap-2">
      <span className="flex items-end gap-[3px]" aria-hidden>
        {[1, 2, 3, 4].map((n) => (
          <span
            key={n}
            className={`w-[3px] rounded-[1px] ${
              n <= llenos ? color : 'bg-grafito-100'
            }`}
            style={{ height: `${5 + n * 3}px` }}
          />
        ))}
      </span>
      {conTexto ? (
        <span className="font-mono text-[0.6875rem] uppercase tracking-[0.08em] text-grafito-600">
          {PRIORIDAD_LABEL[prioridad] ?? prioridad}
        </span>
      ) : (
        <span className="sr-only">Prioridad {PRIORIDAD_LABEL[prioridad] ?? prioridad}</span>
      )}
    </span>
  );
}

// ─── Área ─────────────────────────────────────────────────────────────────────

/** Las cuatro áreas, cada una con su letra de plancha. */
export const LETRA_AREA: Record<Area, string> = {
  Infraestructura: 'I',
  'Higiene Urbana': 'H',
  Animales: 'A',
  'Tránsito y Estacionamiento': 'T',
};

const ESTILO_AREA: Record<Area, string> = {
  Infraestructura: 'border-tinta-300 bg-tinta-50 text-tinta-700',
  'Higiene Urbana': 'border-visto-600/35 bg-visto-100 text-visto-700',
  Animales: 'border-margen-600/35 bg-margen-100 text-margen-600',
  'Tránsito y Estacionamiento': 'border-grafito-400 bg-papel-hondo text-grafito-600',
};

export function MarcaArea({ area }: { area: string | null | undefined }) {
  if (!area) {
    return (
      <span className="inline-flex items-center rounded-hoja border border-grafito-200 bg-papel-hondo px-2 py-0.5 font-mono text-[0.6875rem] uppercase tracking-[0.08em] text-grafito-600">
        Sin área
      </span>
    );
  }
  const clave = area as Area;
  const estilo = ESTILO_AREA[clave] ?? 'border-grafito-200 bg-papel-hondo text-grafito-600';
  const letra = LETRA_AREA[clave];

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-hoja border px-2 py-0.5 text-[0.75rem] ${estilo}`}
    >
      {letra ? (
        <span className="font-mono text-[0.625rem] font-bold tracking-normal" aria-hidden>
          {letra}
        </span>
      ) : null}
      {area}
    </span>
  );
}

// ─── Número de parcela ────────────────────────────────────────────────────────

/**
 * El identificador del reporte, escrito como número de parcela de la hoja.
 * Cuatro cifras con ceros a la izquierda para que la columna quede alineada.
 */
export function NumeroParcela({
  id,
  tamano = 'normal',
}: {
  id: number;
  tamano?: 'normal' | 'grande';
}) {
  const clases =
    tamano === 'grande'
      ? 'text-2xl sm:text-3xl'
      : 'text-[0.8125rem]';
  return (
    <span className={`cifra ${clases} text-grafito-900`}>
      <span className="text-grafito-500" aria-hidden>
        {String(id).padStart(4, '0').slice(0, -String(id).length)}
      </span>
      <span className="sr-only">Parcela </span>
      {id}
    </span>
  );
}

// ─── Tipo de Reporte Animal ──────────────────────────────────────────────────

export type TipoAnimalBadge = 'perdido' | 'encontrado' | 'alerta_cebo' | 'en_transito' | 'adopcion';

const ESTILO_TIPO_ANIMAL: Record<TipoAnimalBadge, { clases: string; etiqueta: string }> = {
  perdido: {
    clases: 'border-sello-500/60 bg-sello-100 text-sello-700',
    etiqueta: 'Perdido',
  },
  encontrado: {
    clases: 'border-tinta-400 bg-tinta-50 text-tinta-700',
    etiqueta: 'Encontrado',
  },
  alerta_cebo: {
    clases: 'border-sello-600 bg-sello-500 text-papel-alto font-semibold',
    etiqueta: 'Alerta Cebo',
  },
  en_transito: {
    clases: 'border-margen-600/50 bg-margen-100 text-margen-600',
    etiqueta: 'En Tránsito',
  },
  adopcion: {
    clases: 'border-visto-600/50 bg-visto-100 text-visto-700',
    etiqueta: 'En Adopción',
  },
};

export function MarcaTipoAnimal({
  tipo,
  tamano = 'normal',
}: {
  tipo: TipoAnimalBadge | string;
  tamano?: 'normal' | 'grande';
}) {
  const conf =
    ESTILO_TIPO_ANIMAL[tipo as TipoAnimalBadge] ?? ESTILO_TIPO_ANIMAL.perdido;
  const pad = tamano === 'grande' ? 'px-3 py-1 text-xs' : 'px-2 py-0.5 text-[0.6875rem]';

  return (
    <span
      className={`inline-flex items-center rounded-hoja border font-mono uppercase tracking-[0.08em] ${pad} ${conf.clases}`}
    >
      {conf.etiqueta}
    </span>
  );
}

// ─── Estado de Salud Animal ──────────────────────────────────────────────────

export type EstadoSaludBadge = 'sano' | 'lastimado' | 'sintomas_envenenamiento' | 'con_collar';

const ESTILO_SALUD_ANIMAL: Record<EstadoSaludBadge, { clases: string; etiqueta: string }> = {
  sano: {
    clases: 'border-visto-600/40 bg-visto-100 text-visto-700',
    etiqueta: 'Buen estado',
  },
  lastimado: {
    clases: 'border-sello-500/50 bg-sello-100 text-sello-700',
    etiqueta: 'Lastimado',
  },
  sintomas_envenenamiento: {
    clases: 'border-sello-700 bg-sello-600 text-papel-alto font-bold',
    etiqueta: 'Posible Intoxicación',
  },
  con_collar: {
    clases: 'border-tinta-300 bg-tinta-50 text-tinta-700',
    etiqueta: 'Tiene collar',
  },
};

export function MarcaSaludAnimal({ estado }: { estado: EstadoSaludBadge | string | null | undefined }) {
  if (!estado) return null;
  const conf = ESTILO_SALUD_ANIMAL[estado as EstadoSaludBadge];
  if (!conf) return null;

  return (
    <span
      className={`inline-flex items-center rounded-hoja border px-2 py-0.5 font-mono text-[0.6875rem] uppercase tracking-[0.08em] ${conf.clases}`}
    >
      {conf.etiqueta}
    </span>
  );
}

// ─── Marcas de registro en esquinas (Hoja de Mensura) ────────────────────────

export function MarcasDeEsquina({ className = '' }: { className?: string }) {
  const comun = 'pointer-events-none absolute size-4 border-tinta-600/25';
  return (
    <div aria-hidden className={className}>
      <span className={`${comun} left-3 top-3 border-l border-t`} />
      <span className={`${comun} right-3 top-3 border-r border-t`} />
      <span className={`${comun} bottom-3 left-3 border-b border-l`} />
      <span className={`${comun} bottom-3 right-3 border-b border-r`} />
    </div>
  );
}
