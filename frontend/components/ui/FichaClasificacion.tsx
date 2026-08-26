'use client';

import React, { useState } from 'react';
import { Icono } from './Icono';
import { MarcaArea } from './marcas';
import { CATEGORIAS, etiquetaLegible, buscarCategoria, AREAS } from '@/lib/taxonomy';

/**
 * Lo que ve el vecino después de que se analiza la foto.
 *
 * Decisión de producto: acá no aparece confianza, ni top-3, ni versión de
 * modelo, ni nombres de arquitectura. La inteligencia se demuestra en que el
 * vecino no tuvo que elegir entre 23 categorías, no en contarla. Toda esa
 * maquinaria vive en el panel municipal.
 */

interface FichaClasificacionProps {
  /** Etiqueta hoja que dedujo el sistema. */
  etiqueta: string;
  /** Corrección elegida por el vecino, si la hubo. */
  correccion: string | null;
  onCorregir: (categoria: string | null) => void;
}

export function FichaClasificacion({
  etiqueta,
  correccion,
  onCorregir,
}: FichaClasificacionProps) {
  const [editando, setEditando] = useState(false);

  const vigente = correccion ?? etiqueta;
  const categoria = buscarCategoria(vigente);
  const nombre = etiquetaLegible(vigente);

  return (
    <section className="rounded-hoja border border-grafito-200 bg-papel-alto">
      {/* Renglón del cajetín: lo que se dedujo. */}
      <div className="border-b border-grafito-200 px-5 py-5">
        <p className="rotulo">
          {correccion ? 'Categoría corregida por vos' : 'Registramos esta situación como'}
        </p>

        <h2 className="mt-2 text-[1.75rem] font-bold leading-tight tracking-[-0.02em] text-grafito-900">
          {nombre}
        </h2>

        <div className="mt-3 flex flex-wrap items-center gap-2.5">
          <MarcaArea area={categoria?.area ?? null} />
          {correccion ? (
            <span className="text-[0.8125rem] text-grafito-500">
              El sistema había propuesto {etiquetaLegible(etiqueta)}.
            </span>
          ) : null}
        </div>

        {categoria ? (
          <p className="mt-3 max-w-[52ch] text-[0.875rem] leading-relaxed text-grafito-600">
            {categoria.description}.
          </p>
        ) : null}
      </div>

      {/* Corrección: el vecino manda sobre la máquina. */}
      {editando ? (
        <div className="px-5 py-5">
          <p className="rotulo mb-3">Elegí la categoría que corresponde</p>

          <div className="max-h-72 space-y-4 overflow-y-auto pr-1">
            {AREAS.map((area) => (
              <div key={area}>
                <p className="mb-1.5 text-[0.75rem] font-semibold uppercase tracking-[0.08em] text-grafito-500">
                  {area}
                </p>
                <div className="grid grid-cols-1 gap-1.5 sm:grid-cols-2">
                  {CATEGORIAS.filter((c) => c.area === area).map((c) => {
                    const activa = vigente === c.name;
                    return (
                      <button
                        key={c.name}
                        type="button"
                        onClick={() => {
                          onCorregir(c.name === etiqueta ? null : c.name);
                          setEditando(false);
                        }}
                        aria-pressed={activa}
                        className={[
                          'flex min-h-11 items-center gap-2 rounded-hoja border px-3 text-left text-[0.875rem] transition-colors',
                          activa
                            ? 'border-tinta-600 bg-tinta-50 font-medium text-tinta-800'
                            : 'border-grafito-200 bg-papel-alto text-grafito-600 hover:border-tinta-300 hover:bg-tinta-50',
                        ].join(' ')}
                      >
                        {activa ? (
                          <Icono nombre="visto" className="size-4 shrink-0 text-tinta-600" />
                        ) : null}
                        {c.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 flex items-center justify-between gap-4 border-t border-grafito-200 pt-4">
            {correccion ? (
              <button
                type="button"
                onClick={() => {
                  onCorregir(null);
                  setEditando(false);
                }}
                className="text-[0.8125rem] text-tinta-700 underline decoration-tinta-200 hover:decoration-tinta-600"
              >
                Volver a la categoría original
              </button>
            ) : (
              <span />
            )}
            <button
              type="button"
              onClick={() => setEditando(false)}
              className="text-[0.8125rem] text-grafito-500 underline decoration-grafito-200 hover:text-grafito-900"
            >
              Cancelar
            </button>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-between gap-4 px-5 py-4">
          <p className="text-[0.8125rem] text-grafito-500">¿No es lo que pasa en la foto?</p>
          <button
            type="button"
            onClick={() => setEditando(true)}
            className="inline-flex min-h-10 items-center gap-2 rounded-hoja border border-tinta-200 bg-papel-alto px-3.5 text-[0.875rem] font-medium text-tinta-700 transition-colors hover:border-tinta-300 hover:bg-tinta-50"
          >
            <Icono nombre="lapiz" className="size-4" />
            Cambiar categoría
          </button>
        </div>
      )}
    </section>
  );
}
