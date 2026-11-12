'use client';

import { useEffect, useState, type ChangeEvent, type FormEvent } from 'react';
import { direccionDesdeCoords, ErrorAPI, leerToken } from '@/lib/api';
import type { PetMatchCandidate, Reporte, TipoMascota, TipoReporteAnimal } from '@/models/reports';
import { publicarReporte } from '@/services/publicarReporte';

export function useNuevoReporte(tipoInicial: TipoReporteAnimal) {
  const [tipoReporte, setTipoReporte] = useState(tipoInicial);
  const [tipoMascota, setTipoMascota] = useState<TipoMascota>('perro');
  const [nombreMascota, setNombreMascota] = useState('');
  const [raza, setRaza] = useState('');
  const [color, setColor] = useState('');
  const [contactoNombre, setContactoNombre] = useState('');
  const [contactoTelefono, setContactoTelefono] = useState('');
  const [descripcion, setDescripcion] = useState('');

  const [archivo, setArchivo] = useState<File | null>(null);
  const [vistaPrevia, setVistaPrevia] = useState<string | null>(null);
  const [lat, setLat] = useState(-36.2333);
  const [lng, setLng] = useState(-61.1167);
  const [direccion, setDireccion] = useState('San Carlos de Bolívar');
  const [gpsBuscando, setGpsBuscando] = useState(false);

  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reporteCreado, setReporteCreado] = useState<Reporte | null>(null);
  const [matchesEncontrados, setMatchesEncontrados] = useState<PetMatchCandidate[]>([]);
  const [mostrarModalMatches, setMostrarModalMatches] = useState(false);

  useEffect(() => {
    if (vistaPrevia) return () => URL.revokeObjectURL(vistaPrevia);
  }, [vistaPrevia]);

  const pedirGps = () => {
    if (!navigator.geolocation) return;
    setGpsBuscando(true);
    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        setLat(coords.latitude);
        setLng(coords.longitude);
        setGpsBuscando(false);
        const dir = await direccionDesdeCoords(coords.latitude, coords.longitude);
        if (dir) setDireccion(dir);
      },
      () => setGpsBuscando(false),
      { timeout: 8000 },
    );
  };

  const handleArchivoSeleccionado = (event: ChangeEvent<HTMLInputElement>) => {
    const foto = event.target.files?.[0];
    if (!foto) return;
    setArchivo(foto);
    setVistaPrevia(URL.createObjectURL(foto));
  };

  const quitarFoto = () => {
    setArchivo(null);
    setVistaPrevia(null);
  };

  const enviar = async (event: FormEvent) => {
    event.preventDefault();
    if (!archivo) {
      setError('Por favor, adjuntá una foto para ayudar a identificar a la mascota.');
      return;
    }
    setEnviando(true);
    setError(null);

    try {
      const matches = await publicarReporte(archivo, {
        description: descripcion,
        latitude: lat,
        longitude: lng,
        address: direccion,
        report_type: tipoReporte,
        pet_type: tipoMascota,
        pet_name: nombreMascota || undefined,
        pet_breed: raza || undefined,
        color_description: color || undefined,
        health_status: 'sano',
        contact_name: contactoNombre || undefined,
        contact_phone: contactoTelefono || undefined,
      }, leerToken(), setReporteCreado);
      setMatchesEncontrados(matches);
      setMostrarModalMatches(matches.length > 0);
    } catch (err) {
      setError(err instanceof ErrorAPI
        ? err.message
        : 'Ocurrió un error al guardar la publicación. Revisá los datos.');
    } finally {
      setEnviando(false);
    }
  };

  return {
    tipoReporte, setTipoReporte, tipoMascota, setTipoMascota, nombreMascota, setNombreMascota,
    raza, setRaza, color, setColor, contactoNombre, setContactoNombre,
    contactoTelefono, setContactoTelefono, descripcion, setDescripcion,
    vistaPrevia, quitarFoto, direccion, setDireccion, gpsBuscando, pedirGps,
    handleArchivoSeleccionado, enviar, enviando, error, reporteCreado,
    matchesEncontrados, mostrarModalMatches, setMostrarModalMatches,
  };
}
