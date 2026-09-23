'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Icono } from '@/components/ui/Icono';
import { API_URL, urlDeImagen, type RegistroRemum } from '@/lib/api';

export default function RemumIndexPage() {
  const [mascotas, setMascotas] = useState<RegistroRemum[]>([]);
  const [cargando, setCargando] = useState(true);
  const [sinSesion, setSinSesion] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetch(`${API_URL}/api/remum/mis-mascotas`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setMascotas(data);
        }
      })
      .finally(() => setCargando(false));
    } else {
      queueMicrotask(() => {
        setSinSesion(true);
        setCargando(false);
      });
    }
  }, []);

  return (
    <div className="min-h-screen bg-lino pb-28">
      {/* Barra Superior Cívica */}
      <div className="sticky top-16 z-30 border-b border-borde-calido bg-white/95 backdrop-blur-md px-4 py-3 shadow-xs">
        <div className="mx-auto flex max-w-xl items-center gap-3">
          <Link href="/" className="grid size-9 place-items-center rounded-full text-corteza-suave hover:bg-lino-suave active:scale-95 transition-all">
            <Icono nombre="flecha-izquierda" className="size-5" />
          </Link>
          <div>
            <div className="inline-flex items-center gap-1.5 rounded-full bg-lino-suave border border-borde-calido px-2 py-0.5 text-[11px] font-bold text-terracota">
              <Icono nombre="escudo" className="size-3 text-terracota" />
              <span>REMUM</span>
            </div>
            <h1 className="font-serif text-lg font-bold text-corteza leading-tight">
              Registro Municipal de Mascotas
            </h1>
          </div>
        </div>
      </div>

      <main className="mx-auto max-w-xl px-4 pt-8">
        <div className="space-y-6 text-center">
          <div className="mx-auto grid size-20 place-items-center rounded-full bg-terracota-50 text-terracota">
            <Icono nombre="credencial" className="size-10" />
          </div>
          
          <div>
            <h2 className="font-serif text-2xl font-bold text-corteza mb-2">Bienvenido a REMUM</h2>
            <p className="text-corteza-suave text-sm">
              El Registro Municipal de Mascotas vincula a tu animal de compañía con una credencial digital y alerta vecinal rápida en caso de extravío.
            </p>
          </div>

          <div className="pt-4 space-y-3">
            <Link 
              href="/remum/nuevo"
              className="inline-flex w-full items-center justify-center gap-2 rounded-xl border-[3px] border-corteza bg-terracota px-4 py-4 font-bold text-white shadow-[4px_4px_0px_0px_var(--color-corteza)] transition-all hover:bg-terracota-600 active:translate-y-1 active:shadow-none"
            >
              <Icono nombre="mas" className="size-5" />
              Registrar Nueva Mascota
            </Link>
            
            <Link 
              href="/remum/escanear"
              className="inline-flex w-full items-center justify-center gap-2 rounded-xl border-[3px] border-corteza bg-lino-suave px-4 py-4 font-bold text-corteza shadow-[4px_4px_0px_0px_var(--color-corteza)] transition-all hover:bg-lino active:translate-y-1 active:shadow-none"
            >
              <Icono nombre="qr" className="size-5 text-corteza" />
              Escanear Credencial QR
            </Link>
          </div>

          <div className="mt-8 rounded-2xl border border-borde-calido bg-white p-5 text-left shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <Icono nombre="pata" className="size-5 text-terracota" />
              <h3 className="font-serif font-bold text-corteza">Mis Mascotas Empadronadas</h3>
            </div>
            
            {cargando ? (
              <p className="text-sm text-corteza-suave mb-4">Cargando...</p>
            ) : sinSesion ? (
              <p className="text-sm text-corteza-suave mb-4">
                Iniciá sesión para ver tus mascotas registradas.
              </p>
            ) : mascotas.length === 0 ? (
              <p className="text-sm text-corteza-suave mb-4">
                Actualmente no tienes mascotas registradas.
              </p>
            ) : (
              <div className="space-y-3">
                {mascotas.map((m) => (
                  <Link 
                    key={m.id}
                    href={`/remum/${m.qr_code_id}`}
                    className="flex items-center gap-4 p-3 rounded-xl border border-borde-calido bg-lino-suave hover:bg-lino transition-colors"
                  >
                    <div className="size-12 rounded-lg bg-gray-200 overflow-hidden shrink-0">
                      {m.image_path ? (
                        <img src={urlDeImagen(m.image_path) || ''} alt={m.pet_name} className="w-full h-full object-cover" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400">
                          <Icono nombre="pata" className="size-6" />
                        </div>
                      )}
                    </div>
                    <div>
                      <h4 className="font-bold text-corteza">{m.pet_name}</h4>
                      <p className="text-xs text-corteza-suave capitalize">{m.pet_type} • {m.status}</p>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
