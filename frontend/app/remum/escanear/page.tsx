'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Icono } from '@/components/ui/Icono';
import { Scanner } from '@yudiel/react-qr-scanner';

export default function EscanearQRPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const handleScan = (result: { rawValue?: string }[]) => {
    if (result && result.length > 0) {
      const qrValue = result[0].rawValue || result[0];
      if (typeof qrValue === 'string') {
        // Buscamos si la URL es del formato Reporte Bolívar REMUM
        const urlMatch = qrValue.match(/\/qr\/([A-Za-z0-9-]+)/);
        if (urlMatch && urlMatch[1]) {
          router.push(`/qr/${urlMatch[1]}`);
        } else {
          setError('El código QR escaneado no pertenece a una credencial válida de REMUM.');
          // Limpiar el error después de 3 segundos
          setTimeout(() => setError(null), 3000);
        }
      }
    }
  };

  return (
    <div className="min-h-screen bg-corteza pb-28">
      {/* Barra Superior */}
      <div className="sticky top-16 z-30 border-b border-corteza-clara bg-corteza/95 backdrop-blur-md px-4 py-3 shadow-xs">
        <div className="mx-auto flex max-w-xl items-center gap-3">
          <Link href="/remum" className="grid size-9 place-items-center rounded-full text-lino hover:bg-corteza-clara active:scale-95 transition-all">
            <Icono nombre="flecha-izquierda" className="size-5" />
          </Link>
          <div>
            <div className="inline-flex items-center gap-1.5 rounded-full bg-corteza-clara px-2 py-0.5 text-[11px] font-bold text-white">
              <Icono nombre="qr" className="size-3" />
              <span>ESCÁNER VECINAL</span>
            </div>
            <h1 className="font-serif text-lg font-bold text-lino leading-tight">
              Leer Credencial REMUM
            </h1>
          </div>
        </div>
      </div>

      <main className="mx-auto max-w-xl px-4 pt-8">
        <div className="space-y-6 text-center">
          <p className="text-lino-suave text-sm">
            Apunta la cámara al código QR de la chapita de la mascota. El escáner lo detectará automáticamente.
          </p>

          {error && (
            <div className="p-3 rounded-xl bg-coral-50 border border-coral-200 text-coral text-sm font-bold animate-fadeIn">
              {error}
            </div>
          )}

          <div className="relative mx-auto max-w-sm rounded-3xl overflow-hidden border-4 border-lino-suave shadow-[0_0_40px_rgba(0,0,0,0.5)]">
            <Scanner
              onScan={handleScan}
              onError={(e) => console.error("Error en cámara:", e)}
              constraints={{ facingMode: 'environment' }}
              components={{ finder: true }}
            />
            {/* Esquinas de Mira (Targeting) */}
            <div className="pointer-events-none absolute inset-0 z-10 flex items-center justify-center p-8">
              <div className="w-full h-full border-2 border-white/20 relative">
                <div className="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-salvia"></div>
                <div className="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-salvia"></div>
                <div className="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-salvia"></div>
                <div className="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-salvia"></div>
              </div>
            </div>
          </div>
          
          <div className="pt-4 flex justify-center">
            <Link href="/sos" className="text-coral-100 hover:text-coral underline text-xs font-bold">
              ¿Encontraste una mascota herida? Contactá a Zoonosis.
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
