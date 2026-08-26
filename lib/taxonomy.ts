/**
 * Espejo en cliente de `ml/taxonomy.py`. Esa es la fuente de verdad.
 * Si cambian las 23 etiquetas hoja, las áreas o las prioridades allá,
 * este archivo se actualiza a mano para que coincida.
 */

export type Area =
  | 'Infraestructura'
  | 'Higiene Urbana'
  | 'Animales'
  | 'Tránsito y Estacionamiento';

export type Estado =
  | 'reportado'
  | 'clasificado'
  | 'pendiente'
  | 'en_proceso'
  | 'resuelto'
  | 'rechazado'
  | 'duplicado'
  | 'requiere_informacion';

export type Prioridad = 'baja' | 'media' | 'alta' | 'critica';

export interface Categoria {
  /** Etiqueta hoja tal como la guarda y devuelve la API, siempre en minúscula. */
  name: string;
  area: Area;
  /** Nombre legible para mostrarle a una persona. */
  label: string;
  /** Descripción textual de `SEED_CATEGORIES` en ml/taxonomy.py. */
  description: string;
}

/** Las 23 etiquetas hoja, en el orden de LABEL_TO_IDX. */
export const CATEGORIAS: Categoria[] = [
  { name: 'abandono', area: 'Animales', label: 'Abandono de animal', description: 'Mascota abandonada recientemente' },
  { name: 'animal_en_riesgo', area: 'Animales', label: 'Animal en riesgo', description: 'Animal en situación de peligro' },
  { name: 'animal_encontrado', area: 'Animales', label: 'Animal encontrado', description: 'Mascota encontrada y retenida o avistada' },
  { name: 'animal_perdido', area: 'Animales', label: 'Animal perdido', description: 'Mascota perdida buscando a su dueño' },
  { name: 'animal_suelto', area: 'Animales', label: 'Animal suelto', description: 'Perro o animal suelto en la vía pública' },
  { name: 'arbol_caido', area: 'Infraestructura', label: 'Árbol caído', description: 'Rama o árbol caído en la vía pública' },
  { name: 'bache', area: 'Infraestructura', label: 'Bache', description: 'Bache en la vía pública' },
  { name: 'basura', area: 'Higiene Urbana', label: 'Basura', description: 'Basura suelta en la vía pública' },
  { name: 'calle_deteriorada', area: 'Infraestructura', label: 'Calle deteriorada', description: 'Calle de tierra o pavimento muy deteriorado' },
  { name: 'luminaria_danada', area: 'Infraestructura', label: 'Luminaria dañada', description: 'Foco de luz apagado o roto' },
  { name: 'microbasural', area: 'Higiene Urbana', label: 'Microbasural', description: 'Acumulación grande de basura en terrenos baldíos o esquinas' },
  { name: 'perdida_agua', area: 'Infraestructura', label: 'Pérdida de agua', description: 'Caño roto o pérdida de agua en la calle' },
  { name: 'posible_animal_herido', area: 'Animales', label: 'Posible animal herido', description: 'Animal con signos de lastimaduras o enfermedad' },
  { name: 'senalizacion_danada', area: 'Tránsito y Estacionamiento', label: 'Señalización dañada', description: 'Señal de tránsito dañada, caída o ilegible' },
  { name: 'cordon_amarillo', area: 'Tránsito y Estacionamiento', label: 'Cordón amarillo', description: 'Vehículo sobre cordón amarillo' },
  { name: 'en_medio_de_calle', area: 'Tránsito y Estacionamiento', label: 'En medio de la calle', description: 'Vehículo detenido o estacionado en medio de la calzada' },
  { name: 'obstruccion_de_entrada', area: 'Tránsito y Estacionamiento', label: 'Obstrucción de entrada', description: 'Vehículo que obstruye una entrada o garaje' },
  { name: 'sobre_vereda', area: 'Tránsito y Estacionamiento', label: 'Sobre vereda', description: 'Vehículo estacionado sobre la vereda' },
  { name: 'lugar_reservado', area: 'Tránsito y Estacionamiento', label: 'Lugar reservado', description: 'Vehículo en lugar reservado (discapacidad, carga, etc.)' },
  { name: 'lugar_prohibido', area: 'Tránsito y Estacionamiento', label: 'Lugar prohibido', description: 'Vehículo en zona de estacionamiento prohibido' },
  { name: 'vehiculo_abandonado', area: 'Tránsito y Estacionamiento', label: 'Vehículo abandonado', description: 'Vehículo aparentemente abandonado en la vía pública' },
  { name: 'obstruccion_de_circulacion', area: 'Tránsito y Estacionamiento', label: 'Obstrucción de circulación', description: 'Objeto o vehículo que bloquea la circulación' },
  { name: 'semaforo_danado', area: 'Tránsito y Estacionamiento', label: 'Semáforo dañado', description: 'Semáforo apagado, caído o fuera de servicio' },
];

