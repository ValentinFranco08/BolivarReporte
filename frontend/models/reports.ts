import type { Estado, Prioridad } from '@/lib/taxonomy';

export interface CategoriaAPI {
  id?: number;
  name: string;
  area: string;
  description?: string | null;
  is_verified?: boolean;
  sample_count?: number;
}

export interface PrediccionAPI {
  id: number;
  predicted_class: string;
  confidence: number;
}

export type TipoReporteAnimal = 'perdido' | 'encontrado' | 'alerta_cebo' | 'en_transito' | 'adopcion' | 'comunitario';
export type TipoMascota = 'perro' | 'gato' | 'otro';
export type EstadoSaludMascota = 'sano' | 'lastimado' | 'sintomas_envenenamiento' | 'con_collar';

export interface Reporte {
  id: number;
  description: string | null;
  image_path: string;
  additional_photos?: { image_path: string }[];
  status: Estado;
  priority: Prioridad;
  address: string | null;
  latitude: number | null;
  longitude: number | null;
  created_at: string;
  is_novel_category?: boolean;
  category: CategoriaAPI | null;
  prediction: PrediccionAPI | null;
  report_type?: TipoReporteAnimal;
  pet_type?: TipoMascota;
  pet_name?: string | null;
  pet_breed?: string | null;
  color_description?: string | null;
  health_status?: EstadoSaludMascota;
  contact_name?: string | null;
  contact_phone?: string | null;
  is_resolved?: boolean;
}

export interface PetMatchCandidate {
  report: Reporte;
  visual_similarity: number;
  semantic_similarity?: number | null;
  distance_km: number;
  combined_score: number;
  query_image_path?: string | null;
  matched_image_path?: string | null;
}

export interface PetMatchResponse {
  matches: PetMatchCandidate[];
  review_candidates?: PetMatchCandidate[];
  total_checked: number;
}

export interface NuevoReporte {
  description: string;
  image_path: string;
  additional_image_paths?: string[];
  predicted_class: string;
  confidence: number;
  corrected_class: string | null;
  latitude: number | null;
  longitude: number | null;
  address: string | null;
  is_novel_category?: boolean;
  suggested_area?: string;
  embedding?: number[] | null;
  report_type?: TipoReporteAnimal;
  pet_type?: TipoMascota;
  pet_name?: string | null;
  pet_breed?: string | null;
  color_description?: string | null;
  health_status?: EstadoSaludMascota;
  contact_name?: string | null;
  contact_phone?: string | null;
}
