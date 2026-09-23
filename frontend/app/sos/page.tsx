'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Icono } from '@/components/ui/Icono';

export default function SOSPage() {
  const [denuncia, setDenuncia] = useState({
    denunciante: '',
    telefono: '',
    direccion: '',
    barrio: '',
    fechaHora: '',
    descripcionCebo: '',
    hayCamaras: false,
    animalesAfectados: '1',
  });

  const imprimirDenuncia = () => {
    window.print();
  };

  return (
    <main className="flex-1 bg-lino pb-16">
      {/* ── 1. Encabezado de Emergencia ── */}
      <section className="border-b border-coral bg-coral-50 py-8 sm:py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div className="max-w-3xl space-y-3">
              <div className="estado-sello inline-flex items-center gap-1.5 bg-coral px-3 py-1 font-bold text-white">
                <Icono nombre="atencion" className="size-3.5" />
                <span>Protocolo de urgencia</span>
              </div>
              <h1 className="text-3xl font-extrabold leading-[.95] tracking-[-.04em] text-corteza sm:text-5xl">
                ¿Sospechás que tu mascota ingirió un cebo tóxico?
              </h1>
              <p className="text-sm sm:text-base text-corteza-suave leading-relaxed">
                Los primeros <strong>10 a 15 minutos</strong> son cruciales. Mantené la calma,
                actuá con rapidez y comunicate de inmediato con una guardia veterinaria en Bolívar.
              </p>
            </div>

            <div className="shrink-0 flex flex-wrap gap-3">
              <Link
                href="/reportes/nuevo?tipo=alerta_cebo"
                className="inline-flex items-center gap-2 border border-coral bg-coral px-5 py-3 text-sm font-bold text-white hover:bg-coral-600"
              >
                <Icono nombre="atencion" className="size-4" />
                <span>Alertar Cebo a la Comunidad</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* ── 2. Columna Izquierda: Protocolo de Primeros Auxilios (4 Pasos) ── */}
        <div className="lg:col-span-2 space-y-6">
          <div className="border border-borde-fuerte bg-lino-alto p-6 shadow-warm-card sm:p-8 space-y-6">
            <div className="border-b border-borde-calido pb-4 flex items-center justify-between">
              <div><p className="rotulo">Leé antes de actuar</p><h2 className="mt-1 text-2xl font-extrabold tracking-[-.03em] text-corteza">
                Pasos inmediatos
              </h2></div>
              <span className="estado-sello bg-coral-50 border border-coral-200 px-3 py-1 font-bold text-coral">
                Ventana crítica: 15 min
              </span>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {/* Paso 1 */}
              <div className="flex items-start gap-4 border-b border-borde-suave py-4">
                <span className="grid size-9 shrink-0 place-items-center border border-corteza bg-corteza text-sm font-bold text-white">
                  1
                </span>
                <div>
                  <h3 className="font-bold text-sm text-corteza">
                    Identificá los síntomas de alarma
                  </h3>
                  <p className="mt-1 text-xs text-corteza-suave leading-relaxed">
                    Salivación excesiva o espuma blanca, tambaleo al caminar, rigidez o debilidad
                    en patas traseras, temblores o convulsiones involuntarias, pupilas muy
                    dilatadas o contraídas.
                  </p>
                </div>
              </div>

              {/* Paso 2 */}
              <div className="flex items-start gap-4 border-b border-borde-suave py-4">
                <span className="grid size-9 shrink-0 place-items-center border border-corteza bg-corteza text-sm font-bold text-white">
                  2
                </span>
                <div>
                  <h3 className="font-bold text-sm text-corteza">
                    Llamá y salí hacia una veterinaria de guardia
                  </h3>
                  <p className="mt-1 text-xs text-corteza-suave leading-relaxed">
                    Avisá por teléfono que vas en camino con un cuadro de intoxicación aguda para
                    que tengan preparados los antídotos (atropina, carbón activado, sueros).
                  </p>
                </div>
              </div>

              {/* Paso 3 */}
              <div className="flex items-start gap-4 border-b border-coral py-4">
                <span className="grid size-9 shrink-0 place-items-center border border-coral bg-coral text-sm font-bold text-white">
                  3
                </span>
                <div>
                  <h3 className="font-bold text-sm text-coral">
                    Qué no hacer
                  </h3>
                  <p className="mt-1 text-xs text-corteza-suave leading-relaxed">
                    <strong>NO le des leche, aceite ni vinagre</strong> (aceleran la absorción del
                    veneno). <strong>NO provoques el vómito</strong> si el animal ya convulsiona o
                    está débil, ya que puede asfixiarse en el intento.
                  </p>
                </div>
              </div>

              {/* Paso 4 */}
              <div className="flex items-start gap-4 py-4">
                <span className="grid size-9 shrink-0 place-items-center border border-corteza bg-corteza text-sm font-bold text-white">
                  4
                </span>
                <div>
                  <h3 className="font-bold text-sm text-corteza">
                    Resguardá una muestra del cebo si es seguro
                  </h3>
                  <p className="mt-1 text-xs text-corteza-suave leading-relaxed">
                    Si viste el cebo en la calle, tomalo usando una bolsa de plástico limpia sin
                    tocarlo con las manos. Esa muestra le sirve al veterinario y a la policía para
                    determinar la sustancia tóxica.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* ── Planilla de Denuncia Vecinal (Ley 14.346) ── */}
          <div className="rounded-3xl bg-white border border-borde-calido p-6 sm:p-8 shadow-warm-card space-y-5">
            <div className="flex items-center justify-between border-b border-borde-calido pb-4">
              <div>
                <h3 className="font-serif text-lg font-bold text-corteza">
                  Generador de Denuncia Vecinal (Ley 14.346)
                </h3>
                <p className="text-xs text-corteza-suave mt-0.5">
                  Completá los datos para imprimir la planilla lista para presentar ante la Comisaría o Fiscalía 15 de Bolívar.
                </p>
              </div>
              <button
                onClick={imprimirDenuncia}
                type="button"
                className="inline-flex items-center gap-1.5 rounded-xl bg-terracota-50 border border-terracota-200 px-3 py-2 text-xs font-bold text-terracota hover:bg-terracota hover:text-white transition-colors"
              >
                <Icono nombre="impresora" className="size-4" />
                <span>Imprimir Planilla</span>
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-corteza mb-1">
                  Nombre y Apellido del vecino
                </label>
                <input
                  type="text"
                  value={denuncia.denunciante}
                  onChange={(e) => setDenuncia({ ...denuncia, denunciante: e.target.value })}
                  placeholder="Ej. Juan Pérez"
                  className="w-full rounded-xl border border-borde-calido px-3 py-2 text-xs text-corteza focus:border-terracota focus:ring-1 focus:ring-terracota"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-corteza mb-1">
                  Teléfono de contacto
                </label>
                <input
                  type="text"
                  value={denuncia.telefono}
                  onChange={(e) => setDenuncia({ ...denuncia, telefono: e.target.value })}
                  placeholder="2314-..."
                  className="w-full rounded-xl border border-borde-calido px-3 py-2 text-xs text-corteza focus:border-terracota focus:ring-1 focus:ring-terracota"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-corteza mb-1">
                  Lugar exacto del hallazgo (calle y altura)
                </label>
                <input
                  type="text"
                  value={denuncia.direccion}
                  onChange={(e) => setDenuncia({ ...denuncia, direccion: e.target.value })}
                  placeholder="Ej. Plaza Alsina, cantero central"
                  className="w-full rounded-xl border border-borde-calido px-3 py-2 text-xs text-corteza focus:border-terracota focus:ring-1 focus:ring-terracota"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-corteza mb-1">
                  Barrio en Bolívar
                </label>
                <input
                  type="text"
                  value={denuncia.barrio}
                  onChange={(e) => setDenuncia({ ...denuncia, barrio: e.target.value })}
                  placeholder="Ej. Barrio Centro / Las Flores"
                  className="w-full rounded-xl border border-borde-calido px-3 py-2 text-xs text-corteza focus:border-terracota focus:ring-1 focus:ring-terracota"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold text-corteza mb-1">
                  Descripción del cebo y circunstancias
                </label>
                <textarea
                  rows={3}
                  value={denuncia.descripcionCebo}
                  onChange={(e) => setDenuncia({ ...denuncia, descripcionCebo: e.target.value })}
                  placeholder="Describí cómo era el cebo (trozo de carne, polvo blanco/azul, olor a químico) y si hay cámaras de seguridad cercanas."
                  className="w-full rounded-xl border border-borde-calido px-3 py-2 text-xs text-corteza focus:border-terracota focus:ring-1 focus:ring-terracota"
                />
              </div>
            </div>
          </div>
        </div>

        {/* ── 3. Columna Derecha: Directorio Telefónico de Bolívar ── */}
        <div className="space-y-6">
          <div className="rounded-3xl bg-white border border-borde-calido p-6 shadow-warm-card space-y-4">
            <h3 className="font-serif text-lg font-bold text-corteza border-b border-borde-calido pb-3">
              Teléfonos de Urgencia en Bolívar
            </h3>

            <div className="space-y-3">
              <a
                href="tel:100"
                className="flex items-center justify-between p-3 rounded-2xl bg-coral-50/60 border border-coral-200 text-coral hover:bg-coral hover:text-white transition-all group"
              >
                <div>
                  <span className="text-xs font-bold block">Bomberos Voluntarios</span>
                  <span className="text-[11px] opacity-80">Emergencias 24 hs</span>
                </div>
                <span className="font-serif text-lg font-extrabold">100</span>
              </a>

              <a
                href="tel:101"
                className="flex items-center justify-between p-3 rounded-2xl bg-lino-suave border border-borde-calido text-corteza hover:bg-terracota hover:text-white transition-all group"
              >
                <div>
                  <span className="text-xs font-bold block">Policía / Comisaría</span>
                  <span className="text-[11px] text-corteza-clara group-hover:text-white/80">Denuncias Ley 14.346</span>
                </div>
                <span className="font-serif text-lg font-extrabold">101</span>
              </a>

              <div className="p-3.5 rounded-2xl bg-salvia-50 border border-salvia-200 space-y-1">
                <span className="text-xs font-bold text-salvia-700 block">
                  Protectora SAPAAB Bolívar
                </span>
                <p className="text-xs text-corteza-suave">
                  Asistencia a animales comunitarios y asesoramiento ante intoxicaciones.
                </p>
                <a
                  href="https://wa.me/5492314480000"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2 inline-flex items-center gap-1 text-xs font-bold text-salvia hover:underline"
                >
                  <Icono nombre="telefono" className="size-3.5" />
                  <span>Contactar por WhatsApp</span>
                </a>
              </div>

              <div className="p-3.5 rounded-2xl bg-terracota-50 border border-terracota-200 space-y-1">
                <span className="text-xs font-bold text-terracota block">
                  Fiscalía Nº 15 de Bolívar
                </span>
                <p className="text-xs text-corteza-suave">
                  Investigación penal de actos de crueldad y envenenamiento animal.
                </p>
                <span className="text-xs font-bold text-corteza block mt-1">
                  Tel: (02314) 42-1200
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
