import Link from 'next/link';
import { Icono } from '@/components/ui/Icono';
import { listarReportes } from '@/lib/api';
import { AREAS, CATEGORIAS } from '@/lib/taxonomy';
import { LETRA_AREA } from '@/components/ui/marcas';

/**
 * Hoja 01 — Portada de la mensura.
 *
 * El primer viewport es la tesis: una hoja de mensura de Bolívar con el
 * cajetín a la izquierda y la grilla de parcelas a la derecha. No hay hero
 * con tres tarjetas: hay una hoja técnica que ya está midiendo la ciudad.
 */

export const dynamic = 'force-dynamic';

async function contarReportes(): Promise<number | null> {
  try {
    const reportes = await listarReportes();
    return reportes.length;
  } catch {
    // El backend puede estar apagado: la hoja se dibuja igual.
    return null;
  }
}

export default async function Portada() {
  const total = await contarReportes();

  return (
    <main className="flex flex-1 flex-col">
      {/* ── Hoja principal ────────────────────────────────────────────────── */}
      <section className="mensura-mayor relative flex flex-1 flex-col border-b border-grafito-200">
        {/* Marco de la hoja: las marcas de esquina del plano. */}
        <MarcasDeEsquina />

        <div className="mx-auto flex w-full max-w-[86rem] flex-1 flex-col gap-10 px-5 py-10 sm:px-8 sm:py-14 lg:flex-row lg:items-stretch lg:gap-16 lg:py-20">
          {/* ── Cajetín ─────────────────────────────────────────────────── */}
          <div className="motion-safe:desplegar flex flex-col lg:w-[46%] lg:shrink-0">
            {/* Datos de hoja: el cajetín que abre toda plancha, arriba a la
                izquierda. Nº de hoja y cifras reales, nada decorativo. */}
            <dl className="grid grid-cols-3 gap-x-6 gap-y-3 border-b border-grafito-200 pb-6">
              <div>
                <dt className="rotulo">Hoja</dt>
                <dd className="cifra mt-0.5 text-xl font-semibold text-grafito-900">Nº 01</dd>
              </div>
              <div>
                <dt className="rotulo">Parcelas</dt>
                <dd className="cifra mt-0.5 text-xl font-semibold text-tinta-700">
                  {total === null ? '—' : String(total)}
                </dd>
              </div>
              <div>
                <dt className="rotulo">Áreas · Categorías</dt>
                <dd className="cifra mt-0.5 text-xl font-semibold text-grafito-900">
                  4 · {CATEGORIAS.length}
                </dd>
              </div>
            </dl>

            <h1 className="titulo-hoja mt-8 text-[2.5rem] font-extrabold leading-[0.95] tracking-[-0.03em] text-grafito-900 sm:text-6xl lg:text-[4.25rem]">
              Sacá una foto.
              <br />
              <span className="text-tinta-600">Nosotros la ubicamos</span>
              <br />
              en el plano.
            </h1>

            <p className="mt-6 max-w-[42ch] text-lg leading-relaxed text-grafito-600">
              Un bache, una luminaria apagada, un animal suelto, un auto sobre la
              vereda. No elegís categoría ni completás un formulario largo: la foto y
              una línea alcanzan.
            </p>

            {/* Obturador: el único botón sólido de la hoja, anclado al pie
                del cajetín. */}
            <div className="mt-auto flex flex-col gap-3 pt-10 sm:flex-row sm:items-center">
              <Link
                href="/reportes/nuevo"
                className="inline-flex min-h-14 items-center justify-center gap-2.5 rounded-hoja border border-tinta-700 bg-tinta-600 px-7 text-base font-semibold text-papel-alto transition-colors hover:bg-tinta-700 active:bg-tinta-800"
              >
                <Icono nombre="camara" className="size-5" />
                Reportar algo
              </Link>
              <Link
                href="/mapa"
                className="inline-flex min-h-14 items-center justify-center gap-2.5 rounded-hoja border border-tinta-200 bg-papel-alto px-7 text-base font-medium text-tinta-700 transition-colors hover:border-tinta-300 hover:bg-tinta-50"
              >
                <Icono nombre="plano" className="size-5" />
                Ver el plano
              </Link>
            </div>
          </div>

          {/* ── Grilla de parcelas por área ──────────────────────────────── */}
          <div className="flex flex-1 flex-col">
            <div className="mb-3 flex items-baseline justify-between gap-4">
              <p className="rotulo">Áreas de la hoja</p>
              <p className="rotulo">Esc. 1:1</p>
            </div>

            <ul className="grid flex-1 grid-cols-1 gap-px overflow-hidden rounded-hoja border border-grafito-200 bg-grafito-200 sm:grid-cols-2">
              {AREAS.map((area, i) => {
                const categorias = CATEGORIAS.filter((c) => c.area === area);
                return (
                  <li
                    key={area}
                    className="motion-safe:desplegar flex flex-col bg-papel-alto p-5 sm:p-6"
                    style={{ animationDelay: `${120 + i * 90}ms` }}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <span
                        className="cifra grid size-9 shrink-0 place-items-center rounded-hoja border border-tinta-200 bg-tinta-50 text-sm font-bold text-tinta-700"
                        aria-hidden
                      >
                        {LETRA_AREA[area]}
                      </span>
                      <span className="cifra text-[0.8125rem] text-grafito-500">
                        {String(categorias.length).padStart(2, '0')}
                      </span>
                    </div>

                    <h2 className="mt-4 text-lg font-semibold leading-snug tracking-[-0.01em] text-grafito-900">
                      {area}
                    </h2>

                    <p className="mt-2 text-[0.875rem] leading-relaxed text-grafito-500">
                      {categorias
                        .slice(0, 3)
                        .map((c) => c.label)
                        .join(' · ')}
                      {categorias.length > 3 ? ' · …' : ''}
                    </p>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </section>

      {/* ── Pie de hoja: el recorrido, en tres renglones medidos ─────────── */}
      <section className="border-b border-grafito-200 bg-papel-alto">
        <div className="mx-auto grid w-full max-w-[86rem] grid-cols-1 gap-px bg-grafito-200 px-0 sm:grid-cols-3">
          <PasoDeHoja
            numero="01"
            icono="camara"
            titulo="Sacás la foto"
            texto="Desde el teléfono, parado frente a lo que encontraste. El navegador toma la ubicación y la resuelve a una dirección."
          />
          <PasoDeHoja
            numero="02"
            icono="regla"
            titulo="Se clasifica solo"
            texto="La foto y tu descripción se analizan juntas para deducir el área y la categoría. Vos no elegís de una lista de 23."
          />
          <PasoDeHoja
            numero="03"
            icono="hoja"
            titulo="Queda con número"
            texto="El reporte queda con número y estado propios. Podés volver y ver si cambió."
          />
        </div>
      </section>

      {/* ── Cinta legal y proveniencia ───────────────────────────────────── */}
      <footer className="bg-papel">
        <div className="mx-auto flex w-full max-w-[86rem] flex-col gap-4 px-5 py-7 sm:flex-row sm:items-start sm:justify-between sm:px-8">
          <div className="max-w-[68ch] space-y-2">
            <p className="text-[0.75rem] leading-relaxed text-grafito-500">
              La IA clasifica la situación a partir de la foto y el texto. No determina una
              infracción legal; eso corresponde a la normativa municipal.
            </p>
            {/* Proveniencia: proyecto académico, no un servicio municipal
                oficial vigente. */}
            <p className="text-[0.75rem] leading-relaxed text-grafito-500">
              Reporte Bolívar es un proyecto académico de la Universidad Nacional del
              Centro de la Provincia de Buenos Aires. No es un servicio municipal
              oficial.
            </p>
          </div>
          <nav className="flex shrink-0 items-center gap-5" aria-label="Secciones">
            <Link
              href="/reportes"
              className="text-[0.8125rem] text-tinta-700 underline decoration-tinta-200 hover:decoration-tinta-600"
            >
              Reportes
            </Link>
            <Link
              href="/dashboard"
              className="text-[0.8125rem] text-tinta-700 underline decoration-tinta-200 hover:decoration-tinta-600"
            >
              Panel municipal
            </Link>
            <Link
              href="/login"
              className="text-[0.8125rem] text-tinta-700 underline decoration-tinta-200 hover:decoration-tinta-600"
            >
              Entrar
            </Link>
          </nav>
        </div>
      </footer>
    </main>
  );
}

function PasoDeHoja({
  numero,
  icono,
  titulo,
  texto,
}: {
  numero: string;
  icono: 'camara' | 'regla' | 'hoja';
  titulo: string;
  texto: string;
}) {
  return (
    <div className="bg-papel-alto px-5 py-8 sm:px-7">
      <div className="flex items-center gap-3">
        <Icono nombre={icono} className="size-5 text-tinta-600" />
        <span className="cifra text-[0.75rem] text-grafito-500">{numero}</span>
      </div>
      <h3 className="mt-3.5 text-base font-semibold tracking-[-0.01em] text-grafito-900">
        {titulo}
      </h3>
      <p className="mt-2 max-w-[46ch] text-[0.875rem] leading-relaxed text-grafito-600">{texto}</p>
    </div>
  );
}

/** Marcas de registro de la plancha, en las cuatro esquinas. */
function MarcasDeEsquina() {
  const comun = 'pointer-events-none absolute size-4 border-tinta-600/25';
  return (
    <div aria-hidden>
      <span className={`${comun} left-3 top-3 border-l border-t`} />
      <span className={`${comun} right-3 top-3 border-r border-t`} />
      <span className={`${comun} bottom-3 left-3 border-b border-l`} />
      <span className={`${comun} bottom-3 right-3 border-b border-r`} />
    </div>
  );
}
