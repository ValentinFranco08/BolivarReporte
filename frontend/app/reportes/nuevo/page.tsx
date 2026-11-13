'use client';

import { Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useNuevoReporte } from '@/controllers/useNuevoReporte';
import type { TipoReporteAnimal, TipoMascota } from '@/models/reports';
import { VisualMatchModal } from '@/components/pets/VisualMatchModal';
import { Icono } from '@/components/ui/Icono';

function FormularioNuevoReporte() {
  const searchParams = useSearchParams();
  const tipoInicial = (searchParams.get('tipo') as TipoReporteAnimal) || 'perdido';
  const {
    tipoReporte, setTipoReporte, tipoMascota, setTipoMascota, nombreMascota, setNombreMascota,
    raza, setRaza, color, setColor, contactoNombre, setContactoNombre,
    contactoTelefono, setContactoTelefono, descripcion, setDescripcion,
    vistaPrevia, quitarFoto, fotosAdicionales, agregarFotos, quitarFotoAdicional, direccion, setDireccion, gpsBuscando, pedirGps,
    handleArchivoSeleccionado, enviar, enviando, error, reporteCreado,
    cotejo, mostrarModalMatches, setMostrarModalMatches,
  } = useNuevoReporte(tipoInicial);

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6 sm:py-10">
      {/* ── Encabezado Vecinal ── */}
      <div className="mb-6 text-center sm:text-left">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-terracota hover:underline mb-2"
        >
          <span>←</span>
          <span>Volver a la cartelera</span>
        </Link>
        <p className="rotulo mb-2">Reportar Mascota</p>
        <h1 className="text-3xl font-extrabold tracking-[-.04em] text-corteza sm:text-4xl">
          Contanos dónde fue visto.
        </h1>
        <p className="text-xs sm:text-sm text-corteza-suave mt-1">
          La foto y el último lugar visto alcanzan para activar la búsqueda entre vecinos.
        </p>
      </div>

      {/* ── Publicación Exitosa ── */}
      {reporteCreado && (
        <div className="rounded-3xl border border-salvia-200 bg-salvia-50 p-6 sm:p-8 text-center shadow-warm-card space-y-4 mb-6">
          <div className="mx-auto size-12 rounded-full bg-salvia text-white flex items-center justify-center">
            <Icono nombre="visto" className="size-6" />
          </div>
          <h2 className="font-serif text-xl font-bold text-salvia-800">
            ¡Publicación subida con éxito a la Red!
          </h2>
          <p className="text-xs sm:text-sm text-corteza-suave max-w-md mx-auto leading-relaxed">
            Tu reporte ya está visible para todos los vecinos de Bolívar y activó el cotejo visual
            automático.
          </p>

          {Boolean(cotejo?.matches.length || cotejo?.review_candidates?.length) ? (
            <div className="pt-2">
              <button
                type="button"
                onClick={() => setMostrarModalMatches(true)}
                className="inline-flex items-center gap-2 rounded-2xl bg-terracota px-5 py-3 text-xs font-bold text-white shadow-warm-card hover:bg-terracota-600 active:scale-95 transition-all"
              >
                <Icono nombre="mira" className="size-4" />
                <span>{cotejo?.matches.length
                  ? `Hay ${cotejo.matches.length} posibles coincidencias. Ver ahora`
                  : 'Revisar avisos de similitud baja'}</span>
              </button>
            </div>
          ) : (
            <>
              {cotejo?.matches.length === 0 && (
                <p className="text-xs text-corteza-suave">Todavía no encontramos coincidencias visuales.</p>
              )}
              <div className="pt-2 flex justify-center gap-3">
                <Link
                  href="/"
                  className="inline-flex items-center gap-2 rounded-2xl bg-white border border-borde-calido px-5 py-2.5 text-xs font-bold text-corteza hover:bg-lino-suave"
                >
                  <span>Ir a la cartelera</span>
                </Link>
                <Link
                  href="/mapa"
                  className="inline-flex items-center gap-2 rounded-2xl bg-terracota px-5 py-2.5 text-xs font-bold text-white shadow-xs hover:bg-terracota-600"
                >
                  <span>Ver en el mapa</span>
                </Link>
              </div>
            </>
          )}
        </div>
      )}

      {/* ── Formulario de Carga ── */}
      {!reporteCreado && (
        <form
          onSubmit={enviar}
          className="border border-borde-fuerte bg-lino-alto p-5 shadow-warm-card sm:p-8 space-y-7"
        >
          {error && (
            <div className="rounded-2xl border border-coral-200 bg-coral-50 p-4 text-xs text-coral">
              {error}
            </div>
          )}

          {/* 1. Selector de Tipo */}
          <div>
            <label className="rotulo mb-3 block">
              Situación
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {(
                [
                  { id: 'perdido', label: 'Estoy buscando', icon: 'Buscar' },
                  { id: 'encontrado', label: 'La encontré', icon: 'Hallazgo' },
                  { id: 'alerta_cebo', label: 'Alerta sanitaria', icon: 'Alerta' },
                  { id: 'adopcion', label: 'Hogar o tránsito', icon: 'Hogar' },
                ] as const
              ).map((t) => {
                const activo = tipoReporte === t.id;
                return (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => setTipoReporte(t.id)}
                    className={`flex flex-col items-start justify-center border p-3 text-left transition-colors ${
                      activo
                        ? t.id === 'alerta_cebo'
                          ? 'bg-coral text-white border-coral font-bold shadow-xs'
                          : 'bg-terracota text-white border-terracota font-bold shadow-xs'
                        : 'bg-lino-suave border-borde-calido text-corteza hover:bg-lino-medio'
                    }`}
                  >
                    <span className="rotulo !text-current">{t.icon}</span>
                    <span className="mt-1 text-xs">{t.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 2. Subida de Foto */}
          <div>
            <label className="block text-xs font-bold text-corteza uppercase tracking-wider mb-2">
              Foto del animal o evidencia
            </label>
            {vistaPrevia ? (
              <div className="relative aspect-[4/3] w-full rounded-2xl overflow-hidden bg-lino-suave border border-borde-calido">
                <img
                  src={vistaPrevia}
                  alt="Vista previa"
                  className="w-full h-full object-cover"
                />
                <button
                  type="button"
                  onClick={quitarFoto}
                  className="absolute top-3 right-3 rounded-xl bg-white/90 backdrop-blur-xs px-3 py-1 text-xs font-bold text-corteza shadow-sm hover:bg-white"
                >
                  Cambiar foto
                </button>
              </div>
            ) : (
              <label className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-borde-calido bg-lino-suave p-8 text-center cursor-pointer hover:bg-lino-medio hover:border-terracota transition-all">
                <div className="size-12 rounded-full bg-white flex items-center justify-center text-terracota shadow-xs">
                  <Icono nombre="camara" className="size-6" />
                </div>
                <span className="mt-3 text-xs font-bold text-corteza">
                  Hacé clic para sacar una foto o subir una de tu galería
                </span>
                <span className="mt-1 text-[11px] text-corteza-clara">
                  Una foto nítida de frente facilita que el comparador visual encuentre coincidencias
                </span>
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={handleArchivoSeleccionado}
                  className="sr-only"
                />
              </label>
            )}
          </div>

          {vistaPrevia && (
            <div className="space-y-2">
              {fotosAdicionales.length < 3 && (
                <label className="inline-flex cursor-pointer text-xs font-bold text-terracota">
                  Agregar fotos de perfil o cuerpo entero (opcional)
                  <input type="file" accept="image/*" multiple onChange={agregarFotos} className="sr-only" />
                </label>
              )}
              {fotosAdicionales.map((foto, index) => (
                <div key={index} className="flex items-center justify-between gap-2 text-xs">
                  <span className="truncate">{foto.name}</span>
                  <button type="button" className="text-terracota" onClick={() => quitarFotoAdicional(index)}>
                    Quitar
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* 3. Datos del Animal */}
          {tipoReporte !== 'alerta_cebo' ? (
            <div className="space-y-3 border-t border-borde-suave pt-4">
              <label className="block text-xs font-bold text-corteza uppercase tracking-wider">
                3. Datos del animal
              </label>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-corteza mb-1">
                    Especie
                  </label>
                  <select
                    value={tipoMascota}
                    onChange={(e) => setTipoMascota(e.target.value as TipoMascota)}
                    className="w-full rounded-xl border border-borde-calido bg-white px-3 py-2 text-xs text-corteza focus:border-terracota focus:ring-1 focus:ring-terracota"
                  >
                    <option value="perro">Perro / Canino</option>
                    <option value="gato">Gato / Felino</option>
                    <option value="otro">Otra especie</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-corteza mb-1">
                    {tipoReporte === 'perdido' ? 'Nombre de tu mascota' : 'Nombre (si responde a uno)'}
                  </label>
                  <input
                    type="text"
                    placeholder="Ej. Milo"
                    value={nombreMascota}
                    onChange={(e) => setNombreMascota(e.target.value)}
                    className="w-full rounded-xl border border-borde-calido bg-white px-3 py-2 text-xs text-corteza focus:border-terracota focus:ring-1 focus:ring-terracota"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-corteza mb-1">
                    Raza o Mestizaje
                  </label>
                  <input
                    type="text"
                    placeholder="Ej. Labrador, Mestizo mediano, Barbincho..."
                    value={raza}
                    onChange={(e) => setRaza(e.target.value)}
                    className="w-full rounded-xl border border-borde-calido bg-white px-3 py-2 text-xs text-corteza focus:border-terracota focus:ring-1 focus:ring-terracota"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-corteza mb-1">
                    Color del pelaje
                  </label>
                  <input
                    type="text"
                    placeholder="Ej. Dorado, marrón con pecho blanco..."
                    value={color}
                    onChange={(e) => setColor(e.target.value)}
                    className="w-full rounded-xl border border-borde-calido bg-white px-3 py-2 text-xs text-corteza focus:border-terracota focus:ring-1 focus:ring-terracota"
                  />
                </div>
              </div>
            </div>
          ) : null}

          {/* 4. Ubicación en Bolívar */}
          <div className="space-y-2 border-t border-borde-suave pt-4">
            <div className="flex items-center justify-between">
              <label className="block text-xs font-bold text-corteza uppercase tracking-wider">
              {tipoReporte === 'alerta_cebo' ? 'Lugar del cebo' : 'Último lugar visto'}
              </label>
              <button
                type="button"
                onClick={pedirGps}
                disabled={gpsBuscando}
                className="inline-flex items-center gap-1 text-[11px] font-bold text-terracota hover:underline"
              >
              <span>{gpsBuscando ? 'Detectando GPS...' : 'Usar mi GPS actual'}</span>
              </button>
            </div>

            <input
              type="text"
              placeholder="Ej. Plaza Alsina, o Av. San Martín y Balcarce..."
              value={direccion || ''}
              onChange={(e) => setDireccion(e.target.value)}
              className="w-full rounded-xl border border-borde-calido bg-white px-3 py-2 text-xs text-corteza focus:border-terracota focus:ring-1 focus:ring-terracota"
            />
          </div>

          {/* 5. Contacto Vecinal */}
          <div className="space-y-3 border-t border-borde-suave pt-4">
            <label className="block text-xs font-bold text-corteza uppercase tracking-wider">
              {tipoReporte === 'alerta_cebo' ? '3. Tu contacto' : '5. Tu contacto (para que te escriban)'}
            </label>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-corteza mb-1">
                  Tu nombre o familia
                </label>
                <input
                  type="text"
                  placeholder="Ej. Martín / Familia Rossi"
                  value={contactoNombre}
                  onChange={(e) => setContactoNombre(e.target.value)}
                  className="w-full rounded-xl border border-borde-calido bg-white px-3 py-2 text-xs text-corteza focus:border-terracota focus:ring-1 focus:ring-terracota"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-corteza mb-1">
                  Teléfono (WhatsApp)
                </label>
                <input
                  type="text"
                  placeholder="2314-..."
                  value={contactoTelefono}
                  onChange={(e) => setContactoTelefono(e.target.value)}
                  className="w-full rounded-xl border border-borde-calido bg-white px-3 py-2 text-xs text-corteza focus:border-terracota focus:ring-1 focus:ring-terracota"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-corteza mb-1">
                Detalles adicionales
              </label>
              <textarea
                rows={2}
                placeholder="¿Tiene collar? ¿Es asustadizo? Cualquier dato ayuda a los vecinos."
                value={descripcion}
                onChange={(e) => setDescripcion(e.target.value)}
                className="w-full rounded-xl border border-borde-calido bg-white px-3 py-2 text-xs text-corteza focus:border-terracota focus:ring-1 focus:ring-terracota"
              />
            </div>
          </div>

          {/* Botón de Envío */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={enviando}
              className="w-full flex items-center justify-center gap-2 rounded-2xl bg-terracota py-3.5 px-4 font-bold text-sm text-white shadow-warm-card hover:bg-terracota-600 active:scale-95 transition-all disabled:opacity-50"
            >
              <Icono nombre="camara" className="size-4" />
              <span>{enviando ? 'Publicando aviso...' : 'Publicar aviso en Bolívar'}</span>
            </button>
          </div>
        </form>
      )}

      {/* Modal de Matches automáticos si se encontraron */}
      {mostrarModalMatches && reporteCreado && (
        <VisualMatchModal
          reporte={reporteCreado}
          onClose={() => setMostrarModalMatches(false)}
        />
      )}
    </div>
  );
}

export default function NuevoReportePage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-64 items-center justify-center">
          <p className="text-xs text-corteza-suave">Cargando formulario...</p>
        </div>
      }
    >
      <FormularioNuevoReporte />
    </Suspense>
  );
}
