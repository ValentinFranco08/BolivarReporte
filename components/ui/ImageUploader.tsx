'use client';

import React, { useCallback, useRef, useState } from 'react';
import { Icono } from './Icono';

interface ImageUploaderProps {
  onImageSelected: (file: File, previewUrl: string) => void;
  onError: (mensaje: string) => void;
  isLoading?: boolean;
}

const MAX_BYTES = 12 * 1024 * 1024;

/**
 * La lámina en blanco de la hoja: el lugar donde se pega la foto.
 * `capture="environment"` abre la cámara trasera directo en el teléfono, que
 * es el gesto real del vecino parado en la calle.
 */
export function ImageUploader({ onImageSelected, onError, isLoading = false }: ImageUploaderProps) {
  const [arrastrando, setArrastrando] = useState(false);
  const entrada = useRef<HTMLInputElement>(null);

  const tomarArchivo = useCallback(
    (file: File) => {
      if (!file.type.startsWith('image/')) {
        onError('Ese archivo no es una imagen. Elegí una foto.');
        return;
      }
      if (file.size > MAX_BYTES) {
        onError('La foto pesa más de 12 MB. Probá con una más liviana.');
        return;
      }
      onImageSelected(file, URL.createObjectURL(file));
    },
    [onImageSelected, onError],
  );

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setArrastrando(true);
      }}
      onDragLeave={(e) => {
        e.preventDefault();
        setArrastrando(false);
      }}
      onDrop={(e) => {
        e.preventDefault();
        setArrastrando(false);
        const file = e.dataTransfer.files?.[0];
        if (file) tomarArchivo(file);
      }}
      className={[
        'relative flex min-h-[19rem] flex-col items-center justify-center rounded-hoja border p-8 text-center transition-colors',
        arrastrando
          ? 'border-tinta-600 bg-tinta-50'
          : 'border-dashed border-grafito-200 bg-papel-alto hover:border-tinta-300 hover:bg-tinta-50/40',
        isLoading ? 'pointer-events-none opacity-60' : '',
      ].join(' ')}
    >
      {/* Escuadras de encuadre: dónde va a caer la lámina. */}
      <div aria-hidden className="pointer-events-none absolute inset-4">
        <span className="absolute left-0 top-0 size-5 border-l border-t border-tinta-600/25" />
        <span className="absolute right-0 top-0 size-5 border-r border-t border-tinta-600/25" />
        <span className="absolute bottom-0 left-0 size-5 border-b border-l border-tinta-600/25" />
        <span className="absolute bottom-0 right-0 size-5 border-b border-r border-tinta-600/25" />
      </div>

      <input
        ref={entrada}
        id="foto-del-reporte"
        type="file"
        accept="image/*"
        capture="environment"
        disabled={isLoading}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) tomarArchivo(file);
        }}
        className="sr-only"
      />

      <Icono nombre="camara" className="size-10 text-tinta-600" />

      <label
        htmlFor="foto-del-reporte"
        className="mt-6 inline-flex min-h-14 cursor-pointer items-center justify-center rounded-hoja border border-tinta-700 bg-tinta-600 px-7 text-base font-semibold text-papel-alto transition-colors hover:bg-tinta-700 active:bg-tinta-800"
      >
        Sacar o elegir una foto
      </label>

      <p className="mt-4 max-w-[34ch] text-[0.875rem] leading-relaxed text-grafito-500">
        En el teléfono se abre la cámara. En la computadora podés arrastrar la imagen
        hasta acá.
      </p>
    </div>
  );
}
