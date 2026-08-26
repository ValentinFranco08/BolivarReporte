'use client';

import React, { useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, ZoomControl } from 'react-leaflet';
import L from 'leaflet';
import { urlDeImagen, type Reporte } from '@/lib/api';
import { etiquetaLegible, ESTADO_LABEL, type Prioridad } from '@/lib/taxonomy';

/** Centro de San Carlos de Bolívar. */
const CENTRO_BOLIVAR: [number, number] = [-36.2312, -61.1136];

/**
 * Chincheta de mensura dibujada a mano en SVG, en la tinta de la hoja.
 * Reemplaza el marcador azul por defecto de Leaflet, que venía además de un
 * CDN externo.
 */
const COLOR_POR_PRIORIDAD: Record<Prioridad, string> = {
  baja: '#6d6d64',
  media: '#1d4ea0',
  alta: '#8a6316',
  critica: '#c8402c',
};

function chincheta(prioridad: Prioridad): L.DivIcon {
  const color = COLOR_POR_PRIORIDAD[prioridad] ?? COLOR_POR_PRIORIDAD.media;
  return L.divIcon({
    className: 'chincheta-mensura',
    html: `
      <svg width="26" height="34" viewBox="0 0 26 34" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M13 33S24 21.5 24 13A11 11 0 1 0 2 13c0 8.5 11 20 11 20Z"
              fill="${color}" stroke="#f4f1e8" stroke-width="1.5"/>
        <circle cx="13" cy="13" r="4" fill="#f4f1e8"/>
      </svg>`,
    iconSize: [26, 34],
    iconAnchor: [13, 33],
    popupAnchor: [0, -30],
  });
}

interface MapProps {
  reports: Reporte[];
}

export default function Map({ reports }: MapProps) {
  const conCoords = useMemo(
    () => reports.filter((r) => r.latitude !== null && r.longitude !== null),
    [reports],
  );

  return (
    <MapContainer
      center={CENTRO_BOLIVAR}
      zoom={14}
      zoomControl={false}
      style={{ height: '100%', width: '100%' }}
    >
      {/* Teselas claras: la hoja se lee al sol. */}
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
      />
      <ZoomControl position="bottomright" />

      {conCoords.map((reporte) => {
        const foto = urlDeImagen(reporte.image_path);
        const categoria =
          reporte.category?.name ?? reporte.prediction?.predicted_class ?? null;

        return (
          <Marker
            key={reporte.id}
            position={[reporte.latitude!, reporte.longitude!]}
            icon={chincheta(reporte.priority)}
          >
            <Popup>
              <div className="w-60 font-sans">
                {foto ? (
                  /* eslint-disable-next-line @next/next/no-img-element */
                  <img
                    src={foto}
                    alt={`Situación reportada: ${etiquetaLegible(categoria)}`}
                    className="h-28 w-full object-cover"
                  />
                ) : null}
                <div className="px-3.5 py-3">
                  <div className="flex items-baseline justify-between gap-2">
                    <span className="cifra text-[0.75rem] text-grafito-500">
                      Nº {reporte.id}
                    </span>
                    <span className="font-mono text-[0.625rem] uppercase tracking-[0.08em] text-grafito-500">
                      {ESTADO_LABEL[reporte.status] ?? reporte.status}
                    </span>
                  </div>

                  <p className="mt-1 text-[0.9375rem] font-semibold leading-snug text-grafito-900">
                    {etiquetaLegible(categoria)}
                  </p>

                  {reporte.description ? (
                    <p className="mt-1.5 line-clamp-2 text-[0.8125rem] leading-relaxed text-grafito-600">
                      {reporte.description}
                    </p>
                  ) : null}

                  {reporte.address ? (
                    <p className="mt-2 truncate text-[0.75rem] text-grafito-500">
                      {reporte.address}
                    </p>
                  ) : null}
                </div>
              </div>
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
}