export const AREAS: Area[] = [
  'Infraestructura',
  'Higiene Urbana',
  'Animales',
  'Tránsito y Estacionamiento',
];

export const ESTADOS: Estado[] = [
  'reportado',
  'clasificado',
  'pendiente',
  'en_proceso',
  'resuelto',
  'rechazado',
  'duplicado',
  'requiere_informacion',
];

export const PRIORIDADES: Prioridad[] = ['baja', 'media', 'alta', 'critica'];

/** Texto legal obligatorio. Copia literal de DISCLAIMER en ml/taxonomy.py. */
export const DISCLAIMER =
  'La IA clasifica la situación a partir de la foto y el texto. No determina una infracción legal; eso corresponde a la normativa municipal.';

const POR_NOMBRE = new Map(CATEGORIAS.map((c) => [c.name, c]));

/**
 * Las etiquetas del checkpoint vienen con prefijo de carpeta
 * (`urban_bache`, `animals_abandono`, `transit_sobre_vereda`).
 */
export function normalizarEtiqueta(label: string): string {
  return label.replace(/^(urban|animals|transit)_/, '');
}

export function buscarCategoria(label: string | null | undefined): Categoria | null {
  if (!label) return null;
  return POR_NOMBRE.get(normalizarEtiqueta(label)) ?? null;
}

/** Nombre legible de una etiqueta, con reserva para valores que no estén en la taxonomía. */
export function etiquetaLegible(label: string | null | undefined): string {
  if (!label) return 'Sin categoría';
  const categoria = buscarCategoria(label);
  if (categoria) return categoria.label;
  const limpia = normalizarEtiqueta(label).replace(/_/g, ' ');
  return limpia.charAt(0).toUpperCase() + limpia.slice(1);
}

export function areaDeEtiqueta(label: string | null | undefined): Area | null {
  return buscarCategoria(label)?.area ?? null;
}

/** Estados en palabras que una persona lee sin traducir. */
export const ESTADO_LABEL: Record<Estado, string> = {
  reportado: 'Reportado',
  clasificado: 'Clasificado',
  pendiente: 'Pendiente',
  en_proceso: 'En proceso',
  resuelto: 'Resuelto',
  rechazado: 'Rechazado',
  duplicado: 'Duplicado',
  requiere_informacion: 'Requiere información',
};

/** Lo que el estado significa para el vecino que espera una respuesta. */
export const ESTADO_EXPLICACION: Record<Estado, string> = {
  reportado: 'Quedó registrado y espera revisión municipal.',
  clasificado: 'Ya tiene área y categoría asignadas.',
  pendiente: 'Revisado y en espera de cuadrilla.',
  en_proceso: 'Hay trabajo en curso sobre este reporte.',
  resuelto: 'El municipio marcó la situación como resuelta.',
  rechazado: 'El municipio no le dio curso.',
  duplicado: 'Ya existía otro reporte de la misma situación.',
  requiere_informacion: 'Falta un dato para poder avanzar.',
};

export const PRIORIDAD_LABEL: Record<Prioridad, string> = {
  baja: 'Baja',
  media: 'Media',
  alta: 'Alta',
  critica: 'Crítica',
};

export function esEstado(valor: string): valor is Estado {
  return (ESTADOS as string[]).includes(valor);
}

export function esPrioridad(valor: string): valor is Prioridad {
  return (PRIORIDADES as string[]).includes(valor);
}
