'use client';

import React, { useEffect, useState } from 'react';
import {
  Reporte,
  PetMatchCandidate,
  obtenerMatchesMascota,
  resolverReporte,
  urlDeImagen,
} from '@/lib/api';
import { Icono } from '@/components/ui/Icono';

interface VisualMatchModalProps {
  reporte: Reporte | null;
  onClose: () => void;
  token?: string | null;
}

export function VisualMatchModal({ reporte, onClose, token }: VisualMatchModalProps) {
  const [cargando, setCargando] = useState(true);
  const [matches, setMatches] = useState<PetMatchCandidate[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [resolviendo, setResolviendo] = useState(false);
  const [resueltoExito, setResueltoExito] = useState(false);
  const [indiceActual, setIndiceActual] = useState(0);

  useEffect(() => {
    if (!reporte) return;
    obtenerMatchesMascota(reporte.id)
      .then((res) => {
        setMatches(res.matches || []);
      })
      .catch((err) => {
        setError(err.message || 'No pudimos calcular las coincidencias visuales.');
      })
      .finally(() => {
        setCargando(false);
      });
  }, [reporte]);

  if (!reporte) return null;

  const handleResolver = async (matchReportId: number) => {
    if (!token) {
      alert('Iniciá sesión para confirmar la recuperación de la mascota en Bolívar Animal.');
      return;
    }
    setResolviendo(true);
    try {
      await resolverReporte(token, reporte.id);
      await resolverReporte(token, matchReportId);
      setResueltoExito(true);
    } catch (e) {
      alert('Error al actualizar el estado: ' + (e as Error).message);
    } finally {
      setResolviendo(false);
    }
  };

  const imgTuReporte = urlDeImagen(reporte.image_path) || '/favicon.ico';
  const candidatoActual = matches[indiceActual];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-corteza/60 backdrop-blur-xs animate-in fade-in duration-150">
      <div role="dialog" aria-modal="true" aria-labelledby="titulo-cotejo" className="relative flex max-h-[92vh] w-full max-w-2xl flex-col overflow-hidden border border-borde-fuerte bg-lino-alto shadow-warm-elevated">
        {/* ── 1. Cabecera Vecinal ── */}
        <div className="flex items-center justify-between border-b border-borde-fuerte px-5 py-4 bg-lino">
          <div className="flex items-center gap-3">
            <div className="grid size-9 place-items-center border border-terracota bg-terracota-50 text-terracota">
              <Icono nombre="mira" className="size-4.5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <p className="rotulo">Cotejo visual</p>
                <h2 id="titulo-cotejo" className="text-base font-extrabold tracking-[-.03em] text-corteza sm:text-lg">
                  Posible coincidencia
                </h2>
                {matches.length > 0 && (
                  <span className="estado-sello bg-salvia-50 border border-salvia-200 px-2 py-0.5 font-bold text-salvia-700">
                    Candidato {indiceActual + 1} de {matches.length}
                  </span>
                )}
              </div>
              <p className="text-xs text-corteza-suave">
                Compará las fotos, la zona y los datos antes de contactar.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Cerrar comparador"
            className="grid size-8 place-items-center border border-borde-fuerte bg-lino-alto text-corteza-suave hover:bg-lino-medio hover:text-corteza"
          >
            <Icono nombre="cruz" className="size-4" />
          </button>
        </div>

        {/* ── 2. Cuerpo Desplazable ── */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
          {/* Alerta de éxito */}
          {resueltoExito && (
            <div className="rounded-2xl border border-salvia-200 bg-salvia-50 p-4 text-center">
              <span className="text-sm font-bold text-salvia-700 block">
                Recuperación confirmada
              </span>
              <p className="mt-1 text-xs text-corteza-suave">
                Ambas publicaciones quedaron marcadas como resueltas en Bolívar Animal.
              </p>
            </div>
          )}

          {/* Estado de Carga */}
          {cargando && (
            <div className="flex flex-col items-center justify-center py-16 space-y-3">
              <div className="flex size-10 items-center justify-center border border-terracota-200 bg-terracota-50">
                <Icono nombre="pata" className="size-5 text-terracota" />
              </div>
              <p className="text-xs font-semibold text-corteza-suave">
                Analizando patrones visuales y buscando vecinos en Bolívar...
              </p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="rounded-2xl border border-coral-200 bg-coral-50 p-4 text-xs text-coral text-center">
              {error}
            </div>
          )}

          {/* Sin coincidencias */}
          {!cargando && !error && matches.length === 0 && (
            <div className="rounded-3xl border border-borde-calido bg-lino-suave p-8 text-center space-y-2">
              <div className="mx-auto size-10 rounded-full bg-white flex items-center justify-center">
                <Icono nombre="mira" className="size-5 text-corteza-clara" />
              </div>
              <h3 className="font-serif text-base font-bold text-corteza">
                No encontramos coincidencias cercanas todavía
              </h3>
              <p className="text-xs max-w-sm mx-auto leading-relaxed text-corteza-suave">
                Tu publicación permanece activa en la red de Bolívar. Si un vecino publica una foto
                con rasgos similares a tu mascota, te avisaremos al instante.
              </p>
            </div>
          )}

          {/* ── Visual Match Side-by-Side (Stitch Screen 2) ── */}
          {!cargando && candidatoActual && (
            <div className="space-y-4">
              {/* Fotos Comparadas Lado a Lado */}
              <div className="grid grid-cols-2 gap-3 border border-borde-fuerte bg-lino p-3 sm:gap-4 sm:p-4">
                {/* Tu Reporte */}
                <div className="flex flex-col gap-1.5">
                    <span className="rotulo !text-corteza">
                    Tu publicación
                  </span>
                  <div className="relative aspect-square w-full overflow-hidden border border-borde-fuerte bg-white">
                    <img
                      src={imgTuReporte}
                      alt="Tu mascota"
                      className="size-full object-cover"
                    />
                    <div className="absolute bottom-2 left-2 bg-corteza/80 text-white px-2 py-0.5 rounded-lg text-[10px] truncate max-w-[90%]">
                      {reporte.address || 'Bolívar'}
                    </div>
                  </div>
                  <span className="text-xs font-bold text-corteza truncate">
                    {reporte.pet_name || 'Tu mascota'}
                  </span>
                </div>

                {/* Candidato Encontrado */}
                <div className="flex flex-col gap-1.5">
                  <div className="flex items-center justify-between">
                    <span className="rotulo !text-salvia-700">
                      Candidato encontrado
                    </span>
                    <span className="text-[11px] font-bold text-terracota">
                      {Math.round(candidatoActual.visual_similarity * 100)}% similitud
                    </span>
                  </div>
                  <div className="relative aspect-square w-full overflow-hidden border border-salvia-200 bg-white">
                    <img
                      src={urlDeImagen(candidatoActual.report.image_path) || '/favicon.ico'}
                      alt="Candidato encontrado"
                      className="size-full object-cover"
                    />
                    <div className="absolute bottom-2 left-2 bg-salvia-700/90 text-white px-2 py-0.5 rounded-lg text-[10px] truncate max-w-[90%]">
                      {candidatoActual.report.address || 'Bolívar'}
                    </div>
                  </div>
                  <span className="text-xs font-bold text-corteza truncate">
                    {candidatoActual.report.pet_name || 'En resguardo temporal'}
                  </span>
                </div>
              </div>

              {/* Barra de Afinidad Visual y Multimodal */}
              <div className="space-y-2 border-y border-borde-fuerte py-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-corteza">
                    Afinidad multimodal (ViT Auto-Crop + Rasgos)
                  </span>
                  <span className="estado-sello bg-terracota-50 border border-terracota-200 px-2.5 py-0.5 font-bold text-terracota">
                    {Math.round(candidatoActual.combined_score * 100)}% Match global
                  </span>
                </div>
                <div className="h-2 w-full overflow-hidden bg-lino-suave">
                  <div
                    className="h-full bg-terracota transition-[width] duration-300"
                    style={{
                      width: `${Math.round(candidatoActual.combined_score * 100)}%`,
                    }}
                  />
                </div>
                
                {/* Desglose de factores */}
                <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px]">
                  <span className="rounded bg-white border border-borde-suave px-2 py-0.5 text-corteza font-medium">
                    👁️ Similitud visual: <strong>{Math.round(candidatoActual.visual_similarity * 100)}%</strong>
                  </span>
                  {candidatoActual.semantic_similarity !== undefined && (
                    <span className="rounded bg-white border border-borde-suave px-2 py-0.5 text-salvia-700 font-medium">
                      🐾 Rasgos y pelaje: <strong>{Math.round(candidatoActual.semantic_similarity * 100)}%</strong>
                    </span>
                  )}
                  <span className="rounded bg-white border border-borde-suave px-2 py-0.5 text-corteza-suave">
                    📍 Distancia: <strong>{candidatoActual.distance_km} km</strong>
                  </span>
                </div>
                
                <p className="text-xs text-corteza-suave leading-relaxed pt-1">
                  Ubicación: a <strong>{candidatoActual.distance_km} km</strong> de donde se reportó
                  ({candidatoActual.report.address || 'Bolívar'}).
                </p>
              </div>

              {/* Botonera de Acción Directa */}
              <div className="space-y-2 pt-1">
                {candidatoActual.report.contact_phone && (
                  <a
                    href={`https://wa.me/${candidatoActual.report.contact_phone.replace(
                      /[^\d+]/g,
                      ''
                    )}?text=${encodeURIComponent(
                      `Hola! Vi tu publicación en Bolívar Animal y el comparador detectó coincidencia con mi mascota (${Math.round(
                        candidatoActual.visual_similarity * 100
                      )}% match). ¿Podemos hablar?`
                    )}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex w-full items-center justify-center gap-2 border border-salvia bg-salvia px-4 py-3 text-sm font-bold text-white hover:bg-salvia-600"
                  >
                    <Icono nombre="telefono" className="size-4" />
                    <span>Contactar por WhatsApp</span>
                  </a>
                )}

                <div className="flex items-center gap-2">
                  {matches.length > 1 && (
                    <button
                      type="button"
                      onClick={() =>
                        setIndiceActual((prev) => (prev + 1) % matches.length)
                      }
                      className="flex-1 py-2.5 px-3 rounded-2xl bg-white border border-borde-calido text-corteza font-semibold text-xs hover:bg-lino-suave transition-colors"
                    >
                      Ver siguiente candidato ({indiceActual + 1} de {matches.length}) →
                    </button>
                  )}

                  <button
                    type="button"
                    disabled={resolviendo || resueltoExito}
                    onClick={() => handleResolver(candidatoActual.report.id)}
                    className="py-2.5 px-4 rounded-2xl bg-terracota-50 border border-terracota-200 text-terracota font-bold text-xs hover:bg-terracota hover:text-white transition-colors"
                  >
                    Confirmar Recuperación de la Mascota
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ── 3. Pie del Modal ── */}
        <div className="border-t border-borde-calido bg-lino-suave/80 px-5 py-3 flex items-center justify-between text-xs text-corteza-clara">
          <span>San Carlos de Bolívar · Red Vecinal</span>
          <button
            onClick={onClose}
            className="font-bold text-corteza hover:text-terracota transition-colors"
          >
            Cerrar comparador
          </button>
        </div>
      </div>
    </div>
  );
}
