'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Icono } from '@/components/ui/Icono';
import { API_URL, type RegistroRemum } from '@/lib/api';

export default function QRViewPage() {
  const params = useParams();
  const qrId = params?.id as string;
  const [remumData, setRemumData] = useState<RegistroRemum | null>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    if (!qrId) return;
    fetch(`${API_URL}/api/remum/${qrId}`)
      .then(res => res.json())
      .then(data => {
        setRemumData(data as RegistroRemum);
        setCargando(false);
      })
      .catch(err => {
        console.error(err);
        setCargando(false);
      });
  }, [qrId]);

  if (cargando) {
    return <div className="min-h-screen grid place-items-center bg-lino"><div className="animate-pulse font-bold text-corteza">Cargando Credencial Pública...</div></div>;
  }

  if (!remumData || remumData.detail) {
    return <div className="min-h-screen grid place-items-center bg-lino"><div className="font-bold text-coral">Credencial no encontrada.</div></div>;
  }

  return (
    <div className="min-h-screen pb-28 bg-lino">
      {/* Barra Superior Cívica */}
      <div className="sticky top-0 z-30 border-b border-borde-calido bg-white/95 backdrop-blur-md px-4 py-3 shadow-xs">
        <div className="mx-auto flex max-w-xl items-center gap-3">
          <Link href="/" className="grid size-9 place-items-center rounded-full text-corteza-suave hover:bg-lino-suave active:scale-95 transition-all">
            <Icono nombre="flecha-izquierda" className="size-5" />
          </Link>
          <div>
            <div className="inline-flex items-center gap-1.5 rounded-full bg-lino-suave border border-borde-calido px-2 py-0.5 text-[11px] font-bold text-terracota">
              <Icono nombre="escudo" className="size-3 text-terracota" />
              <span>VISTA PÚBLICA</span>
            </div>
            <h1 className="font-serif text-lg font-bold text-corteza leading-tight">
              Registro Municipal
            </h1>
          </div>
        </div>
      </div>

      <main className="mx-auto max-w-xl px-4 pt-6 space-y-6">
        {/* Tarjeta Oficial REMUM Pública */}
        <section className="relative rounded-3xl border border-borde-calido bg-white shadow-passport overflow-hidden">
          <div className="bg-gradient-to-r from-terracota to-terracota-600 px-4 py-3 text-white flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Icono nombre="pata" className="size-4 text-white" />
              <span className="font-mono text-xs font-bold tracking-wider uppercase">
                REMUM · {remumData.qr_code_id}
              </span>
            </div>
            <div className="flex items-center space-x-1 text-[11px] font-bold bg-white/20 px-2 py-0.5 rounded-md backdrop-blur-xs">
              <Icono nombre="visto" className="size-3 text-white" />
              <span>VERIFICADO</span>
            </div>
          </div>

          <div className="p-4 sm:p-5 pb-4">
            <div className="flex gap-4 items-start">
              <div className="relative shrink-0 w-28 h-36 rounded-2xl overflow-hidden border-2 border-borde-calido bg-lino-suave shadow-xs">
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
              </div>

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

                <div className="space-y-1.5 pt-1 text-xs">
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

            {/* Acciones Ciudadanas */}
            <div className="mt-5 space-y-2">
              <button 
                onClick={() => window.open(`https://wa.me/5492314155555?text=Hola!%20Encontré%20a%20tu%20mascota%20${remumData.pet_name}%20con%20la%20chapita%20${remumData.qr_code_id}`, '_blank')}
                className="w-full bg-salvia hover:bg-salvia-600 text-white font-bold py-3.5 rounded-xl shadow-[4px_4px_0px_0px_var(--color-corteza)] border-[3px] border-corteza active:translate-y-1 active:shadow-none transition-all flex items-center justify-center gap-2"
              >
                <Icono nombre="telefono" className="size-5" />
                Contactar al Tutor (WhatsApp)
              </button>

              {remumData.status === 'extraviado' && (
                <div className="mt-2 flex items-center gap-2 rounded-xl border border-coral-200 bg-coral-50 p-3 text-sm font-bold text-coral animate-pulse">
                  <Icono nombre="atencion" className="size-5" />
                  <p>¡ESTE ANIMAL ESTÁ REPORTADO COMO EXTRAVIADO!</p>
                </div>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
