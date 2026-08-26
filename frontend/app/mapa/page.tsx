'use client';

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { Icono } from '@/components/ui/Icono';
import { Aviso, Compas } from '@/components/ui/primitivas';
import { ErrorAPI, listarReportes, type Reporte } from '@/lib/api';
import { PRIORIDAD_LABEL, PRIORIDADES } from '@/lib/taxonomy';

const Plano = dynamic(() => import('@/components/ui/Map'), {
  ssr: false,
  loading: () => (
    <div
      role="status"
      className="mensura flex size-full items-center justify-center gap-3 bg-papel-hondo text-[0.9375rem] text-grafito-600"
    >
      <Compas className="text-tinta-600" />
      Desplegando el plano…
    </div>
  ),
});

const COLOR_POR_PRIORIDAD: Record<string, string> = {
  baja: 'bg-grafito-500',
  media: 'bg-tinta-500',
  alta: 'bg-margen-600',
  critica: 'bg-sello-500',
};

/**
 * Hoja de plano — la mensura sobre el territorio real.
 * El cajetín flota sobre el plano, como el rótulo de una plancha.
 */
export default function MapaPage() {
  const [reportes, setReportes] = useState<Reporte[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    let vivo = true;
    listarReportes()
      .then((data) => {
        if (vivo) setReportes(data);
      })
      .catch((e) => {
        if (vivo)
          setError(
            e instanceof ErrorAPI ? e.message : 'No pudimos cargar los reportes del plano.',
          );
      })
      .finally(() => {
        if (vivo) setCargando(false);
      });
    return () => {
      vivo = false;
    };
  }, []);

  const ubicados = reportes.filter((r) => r.latitude !== null && r.longitude !== null);

  return (
    <main className="relative flex flex-1 flex-col">
      {/* Cajetín flotante */}
      <div className="pointer-events-none absolute inset-x-0 top-0 z-20 p-4 sm:p-5">
        <div className="mx-auto flex w-full max-w-[86rem] flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          {/* Cajetín de plancha: papel opaco sobre el plano. */}
          <div className="pointer-events-auto rounded-hoja border border-grafito-200 bg-papel-alto px-4 py-3 shadow-[0_1px_2px_rgba(16,20,24,0.06),0_8px_20px_-6px_rgba(16,20,24,0.14)]">
            <div className="flex items-center gap-3">
              <Link
                href="/"
                className="inline-flex size-10 shrink-0 items-center justify-center rounded-hoja border border-grafito-200 text-grafito-600 transition-colors hover:border-tinta-300 hover:bg-tinta-50 hover:text-tinta-700"
              >
                <Icono nombre="flecha-izquierda" className="size-4.5" titulo="Volver al inicio" />
              </Link>
              <div>
                <h1 className="text-lg font-bold tracking-[-0.02em] text-grafito-900">
                  Plano de Bolívar
                </h1>
                <p className="cifra text-[0.8125rem] text-grafito-600">
                  {cargando ? 'Desplegando reportes…' : `${ubicados.length} reportes ubicados`}
                </p>
              </div>
            </div>

            {/* Referencias de la plancha */}
            <dl className="mt-3.5 flex flex-wrap items-center gap-x-4 gap-y-1.5 border-t border-grafito-200 pt-3">
              <dt className="rotulo w-full sm:w-auto">Prioridad</dt>
              {PRIORIDADES.map((p) => (
                <div key={p} className="flex items-center gap-1.5">
                  <span
                    aria-hidden
                    className={`size-2.5 rounded-full ${COLOR_POR_PRIORIDAD[p]}`}
                  />
                  <dd className="text-[0.75rem] text-grafito-600">{PRIORIDAD_LABEL[p]}</dd>
                </div>
              ))}
            </dl>
          </div>

          <div className="pointer-events-auto flex gap-2.5">
            <Link
              href="/reportes"
              className="inline-flex min-h-12 items-center gap-2 rounded-hoja border border-grafito-200 bg-papel-alto px-4 text-[0.9375rem] font-medium text-tinta-700 shadow-[0_1px_2px_rgba(16,20,24,0.06)] transition-colors hover:border-tinta-300 hover:bg-tinta-50"
            >
              <Icono nombre="hoja" className="size-[1.125em]" />
              Listado
            </Link>
            <Link
              href="/reportes/nuevo"
              className="inline-flex min-h-12 items-center gap-2 rounded-hoja border border-tinta-700 bg-tinta-600 px-4 text-[0.9375rem] font-semibold text-papel-alto shadow-[0_1px_2px_rgba(16,20,24,0.12)] transition-colors hover:bg-tinta-700"
            >
              <Icono nombre="camara" className="size-[1.125em]" />
              Reportar
            </Link>
          </div>
        </div>

        {error ? (
          <div className="pointer-events-auto mx-auto mt-3 w-full max-w-[86rem] sm:max-w-md">
            <Aviso tono="error">{error}</Aviso>
          </div>
        ) : null}
      </div>

      {/* El plano ocupa la hoja entera */}
      <div className="min-h-[38rem] flex-1">
        <Plano reports={reportes} />
      </div>
    </main>
  );
}
