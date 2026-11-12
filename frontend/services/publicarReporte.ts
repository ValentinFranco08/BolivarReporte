import { analizar, crearReporte, obtenerMatchesMascota } from '@/lib/api';
import type { NuevoReporte, Reporte, PetMatchCandidate } from '@/models/reports';

type DatosPublicacion = Omit<NuevoReporte, 'image_path' | 'predicted_class' | 'confidence' | 'corrected_class'>;

export async function publicarReporte(
  archivo: File,
  datos: DatosPublicacion,
  token: string | null,
  alPublicar: (reporte: Reporte) => void,
): Promise<PetMatchCandidate[]> {
  let analizado = null;
  try {
    analizado = await analizar(archivo, datos.description || 'Animal');
  } catch (err) {
    console.warn('Inferencia visual preliminar no disponible, continuando:', err);
  }

  const prediccion = analizado?.predictions?.[0];
  const reporte = await crearReporte(token, {
    ...datos,
    description: datos.description || 'Reporte comunitario en Bolívar',
    image_path: analizado?.image_path || '',
    predicted_class: prediccion?.label || 'mascota',
    confidence: prediccion?.score || 0.9,
    corrected_class: null,
  });
  alPublicar(reporte);

  try {
    const resultado = await obtenerMatchesMascota(reporte.id);
    return resultado?.matches ?? [];
  } catch (err) {
    console.warn('Error al buscar matches iniciales:', err);
    return [];
  }
}
