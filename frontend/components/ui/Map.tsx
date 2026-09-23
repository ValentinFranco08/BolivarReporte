'use client';

import React, { useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, ZoomControl, Circle } from 'react-leaflet';
import L from 'leaflet';
import { urlDeImagen, type Reporte } from '@/lib/api';

/** Centro de San Carlos de Bolívar. */
const CENTRO_BOLIVAR: [number, number] = [-36.2312, -61.1136];

function getPetMarkerIcon(tipo?: string): L.DivIcon {
  const configs: Record<string, { bg: string; color: string; border: string; icon: string }> = {
    perdido: { bg: '#fffbeb', color: '#b45309', border: '#d97706', icon: '🔍' },
    encontrado: { bg: '#f2f8f4', color: '#2c6a49', border: '#3d7a58', icon: '🐾' },
    en_transito: { bg: '#fffbeb', color: '#b45309', border: '#d97706', icon: '🏡' },
    alerta_cebo: { bg: '#e11d48', color: '#ffffff', border: '#be123c', icon: '🚨' },
    adopcion: { bg: '#fff1f2', color: '#be123c', border: '#e11d48', icon: '❤️' },
  };

  const current = configs[tipo || 'perdido'] || configs.perdido;

  return L.divIcon({
    className: 'marcador-vecinal',
    html: `
      <div style="
        position: relative;
        width: 36px;
        height: 36px;
        background-color: ${current.bg};
        border: 2.5px solid ${current.border};
        border-radius: 9999px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        box-shadow: 0 4px 12px rgba(92, 60, 36, 0.2);
        cursor: pointer;
      ">
        <span>${current.icon}</span>
        <div style="
          position: absolute;
          bottom: -6px;
          left: 50%;
          transform: translateX(-50%);
          width: 0;
          height: 0;
          border-left: 5px solid transparent;
          border-right: 5px solid transparent;
          border-top: 6px solid ${current.border};
        "></div>
      </div>`,
    iconSize: [36, 42],
    iconAnchor: [18, 42],
    popupAnchor: [0, -42],
  });
}

interface MapProps {
  reports: Reporte[];
}

export default function Map({ reports }: MapProps) {
  const conCoords = useMemo(
    () => reports.filter((r) => r.latitude !== null && r.longitude !== null),
    [reports]
  );

  return (
    <MapContainer
      center={CENTRO_BOLIVAR}
      zoom={14}
      zoomControl={false}
      style={{ minHeight: '100vh', width: '100%', zIndex: 10 }}
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
      />
      <ZoomControl position="bottomright" />

      {conCoords.map((reporte) => {
        const foto = urlDeImagen(reporte.image_path);
        const tipo = reporte.report_type || 'perdido';
        const esAlertaCebo = tipo === 'alerta_cebo';
        const waPhone = reporte.contact_phone?.replace(/[^\d+]/g, '');

        return (
          <React.Fragment key={reporte.id}>
            {/* Si es alerta de cebo, trazamos el perímetro de advertencia en coral */}
            {esAlertaCebo && (
              <Circle
                center={[reporte.latitude!, reporte.longitude!]}
                radius={250}
                pathOptions={{
                  color: '#e11d48',
                  fillColor: '#e11d48',
                  fillOpacity: 0.15,
                  dashArray: '4, 8',
                  weight: 2,
                }}
              />
            )}

            <Marker
              position={[reporte.latitude!, reporte.longitude!]}
              icon={getPetMarkerIcon(tipo)}
            >
              <Popup className="popup-vecinal" maxWidth={280}>
                <div style={{ fontFamily: 'var(--font-sans)', padding: '2px' }}>
                  {foto && (
                    <div style={{ position: 'relative', width: '100%', height: '140px', borderRadius: '16px', overflow: 'hidden', marginBottom: '8px' }}>
                      <img
                        src={foto}
                        alt={reporte.pet_name || 'Mascota'}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      />
                    </div>
                  )}

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 'bold', color: esAlertaCebo ? '#e11d48' : '#d97736' }}>
                      {esAlertaCebo ? '⚠️ CEBO TÓXICO' : tipo === 'encontrado' ? '🛡️ ENCONTRADO' : '🔍 PERDIDO'}
                    </span>
                    <span style={{ fontSize: '11px', color: '#78655b' }}>
                      {new Date(reporte.created_at).toLocaleDateString('es-AR', { day: 'numeric', month: 'short' })}
                    </span>
                  </div>

                  <h4 style={{ margin: '0 0 4px 0', fontSize: '15px', fontWeight: 'bold', color: '#3a2a20' }}>
                    {reporte.pet_name || (esAlertaCebo ? 'Peligro en vía pública' : 'Mascota registrada')}
                  </h4>

                  {reporte.address && (
                    <p style={{ margin: '0 0 6px 0', fontSize: '12px', color: '#554339' }}>
                      📍 {reporte.address}
                    </p>
                  )}

                  {reporte.description && (
                    <p style={{ margin: '0 0 8px 0', fontSize: '11px', color: '#78655b', lineHeight: '1.4' }}>
                      {reporte.description}
                    </p>
                  )}

                  {waPhone ? (
                    <a
                      href={`https://wa.me/${waPhone}?text=${encodeURIComponent(
                        `Hola! Te escribo desde Bolívar Animal por la publicación de ${reporte.pet_name || 'la mascota'}.`
                      )}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'block',
                        textAlign: 'center',
                        backgroundColor: '#3d7a58',
                        color: '#ffffff',
                        padding: '8px 12px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        fontWeight: 'bold',
                        textDecoration: 'none',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                      }}
                    >
                      💬 Contactar por WhatsApp
                    </a>
                  ) : (
                    <span style={{ fontSize: '11px', color: '#78655b' }}>Sin teléfono registrado</span>
                  )}
                </div>
              </Popup>
            </Marker>
          </React.Fragment>
        );
      })}
    </MapContainer>
  );
}
