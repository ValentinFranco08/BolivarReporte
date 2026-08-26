'use client';

import React, { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ImageUploader } from '@/components/ui/ImageUploader';
import { FichaClasificacion } from '@/components/ui/FichaClasificacion';
import { Icono } from '@/components/ui/Icono';
import { Aviso, Boton, CampoArea, Compas } from '@/components/ui/primitivas';
import { NumeroParcela } from '@/components/ui/marcas';
import {
  ErrorAPI,
  analizar,
  crearReporte,
  direccionDesdeCoords,
  leerToken,
  type Reporte,
  type RespuestaPrediccion,
} from '@/lib/api';

type EstadoUbicacion = 'inicial' | 'buscando' | 'lista' | 'sin_permiso';

/**
 * Hoja de alta — el flujo del vecino.
 *
 * Una sola columna en el teléfono, un solo gesto por paso, y nada de jerga de
 * modelos: el vecino nunca ve confianza, top-3 ni nombres de arquitectura.
 */
export default function NuevoReporte() {
  const router = useRouter();

  const [archivo, setArchivo] = useState<File | null>(null);
  const [vistaPrevia, setVistaPrevia] = useState<string | null>(null);
  const [descripcion, setDescripcion] = useState('');
  const [resultado, setResultado] = useState<RespuestaPrediccion | null>(null);
  const [correccion, setCorreccion] = useState<string | null>(null);

  const [analizando, setAnalizando] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [registrado, setRegistrado] = useState<Reporte | null>(null);

  const [lat, setLat] = useState<number | null>(null);
  const [lng, setLng] = useState<number | null>(null);
  const [direccion, setDireccion] = useState<string | null>(null);
  // Arranca en 'buscando': el permiso se pide al montar, así el efecto no
  // necesita fijar estado de forma sincrónica.
  const [ubicacion, setUbicacion] = useState<EstadoUbicacion>('buscando');

  const urlCreada = useRef<string | null>(null);

  useEffect(() => {
    return () => {
      if (urlCreada.current) URL.revokeObjectURL(urlCreada.current);
    };
  }, []);

  /**
   * Consulta al GPS. La geolocalización es un sistema externo: el estado se
   * fija sólo dentro de los callbacks, así el efecto no encadena renders.
   */
  const consultarGps = React.useCallback(() => {
    if (!navigator.geolocation) {
      queueMicrotask(() => setUbicacion('sin_permiso'));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;
        setLat(latitude);
        setLng(longitude);
        setDireccion(await direccionDesdeCoords(latitude, longitude));
        setUbicacion('lista');
      },
      () => setUbicacion('sin_permiso'),
      { enableHighAccuracy: true, timeout: 8000 },
    );
  }, []);

  useEffect(() => {
    consultarGps();
  }, [consultarGps]);

  const reintentarUbicacion = () => {
    setUbicacion('buscando');
    consultarGps();
  };

  // Un solo gesto: elegir la foto dispara el análisis y despliega el resto.
  const alElegirFoto = async (file: File, url: string) => {
    if (urlCreada.current) URL.revokeObjectURL(urlCreada.current);
    urlCreada.current = url;

    setArchivo(file);
    setVistaPrevia(url);
    setResultado(null);
    setCorreccion(null);
    setError(null);
    await ejecutarAnalisis(file, descripcion);
  };

  const ejecutarAnalisis = async (file: File, texto: string) => {
    setAnalizando(true);
    setError(null);
    try {
      setResultado(await analizar(file, texto));
    } catch (e) {
      setError(
        e instanceof ErrorAPI
          ? e.message
          : 'No pudimos analizar la foto. Probá de nuevo en un momento.',
      );
    } finally {
      setAnalizando(false);
    }
  };

  const empezarDeNuevo = () => {
    if (urlCreada.current) URL.revokeObjectURL(urlCreada.current);
    urlCreada.current = null;
    setArchivo(null);
    setVistaPrevia(null);
    setDescripcion('');
    setResultado(null);
    setCorreccion(null);
    setError(null);
    setRegistrado(null);
  };

  const confirmar = async () => {
    if (!resultado) return;
    const token = leerToken();
    if (!token) {
      router.push('/login?volver=/reportes/nuevo');
      return;
    }

    setEnviando(true);
    setError(null);
    try {
      const creado = await crearReporte(token, {
        description: descripcion,
        image_path: resultado.image_path,
        predicted_class: resultado.predictions[0].label,
        confidence: resultado.predictions[0].score,
        corrected_class: correccion,
        latitude: lat,
        longitude: lng,
        address: direccion,
      });
      setRegistrado(creado);
    } catch (e) {
      if (e instanceof ErrorAPI && e.status === 401) {
        router.push('/login?volver=/reportes/nuevo');
        return;
      }
      setError(e instanceof ErrorAPI ? e.message : 'No pudimos registrar el reporte.');
    } finally {
      setEnviando(false);
    }
  };

  // ── Constancia ─────────────────────────────────────────────────────────────
  if (registrado) {
    return (
      <main className="mensura-mayor flex flex-1 items-center justify-center px-5 py-12">
        <div className="motion-safe:desplegar w-full max-w-lg rounded-hoja border border-grafito-200 bg-papel-alto shadow-[0_1px_2px_rgba(16,20,24,0.06),0_8px_20px_-6px_rgba(16,20,24,0.14)]">
          <div className="flex items-start justify-between gap-4 border-b border-grafito-200 px-6 py-5">
            <div>
              <p className="rotulo">Constancia de reporte</p>
              <p className="mt-1.5">
                <NumeroParcela id={registrado.id} tamano="grande" />
              </p>
            </div>
            <span className="motion-safe:sellar mt-1 inline-flex shrink-0 items-center gap-1.5 rounded-hoja border border-visto-600/40 bg-visto-100 px-2.5 py-1 font-mono text-[0.6875rem] uppercase tracking-[0.08em] text-visto-700">
              <Icono nombre="visto" className="size-3.5" />
              Registrado
            </span>
          </div>

          <div className="px-6 py-6">
            <h1 className="text-xl font-semibold tracking-[-0.01em] text-grafito-900">
              Quedó anotado en la hoja de reportes.
            </h1>
            <p className="mt-2.5 text-[0.9375rem] leading-relaxed text-grafito-600">
              El municipio lo va a revisar y puede cambiarle el estado. Anotate el número{' '}
              <span className="cifra font-semibold text-grafito-900">{registrado.id}</span> para
              seguirlo.
            </p>

            <dl className="mt-6 divide-y divide-grafito-200 border-y border-grafito-200">
              <FilaConstancia rotulo="Estado inicial" valor="Reportado" />
              {direccion ? <FilaConstancia rotulo="Ubicación" valor={direccion} /> : null}
              <FilaConstancia
                rotulo="Fecha"
                valor={new Date(registrado.created_at).toLocaleString('es-AR', {
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              />
            </dl>

            <div className="mt-7 flex flex-col gap-3 sm:flex-row">
              <Boton onClick={empezarDeNuevo} icono="camara" anchoCompleto>
                Reportar otra cosa
              </Boton>
              <Link
                href="/reportes"
                className="inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-hoja border border-tinta-200 bg-papel-alto px-5 text-[0.9375rem] font-medium text-tinta-700 transition-colors hover:border-tinta-300 hover:bg-tinta-50"
              >
                <Icono nombre="hoja" className="size-[1.125em]" />
                Ver todos los reportes
              </Link>
            </div>
          </div>
        </div>
      </main>
    );
  }

  // ── Alta ───────────────────────────────────────────────────────────────────
  return (
    <main className="mensura-mayor flex-1">
      <div className="mx-auto w-full max-w-[68rem] px-5 py-8 sm:px-8 sm:py-12">
        {/* Encabezado de hoja */}
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="inline-flex size-11 shrink-0 items-center justify-center rounded-hoja border border-grafito-200 bg-papel-alto text-grafito-600 transition-colors hover:border-tinta-300 hover:bg-tinta-50 hover:text-tinta-700"
          >
            <Icono nombre="flecha-izquierda" className="size-5" titulo="Volver al inicio" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-[-0.02em] text-grafito-900 sm:text-3xl">
              ¿Qué encontraste?
            </h1>
            <p className="mt-1 text-[0.9375rem] text-grafito-600">
              Una foto y una línea alcanzan.
            </p>
          </div>
        </div>

        {/* Ubicación: dato de hoja, arriba y siempre visible. */}
        <div className="mt-7">
          <BarraUbicacion
            estado={ubicacion}
            direccion={direccion}
            onReintentar={reintentarUbicacion}
          />
        </div>

        {error ? (
          <div className="mt-5">
            <Aviso tono="error">{error}</Aviso>
          </div>
        ) : null}

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2 lg:gap-8">
          {/* ── La lámina: la foto ─────────────────────────────────────── */}
          <div>
            {!vistaPrevia ? (
              <ImageUploader
                onImageSelected={alElegirFoto}
                onError={setError}
                isLoading={analizando}
              />
            ) : (
              <figure className="relative overflow-hidden rounded-hoja border border-grafito-200 bg-papel-alto p-2">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={vistaPrevia}
                  alt="Foto que vas a reportar"
                  className="aspect-square w-full rounded-[1px] object-cover"
                />
                <button
                  type="button"
                  onClick={empezarDeNuevo}
                  disabled={analizando || enviando}
                  className="absolute right-4 top-4 inline-flex min-h-10 items-center gap-1.5 rounded-hoja border border-grafito-200 bg-papel-alto px-3 text-[0.8125rem] font-medium text-grafito-600 transition-colors hover:bg-papel-alto disabled:opacity-50"
                >
                  <Icono nombre="cruz" className="size-4" />
                  Cambiar foto
                </button>
              </figure>
            )}
          </div>

          {/* ── El cajetín: descripción, clasificación y confirmación ─── */}
          <div className="flex flex-col gap-6">
            {vistaPrevia ? (
              <>
                <div className="rounded-hoja border border-grafito-200 bg-papel-alto px-5 py-5">
                  <CampoArea
                    etiqueta="Contanos algo más (opcional)"
                    ayuda="Una línea alcanza. Ayuda a clasificar mejor la situación."
                    rows={3}
                    placeholder="Ej: está hace una semana y ya se llevó dos ruedas."
                    value={descripcion}
                    onChange={(e) => setDescripcion(e.target.value)}
                    disabled={analizando || enviando}
                  />
                  {archivo && resultado ? (
                    <button
                      type="button"
                      onClick={() => ejecutarAnalisis(archivo, descripcion)}
                      disabled={analizando}
                      className="mt-3 text-[0.8125rem] text-tinta-700 underline decoration-tinta-200 hover:decoration-tinta-600 disabled:text-grafito-500"
                    >
                      Volver a clasificar con esta descripción
                    </button>
                  ) : null}
                </div>

                {analizando ? (
                  <div
                    role="status"
                    className="flex items-center gap-3 rounded-hoja border border-grafito-200 bg-papel-alto px-5 py-6 text-[0.9375rem] text-grafito-600"
                  >
                    <Compas className="text-tinta-600" />
                    Estamos mirando la foto…
                  </div>
                ) : null}

                {resultado && !analizando ? (
                  <div className="motion-safe:desplegar flex flex-col gap-6">
                    <FichaClasificacion
                      etiqueta={resultado.predictions[0].label}
                      correccion={correccion}
                      onCorregir={setCorreccion}
                    />

                    <div className="rounded-hoja border border-grafito-200 bg-papel-alto px-5 py-5">
                      <Boton
                        onClick={confirmar}
                        cargando={enviando}
                        tamano="grande"
                        anchoCompleto
                        icono={enviando ? undefined : 'visto'}
                      >
                        {enviando ? 'Registrando…' : 'Confirmar y enviar'}
                      </Boton>
                      <p className="mt-3.5 text-[0.75rem] leading-relaxed text-grafito-500">
                        La IA clasifica la situación a partir de la foto y el texto. No
                        determina una infracción legal; eso corresponde a la normativa
                        municipal.
                      </p>
                    </div>
                  </div>
                ) : null}
              </>
            ) : (
              /* Estado vacío: la hoja ya dibujada, esperando. */
              <div className="flex flex-col justify-center rounded-hoja border border-grafito-200 bg-papel-alto px-6 py-8">
                <p className="rotulo">Cómo sigue</p>
                <ol className="mt-4 space-y-4">
                  {[
                    'Elegís la foto y la clasificamos sola.',
                    'Si la categoría no es la correcta, la cambiás vos.',
                    'Confirmás y el reporte queda con número y estado.',
                  ].map((texto, i) => (
                    <li key={texto} className="flex gap-3.5">
                      <span className="cifra mt-px shrink-0 text-[0.8125rem] text-grafito-500">
                        {String(i + 1).padStart(2, '0')}
                      </span>
                      <span className="text-[0.9375rem] leading-relaxed text-grafito-600">
                        {texto}
                      </span>
                    </li>
                  ))}
                </ol>
                <p className="mt-6 border-t border-grafito-200 pt-4 text-[0.8125rem] leading-relaxed text-grafito-500">
                  No tenés que elegir entre 23 categorías: eso lo deduce el sistema.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}

function FilaConstancia({ rotulo, valor }: { rotulo: string; valor: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 py-3">
      <dt className="rotulo shrink-0">{rotulo}</dt>
      <dd className="text-right text-[0.875rem] text-grafito-900">{valor}</dd>
    </div>
  );
}

function BarraUbicacion({
  estado,
  direccion,
  onReintentar,
}: {
  estado: EstadoUbicacion;
  direccion: string | null;
  onReintentar: () => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-2 rounded-hoja border border-grafito-200 bg-papel-alto px-4 py-3">
      <span className="rotulo shrink-0">Ubicación</span>

      {estado === 'buscando' ? (
        <span className="flex items-center gap-2 text-[0.875rem] text-grafito-600">
          <Compas className="text-tinta-600" />
          Buscando dónde estás…
        </span>
      ) : null}

      {estado === 'lista' && direccion ? (
        <span className="flex min-w-0 items-center gap-2 text-[0.875rem] font-medium text-grafito-900">
          <Icono nombre="chincheta" className="size-4 shrink-0 text-tinta-600" />
          <span className="truncate">{direccion}</span>
        </span>
      ) : null}

      {estado === 'sin_permiso' ? (
        <>
          <span className="flex items-center gap-2 text-[0.875rem] text-grafito-600">
            <Icono nombre="atencion" className="size-4 shrink-0 text-margen-600" />
            Sin ubicación. El reporte se puede enviar igual.
          </span>
          <button
            type="button"
            onClick={onReintentar}
            className="text-[0.8125rem] text-tinta-700 underline decoration-tinta-200 hover:decoration-tinta-600"
          >
            Reintentar
          </button>
        </>
      ) : null}

      {estado === 'inicial' ? (
        <span className="text-[0.875rem] text-grafito-500">Activá el GPS para ubicarlo.</span>
      ) : null}
    </div>
  );
}
