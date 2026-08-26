/**
 * Única puerta de salida al backend. Antes había 13 `http://localhost:8000`
 * escritos a mano; ahora la URL vive en NEXT_PUBLIC_API_URL.
 */

import type { Estado, Prioridad } from './taxonomy';

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '') ?? 'http://localhost:8000';

/** `image_path` viene relativo (`/uploads/<uuid>.jpg`); el host lo compone el cliente. */
export function urlDeImagen(imagePath: string | null | undefined): string | null {
  if (!imagePath) return null;
  if (/^https?:\/\//.test(imagePath)) return imagePath;
  return `${API_URL}${imagePath.startsWith('/') ? '' : '/'}${imagePath}`;
}

// ─── Tipos de la API ──────────────────────────────────────────────────────────

export interface CategoriaAPI {
  id?: number;
  name: string;
  area: string;
  description?: string | null;
}

export interface PrediccionAPI {
  id: number;
  predicted_class: string;
  confidence: number;
}

export interface Reporte {
  id: number;
  description: string | null;
  image_path: string;
  status: Estado;
  priority: Prioridad;
  address: string | null;
  latitude: number | null;
  longitude: number | null;
  created_at: string;
  category: CategoriaAPI | null;
  prediction: PrediccionAPI | null;
}

export interface Clasificacion {
  category: string;
  subcategory: string;
  type: string;
  label: string;
  confidence: number;
  requires_review: boolean;
  priority: string;
  legal_status: string;
  disclaimer: string;
}

export interface PrediccionCruda {
  label: string;
  score: number;
}

export interface RespuestaPrediccion {
  predictions: PrediccionCruda[];
  classification?: Clasificacion;
  model_version: string;
  image_path: string;
}

export interface Usuario {
  id: number;
  name: string;
  email: string;
  role: 'citizen' | 'admin';
}

// ─── Errores ──────────────────────────────────────────────────────────────────

export class ErrorAPI extends Error {
  readonly status: number;
  constructor(mensaje: string, status: number) {
    super(mensaje);
    this.name = 'ErrorAPI';
    this.status = status;
  }
}

/** Mensajes que nombran el problema y la salida, nunca un código pelado. */
function mensajeSegunEstado(status: number, detalle?: string): string {
  if (detalle) return detalle;
  if (status === 401) return 'Tu sesión venció. Volvé a entrar.';
  if (status === 403) return 'Tu cuenta no tiene permiso para esta acción.';
  if (status === 404) return 'No encontramos lo que buscabas.';
  if (status === 413) return 'La foto es muy grande. Probá con una más liviana.';
  if (status >= 500) return 'El servidor no respondió. Probá de nuevo en un minuto.';
  return 'No pudimos completar la operación.';
}

async function extraerDetalle(res: Response): Promise<string | undefined> {
  try {
    const cuerpo = await res.json();
    const detail = cuerpo?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail) && typeof detail[0]?.msg === 'string') return detail[0].msg;
  } catch {
    // Sin cuerpo JSON: usamos el mensaje por estado.
  }
  return undefined;
}

async function pedir<T>(ruta: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${ruta}`, init);
  } catch {
    throw new ErrorAPI('No pudimos conectar con el servidor. Revisá tu conexión.', 0);
  }
  if (!res.ok) {
    throw new ErrorAPI(mensajeSegunEstado(res.status, await extraerDetalle(res)), res.status);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ─── Sesión ───────────────────────────────────────────────────────────────────

const CLAVE_TOKEN = 'token';

export function leerToken(): string | null {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem(CLAVE_TOKEN);
}

export function guardarToken(token: string): void {
  window.localStorage.setItem(CLAVE_TOKEN, token);
}

export function borrarToken(): void {
  window.localStorage.removeItem(CLAVE_TOKEN);
}

function conAuth(token: string, extra?: HeadersInit): HeadersInit {
  return { ...extra, Authorization: `Bearer ${token}` };
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

/** El login es form-urlencoded y el email viaja en `username` (OAuth2PasswordRequestForm). */
export async function login(email: string, password: string): Promise<string> {
  const cuerpo = new URLSearchParams({ username: email, password });
  const data = await pedir<{ access_token: string }>('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: cuerpo.toString(),
  });
  return data.access_token;
}

export function registrar(name: string, email: string, password: string): Promise<Usuario> {
  return pedir<Usuario>('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  });
}

export function usuarioActual(token: string): Promise<Usuario> {
  return pedir<Usuario>('/api/auth/me', { headers: conAuth(token) });
}

// ─── Reportes ─────────────────────────────────────────────────────────────────

/** Devuelve un array plano: la API no envuelve en paginación. */
export function listarReportes(): Promise<Reporte[]> {
  return pedir<Reporte[]>('/api/reports', { cache: 'no-store' });
}

export function analizar(file: File, texto: string): Promise<RespuestaPrediccion> {
  const form = new FormData();
  form.append('file', file);
  form.append('text', texto);
  return pedir<RespuestaPrediccion>('/api/ai/predict', { method: 'POST', body: form });
}

export interface NuevoReporte {
  description: string;
  image_path: string;
  predicted_class: string;
  confidence: number;
  corrected_class: string | null;
  latitude: number | null;
  longitude: number | null;
  address: string | null;
}

export function crearReporte(token: string, reporte: NuevoReporte): Promise<Reporte> {
  return pedir<Reporte>('/api/reports', {
    method: 'POST',
    headers: conAuth(token, { 'Content-Type': 'application/json' }),
    body: JSON.stringify(reporte),
  });
}

export function actualizarReporte(
  token: string,
  id: number,
  cambios: { status?: Estado; priority?: Prioridad },
): Promise<Reporte> {
  return pedir<Reporte>(`/api/reports/${id}`, {
    method: 'PATCH',
    headers: conAuth(token, { 'Content-Type': 'application/json' }),
    body: JSON.stringify(cambios),
  });
}

export function enviarCorreccion(
  token: string,
  prediccionId: number,
  correcta: boolean,
  claseCorrecta: string | null,
): Promise<unknown> {
  return pedir(`/api/predictions/${prediccionId}/feedback`, {
    method: 'POST',
    headers: conAuth(token, { 'Content-Type': 'application/json' }),
    body: JSON.stringify({ correct: correcta, correct_class: correcta ? null : claseCorrecta }),
  });
}

// ─── Geolocalización ──────────────────────────────────────────────────────────

/** Reverse geocoding con Nominatim para mostrar una dirección legible. */
export async function direccionDesdeCoords(lat: number, lng: number): Promise<string> {
  const reserva = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&addressdetails=1`,
      { headers: { 'Accept-Language': 'es' } },
    );
    if (!res.ok) return reserva;
    const geo = await res.json();
    const dir = geo?.address ?? {};
    const calle = dir.road || dir.pedestrian || dir.footway || '';
    const altura = dir.house_number || '';
    const localidad = dir.city || dir.town || dir.village || '';
    const legible = [calle, altura].filter(Boolean).join(' ');
    return legible || localidad || geo?.display_name || reserva;
  } catch {
    return reserva;
  }
}
