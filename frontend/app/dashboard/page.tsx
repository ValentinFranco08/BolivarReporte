'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Icono } from '@/components/ui/Icono';
import {
  Aviso,
  Boton,
  CampoSelect,
  Compas,
  Dialogo,
} from '@/components/ui/primitivas';
import { MarcaArea, MarcaEstado, MarcaPrioridad, NumeroParcela } from '@/components/ui/marcas';
import {
  ErrorAPI,
  actualizarReporte,
  borrarToken,
  enviarCorreccion,
  leerToken,
  listarReportes,
  urlDeImagen,
  type Reporte,
} from '@/lib/api';
import {
  AREAS,
  CATEGORIAS,
  ESTADOS,
  ESTADO_LABEL,
  PRIORIDADES,
  PRIORIDAD_LABEL,
  etiquetaLegible,
  type Estado,
  type Prioridad,
} from '@/lib/taxonomy';

/**
 * Panel municipal — la mesa de triage.
 *
 * Acá sí vive la maquinaria: confianza del modelo, corrección para
 * reentrenamiento y cambio de estado. Es la única superficie donde eso
 * corresponde. Trabajo de escritorio, operable por teclado de punta a punta.
 */
export default function Panel() {
  const router = useRouter();

  // El token se lee una sola vez al inicializar; leerlo dentro del efecto
  // obligaba a fijar estado de forma sincrónica y encadenaba renders.
  const [token] = useState<string | null>(() => leerToken());
  const [reportes, setReportes] = useState<Reporte[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [abierto, setAbierto] = useState<Reporte | null>(null);

  const [filtroEstado, setFiltroEstado] = useState('todos');
  const [filtroArea, setFiltroArea] = useState('todas');
  const [filtroPrioridad, setFiltroPrioridad] = useState('todas');
  const [busqueda, setBusqueda] = useState('');

  useEffect(() => {
    if (!token) {
      router.push('/login?volver=/dashboard');
      return;
    }
    let vivo = true;
    listarReportes()
      .then((data) => {
        if (vivo) setReportes(data);
      })
      .catch((e) => {
        if (vivo)
          setError(
            e instanceof ErrorAPI ? e.message : 'No pudimos cargar la cola de reportes.',
          );
      })
      .finally(() => {
        if (vivo) setCargando(false);
      });
    return () => {
      vivo = false;
    };
  }, [router, token]);

  const alActualizar = useCallback((actualizado: Reporte) => {
    setReportes((prev) => prev.map((r) => (r.id === actualizado.id ? actualizado : r)));
    setAbierto(actualizado);
  }, []);

  const salir = () => {
    borrarToken();
    router.push('/');
  };

  const resumen = useMemo(
    () => ({
      total: reportes.length,
      sinGestionar: reportes.filter((r) => r.status === 'reportado').length,
      enProceso: reportes.filter((r) => r.status === 'en_proceso').length,
      resueltos: reportes.filter((r) => r.status === 'resuelto').length,
      criticos: reportes.filter((r) => r.priority === 'critica').length,
    }),
    [reportes],
  );

  const visibles = useMemo(() => {
    const q = busqueda.trim().toLowerCase();
    return reportes.filter((r) => {
      if (filtroEstado !== 'todos' && r.status !== filtroEstado) return false;
      if (filtroArea !== 'todas' && r.category?.area !== filtroArea) return false;
      if (filtroPrioridad !== 'todas' && r.priority !== filtroPrioridad) return false;
      if (!q) return true;
      return (
        r.description?.toLowerCase().includes(q) ||
        r.category?.name.toLowerCase().includes(q) ||
        r.address?.toLowerCase().includes(q) ||
        String(r.id).includes(q)
      );
    });
  }, [reportes, filtroEstado, filtroArea, filtroPrioridad, busqueda]);

  return (
    <main className="mensura-mayor flex-1">
      <div className="mx-auto w-full max-w-[92rem] px-5 py-8 sm:px-8 sm:py-10">
        {/* Encabezado de plancha */}
        <div className="flex flex-col gap-5 border-b border-grafito-200 pb-7 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-[-0.02em] text-grafito-900 sm:text-3xl">
              Cola de reportes
            </h1>
            <p className="mt-1.5 text-[0.9375rem] text-grafito-600">
              Reportes ciudadanos de Bolívar, listos para gestión.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2.5">
            <Link
              href="/mapa"
              className="inline-flex min-h-11 items-center gap-2 rounded-hoja border border-grafito-200 bg-papel-alto px-3.5 text-[0.875rem] font-medium text-tinta-700 transition-colors hover:border-tinta-300 hover:bg-tinta-50"
            >
              <Icono nombre="plano" className="size-4" />
              Plano
            </Link>
            <Link
              href="/reportes"
              className="inline-flex min-h-11 items-center gap-2 rounded-hoja border border-grafito-200 bg-papel-alto px-3.5 text-[0.875rem] font-medium text-tinta-700 transition-colors hover:border-tinta-300 hover:bg-tinta-50"
            >
              <Icono nombre="hoja" className="size-4" />
              Vista pública
            </Link>
            <button
              type="button"
              onClick={salir}
              className="inline-flex min-h-11 items-center gap-2 rounded-hoja border border-grafito-200 bg-papel-alto px-3.5 text-[0.875rem] font-medium text-grafito-600 transition-colors hover:border-sello-500/40 hover:bg-sello-100 hover:text-sello-700"
            >
              <Icono nombre="salir" className="size-4" />
              Salir
            </button>
          </div>
        </div>

        {/* Cifras del cajetín */}
        <dl className="grid grid-cols-2 gap-px overflow-hidden border-x border-b border-grafito-200 bg-grafito-200 sm:grid-cols-3 lg:grid-cols-5">
          <Cifra rotulo="Total en hoja" valor={resumen.total} />
          <Cifra rotulo="Sin gestionar" valor={resumen.sinGestionar} destacar={resumen.sinGestionar > 0} />
          <Cifra rotulo="En proceso" valor={resumen.enProceso} />
          <Cifra rotulo="Resueltos" valor={resumen.resueltos} />
          <Cifra rotulo="Críticos" valor={resumen.criticos} alerta={resumen.criticos > 0} />
        </dl>

        {/* Filtros */}
        <div className="mt-7 grid grid-cols-1 gap-3 rounded-hoja border border-grafito-200 bg-papel-alto p-4 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <label htmlFor="busqueda" className="rotulo mb-1.5 block">
              Buscar
            </label>
            <div className="relative">
              <Icono
                nombre="lupa"
                className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-grafito-500"
              />
              <input
                id="busqueda"
                type="search"
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                placeholder="Número, dirección, descripción…"
                className="w-full rounded-hoja border border-grafito-200 bg-papel-alto py-3 pl-9 pr-3 text-[0.9375rem] text-grafito-900 placeholder:text-grafito-500 transition-colors hover:border-grafito-400 focus:border-tinta-600"
              />
            </div>
          </div>

          <CampoSelect
            etiqueta="Estado"
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
            opciones={[
              { valor: 'todos', texto: 'Todos los estados' },
              ...ESTADOS.map((s) => ({ valor: s, texto: ESTADO_LABEL[s] })),
            ]}
          />

          <CampoSelect
            etiqueta="Área"
            value={filtroArea}
            onChange={(e) => setFiltroArea(e.target.value)}
            opciones={[
              { valor: 'todas', texto: 'Todas las áreas' },
              ...AREAS.map((a) => ({ valor: a, texto: a })),
            ]}
          />

          <CampoSelect
            etiqueta="Prioridad"
            value={filtroPrioridad}
            onChange={(e) => setFiltroPrioridad(e.target.value)}
            opciones={[
              { valor: 'todas', texto: 'Todas las prioridades' },
              ...PRIORIDADES.map((p) => ({ valor: p, texto: PRIORIDAD_LABEL[p] })),
            ]}
          />
        </div>

        {/* Tabla */}
        <div className="mt-5">
          {cargando ? (
            <div
              role="status"
              className="flex items-center justify-center gap-3 rounded-hoja border border-grafito-200 bg-papel-alto py-20 text-[0.9375rem] text-grafito-600"
            >
              <Compas className="text-tinta-600" />
              Abriendo la cola…
            </div>
          ) : error ? (
            <Aviso tono="error">{error}</Aviso>
          ) : visibles.length === 0 ? (
            <div className="rounded-hoja border border-grafito-200 bg-papel-alto px-6 py-16 text-center">
              <p className="text-lg font-semibold text-grafito-900">
                {reportes.length === 0 ? 'La cola está vacía' : 'Ningún reporte con esos filtros'}
              </p>
              <p className="mx-auto mt-2 max-w-[46ch] text-[0.9375rem] text-grafito-600">
                {reportes.length === 0
                  ? 'Todavía no entró ningún reporte de vecinos.'
                  : 'Probá ampliando el estado, el área o la prioridad.'}
              </p>
            </div>
          ) : (
            <>
              <p className="rotulo mb-2">
                {visibles.length} de {reportes.length} reportes
              </p>
              {/* `relative` hace que los sr-only absolutos (y el clip del
                  scroll) queden contenidos: sin él, los spans accesibles
                  escapaban del contenedor y estiraban el documento. */}
              <div className="relative overflow-x-auto rounded-hoja border border-grafito-200 bg-papel-alto">
                <table className="w-full min-w-[54rem] text-left text-[0.875rem]">
                  <caption className="sr-only">
                    Reportes de vecinos con estado, prioridad y clasificación
                  </caption>
                  <thead>
                    <tr className="border-b border-grafito-200 bg-papel">
                      <Th>Nº</Th>
                      <Th>Foto</Th>
                      <Th>Categoría</Th>
                      <Th className="hidden lg:table-cell">Dirección</Th>
                      <Th className="hidden xl:table-cell">Confianza</Th>
                      <Th>Estado</Th>
                      <Th>Prioridad</Th>
                      <Th className="hidden sm:table-cell">Fecha</Th>
                      <th className="px-3 py-2.5">
                        <span className="sr-only">Acciones</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-grafito-100">
                    {visibles.map((r) => {
                      const foto = urlDeImagen(r.image_path);
                      const categoria = r.category?.name ?? r.prediction?.predicted_class ?? null;
                      return (
                        <tr key={r.id} className="transition-colors hover:bg-tinta-50/50">
                          <td className="px-3 py-2.5">
                            <NumeroParcela id={r.id} />
                          </td>
                          <td className="px-3 py-2.5">
                            {foto ? (
                              /* eslint-disable-next-line @next/next/no-img-element */
                              <img
                                src={foto}
                                alt=""
                                loading="lazy"
                                className="size-12 rounded-[1px] border border-grafito-100 object-cover"
                              />
                            ) : (
                              <div className="mensura grid size-12 place-items-center rounded-[1px] border border-grafito-100">
                                <span className="font-mono text-[0.5625rem] uppercase text-grafito-500">
                                  s/f
                                </span>
                              </div>
                            )}
                          </td>
                          <td className="px-3 py-2.5">
                            <span className="block font-medium text-grafito-900">
                              {etiquetaLegible(categoria)}
                            </span>
                            <span className="mt-1 block">
                              <MarcaArea area={r.category?.area ?? null} />
                            </span>
                          </td>
                          <td className="hidden max-w-[13rem] px-3 py-2.5 lg:table-cell">
                            <span className="block truncate text-grafito-600" title={r.address ?? ''}>
                              {r.address ?? '—'}
                            </span>
                          </td>
                          <td className="hidden px-3 py-2.5 xl:table-cell">
                            {r.prediction ? (
                              <Confianza valor={r.prediction.confidence} />
                            ) : (
                              <span className="text-grafito-500">—</span>
                            )}
                          </td>
                          <td className="px-3 py-2.5">
                            <MarcaEstado estado={r.status} />
                          </td>
                          <td className="px-3 py-2.5">
                            <MarcaPrioridad prioridad={r.priority} conTexto={false} />
                          </td>
                          <td className="hidden px-3 py-2.5 sm:table-cell">
                            <time
                              dateTime={r.created_at}
                              className="cifra text-[0.75rem] text-grafito-500"
                            >
                              {new Date(r.created_at).toLocaleDateString('es-AR', {
                                day: '2-digit',
                                month: '2-digit',
                                year: '2-digit',
                              })}
                            </time>
                          </td>
                          <td className="px-3 py-2.5 text-right">
                            {/* Un botón real: la fila entera ya no es un div clicable. */}
                            <button
                              type="button"
                              onClick={() => setAbierto(r)}
                              className="inline-flex min-h-9 items-center rounded-hoja border border-tinta-200 bg-papel-alto px-3 text-[0.8125rem] font-medium text-tinta-700 transition-colors hover:border-tinta-300 hover:bg-tinta-50"
                            >
                              Gestionar
                              <span className="sr-only"> el reporte número {r.id}</span>
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </div>

      {abierto && token ? (
        <FichaGestion
          reporte={abierto}
          token={token}
          onCerrar={() => setAbierto(null)}
          onActualizar={alActualizar}
        />
      ) : null}
    </main>
  );
}

// ─── Piezas ───────────────────────────────────────────────────────────────────

function Th({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <th
      scope="col"
      className={`px-3 py-2.5 font-mono text-[0.6875rem] font-normal uppercase tracking-[0.1em] text-grafito-500 ${className}`}
    >
      {children}
    </th>
  );
}

function Cifra({
  rotulo,
  valor,
  destacar = false,
  alerta = false,
}: {
  rotulo: string;
  valor: number;
  destacar?: boolean;
  alerta?: boolean;
}) {
  return (
    <div className="bg-papel-alto px-4 py-4">
      <dt className="rotulo">{rotulo}</dt>
      <dd
        className={[
          'cifra mt-1 text-2xl font-semibold',
          alerta ? 'text-sello-700' : destacar ? 'text-tinta-700' : 'text-grafito-900',
        ].join(' ')}
      >
        {valor}
      </dd>
    </div>
  );
}

/** Confianza del modelo: dato municipal, nunca visible al vecino. */
function Confianza({ valor }: { valor: number }) {
  const pct = Math.round(valor * 100);
  const bajo = valor < 0.55;
  return (
    <span className="flex items-center gap-2">
      <span aria-hidden className="h-1.5 w-14 overflow-hidden rounded-[1px] bg-grafito-100">
        <span
          className={`block h-full ${bajo ? 'bg-margen-600' : 'bg-tinta-500'}`}
          style={{ width: `${pct}%` }}
        />
      </span>
      <span className={`cifra text-[0.75rem] ${bajo ? 'text-margen-600' : 'text-grafito-600'}`}>
        {pct}%
      </span>
    </span>
  );
}

// ─── Ficha de gestión ─────────────────────────────────────────────────────────

function FichaGestion({
  reporte,
  token,
  onCerrar,
  onActualizar,
}: {
  reporte: Reporte;
  token: string;
  onCerrar: () => void;
  onActualizar: (r: Reporte) => void;
}) {
  const [estado, setEstado] = useState<Estado>(reporte.status);
  const [prioridad, setPrioridad] = useState<Prioridad>(reporte.priority);
  const [guardando, setGuardando] = useState(false);
  const [guardado, setGuardado] = useState(false);
  const [errorGuardar, setErrorGuardar] = useState<string | null>(null);

  const [modoCorreccion, setModoCorreccion] = useState(false);
  const [claseCorrecta, setClaseCorrecta] = useState('');
  const [enviandoFeedback, setEnviandoFeedback] = useState(false);
  const [feedbackListo, setFeedbackListo] = useState(false);
  const [errorFeedback, setErrorFeedback] = useState<string | null>(null);

  const foto = urlDeImagen(reporte.image_path);
  const categoria = reporte.category?.name ?? reporte.prediction?.predicted_class ?? null;
  const hayCambios = estado !== reporte.status || prioridad !== reporte.priority;

  const guardar = async () => {
    setGuardando(true);
    setErrorGuardar(null);
    try {
      onActualizar(await actualizarReporte(token, reporte.id, { status: estado, priority: prioridad }));
      setGuardado(true);
      setTimeout(() => setGuardado(false), 2400);
    } catch (e) {
      setErrorGuardar(
        e instanceof ErrorAPI ? e.message : 'No pudimos guardar los cambios.',
      );
    } finally {
      setGuardando(false);
    }
  };

  const mandarFeedback = async (correcta: boolean) => {
    if (!reporte.prediction) return;
    setEnviandoFeedback(true);
    setErrorFeedback(null);
    try {
      await enviarCorreccion(token, reporte.prediction.id, correcta, claseCorrecta || null);
      setFeedbackListo(true);
    } catch (e) {
      setErrorFeedback(
        e instanceof ErrorAPI ? e.message : 'No pudimos registrar la corrección.',
      );
    } finally {
      setEnviandoFeedback(false);
    }
  };

  return (
    <Dialogo
      titulo={`Reporte Nº ${reporte.id}`}
      descripcion={etiquetaLegible(categoria)}
      onCerrar={onCerrar}
    >
      <div className="max-h-[calc(90vh-5rem)] overflow-y-auto px-5 py-5">
        {foto ? (
          /* eslint-disable-next-line @next/next/no-img-element */
          <img
            src={foto}
            alt={`Situación reportada: ${etiquetaLegible(categoria)}`}
            className="h-52 w-full rounded-hoja border border-grafito-200 object-cover"
          />
        ) : null}

        {/* Datos de hoja */}
        <dl className="mt-5 grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-2">
          <div>
            <dt className="rotulo">Categoría</dt>
            <dd className="mt-1 font-medium text-grafito-900">{etiquetaLegible(categoria)}</dd>
            <dd className="mt-1.5">
              <MarcaArea area={reporte.category?.area ?? null} />
            </dd>
          </div>
          <div>
            <dt className="rotulo">Ingresado</dt>
            <dd className="mt-1 text-[0.875rem] text-grafito-900">
              {new Date(reporte.created_at).toLocaleString('es-AR', {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </dd>
          </div>
          {reporte.address ? (
            <div className="sm:col-span-2">
              <dt className="rotulo">Dirección</dt>
              <dd className="mt-1 flex items-start gap-1.5 text-[0.875rem] text-grafito-900">
                <Icono nombre="chincheta" className="mt-px size-4 shrink-0 text-grafito-500" />
                {reporte.address}
              </dd>
            </div>
          ) : null}
          {reporte.description ? (
            <div className="sm:col-span-2">
              <dt className="rotulo">Descripción del vecino</dt>
              <dd className="mt-1.5 rounded-hoja border border-grafito-200 bg-papel px-3.5 py-3 text-[0.875rem] leading-relaxed text-grafito-600">
                {reporte.description}
              </dd>
            </div>
          ) : null}
        </dl>

        {/* Clasificación automática: maquinaria de uso interno */}
        {reporte.prediction ? (
          <section className="mt-6 rounded-hoja border border-grafito-200 bg-papel">
            <div className="flex items-center justify-between gap-3 border-b border-grafito-200 px-4 py-3">
              <p className="rotulo">Clasificación automática</p>
              <Confianza valor={reporte.prediction.confidence} />
            </div>

            <div className="px-4 py-4">
              <p className="text-[0.875rem] text-grafito-600">
                Propuesta:{' '}
                <span className="font-medium text-grafito-900">
                  {etiquetaLegible(reporte.prediction.predicted_class)}
                </span>
              </p>

              {reporte.prediction.confidence < 0.55 ? (
                <p className="mt-2.5">
                  <span className="inline-flex items-center gap-1.5 rounded-hoja border border-margen-600/30 bg-margen-100 px-2 py-0.5 font-mono text-[0.6875rem] uppercase tracking-[0.08em] text-margen-600">
                    <Icono nombre="atencion" className="size-3.5" />
                    Requiere revisión humana
                  </span>
                </p>
              ) : null}

              {errorFeedback ? (
                <div className="mt-3.5">
                  <Aviso tono="error">{errorFeedback}</Aviso>
                </div>
              ) : null}

              {feedbackListo ? (
                <div className="mt-3.5">
                  <Aviso tono="visto">
                    Corrección registrada. Queda disponible para el reentrenamiento.
                  </Aviso>
                </div>
              ) : (
                <div className="mt-4 border-t border-grafito-200 pt-4">
                  <p className="text-[0.8125rem] text-grafito-600">
                    ¿La clasificación es correcta?
                  </p>

                  {!modoCorreccion ? (
                    <div className="mt-2.5 flex flex-wrap gap-2.5">
                      <Boton
                        tono="contorno"
                        tamano="chico"
                        icono="visto"
                        cargando={enviandoFeedback}
                        onClick={() => mandarFeedback(true)}
                      >
                        Sí, es correcta
                      </Boton>
                      <Boton
                        tono="sello"
                        tamano="chico"
                        icono="lapiz"
                        onClick={() => setModoCorreccion(true)}
                      >
                        No, corregir
                      </Boton>
                    </div>
                  ) : (
                    <div className="mt-3">
                      <CampoSelect
                        etiqueta="Categoría correcta"
                        value={claseCorrecta}
                        onChange={(e) => setClaseCorrecta(e.target.value)}
                        opciones={[
                          { valor: '', texto: 'Elegí la categoría real…' },
                          ...CATEGORIAS.map((c) => ({
                            valor: c.name,
                            texto: `${c.label} · ${c.area}`,
                          })),
                        ]}
                      />
                      <div className="mt-3 flex flex-wrap gap-2.5">
                        <Boton
                          tamano="chico"
                          disabled={!claseCorrecta}
                          cargando={enviandoFeedback}
                          onClick={() => mandarFeedback(false)}
                        >
                          Guardar corrección
                        </Boton>
                        <Boton
                          tono="callado"
                          tamano="chico"
                          onClick={() => {
                            setModoCorreccion(false);
                            setClaseCorrecta('');
                          }}
                        >
                          Cancelar
                        </Boton>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </section>
        ) : null}

        {/* Gestión */}
        <section className="mt-6 border-t border-grafito-200 pt-5">
          <p className="rotulo mb-3">Gestión del reporte</p>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <CampoSelect
              etiqueta="Estado"
              value={estado}
              onChange={(e) => setEstado(e.target.value as Estado)}
              opciones={ESTADOS.map((s) => ({ valor: s, texto: ESTADO_LABEL[s] }))}
            />
            <CampoSelect
              etiqueta="Prioridad"
              value={prioridad}
              onChange={(e) => setPrioridad(e.target.value as Prioridad)}
              opciones={PRIORIDADES.map((p) => ({ valor: p, texto: PRIORIDAD_LABEL[p] }))}
            />
          </div>

          {errorGuardar ? (
            <div className="mt-4">
              <Aviso tono="error">{errorGuardar}</Aviso>
            </div>
          ) : null}

          <div className="mt-4 flex items-center gap-3">
            <Boton onClick={guardar} cargando={guardando} disabled={!hayCambios}>
              {guardado ? 'Guardado' : 'Guardar cambios'}
            </Boton>
            {guardado ? (
              <span className="inline-flex items-center gap-1.5 text-[0.8125rem] text-visto-700">
                <Icono nombre="visto" className="size-4" />
                Actualizado
              </span>
            ) : !hayCambios ? (
              <span className="text-[0.8125rem] text-grafito-500">Sin cambios por guardar.</span>
            ) : null}
          </div>
        </section>
      </div>
    </Dialogo>
  );
}
