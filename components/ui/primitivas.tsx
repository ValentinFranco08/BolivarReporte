'use client';

/**
 * Primitivas del cajetín. Existen para que la accesibilidad sea estructural y
 * no una corrección puntual: todo campo tiene label asociada por id, los
 * botones declaran estado, y el diálogo atrapa el foco.
 */

import React, { useEffect, useId, useRef } from 'react';
import { Icono, type NombreIcono } from './Icono';

// ─── Botón ────────────────────────────────────────────────────────────────────

type TonoBoton = 'tinta' | 'contorno' | 'callado' | 'sello';

const TONOS: Record<TonoBoton, string> = {
  tinta:
    'bg-tinta-600 text-papel-alto border-tinta-700 hover:bg-tinta-700 active:bg-tinta-800 disabled:bg-grafito-200 disabled:text-grafito-500 disabled:border-grafito-200',
  contorno:
    'bg-papel-alto text-tinta-700 border-tinta-200 hover:bg-tinta-50 hover:border-tinta-300 active:bg-tinta-100 disabled:text-grafito-500 disabled:border-grafito-100',
  callado:
    'bg-transparent text-grafito-600 border-transparent hover:bg-papel-hondo active:bg-grafito-100 disabled:text-grafito-500',
  sello:
    'bg-papel-alto text-sello-700 border-sello-500/40 hover:bg-sello-100 active:bg-sello-100 disabled:text-grafito-500 disabled:border-grafito-100',
};

const TAMANOS = {
  // 48px de alto: objetivo táctil para un pulgar en la calle.
  normal: 'min-h-12 px-5 text-[0.9375rem]',
  grande: 'min-h-14 px-6 text-base',
  chico: 'min-h-9 px-3 text-[0.8125rem]',
} as const;

interface BotonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  tono?: TonoBoton;
  tamano?: keyof typeof TAMANOS;
  icono?: NombreIcono;
  cargando?: boolean;
  anchoCompleto?: boolean;
}

export function Boton({
  tono = 'tinta',
  tamano = 'normal',
  icono,
  cargando = false,
  anchoCompleto = false,
  className = '',
  children,
  disabled,
  ...resto
}: BotonProps) {
  return (
    <button
      {...resto}
      disabled={disabled || cargando}
      aria-busy={cargando || undefined}
      className={[
        'inline-flex items-center justify-center gap-2 rounded-hoja border font-medium',
        'transition-colors duration-150',
        'disabled:cursor-not-allowed',
        TONOS[tono],
        TAMANOS[tamano],
        anchoCompleto ? 'w-full' : '',
        className,
      ].join(' ')}
    >
      {cargando ? (
        <Compas />
      ) : icono ? (
        <Icono nombre={icono} className="size-[1.125em] shrink-0" />
      ) : null}
      {children}
    </button>
  );
}

/** El compás que gira mientras se mide. Reemplaza el spinner genérico. */
export function Compas({ className = '' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="square"
      aria-hidden
      className={`size-[1.125em] shrink-0 motion-safe:animate-spin ${className}`}
    >
      <circle cx="12" cy="12" r="8.5" strokeOpacity={0.25} />
      <path d="M12 3.5a8.5 8.5 0 0 1 8.5 8.5" />
    </svg>
  );
}

// ─── Campos ───────────────────────────────────────────────────────────────────

const BASE_CAMPO =
  'w-full rounded-hoja border border-grafito-200 bg-papel-alto px-3.5 py-3 text-[0.9375rem] text-grafito-900 placeholder:text-grafito-500 transition-colors hover:border-grafito-400 focus:border-tinta-600 disabled:bg-papel-hondo disabled:text-grafito-500';

interface CampoBase {
  etiqueta: string;
  /** Aclaración bajo el campo. Se asocia con aria-describedby. */
  ayuda?: string;
  error?: string | null;
}

