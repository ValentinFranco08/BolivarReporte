'use client';

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { Icono } from '@/components/ui/Icono';
import { ErrorAPI, listarReportes, listarComunitarios, type Reporte } from '@/lib/api';

const Plano = dynamic(() => import('@/components/ui/Map'), {
  ssr: false,
  loading: () => (
    <div
      role="status"
      className="flex size-full items-center justify-center gap-3 bg-lino text-sm font-semibold text-corteza-suave"
    >
      <div className="flex size-8 items-center justify-center border border-terracota-200 bg-terracota-50">
        <Icono nombre="pata" className="size-4 text-terracota" />
      </div>
      Cargando el mapa vecinal de Bolívar…
    </div>
  ),
});

export default function MapaPage() {
  const [reportes, setReportes] = useState<Reporte[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    let vivo = true;
    Promise.all([
      listarReportes(),
      listarComunitarios().catch(() => []) // Fallback si falla comunitarios
    ])
      .then(([dataReportes, dataComunitarios]) => {
        if (!vivo) return;
        // Mapear comunitarios al formato visual de Reporte
        const mockComunitarios = dataComunitarios.map(c => ({
          id: -c.id, // ID negativo para que no colisione con reportes
          description: `Perro comunitario: ${c.pet_name}`,
          image_path: c.image_path,
          status: 'resuelto' as const,
          priority: 'baja' as const,
          address: c.address,
          latitude: c.latitude,
          longitude: c.longitude,
          created_at: c.created_at,
          category: null,
          prediction: null,
          report_type: 'comunitario' as const,
          pet_type: c.pet_type,
          pet_name: c.pet_name,
          pet_breed: c.pet_breed,
          color_description: c.color_description
        }));

        setReportes([...dataReportes, ...mockComunitarios]);
      })
      .catch((e) => {
        if (vivo)
          setError(
            e instanceof ErrorAPI ? e.message : 'No pudimos cargar los reportes del mapa.',
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
      {/* Panel flotante superior */}
      <div className="pointer-events-none absolute inset-x-0 top-0 z-20 p-3 sm:p-5">
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="pointer-events-auto max-w-md border border-borde-fuerte bg-lino-alto px-4 py-3 shadow-warm-card">
            <div className="flex items-center gap-3">
              <Link
                href="/"
                aria-label="Volver a la cartelera"
                className="inline-flex size-9 shrink-0 items-center justify-center border border-borde-fuerte bg-lino text-corteza hover:bg-terracota hover:text-white transition-all"
              >
                <Icono nombre="flecha-izquierda" className="size-4" />
              </Link>
              <div>
                <p className="rotulo">Actividad territorial</p>
                <h1 className="text-lg font-extrabold tracking-[-.03em] text-corteza leading-tight">
                  Mapa de rastreo
                </h1>
                <p className="text-xs text-corteza-suave">
                  {cargando ? 'Ubicando en el mapa…' : `${ubicados.length} avisos y alertas en Bolívar`}
                </p>
              </div>
            </div>

            {/* Leyenda amigable */}
            <div className="mt-3 flex flex-wrap items-center gap-1.5 border-t border-borde-suave pt-2 text-[11px]">
              <span className="estado-sello inline-flex items-center gap-1 bg-amber-50 border-amber-200 px-2 py-1 text-amber-800 font-semibold">
                Se busca
              </span>
              <span className="estado-sello inline-flex items-center gap-1 bg-salvia-50 border-salvia-200 px-2 py-1 text-salvia-700 font-semibold">
                Hallazgo
              </span>
              <span className="estado-sello inline-flex items-center gap-1 bg-coral-50 border-coral-200 px-2 py-1 text-coral font-bold">
                Alerta sanitaria
              </span>
              <span className="estado-sello inline-flex items-center gap-1 border-ambar bg-ambar-50 px-2 py-1 text-ambar font-semibold">
                Hogar y tránsito
              </span>
            </div>
          </div>

          <div className="pointer-events-auto flex items-center gap-2">
            <Link
              href="/sos"
              className="inline-flex h-10 items-center gap-1.5 rounded-md border border-coral-200 bg-coral-50 px-3.5 text-xs font-bold text-coral hover:bg-coral hover:text-white"
            >
              <Icono nombre="atencion" className="size-3.5" />
              <span>SOS Cebos</span>
            </Link>
            <Link
              href="/reportes/nuevo"
              className="boton-principal inline-flex h-10 items-center gap-1.5 px-4 text-xs"
            >
              <Icono nombre="camara" className="size-3.5" />
              <span>+ Publicar</span>
            </Link>
          </div>
        </div>

        {error ? (
          <div className="pointer-events-auto mx-auto mt-3 w-full max-w-md rounded-md border border-coral-200 bg-coral-50 p-3 text-xs text-coral">
            {error}
          </div>
        ) : null}
      </div>

      {/* El mapa interactivo */}
      <div className="min-h-[38rem] flex-1">
        <Plano reports={reportes} />
      </div>
    </main>
  );
}
