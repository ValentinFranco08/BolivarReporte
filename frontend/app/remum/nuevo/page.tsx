'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Icono } from '@/components/ui/Icono';

export default function NuevoEmpadronamientoPage() {
  const router = useRouter();
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState('');
  const [coordenadas, setCoordenadas] = useState<{ lat: number, lng: number } | null>(null);

  // Intentamos obtener la ubicación apenas carga si es posible
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setCoordenadas({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => console.warn("No se pudo obtener la ubicación inicial.")
      );
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login?volver=/remum/nuevo');
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setCargando(true);
    setError('');

    const form = e.currentTarget;
    const formData = new FormData(form);
    
    // FastAPI form parsing para booleanos
    const isCommunity = formData.get('is_community_pet') === 'on';
    formData.set('is_community_pet', isCommunity ? 'true' : 'false');

    // Si es mascota comunitaria, exigimos coordenadas (o usamos las que ya teníamos)
    if (isCommunity) {
      if (coordenadas) {
        formData.append('latitude', coordenadas.lat.toString());
        formData.append('longitude', coordenadas.lng.toString());
      } else {
        // Pedimos ubicación on the fly si no la teníamos
        try {
          const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject);
          });
          formData.append('latitude', pos.coords.latitude.toString());
          formData.append('longitude', pos.coords.longitude.toString());
        } catch {
          setError('Para registrar una mascota comunitaria necesitamos tu ubicación (GPS). Por favor habilitala.');
          setCargando(false);
          return;
        }
      }
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Debes iniciar sesión para registrar una mascota.');
      }

      const response = await fetch('http://localhost:8001/api/remum/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Error al registrar la mascota en REMUM. Asegúrate de estar logueado.');
      }

      const data = await response.json();
      router.push(`/remum/${data.qr_code_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="min-h-screen bg-lino pb-20">
      <div className="sticky top-16 z-30 border-b border-borde-calido bg-white/95 backdrop-blur-md px-4 py-3 shadow-xs">
        <div className="mx-auto flex max-w-xl items-center gap-3">
          <Link href="/" className="grid size-9 place-items-center rounded-full text-corteza-suave hover:bg-lino-suave active:scale-95 transition-all">
            <Icono nombre="flecha-izquierda" className="size-5" />
          </Link>
          <div>
            <div className="inline-flex items-center gap-1.5 rounded-full bg-lino-suave border border-borde-calido px-2 py-0.5 text-[11px] font-bold text-terracota">
              <Icono nombre="escudo" className="size-3 text-terracota" />
              <span>NUEVO EMPADRONAMIENTO</span>
            </div>
            <h1 className="font-serif text-lg font-bold text-corteza leading-tight">
              Registrar Mascota en REMUM
            </h1>
          </div>
        </div>
      </div>

      <main className="mx-auto max-w-xl px-4 pt-6">
        <form onSubmit={handleSubmit} className="space-y-6" encType="multipart/form-data">
          
          {error && (
            <div className="p-3 rounded-xl bg-coral-50 border border-coral-200 text-coral text-sm font-medium">
              {error}
            </div>
          )}

          <div className="space-y-4 rounded-2xl bg-white p-5 border border-borde-calido shadow-sm">
            <h2 className="font-serif text-lg font-bold text-corteza">Foto de la Mascota</h2>
            <div className="space-y-1.5">
              <label className="text-sm font-bold text-corteza block">Subir imagen frontal</label>
              <input 
                type="file"
                name="file" 
                accept="image/*"
                required
                className="w-full bg-lino-suave border border-borde-calido rounded-xl px-4 py-2.5 text-sm outline-none file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-bold file:bg-terracota-50 file:text-terracota hover:file:bg-terracota-100" 
              />
            </div>
          </div>

          <div className="space-y-4 rounded-2xl bg-white p-5 border border-borde-calido shadow-sm">
            <h2 className="font-serif text-lg font-bold text-corteza">Datos del Animal</h2>
            
            <div className="space-y-1.5">
              <label className="text-sm font-bold text-corteza block">Nombre</label>
              <input 
                name="pet_name" 
                required 
                className="w-full bg-lino-suave border border-borde-calido rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-terracota/50" 
                placeholder="Ej. Milo"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-sm font-bold text-corteza block">Especie</label>
                <select name="pet_type" className="w-full bg-lino-suave border border-borde-calido rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-terracota/50">
                  <option value="perro">Perro</option>
                  <option value="gato">Gato</option>
                  <option value="otro">Otro</option>
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-bold text-corteza block">Raza / Tipo</label>
                <input 
                  name="pet_breed" 
                  className="w-full bg-lino-suave border border-borde-calido rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-terracota/50" 
                  placeholder="Ej. Mestizo"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-bold text-corteza block">Color y Pelaje</label>
              <input 
                name="color_description" 
                className="w-full bg-lino-suave border border-borde-calido rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-terracota/50" 
                placeholder="Ej. Dorado claro, pelo corto"
              />
            </div>
          </div>

          <div className="space-y-4 rounded-2xl bg-white p-5 border border-borde-calido shadow-sm">
            <h2 className="font-serif text-lg font-bold text-corteza">Datos de Registro</h2>
            
            <div className="space-y-1.5">
              <label className="text-sm font-bold text-corteza block">Barrio / Dirección de residencia</label>
              <input 
                name="address" 
                className="w-full bg-lino-suave border border-borde-calido rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-terracota/50" 
                placeholder="Ej. Barrio Las Flores, Bolívar"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-bold text-corteza block">Número de Microchip (Opcional)</label>
              <input 
                name="chip_number" 
                className="w-full bg-lino-suave border border-borde-calido rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-terracota/50" 
                placeholder="Ej. 98109810234912"
              />
            </div>

            <label className="flex items-start gap-3 p-3 bg-lino-suave/50 border border-borde-calido rounded-xl cursor-pointer hover:bg-lino-suave transition-colors">
              <input type="checkbox" name="is_community_pet" className="mt-1 size-4 rounded border-borde-calido text-terracota focus:ring-terracota" />
              <div>
                <span className="text-sm font-bold text-corteza block">Mascota Comunitaria</span>
                <span className="text-xs text-corteza-suave">Marque si el animal vive en la calle o espacio público y es cuidado por vecinos.</span>
              </div>
            </label>
          </div>

          <button 
            type="submit" 
            disabled={cargando}
            className="w-full bg-terracota hover:bg-terracota-600 text-white font-bold py-3.5 rounded-xl shadow-[4px_4px_0px_0px_var(--color-corteza)] border-[3px] border-corteza active:translate-y-1 active:shadow-none transition-all disabled:opacity-50"
          >
            {cargando ? 'Registrando...' : 'Emitir Credencial REMUM'}
          </button>
        </form>
      </main>
    </div>
  );
}