export function CampoTexto({
  etiqueta,
  ayuda,
  error,
  className = '',
  ...resto
}: CampoBase & React.InputHTMLAttributes<HTMLInputElement>) {
  const id = useId();
  const idAyuda = `${id}-ayuda`;
  const idError = `${id}-error`;
  const descrito = [ayuda ? idAyuda : null, error ? idError : null].filter(Boolean).join(' ');

  return (
    <div className={className}>
      <label htmlFor={id} className="rotulo mb-1.5 block">
        {etiqueta}
      </label>
      <input
        {...resto}
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={descrito || undefined}
        className={`${BASE_CAMPO} ${error ? 'border-sello-500' : ''}`}
      />
      {ayuda ? (
        <p id={idAyuda} className="mt-1.5 text-[0.8125rem] text-grafito-500">
          {ayuda}
        </p>
      ) : null}
      {error ? (
        <p id={idError} className="mt-1.5 flex items-start gap-1.5 text-[0.8125rem] text-sello-700">
          <Icono nombre="atencion" className="mt-px size-4 shrink-0" />
          {error}
        </p>
      ) : null}
    </div>
  );
}

export function CampoArea({
  etiqueta,
  ayuda,
  error,
  className = '',
  ...resto
}: CampoBase & React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const id = useId();
  const idAyuda = `${id}-ayuda`;
  const idError = `${id}-error`;
  const descrito = [ayuda ? idAyuda : null, error ? idError : null].filter(Boolean).join(' ');

  return (
    <div className={className}>
      <label htmlFor={id} className="rotulo mb-1.5 block">
        {etiqueta}
      </label>
      <textarea
        {...resto}
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={descrito || undefined}
        className={`${BASE_CAMPO} resize-y leading-relaxed ${error ? 'border-sello-500' : ''}`}
      />
      {ayuda ? (
        <p id={idAyuda} className="mt-1.5 text-[0.8125rem] text-grafito-500">
          {ayuda}
        </p>
      ) : null}
      {error ? (
        <p id={idError} className="mt-1.5 flex items-start gap-1.5 text-[0.8125rem] text-sello-700">
          <Icono nombre="atencion" className="mt-px size-4 shrink-0" />
          {error}
        </p>
      ) : null}
    </div>
  );
}

interface CampoSelectProps
  extends CampoBase,
    React.SelectHTMLAttributes<HTMLSelectElement> {
  opciones: { valor: string; texto: string }[];
}

export function CampoSelect({
  etiqueta,
  ayuda,
  opciones,
  className = '',
  ...resto
}: CampoSelectProps) {
  const id = useId();
  return (
    <div className={className}>
      <label htmlFor={id} className="rotulo mb-1.5 block">
        {etiqueta}
      </label>
      <div className="relative">
        <select
          {...resto}
          id={id}
          className={`${BASE_CAMPO} appearance-none pr-10`}
        >
          {opciones.map((o) => (
            <option key={o.valor} value={o.valor}>
              {o.texto}
            </option>
          ))}
        </select>
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.5}
          aria-hidden
          className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-grafito-500"
        >
          <path d="M6 9.5l6 6 6-6" />
        </svg>
      </div>
      {ayuda ? <p className="mt-1.5 text-[0.8125rem] text-grafito-500">{ayuda}</p> : null}
    </div>
  );
}

// ─── Diálogo ──────────────────────────────────────────────────────────────────

interface DialogoProps {
  titulo: string;
  onCerrar: () => void;
  children: React.ReactNode;
  /** Se anuncia bajo el título y se asocia con aria-describedby. */
  descripcion?: string;
}

/**
 * Diálogo con role, foco atrapado, cierre con Escape y devolución del foco al
 * elemento que lo abrió. El modal anterior no tenía nada de esto.
 */
