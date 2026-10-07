'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Icono } from '@/components/ui/Icono';

type SeccionTab = 'general' | 'red_neuronal' | 'taxonomia' | 'ecosistema' | 'comparativa';

export default function InfografiaPage() {
  const [tabActiva, setTabActiva] = useState<SeccionTab>('general');

  return (
    <main className="min-h-screen pb-20">
      {/* Header Banner */}
      <section className="border-b border-borde-fuerte bg-lino-alto">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
            <div>
              <div className="flex items-center gap-2">
                <span className="rotulo text-terracota">Proyecto de Inteligencia Artificial Cívica</span>
                <span className="rounded bg-salvia-50 px-2 py-0.5 font-mono text-[10px] font-bold text-salvia border border-salvia">
                  TEST ACCURACY: 96.7% (FINE-TUNED)
                </span>
              </div>
              <h1 className="mt-2 text-3xl font-extrabold tracking-[-.04em] sm:text-5xl">
                Infografía Técnica & Cívica
              </h1>
              <p className="mt-2 max-w-3xl text-sm leading-relaxed text-corteza-suave sm:text-base">
                De la queja informal en redes al rescate coordinado: Deep Learning Multimodal (ViT-Base + RoBERTa-BNE con Cross-Attention), sistema REMUM de trazabilidad con chapas QR y mapa geoespacial en San Carlos de Bolívar.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <a
                href="/infografia.html"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 rounded-md border border-corteza px-3 py-2 text-xs font-bold hover:bg-lino"
                title="Abrir versión imprimible independiente"
              >
                <Icono nombre="impresora" className="size-4" />
                Versión Imprimible / PDF
              </a>
              <Link
                href="/mapa"
                className="boton-principal inline-flex items-center gap-2 px-4 py-2 text-xs font-bold"
              >
                <Icono nombre="plano" className="size-4" />
                Ver Mapa en Vivo
              </Link>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="mt-8 flex gap-2 overflow-x-auto border-b border-borde-suave pb-2">
            {[
              { id: 'general', label: '1. Póster & Resumen', icono: 'hoja' as const },
              { id: 'red_neuronal', label: '2. Red Multimodal (ViT + RoBERTa)', icono: 'regla' as const },
              { id: 'taxonomia', label: '3. Taxonomía (6 Clases)', icono: 'filtro' as const },
              { id: 'ecosistema', label: '4. REMUM & Mapa', icono: 'credencial' as const },
              { id: 'comparativa', label: '5. Paradigma Cívico', icono: 'compas' as const },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setTabActiva(tab.id as SeccionTab)}
                className={`inline-flex items-center gap-2 whitespace-nowrap rounded-md px-4 py-2.5 text-xs font-bold transition-colors ${
                  tabActiva === tab.id
                    ? 'bg-corteza text-lino-alto'
                    : 'bg-lino hover:bg-lino-suave text-corteza'
                }`}
              >
                <Icono nombre={tab.icono} className="size-3.5" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Main Content Area */}
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        
        {/* KPI Cards Row */}
        <section className="mb-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="ficha-vecinal p-5 border-l-4 border-l-terracota">
            <span className="rotulo block">Exactitud del Modelo</span>
            <div className="mt-2 text-4xl font-extrabold tracking-tight text-terracota">96.7%</div>
            <p className="mt-1 text-xs text-corteza-suave">
              Accuracy comprobada en test con fine-tuning progresivo (Macro F1: 0.942).
            </p>
          </div>

          <div className="ficha-vecinal p-5 border-l-4 border-l-salvia">
            <span className="rotulo block">Corpus Curado</span>
            <div className="mt-2 text-4xl font-extrabold tracking-tight text-salvia">600</div>
            <p className="mt-1 text-xs text-corteza-suave">
              Fotos y relatos locales auditados (100 muestras por categoría).
            </p>
          </div>

          <div className="ficha-vecinal p-5 border-l-4 border-l-corteza">
            <span className="rotulo block">Espacio Multimodal</span>
            <div className="mt-2 text-4xl font-extrabold tracking-tight text-corteza">768d</div>
            <p className="mt-1 text-xs text-corteza-suave">
              Vectores normalizados para matching y búsqueda por similitud visual.
            </p>
          </div>

          <div className="ficha-vecinal p-5 border-l-4 border-l-coral">
            <span className="rotulo block">Revisión Humana</span>
            <div className="mt-2 text-4xl font-extrabold tracking-tight text-coral">&lt;55%</div>
            <p className="mt-1 text-xs text-corteza-suave">
              Umbral estricto para derivar a validación comunitaria/operativa.
            </p>
          </div>
        </section>

        {/* Tab 1: Póster & Resumen */}
        {tabActiva === 'general' && (
          <div className="space-y-8">
            <div className="overflow-hidden rounded-xl border-2 border-corteza bg-lino-alto shadow-warm-card">
              <div className="bg-corteza px-5 py-3 text-lino-alto flex justify-between items-center text-xs font-mono">
                <span>PÓSTER TÉCNICO OFICIAL · SAN CARLOS DE BOLÍVAR</span>
                <span className="text-terracota-100">FIGURA I.1</span>
              </div>
              <img
                src="/infografia_bolivar_animal.jpg"
                alt="Infografía del Proyecto Bolívar Animal"
                className="w-full h-auto object-contain border-b border-borde-fuerte"
              />
              <div className="p-6 bg-lino-alto">
                <h3 className="text-lg font-extrabold tracking-tight">
                  Integración de Inteligencia Artificial Multimodal con Operaciones Territoriales
                </h3>
                <p className="mt-2 text-sm text-corteza-suave leading-relaxed">
                  El sistema articula dos canales de captura: la visión computacional mediante parches de imagen y el procesamiento de lenguaje natural en español. La matriz de Cross-Attention unifica ambas representaciones para predecir la criticidad de la situación y situarla inmediatamente en la cartografía municipal.
                </p>
              </div>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
              <div className="ficha-vecinal p-6">
                <span className="rotulo text-terracota">Problema Real</span>
                <h4 className="mt-2 text-base font-bold">Pérdida en el "feed" social</h4>
                <p className="mt-2 text-xs leading-relaxed text-corteza-suave">
                  Las publicaciones en grupos vecinales de Facebook o WhatsApp carecen de ubicación precisa, no tienen estado de seguimiento y generan avisos duplicados que confunden a quienes buscan o rescatan.
                </p>
              </div>
              <div className="ficha-vecinal p-6">
                <span className="rotulo text-salvia">Solución Técnica</span>
                <h4 className="mt-2 text-base font-bold">Fusión Atencional Guiada</h4>
                <p className="mt-2 text-xs leading-relaxed text-corteza-suave">
                  El texto aportado por el vecino guía la inspección visual de la red neuronal mediante atención cruzada, alcanzando 96.7% de precisión tras el fine-tuning de ViT y RoBERTa.
                </p>
              </div>
              <div className="ficha-vecinal p-6">
                <span className="rotulo text-corteza">Impacto Ciudadano</span>
                <h4 className="mt-2 text-base font-bold">Trazabilidad de Punto a Fin</h4>
                <p className="mt-2 text-xs leading-relaxed text-corteza-suave">
                  Cada reporte tiene ciclo de vida comprobable (Reportado ➔ En Proceso ➔ Resuelto) y geolocalización activa para actuar con cuadrillas y vecinos en cuestión de minutos.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Red Multimodal */}
        {tabActiva === 'red_neuronal' && (
          <div className="space-y-8">
            <div className="ficha-vecinal p-6 sm:p-8">
              <span className="rotulo text-terracota">Ingeniería de Deep Learning</span>
              <h2 className="mt-1 text-2xl font-extrabold tracking-tight">
                Arquitectura ViT + RoBERTa con Fusión por Cross-Attention
              </h2>
              <p className="mt-2 text-sm text-corteza-suave max-w-3xl">
                La hipótesis central del proyecto es que la clasificación de situaciones animales en la vía pública mejora sustancialmente cuando el modelo relaciona simultáneamente la evidencia fotográfica con el relato testimonial del vecino.
              </p>

              {/* Flow Schema */}
              <div className="mt-8 grid gap-4 lg:grid-cols-4">
                <div className="border border-borde-fuerte rounded-lg p-5 bg-lino">
                  <span className="font-mono text-xs font-bold text-salvia block">1. VISIÓN</span>
                  <h4 className="mt-1 text-sm font-bold">Vision Transformer (ViT)</h4>
                  <p className="mt-2 text-xs text-corteza-suave">
                    Imagen de 224x224 dividida en parches de 16x16. Genera 197 tokens visuales de 768 dimensiones.
                  </p>
                  <div className="mt-3 font-mono text-[11px] text-corteza bg-lino-alto p-2 rounded border border-borde-suave">
                    ViT-Base/16 (Google)
                  </div>
                </div>

                <div className="border border-borde-fuerte rounded-lg p-5 bg-lino">
                  <span className="font-mono text-xs font-bold text-terracota block">2. LENGUAJE</span>
                  <h4 className="mt-1 text-sm font-bold">RoBERTa-BNE</h4>
                  <p className="mt-2 text-xs text-corteza-suave">
                    Procesador de lenguaje natural en español. Tokeniza y captura semántica de extravío, urgencia y señas.
                  </p>
                  <div className="mt-3 font-mono text-[11px] text-corteza bg-lino-alto p-2 rounded border border-borde-suave">
                    PlanTL RoBERTa Base BNE
                  </div>
                </div>

                <div className="border-2 border-terracota rounded-lg p-5 bg-terracota-50">
                  <span className="font-mono text-xs font-bold text-terracota block">3. FUSIÓN ATENCIONAL</span>
                  <h4 className="mt-1 text-sm font-bold">Cross-Attention</h4>
                  <p className="mt-2 text-xs text-corteza-suave">
                    Query = Texto. Key / Value = Imagen. 8 cabezas de atención cruzada que interrogan los parches visuales.
                  </p>
                  <div className="mt-3 font-mono text-[11px] text-terracota-700 bg-white p-2 rounded border border-terracota-200">
                    CrossAttentionFusion(768d)
                  </div>
                </div>

                <div className="border border-borde-fuerte rounded-lg p-5 bg-lino">
                  <span className="font-mono text-xs font-bold text-corteza block">4. DECISIÓN</span>
                  <h4 className="mt-1 text-sm font-bold">MLP Classification Head</h4>
                  <p className="mt-2 text-xs text-corteza-suave">
                    Linear 768 ➔ 512 (GELU) ➔ 256 (GELU) ➔ 6 Clases logits con dropout del 30% y 20%.
                  </p>
                  <div className="mt-3 font-mono text-[11px] text-corteza bg-lino-alto p-2 rounded border border-borde-suave">
                    Softmax ➔ Probabilidades
                  </div>
                </div>
              </div>

              {/* Code Snippet highlight */}
              <div className="mt-8 rounded-lg border border-corteza bg-corteza p-5 text-lino-alto font-mono text-xs overflow-x-auto">
                <div className="text-terracota-200 pb-2 border-b border-corteza-suave mb-3">
                  // ml/models/multimodal.py · Forward pass con Cross-Attention
                </div>
                <pre>{`visual_tokens = self.vit(pixel_values)                       # (B, 197, 768)
text_tokens   = self.roberta(input_ids, attention_mask)      # (B, seq_len, 768)

# Fusión: El texto 'interroga' a los parches de la imagen
fused_features = self.fusion(text_tokens=text_tokens, visual_tokens=visual_tokens)

# Mean pooling enmascarado sobre la longitud de texto
pooled = (fused_features * mask).sum(dim=1) / mask.sum(dim=1)  # (B, 768)
logits = self.classifier(pooled)                               # (B, 6 clases)`}</pre>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Taxonomía */}
        {tabActiva === 'taxonomia' && (
          <div className="space-y-6">
            <div className="ficha-vecinal p-6">
              <span className="rotulo text-salvia">Taxonomía Operativa Oficial</span>
              <h2 className="mt-1 text-2xl font-extrabold tracking-tight">
                6 Categorías de Intervención en Bienestar Animal
              </h2>
              <p className="mt-2 text-sm text-corteza-suave max-w-3xl">
                Cada etiqueta predicha por la red neuronal desencadena una prioridad de respuesta municipal y comunitaria según el riesgo vital del animal.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[
                {
                  id: 'animal_perdido',
                  nombre: 'Animal Perdido',
                  prio: 'Media',
                  prioClass: 'bg-ambar-50 text-ambar border-ambar',
                  icono: 'lupa' as const,
                  desc: 'Mascota que escapó de su hogar o tutor. Activa alerta vecinal, pin terracota en mapa y cotejo fotográfico con animales en tránsito.',
                },
                {
                  id: 'animal_encontrado',
                  nombre: 'Animal Encontrado',
                  prio: 'Media',
                  prioClass: 'bg-ambar-50 text-ambar border-ambar',
                  icono: 'corazon' as const,
                  desc: 'Animal avistado o retenido temporalmente por un vecino. Permite cruzar señas con personas que buscan en el mismo radio.',
                },
                {
                  id: 'animal_suelto',
                  nombre: 'Animal Suelto',
                  prio: 'Media',
                  prioClass: 'bg-ambar-50 text-ambar border-ambar',
                  icono: 'pata' as const,
                  desc: 'Canino o felino deambulando en la vía pública sin tutor inmediato. Registra cuadrante para monitoreo barrial y vacunación.',
                },
                {
                  id: 'animal_en_riesgo',
                  nombre: 'Animal en Riesgo',
                  prio: 'Alta',
                  prioClass: 'bg-coral-50 text-coral border-coral',
                  icono: 'atencion' as const,
                  desc: 'Situación de peligro inminente: animal en zanja, atrapado en rejas, en ruta o en condiciones climáticas extremas.',
                },
                {
                  id: 'posible_animal_herido',
                  nombre: 'Posible Animal Herido',
                  prio: 'Alta',
                  prioClass: 'bg-coral-50 text-coral border-coral',
                  icono: 'mira' as const,
                  desc: 'Traumatismos, atropellos o heridas visibles. Dispara notificación prioritaria para asistencia veterinaria de urgencia.',
                },
                {
                  id: 'abandono',
                  nombre: 'Abandono',
                  prio: 'Alta',
                  prioClass: 'bg-coral-50 text-coral border-coral',
                  icono: 'hoja' as const,
                  desc: 'Camadas en cajas, animales atados o abandonados en descampados. Requiere tránsito de urgencia y articulación con refugio.',
                },
              ].map((item) => (
                <div key={item.id} className="ficha-vecinal p-5 flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-center">
                      <span className="font-mono text-xs text-corteza-clara">{item.id}</span>
                      <span className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded border ${item.prioClass}`}>
                        Prioridad {item.prio}
                      </span>
                    </div>
                    <div className="mt-3 flex items-center gap-2">
                      <span className="grid size-8 place-items-center rounded bg-lino text-corteza">
                        <Icono nombre={item.icono} className="size-4" />
                      </span>
                      <h4 className="text-base font-bold text-corteza">{item.nombre}</h4>
                    </div>
                    <p className="mt-3 text-xs leading-relaxed text-corteza-suave">{item.desc}</p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-borde-suave flex items-center justify-between text-[11px] font-mono text-corteza-clara">
                    <span>Muestras: 100 curadas</span>
                    <span>Confidence &gt; 55%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 4: Ecosistema Territorial */}
        {tabActiva === 'ecosistema' && (
          <div className="space-y-8">
            <div className="grid gap-6 md:grid-cols-2">
              <div className="ficha-vecinal p-6">
                <div className="flex items-center gap-2 text-salvia">
                  <Icono nombre="qr" className="size-5" />
                  <span className="rotulo text-salvia">Trazabilidad Inteligente</span>
                </div>
                <h3 className="mt-2 text-xl font-extrabold">REMUM: Registro Municipal de Mascotas</h3>
                <p className="mt-2 text-xs leading-relaxed text-corteza-suave">
                  Cada animal registrado en el municipio cuenta con una credencial física con código QR inalterable. El escaneo con cualquier teléfono móvil revela de inmediato la ficha médica, los contactos de emergencia y el estado de la mascota.
                </p>
                <div className="mt-4 space-y-3">
                  <div className="flex items-start gap-2 text-xs">
                    <span className="font-bold text-salvia">▪</span>
                    <span><strong>Botón de Pánico GPS:</strong> Si el tutor activa el aviso de pérdida, el navegador captura al instante la geolocalización precisa e impacta el mapa de búsqueda.</span>
                  </div>
                  <div className="flex items-start gap-2 text-xs">
                    <span className="font-bold text-salvia">▪</span>
                    <span><strong>Mascotas Comunitarias:</strong> Registro especial para perros barriales con padrinos asignados, control antiparasitario y seguimiento colectivo.</span>
                  </div>
                </div>
                <div className="mt-6">
                  <Link href="/remum" className="inline-flex items-center gap-2 text-xs font-bold text-salvia hover:underline">
                    Ver Registro REMUM en vivo →
                  </Link>
                </div>
              </div>

              <div className="ficha-vecinal p-6">
                <div className="flex items-center gap-2 text-terracota">
                  <Icono nombre="plano" className="size-5" />
                  <span className="rotulo text-terracota">Cartografía Viva</span>
                </div>
                <h3 className="mt-2 text-xl font-extrabold">Mapa Geoespacial San Carlos de Bolívar</h3>
                <p className="mt-2 text-xs leading-relaxed text-corteza-suave">
                  El mapa interactivo OpenStreetMap conecta las publicaciones vecinales con coordenadas exactas en la planta urbana de Bolívar.
                </p>
                <div className="mt-4 space-y-3">
                  <div className="flex items-start gap-2 text-xs">
                    <span className="font-bold text-terracota">▪</span>
                    <span><strong>Capas discriminadas:</strong> Pines terracota para búsquedas activas, verdes para mascotas en resguardo, y amarillos para comunitarios.</span>
                  </div>
                  <div className="flex items-start gap-2 text-xs">
                    <span className="font-bold text-coral">▪</span>
                    <span><strong>Alerta Sanitaria por Cebos:</strong> Mapeo geográfico de alertas de cebos sospechosos o envenenamientos para advertir a paseadores.</span>
                  </div>
                </div>
                <div className="mt-6">
                  <Link href="/mapa" className="inline-flex items-center gap-2 text-xs font-bold text-terracota hover:underline">
                    Explorar el mapa interactivo →
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 5: Comparativa */}
        {tabActiva === 'comparativa' && (
          <div className="ficha-vecinal overflow-hidden">
            <div className="p-6 border-b border-borde-fuerte bg-lino-alto">
              <span className="rotulo text-terracota">El Diferencial Metodológico</span>
              <h3 className="mt-1 text-2xl font-extrabold tracking-tight">
                ¿Por qué Bolívar Animal no es otra red social?
              </h3>
              <p className="mt-2 text-xs text-corteza-suave">
                El valor no está en la publicación, sino en todo lo que ocurre después: clasificación automática, auditoría humana y resolución verificada.
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-borde-fuerte bg-lino-suave font-mono">
                    <th className="p-4">Dimensión</th>
                    <th className="p-4 text-coral bg-coral-50">Red Social Convencional (Facebook/WhatsApp)</th>
                    <th className="p-4 text-salvia bg-salvia-50">Bolívar Animal (Plataforma Inteligente)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-borde-suave">
                  <tr>
                    <td className="p-4 font-bold">Estructura del Dato</td>
                    <td className="p-4 text-corteza-suave">Texto libre, confuso, sin verificación ni categorización.</td>
                    <td className="p-4 font-bold text-corteza">Formulario guiado con inferencia multimodal ViT + RoBERTa.</td>
                  </tr>
                  <tr>
                    <td className="p-4 font-bold">Geolocalización</td>
                    <td className="p-4 text-corteza-suave">"Cerca de la plaza", sin pin exacto ni coordenadas.</td>
                    <td className="p-4 font-bold text-corteza">GPS exacto sobre OpenStreetMap con radios de búsqueda.</td>
                  </tr>
                  <tr>
                    <td className="p-4 font-bold">Prioridad Operativa</td>
                    <td className="p-4 text-corteza-suave">La visibilidad depende del algoritmo de likes o difusión.</td>
                    <td className="p-4 font-bold text-corteza">Prioridad basada en gravedad real (heridos/abandono = urgente).</td>
                  </tr>
                  <tr>
                    <td className="p-4 font-bold">Cotejo Visual</td>
                    <td className="p-4 text-corteza-suave">Cada usuario debe revisar cientos de posteos manualmente.</td>
                    <td className="p-4 font-bold text-corteza">Comparación de embeddings visuales de 768d entre avisos.</td>
                  </tr>
                  <tr>
                    <td className="p-4 font-bold">Cierre del Incidente</td>
                    <td className="p-4 text-corteza-suave">Los avisos quedan abiertos por años; nadie actualiza si apareció.</td>
                    <td className="p-4 font-bold text-corteza">Ciclo de vida formal que pasa a 'RESUELTO' tras el reencuentro.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

      </div>
    </main>
  );
}
