'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Icono } from '@/components/ui/Icono';
import { QRCodeSVG } from 'qrcode.react';
import { API_URL, type EventoSaludRemum, type RegistroRemum } from '@/lib/api';

interface Padrino {
  nombre: string;
  tarea: string;
  icono: string;
}

export default function RemumPage() {
  const params = useParams();
  const qrId = params?.id as string;
  const [remumData, setRemumData] = useState<RegistroRemum | null>(null);
  const [cargando, setCargando] = useState(true);

  const [modalAlertaAbierto, setModalAlertaAbierto] = useState(false);
  const [estadoMascota, setEstadoMascota] = useState<'a_salvo' | 'extraviado'>('a_salvo');
  const [padrinos, setPadrinos] = useState<Padrino[]>([]);
  const [eventosSalud, setEventosSalud] = useState<EventoSaludRemum[]>([]);
  const [sumadoPadrino, setSumadoPadrino] = useState(false);
  const [copiadoLink, setCopiadoLink] = useState(false);
  const [nuevaVacunaTitulo, setNuevaVacunaTitulo] = useState('');
  const [nuevaVacunaDetalle, setNuevaVacunaDetalle] = useState('');

  useEffect(() => {
    if (!qrId) return;
    fetch(`${API_URL}/api/remum/${qrId}`)
      .then(res => res.json())
      .then(data => {
        const registro = data as RegistroRemum;
        setRemumData(registro);
        setEstadoMascota(data.status);
        if (registro.godparents) {
          setPadrinos(registro.godparents.map((g) => ({ nombre: g.name, tarea: g.task, icono: 'pata' })));
        }
        if (registro.health_events) {
          setEventosSalud(registro.health_events as EventoSaludRemum[]);
        }
        setCargando(false);
      })
      .catch(err => {
        console.error(err);
        setCargando(false);
      });
  }, [qrId]);

  const activarAlertaExtravio = async () => {
    try {
      const token = localStorage.getItem('token');
      let url = `${API_URL}/api/remum/${qrId}/alerta`;
      
      // Intentar anexar coordenadas para que aparezca en el mapa
      try {
        const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 });
        });
        url += `?lat=${pos.coords.latitude}&lng=${pos.coords.longitude}`;
      } catch (err) {
        console.warn("No se pudo obtener GPS para la alerta, se enviará sin coordenadas.", err);
      }

      await fetch(url, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setEstadoMascota('extraviado');
      setModalAlertaAbierto(false);
    } catch (e) {
      console.error(e);
    }
  };

  const cancelarAlertaExtravio = () => {
    // TODO: endpoint para resolver alerta
    setEstadoMascota('a_salvo');
  };

  const handleSumarsePadrino = async () => {
    if (!sumadoPadrino) {
      try {
        const token = localStorage.getItem('token');
        const payload = {
          name: 'Vos (Vecino Voluntario)',
          task: 'Paseo y seguimiento vecinal'
        };
        const res = await fetch(`http://localhost:8001/api/remum/${qrId}/padrinos`, {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          setPadrinos((prev) => [...prev, { nombre: payload.name, tarea: payload.task, icono: '🐾' }]);
          setSumadoPadrino(true);
        }
      } catch(e) {
        console.error(e);
      }
    }
  };

  const agregarEventoSalud = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const payload = {
        title: nuevaVacunaTitulo,
        description: nuevaVacunaDetalle,
        event_date: new Date().toISOString()
      };
      const res = await fetch(`http://localhost:8001/api/remum/${qrId}/salud`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        setEventosSalud([data, ...eventosSalud]);
        setNuevaVacunaTitulo('');
        setNuevaVacunaDetalle('');
      }
    } catch(e) {
      console.error(e);
    }
  };

  const handleCopiarEnlace = () => {
    if (typeof window !== 'undefined') {
      navigator.clipboard.writeText(window.location.origin + `/qr/${qrId}`);
      setCopiadoLink(true);
      setTimeout(() => setCopiadoLink(false), 3000);
    }
  };

  if (cargando) {
    return <div className="min-h-screen grid place-items-center bg-lino"><div className="animate-pulse font-bold text-corteza">Cargando Credencial...</div></div>;
  }

  if (!remumData || remumData.detail) {
    return <div className="min-h-screen grid place-items-center bg-lino"><div className="font-bold text-coral">Credencial no encontrada.</div></div>;
  }

  return (
    <div className="min-h-screen pb-28">
      {/* Barra Superior Cívica */}
      <div className="sticky top-16 z-30 border-b border-borde-calido bg-lino/95 backdrop-blur-md px-4 py-3 shadow-xs">
        <div className="mx-auto flex max-w-xl items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="grid size-9 place-items-center rounded-full text-corteza-suave hover:bg-lino-suave active:scale-95 transition-all"
              aria-label="Volver a la cartelera"
            >
              <Icono nombre="flecha-izquierda" className="size-5" />
            </Link>
            <div>
              <div className="inline-flex items-center gap-1.5 rounded-full bg-lino-suave border border-borde-calido px-2 py-0.5 text-[11px] font-bold text-terracota">
                <Icono nombre="escudo" className="size-3 text-terracota" />
                <span>MUNICIPIO DE BOLÍVAR · REMUM</span>
              </div>
              <h1 className="font-serif text-lg font-bold text-corteza leading-tight">
                Credencial y Libreta Sanitaria
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={handleCopiarEnlace}
              title="Copiar enlace de credencial pública"
              className="grid size-9 place-items-center rounded-full text-corteza-suave hover:bg-lino-suave active:scale-95 transition-all"
            >
              <Icono nombre="compartir" className="size-4" />
            </button>
            <Link
              href="/sos"
              title="Urgencias y veterinarias de turno"
              className="grid size-9 place-items-center rounded-full text-coral hover:bg-coral-50 active:scale-95 transition-all"
            >
              <Icono nombre="atencion" className="size-4" />
            </Link>
          </div>
        </div>
      </div>

      <main className="mx-auto max-w-xl px-4 pt-4 space-y-5">
        {/* Banner de Copiado Exitoso */}
        {copiadoLink && (
          <div className="rounded-xl border border-salvia-200 bg-salvia-50 px-3.5 py-2.5 text-xs font-semibold text-salvia-700 shadow-xs flex items-center justify-between animate-fadeIn">
            <span className="flex items-center gap-2">
              <Icono nombre="visto" className="size-4 text-salvia" />
              ¡Enlace de chapita copiado al portapapeles!
            </span>
            <span className="text-[10px] text-salvia-600">Listo para compartir</span>
          </div>
        )}

        {/* Subtítulo & Estado de Vigencia Municipal */}
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center space-x-2">
            <span className="size-2.5 rounded-full bg-salvia animate-pulse" />
            <p className="text-xs font-medium text-corteza-suave">
              Libreta Sanitaria Digital Verificada
            </p>
          </div>
          <span className="text-[11px] font-bold text-salvia px-2.5 py-0.5 rounded-full bg-salvia-50 border border-salvia-200">
            Válida 2026/2027
          </span>
        </div>

        {/* ═══════════════════════════════════════════════════════════════════
            PASAPORTE CÍVICO: TARJETA OFICIAL REMUM
            ═══════════════════════════════════════════════════════════════════ */}
        <section className="relative rounded-3xl border border-borde-calido bg-white shadow-passport overflow-hidden">
          {/* Tira Oficial Superior */}
          <div className="bg-gradient-to-r from-terracota to-terracota-600 px-4 py-3 text-white flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Icono nombre="pata" className="size-4 text-white" />
              <span className="font-mono text-xs font-bold tracking-wider uppercase">
                REMUM · {remumData.qr_code_id}
              </span>
            </div>
            <div className="flex items-center space-x-1 text-[11px] font-bold bg-white/20 px-2 py-0.5 rounded-md backdrop-blur-xs">
              <Icono nombre="escudo" className="size-3 text-white" />
              <span>OFICIAL</span>
            </div>
          </div>

          {/* Grilla de Identidad: Foto y Metadatos */}
          <div className="p-4 sm:p-5 pb-3">
            <div className="flex gap-4 items-start">
              {/* Marco Fotográfico con Sello de Verificación */}
              <div className="relative shrink-0 w-28 h-36 rounded-2xl overflow-hidden border-2 border-borde-calido bg-lino-suave shadow-xs">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={remumData.image_path ? `http://localhost:8001${remumData.image_path}` : 'https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=600&auto=format&fit=crop'}
                  alt={remumData.pet_name}
                  className="w-full h-full object-cover object-center"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src =
                      'https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=600&auto=format&fit=crop';
                  }}
                />
                <div className="absolute bottom-0 inset-x-0 bg-corteza/90 text-white text-center py-0.5 text-[10px] font-bold font-mono tracking-widest uppercase truncate px-1">
                  {remumData.pet_name}
                </div>
                <div className="absolute top-1.5 left-1.5 bg-white/95 rounded-full p-1 shadow-xs">
                  <Icono nombre="visto" className="size-3.5 text-salvia" />
                </div>
              </div>

              {/* Información de la Mascota */}
              <div className="flex-1 min-w-0 space-y-2">
                <div>
                  <div className="flex items-baseline justify-between">
                    <h2 className="font-serif text-2xl font-bold text-corteza leading-none truncate pr-2">
                      {remumData.pet_name}
                    </h2>
                    <span className="text-[11px] bg-terracota-50 text-terracota border border-terracota-200 px-2 py-0.5 rounded-full font-bold uppercase shrink-0">
                      {remumData.pet_type}
                    </span>
                  </div>
                  <p className="text-xs text-corteza-suave font-medium mt-0.5 capitalize">
                    {remumData.pet_breed || 'Sin raza'} · {remumData.color_description || 'Color n/a'}
                  </p>
                </div>

                {/* Pastillas de Información Vecinal */}
                <div className="space-y-1.5 pt-1 text-xs">
                  <div className="flex items-center gap-2 bg-lino-suave/80 px-2.5 py-1.5 rounded-xl border border-borde-calido/70">
                    <span className="font-mono text-[11px] font-bold text-corteza truncate">
                      🔖 Chip: {remumData.chip_number || 'Sin chip asociado'}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 bg-lino-suave/80 px-2.5 py-1.5 rounded-xl border border-borde-calido/70">
                    <Icono nombre="chincheta" className="size-3.5 text-terracota shrink-0" />
                    <span className="text-[11px] text-corteza font-medium truncate">
                      {remumData.address || 'Bolívar'}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 bg-lino-suave/80 px-2.5 py-1.5 rounded-xl border border-borde-calido/70">
                    <Icono nombre="credencial" className="size-3.5 text-terracota shrink-0" />
                    <span className="text-[11px] text-corteza font-medium truncate">
                      Tutor Registrado #{remumData.user_id}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Estado de Seguridad & Botón de Emergencia */}
            <div className="mt-4 pt-3 border-t border-borde-calido/80">
              {estadoMascota === 'a_salvo' ? (
                <div className="flex items-center justify-between bg-salvia-50/70 px-3.5 py-2.5 rounded-xl border border-salvia-200">
                  <div className="flex items-center space-x-2">
                    <span className="size-3 rounded-full bg-salvia flex items-center justify-center ring-4 ring-salvia/20">
                      <span className="size-1.5 rounded-full bg-white" />
                    </span>
                    <span className="text-xs font-bold text-salvia-700">
                      En Casa con su Familia
                    </span>
                  </div>
                  <span className="text-[10px] text-salvia-600 font-medium">Actualizado hoy</span>
                </div>
              ) : (
                <div className="flex items-center justify-between bg-coral-50 px-3.5 py-2.5 rounded-xl border border-coral-200">
                  <div className="flex items-center space-x-2">
                    <span className="size-3 rounded-full bg-coral flex items-center justify-center ring-4 ring-coral/20 animate-pulse">
                      <span className="size-1.5 rounded-full bg-white" />
                    </span>
                    <span className="text-xs font-bold text-coral">
                      ⚠️ ¡Alerta Vecinal e IA Activa!
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={cancelarAlertaExtravio}
                    className="text-[11px] font-bold text-salvia underline hover:text-salvia-700"
                  >
                    Ya volvió a casa
                  </button>
                </div>
              )}

              {/* Botón Pánico para Mascota Perdida */}
              {estadoMascota === 'a_salvo' ? (
                <button
                  type="button"
                  onClick={() => setModalAlertaAbierto(true)}
                  className="mt-2.5 w-full bg-coral-50 hover:bg-coral-100 text-coral border border-coral-200 hover:border-coral-300 active:scale-[0.99] transition-all rounded-xl py-2.5 px-3 flex items-center justify-center space-x-2 text-xs font-bold shadow-xs"
                >
                  <Icono nombre="atencion" className="size-4 text-coral animate-pulse" />
                  <span>¡Se me perdió! Activar alerta vecinal e IA</span>
                </button>
              ) : (
                <div className="mt-2 p-2.5 rounded-xl bg-coral-50/50 border border-coral-100 text-[11px] text-coral leading-tight text-center">
                  La foto biométrica de {remumData.pet_name} se está cotejando automáticamente con cada reporte en Bolívar.
                </div>
              )}
            </div>
          </div>

          {/* Efecto Troquelado / Perforación de Boleto */}
          <div className="relative h-4 bg-lino flex items-center justify-center">
            <div className="w-full border-b-2 border-dashed border-borde-calido" />
            <div className="absolute -left-3 size-6 rounded-full bg-lino border-r border-borde-calido" />
            <div className="absolute -right-3 size-6 rounded-full bg-lino border-l border-borde-calido" />
          </div>

          {/* ─────────────────────────────────────────────────────────────
              SECCIÓN QR DINÁMICO & RECUPERACIÓN VECINAL
              ───────────────────────────────────────────────────────────── */}
          <div className="p-4 sm:p-5 bg-lino-suave/40">
            <div className="flex items-center gap-4">
              {/* Código QR SVG Táctil de Alto Contraste */}
              <div className="relative p-2 bg-white rounded-2xl border border-borde-calido shadow-xs shrink-0 flex flex-col items-center justify-center">
                <QRCodeSVG
                  value={`http://localhost:3000/qr/${qrId}`}
                  size={80}
                  level="Q"
                  fgColor="#3A2A20"
                  bgColor="#FFFFFF"
                />
                <span className="text-[9px] font-mono font-bold text-corteza-suave mt-1.5 uppercase">
                  {remumData.qr_code_id}
                </span>
              </div>

              <div className="space-y-1.5 flex-1">
                <div className="flex items-center space-x-1.5 text-terracota">
                  <Icono nombre="qr" className="size-4" />
                  <h3 className="font-serif text-sm font-bold text-corteza">
                    Escaneo público en Bolívar
                  </h3>
                </div>
                <p className="text-[12px] leading-snug text-corteza-suave">
                  Cualquier vecino que escanee la chapita del collar verá tu contacto directo y centro de auxilio.
                </p>

                <div className="flex flex-wrap gap-2 pt-1">
                  <button
                    type="button"
                    onClick={() => {
                      alert('Descargando archivo vectorial oficial para impresión de chapita de collar...');
                    }}
                    className="inline-flex items-center gap-1.5 text-[11px] font-bold text-terracota bg-terracota-50 hover:bg-terracota-100 px-3 py-1.5 rounded-xl border border-terracota-200 transition-colors"
                  >
                    <Icono nombre="impresora" className="size-3.5" />
                    <span>Descargar para chapita</span>
                  </button>

                  <Link
                    href="/qr/bol-0042"
                    className="inline-flex items-center gap-1 text-[11px] font-bold text-corteza-suave bg-white hover:bg-lino px-2.5 py-1.5 rounded-xl border border-borde-calido transition-colors"
                  >
                    <span>Ver qué ve el vecino</span>
                    <Icono nombre="flecha-derecha" className="size-3" />
                  </Link>
                </div>
              </div>
            </div>
            <p className="mt-2.5 text-[10px] text-center text-corteza-clara italic">
              * Aceptado e imprimible en ferreterías y veterinarias adheridas de Bolívar
            </p>
          </div>

          {/* ─────────────────────────────────────────────────────────────
              LIBRETA SANITARIA DIGITAL (SEMÁFORO ZOONOSIS)
              ───────────────────────────────────────────────────────────── */}
          <div className="p-4 sm:p-5 border-t border-borde-calido bg-white">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Icono nombre="escudo" className="size-4 text-salvia" />
                <h3 className="font-serif text-sm font-bold text-corteza">
                  Semáforo Sanitario y Zoonosis
                </h3>
              </div>
              <span className="text-[10px] text-salvia font-bold bg-salvia-50 border border-salvia-200 px-2 py-0.5 rounded-full">
                100% REGULAR
              </span>
            </div>

            <div className="space-y-2.5">
              {eventosSalud.map((ev, i) => (
                <div key={i} className="flex items-start justify-between p-2.5 rounded-xl bg-lino-suave/50 border border-borde-calido">
                  <div className="flex items-start space-x-2.5">
                    <span className="mt-0.5 size-5 rounded-full bg-salvia-100 flex items-center justify-center text-salvia">
                      <Icono nombre="visto" className="size-3 text-salvia font-bold" />
                    </span>
                    <div>
                      <p className="text-xs font-bold text-corteza flex items-center gap-1.5">
                        {ev.title}
                      </p>
                      <p className="text-[11px] text-corteza-suave">
                        {ev.description || 'Sin detalle'} · {new Date(ev.event_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}

              {/* Formulario Inline para Libreta */}
              <form onSubmit={agregarEventoSalud} className="mt-4 p-3 border border-dashed border-borde-calido rounded-xl bg-white space-y-2">
                <p className="text-xs font-bold text-corteza">Añadir Nuevo Evento</p>
                <input 
                  value={nuevaVacunaTitulo} 
                  onChange={(e)=>setNuevaVacunaTitulo(e.target.value)}
                  placeholder="Ej. Vacuna Antirrábica" 
                  className="w-full bg-lino-suave border border-borde-calido rounded-lg px-3 py-1.5 text-xs outline-none" required
                />
                <input 
                  value={nuevaVacunaDetalle} 
                  onChange={(e)=>setNuevaVacunaDetalle(e.target.value)}
                  placeholder="Detalles (clínica, lote, etc.)" 
                  className="w-full bg-lino-suave border border-borde-calido rounded-lg px-3 py-1.5 text-xs outline-none"
                />
                <button type="submit" className="w-full bg-terracota text-white text-xs font-bold py-1.5 rounded-lg hover:bg-terracota-600 transition-colors">
                  Añadir a Libreta
                </button>
              </form>
            </div>

            {/* Beneficio Fiscal Municipal */}
            <div className="mt-3.5 p-3 rounded-2xl bg-terracota-50 border border-terracota-200/70 flex items-center space-x-3">
              <span className="grid size-8 place-items-center rounded-xl bg-terracota text-white shrink-0 text-sm">
                ⭐
              </span>
              <div>
                <p className="text-xs font-bold text-corteza">
                  Beneficio Municipal: Contribuyente Ejemplar
                </p>
                <p className="text-[11px] text-corteza-suave">
                  15% de descuento en tasa de ABL anual (Ordenanza REMUM 241/24).
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════════════
            ANIMALES COMUNITARIOS & PADRINAZGO VECINAL
            ═══════════════════════════════════════════════════════════════════ */}
        <section className="space-y-3 pt-2">
          <div className="flex items-center justify-between px-1">
            <div>
              <h3 className="font-serif text-lg font-bold text-corteza">
                Animales de la Vecindad
              </h3>
              <p className="text-xs text-corteza-suave">
                Padrinazgo colectivo en San Carlos de Bolívar
              </p>
            </div>
            <Link
              href="/mapa"
              className="text-terracota text-xs font-bold hover:underline flex items-center gap-0.5"
            >
              <span>Ver mapa</span>
              <Icono nombre="flecha-derecha" className="size-3" />
            </Link>
          </div>

          {/* Ficha Comunitaria: Barbincho */}
          <article className="rounded-2xl border border-borde-calido bg-white p-4 shadow-warm-card space-y-3">
            <div className="flex gap-3.5">
              <div className="relative size-24 rounded-2xl overflow-hidden shrink-0 bg-lino-suave border border-borde-calido">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src="http://localhost:8001/uploads/demo_parque.jpg"
                  alt="Barbincho perro comunitario de la Plaza Alsina"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src =
                      'https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=600&auto=format&fit=crop';
                  }}
                />
                <span className="absolute bottom-1 left-1 bg-corteza/80 text-[9px] font-bold text-white px-1.5 py-0.5 rounded backdrop-blur-xs">
                  Plaza Alsina
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] text-salvia font-bold tracking-wide uppercase px-2 py-0.5 rounded-md bg-salvia-50 border border-salvia-200">
                      🐕 Perro Comunitario
                    </span>
                    <h4 className="font-serif text-lg font-bold text-corteza mt-1">Barbincho</h4>
                  </div>
                  <span
                    className="size-3 rounded-full bg-emerald-500 ring-4 ring-emerald-100"
                    title="Cuidado comunitario activo"
                  />
                </div>
                <p className="text-[12px] text-corteza-suave mt-1 line-clamp-2">
                  Habitante noble. Tiene casita comunitaria y vecinos que lo asisten diariamente.
                </p>
              </div>
            </div>

            {/* Red Activa de Padrinos */}
            <div className="bg-lino-suave/60 rounded-xl p-3 border border-borde-calido/70 space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-corteza">
                <span className="flex items-center gap-1.5">
                  <Icono nombre="corazon" className="size-3.5 text-coral" />
                  Red Activa de Cuidados
                </span>
                <span className="text-salvia font-bold">
                  {padrinos.length} vecinos activos
                </span>
              </div>

              <div className="text-xs text-corteza-suave space-y-1.5 divide-y divide-borde-calido/40">
                {padrinos.map((p, idx) => (
                  <div key={idx} className="flex items-center justify-between pt-1 first:pt-0">
                    <span className="truncate flex items-center gap-1">
                      <span>{p.icono}</span>
                      <strong>{p.nombre}</strong>
                    </span>
                    <span className="text-corteza-clara text-[11px]">{p.tarea}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Acción de Sumarse como Padrino */}
            <button
              type="button"
              onClick={handleSumarsePadrino}
              disabled={sumadoPadrino}
              className={`w-full py-2.5 px-4 rounded-xl flex items-center justify-center space-x-2 text-xs font-bold shadow-xs active:translate-y-[1px] transition-all ${
                sumadoPadrino
                  ? 'bg-salvia-50 text-salvia border border-salvia-200 cursor-default'
                  : 'bg-salvia hover:bg-salvia-600 text-white'
              }`}
            >
              <Icono nombre="corazon" className="size-4" />
              <span>
                {sumadoPadrino
                  ? '¡Te sumaste a la Red de Cuidados de Barbincho!'
                  : '+ Sumarme como Padrino Responsable'}
              </span>
            </button>
          </article>

          {/* Banner de Guardia Veterinaria Municipal */}
          <div className="bg-gradient-to-r from-lino-suave to-white rounded-2xl p-3.5 border border-borde-calido flex items-center justify-between shadow-xs">
            <div className="flex items-center space-x-3">
              <div className="size-9 rounded-xl bg-terracota text-white flex items-center justify-center shrink-0">
                <Icono nombre="telefono" className="size-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-corteza">Guardia Veterinaria Bolívar</p>
                <p className="text-[11px] text-corteza-suave">
                  Turnos y castraciones gratuitas del municipio (Zoonosis)
                </p>
              </div>
            </div>
            <a
              href="tel:2314421111"
              className="p-2.5 rounded-xl bg-white hover:bg-lino text-terracota border border-borde-calido shadow-xs active:scale-95 transition-all"
              title="Llamar a Guardia Veterinaria de Bolívar"
            >
              <Icono nombre="telefono" className="size-4" />
            </a>
          </div>
        </section>
      </main>

      {/* ═══════════════════════════════════════════════════════════════════
          MODAL DE CONFIRMACIÓN: ALERTA DE EXTRAVÍO VECINAL & COTEJO IA
          ═══════════════════════════════════════════════════════════════════ */}
      {modalAlertaAbierto && (
        <div className="fixed inset-0 z-50 bg-corteza/60 backdrop-blur-xs flex items-end sm:items-center justify-center p-4">
          <div className="bg-white w-full max-w-sm rounded-3xl border border-borde-calido p-5 shadow-2xl space-y-4 animate-scaleUp">
            <div className="flex items-center justify-between pb-2 border-b border-borde-calido">
              <div className="flex items-center space-x-2 text-coral font-bold">
                <Icono nombre="atencion" className="size-5 text-coral animate-pulse" />
                <span className="font-serif text-base text-corteza">
                  Alerta de Extravío de Mascota
                </span>
              </div>
              <button
                type="button"
                onClick={() => setModalAlertaAbierto(false)}
                className="size-8 rounded-full flex items-center justify-center text-corteza-suave hover:bg-lino-suave"
              >
                <Icono nombre="cruz" className="size-4" />
              </button>
            </div>

            <p className="text-xs text-corteza-suave leading-relaxed">
              Al confirmar, se enviará una notificación geolocalizada a los vecinos de{' '}
              <strong>Barrio Las Flores</strong> y radio de 2 km en Bolívar, activando el reconocimiento por foto IA (ViT-B/16).
            </p>

            <div className="p-3 bg-coral-50 border border-coral-200 rounded-2xl space-y-1">
              <div className="text-xs font-bold text-coral flex items-center gap-1">
                <span>⚠️ Confirmar Extravío de Milo</span>
              </div>
              <p className="text-[11px] text-corteza font-medium">
                Última zona detectada: Calle Brown y Balcarce, Bolívar.
              </p>
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setModalAlertaAbierto(false)}
                className="flex-1 py-2.5 rounded-xl border border-borde-calido text-corteza text-xs font-bold hover:bg-lino-suave transition-colors"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={activarAlertaExtravio}
                className="flex-1 py-2.5 rounded-xl bg-coral hover:bg-coral-600 text-white text-xs font-bold shadow-md active:scale-95 transition-transform"
              >
                Emitir Alerta Ya
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