export function Dialogo({ titulo, descripcion, onCerrar, children }: DialogoProps) {
  const panel = useRef<HTMLDivElement>(null);
  const focoPrevio = useRef<HTMLElement | null>(null);
  const idTitulo = useId();
  const idDescripcion = useId();

  useEffect(() => {
    focoPrevio.current = document.activeElement as HTMLElement | null;
    const { body } = document;
    const overflowPrevio = body.style.overflow;
    body.style.overflow = 'hidden';

    const foco = () =>
      panel.current?.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
      ) ?? new NodeList() as unknown as NodeListOf<HTMLElement>;

    foco()[0]?.focus();

    const alPresionar = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onCerrar();
        return;
      }
      if (e.key !== 'Tab') return;
      const enfocables = Array.from(foco());
      if (enfocables.length === 0) return;
      const primero = enfocables[0];
      const ultimo = enfocables[enfocables.length - 1];
      if (e.shiftKey && document.activeElement === primero) {
        e.preventDefault();
        ultimo.focus();
      } else if (!e.shiftKey && document.activeElement === ultimo) {
        e.preventDefault();
        primero.focus();
      }
    };

    document.addEventListener('keydown', alPresionar);
    return () => {
      document.removeEventListener('keydown', alPresionar);
      body.style.overflow = overflowPrevio;
      focoPrevio.current?.focus();
    };
  }, [onCerrar]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-grafito-900/55 p-4 sm:items-center sm:p-6"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onCerrar();
      }}
    >
      <div
        ref={panel}
        role="dialog"
        aria-modal="true"
        aria-labelledby={idTitulo}
        aria-describedby={descripcion ? idDescripcion : undefined}
        className="motion-safe:desplegar my-auto w-full max-w-2xl rounded-hoja border border-grafito-200 bg-papel shadow-[0_2px_4px_rgba(16,20,24,0.08),0_22px_44px_-12px_rgba(16,20,24,0.22)]"
      >
        <div className="flex items-start justify-between gap-4 border-b border-grafito-200 bg-papel-alto px-5 py-4">
          <div>
            <h2 id={idTitulo} className="text-lg font-semibold tracking-tight text-grafito-900">
              {titulo}
            </h2>
            {descripcion ? (
              <p id={idDescripcion} className="mt-0.5 text-[0.8125rem] text-grafito-500">
                {descripcion}
              </p>
            ) : null}
          </div>
          <button
            type="button"
            onClick={onCerrar}
            className="-mr-1.5 -mt-1 inline-flex size-10 shrink-0 items-center justify-center rounded-hoja text-grafito-500 transition-colors hover:bg-papel-hondo hover:text-grafito-900"
          >
            <Icono nombre="cruz" className="size-5" titulo="Cerrar" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

// ─── Avisos ───────────────────────────────────────────────────────────────────

export function Aviso({
  tono = 'atencion',
  children,
}: {
  tono?: 'atencion' | 'error' | 'visto';
  children: React.ReactNode;
}) {
  const estilos = {
    atencion: 'border-margen-600/30 bg-margen-100 text-margen-600',
    error: 'border-sello-500/30 bg-sello-100 text-sello-700',
    visto: 'border-visto-600/30 bg-visto-100 text-visto-700',
  }[tono];

  const icono: NombreIcono = tono === 'visto' ? 'visto' : 'atencion';

  return (
    <div
      role={tono === 'error' ? 'alert' : 'status'}
      className={`flex items-start gap-2.5 rounded-hoja border px-4 py-3 text-[0.875rem] ${estilos}`}
    >
      <Icono nombre={icono} className="mt-px size-[1.125rem] shrink-0" />
      <span>{children}</span>
    </div>
  );
}

/** Cinta del descargo legal. Texto obligatorio, nunca decorativo. */
export function DescargoLegal({ className = '' }: { className?: string }) {
  return (
    <p
      className={`border-t border-grafito-200 pt-3 text-[0.75rem] leading-relaxed text-grafito-500 ${className}`}
    >
      La IA clasifica la situación a partir de la foto y el texto. No determina una
      infracción legal; eso corresponde a la normativa municipal.
    </p>
  );
}
