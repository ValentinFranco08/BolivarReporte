'use client';

import React, { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { Icono } from '@/components/ui/Icono';
import { Aviso, Compas } from '@/components/ui/primitivas';
import { MarcaArea, MarcaEstado, MarcaPrioridad, NumeroParcela } from '@/components/ui/marcas';
import { ErrorAPI, listarReportes, urlDeImagen, type Reporte } from '@/lib/api';
import { AREAS, ESTADO_EXPLICACION, etiquetaLegible } from '@/lib/taxonomy';

/**
 * Hoja de parcelas — el listado público.
 *
 * Cada reporte es un renglón de la hoja con su número, no una tarjeta suelta
 * en una grilla. La superficie de la foto ancla el renglón; el estado se lee
 * en palabras.
 */
export default function ListaReportes() {
  const [reportes, setReportes] = useState<Reporte[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [areaFiltro, setAreaFiltro] = useState<string>('todas');

  useEffect(() => {
    let vivo = true;
    listarReportes()
      .then((data) => {
        if (vivo) setReportes(data);
      })
      .catch((e) => {
        if (vivo)
          setError(
            e instanceof ErrorAPI ? e.message : 'No pudimos cargar los reportes.',
          );
      })
      .finally(() => {
        if (vivo) setCargando(false);
      });
    return () => {
      vivo = false;
    };
  }, []);

  const visibles = useMemo(
    () =>
      areaFiltro === 'todas'
        ? reportes
        : reportes.filter((r) => r.category?.area === areaFiltro),
    [reportes, areaFiltro],
  );

  return (
    <main className="mensura-mayor flex-1">
      <div className="mx-auto w-full max-w-[86rem] px-5 py-8 sm:px-8 sm:py-12">
        {/* Encabezado */}
        <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="inline-flex size-11 shrink-0 items-center justify-center rounded-hoja border border-grafito-200 bg-papel-alto text-grafito-600 transition-colors hover:border-tinta-300 hover:bg-tinta-50 hover:text-tinta-700"
            >
              <Icono nombre="flecha-izquierda" className="size-5" titulo="Volver al inicio" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold tracking-[-0.02em] text-grafito-900 sm:text-3xl">
                Reportes de la ciudad
              </h1>
              <p className="mt-1 text-[0.9375rem] text-grafito-600">
                Cada reporte es una parcela de la hoja, con número y estado.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/mapa"
              className="inline-flex min-h-12 items-center gap-2 rounded-hoja border border-tinta-200 bg-papel-alto px-4 text-[0.9375rem] font-medium text-tinta-700 transition-colors hover:border-tinta-300 hover:bg-tinta-50"
            >
              <Icono nombre="plano" className="size-[1.125em]" />
              Plano
            </Link>
            <Link
              href="/reportes/nuevo"
              className="inline-flex min-h-12 items-center gap-2 rounded-hoja border border-tinta-700 bg-tinta-600 px-4 text-[0.9375rem] font-semibold text-papel-alto transition-colors hover:bg-tinta-700"
            >
              <Icono nombre="camara" className="size-[1.125em]" />
              Reportar
            </Link>
          </div>
        </div>

        {/* Filtro por área */}
        <div className="mt-7 flex flex-wrap items-center gap-2">
          <span className="rotulo mr-1">Área</span>
          <FiltroArea
            activo={areaFiltro === 'todas'}
            onClick={() => setAreaFiltro('todas')}
            texto={`Todas (${reportes.length})`}
          />
          {AREAS.map((area) => {
            const n = reportes.filter((r) => r.category?.area === area).length;
            return (
              <FiltroArea
                key={area}
                activo={areaFiltro === area}
                onClick={() => setAreaFiltro(area)}
                texto={`${area} (${n})`}
              />
            );
          })}
        </div>

        {/* Cuerpo */}
        <div className="mt-6">
          {cargando ? (
            <div
              role="status"
              className="flex items-center justify-center gap-3 rounded-hoja border border-grafito-200 bg-papel-alto py-20 text-[0.9375rem] text-grafito-600"
            >
              <Compas className="text-tinta-600" />
              Abriendo la hoja…
            </div>
          ) : error ? (
            <Aviso tono="error">{error}</Aviso>
          ) : visibles.length === 0 ? (
            <HojaVacia hayReportes={reportes.length > 0} onVerTodas={() => setAreaFiltro('todas')} />
          ) : (
            <ul className="grid grid-cols-1 gap-px overflow-hidden rounded-hoja border border-grafito-200 bg-grafito-200 md:grid-cols-2 xl:grid-cols-3">
              {visibles.map((reporte, i) => (
                <li
                  key={reporte.id}
                  className="motion-safe:desplegar bg-papel-alto"
                  style={{ animationDelay: `${Math.min(i, 8) * 45}ms` }}
                >
                  <ParcelaReporte reporte={reporte} />
                </li>
              ))}
            </ul>
          )}
        </div>

        <p className="mt-8 border-t border-grafito-200 pt-4 text-[0.75rem] leading-relaxed text-grafito-500">
          La IA clasifica la situación a partir de la foto y el texto. No determina una
          infracción legal; eso corresponde a la normativa municipal.
        </p>
      </div>
    </main>
  );
}

function FiltroArea({
  activo,
  texto,
  onClick,
}: {
  activo: boolean;
  texto: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={activo}
      className={[
        'inline-flex min-h-10 items-center rounded-hoja border px-3 text-[0.875rem] transition-colors',
        activo
          ? 'border-tinta-600 bg-tinta-600 font-medium text-papel-alto'
          : 'border-grafito-200 bg-papel-alto text-grafito-600 hover:border-tinta-300 hover:bg-tinta-50',
      ].join(' ')}
    >
      {texto}
    </button>
  );
}

function ParcelaReporte({ reporte }: { reporte: Reporte }) {
  const foto = urlDeImagen(reporte.image_path);
  const categoria = reporte.category?.name ?? reporte.prediction?.predicted_class ?? null;

  return (
    <article className="flex h-full flex-col">
      {/* Renglón superior: número y estado */}
      <div className="flex items-center justify-between gap-3 border-b border-grafito-200 px-4 py-2.5">
        <NumeroParcela id={reporte.id} />
        <MarcaEstado estado={reporte.status} />
      </div>

      {/* La lámina */}
      <div className="relative aspect-[4/3] w-full overflow-hidden bg-papel-hondo">
        {foto ? (
          /* eslint-disable-next-line @next/next/no-img-element */
          <img
            src={foto}
            alt={`Situación reportada: ${etiquetaLegible(categoria)}`}
            loading="lazy"
            className="size-full object-cover"
          />
        ) : (
          <div className="mensura flex size-full items-center justify-center">
            <span className="rotulo">Sin foto</span>
          </div>
        )}
      </div>

      {/* Cajetín */}
      <div className="flex flex-1 flex-col px-4 py-4">
        <h2 className="text-base font-semibold leading-snug tracking-[-0.01em] text-grafito-900">
          {etiquetaLegible(categoria)}
        </h2>

        <div className="mt-2.5">
          <MarcaArea area={reporte.category?.area ?? null} />
        </div>

        {reporte.description ? (
          <p className="mt-3 line-clamp-2 text-[0.875rem] leading-relaxed text-grafito-600">
            {reporte.description}
          </p>
        ) : null}

        <p className="mt-3 text-[0.8125rem] leading-relaxed text-grafito-500">
          {ESTADO_EXPLICACION[reporte.status]}
        </p>

        {reporte.address ? (
          <p className="mt-3 flex items-start gap-1.5 text-[0.8125rem] text-grafito-600">
            <Icono nombre="chincheta" className="mt-px size-4 shrink-0 text-grafito-500" />
            <span className="line-clamp-1">{reporte.address}</span>
          </p>
        ) : null}

        <div className="mt-auto flex items-center justify-between gap-3 border-t border-grafito-200 pt-4">
          <time
            dateTime={reporte.created_at}
            className="cifra text-[0.75rem] text-grafito-500"
          >
            {new Date(reporte.created_at).toLocaleDateString('es-AR', {
              day: '2-digit',
              month: '2-digit',
              year: 'numeric',
            })}
          </time>
          <MarcaPrioridad prioridad={reporte.priority} />
        </div>
      </div>
    </article>
  );
}

/** La hoja vacía es una invitación dibujada, con las parcelas ya trazadas. */
function HojaVacia({
  hayReportes,
  onVerTodas,
}: {
  hayReportes: boolean;
  onVerTodas: () => void;
}) {
  return (
    <div className="rounded-hoja border border-grafito-200 bg-papel-alto px-6 py-16 text-center">
      {/* Parcelas trazadas y vacías, esperando. */}
      <div aria-hidden className="mx-auto grid max-w-xs grid-cols-3 gap-px bg-grafito-100">
        {Array.from({ length: 9 }).map((_, i) => (
          <div
            key={i}
            className="mensura aspect-square bg-papel"
            style={{ opacity: 1 - i * 0.07 }}
          />
        ))}
      </div>

      <h2 className="mt-8 text-lg font-semibold tracking-[-0.01em] text-grafito-900">
        {hayReportes ? 'Ningún reporte en esta área' : 'La hoja está en blanco'}
      </h2>
      <p className="mx-auto mt-2 max-w-[44ch] text-[0.9375rem] leading-relaxed text-grafito-600">
        {hayReportes
          ? 'Probá con otra área o mirá la hoja completa.'
          : 'Todavía no hay reportes registrados en Bolívar. El primero puede ser el tuyo.'}
      </p>

      <div className="mt-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
        {hayReportes ? (
          <button
            type="button"
            onClick={onVerTodas}
            className="inline-flex min-h-12 items-center rounded-hoja border border-tinta-200 bg-papel-alto px-5 text-[0.9375rem] font-medium text-tinta-700 transition-colors hover:border-tinta-300 hover:bg-tinta-50"
          >
            Ver la hoja completa
          </button>
        ) : null}
        <Link
          href="/reportes/nuevo"
          className="inline-flex min-h-12 items-center gap-2 rounded-hoja border border-tinta-700 bg-tinta-600 px-5 text-[0.9375rem] font-semibold text-papel-alto transition-colors hover:bg-tinta-700"
        >
          <Icono nombre="camara" className="size-[1.125em]" />
          Reportar algo
        </Link>
      </div>
    </div>
  );
}
