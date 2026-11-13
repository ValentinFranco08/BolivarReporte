import { analizar, crearReporte, obtenerMatchesMascota } from '@/lib/api';
import type { NuevoReporte, Reporte, PetMatchResponse } from '@/models/reports';

type DatosPublicacion = Omit<NuevoReporte, 'image_path' | 'additional_image_paths' | 'predicted_class' | 'confidence' | 'corrected_class'>;

export async function publicarReporte(
  archivo: File,
  datos: DatosPublicacion,
  token: string | null,
  alPublicar: (reporte: Reporte) => void,
  fotosAdicionales: File[] = [],
): Promise<PetMatchResponse | null> {
  const analizado = await analizar(archivo, datos.description || 'Animal');
  if (!analizado?.image_path) {
    throw new Error('No se pudo subir la foto principal.');
  }
  const fotos = await Promise.all(fotosAdicionales.map(foto => analizar(foto, '')));
  if (fotos.some(foto => !foto.image_path)) {
    throw new Error('No se pudo subir una de las fotos adicionales.');
  }
  const prediccion = analizado?.predictions?.[0];
  const reporte = await crearReporte(token, {
    ...datos,
    description: datos.description || 'Reporte comunitario en Bolívar',
    image_path: analizado.image_path,
    additional_image_paths: fotos.map(foto => foto.image_path),
    predicted_class: prediccion?.label || 'mascota',
    confidence: prediccion?.score || 0.9,
    corrected_class: null,
  });
  alPublicar(reporte);

  try {
    return await obtenerMatchesMascota(reporte.id);
  } catch (err) {
    console.warn('Error al buscar matches iniciales:', err);
    return null;
  }
}
