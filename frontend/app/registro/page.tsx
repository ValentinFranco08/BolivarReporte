'use client';

import React, { Suspense, useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { Aviso, Boton, CampoTexto } from '@/components/ui/primitivas';
import { Icono } from '@/components/ui/Icono';
import { ErrorAPI, guardarToken, login, registrar } from '@/lib/api';

const MIN_PASSWORD = 8;

function FormularioRegistro() {
  const router = useRouter();
  const params = useSearchParams();
  const volver = params.get('volver') ?? '/reportes/nuevo';

  const [nombre, setNombre] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorPassword, setErrorPassword] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const crear = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password.length < MIN_PASSWORD) {
      setErrorPassword(`Usá al menos ${MIN_PASSWORD} caracteres.`);
      return;
    }
    setErrorPassword(null);
    setEnviando(true);
    setError(null);

    try {
      await registrar(nombre, email, password);
      // Entramos solos: el vecino no debería tener que loguearse dos veces.
      try {
        guardarToken(await login(email, password));
        router.push(volver);
      } catch {
        router.push(`/login?volver=${encodeURIComponent(volver)}`);
      }
    } catch (err) {
      setError(
        err instanceof ErrorAPI ? err.message : 'No pudimos crear tu cuenta.',
      );
      setEnviando(false);
    }
  };

  return (
    <form onSubmit={crear} className="mt-6 space-y-4">
      {error ? <Aviso tono="error">{error}</Aviso> : null}

      <CampoTexto
        etiqueta="Nombre y apellido"
        type="text"
        name="name"
        autoComplete="name"
        required
        value={nombre}
        onChange={(e) => setNombre(e.target.value)}
      />
      <CampoTexto
        etiqueta="Email"
        type="email"
        name="email"
        autoComplete="email"
        required
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <CampoTexto
        etiqueta="Contraseña"
        type="password"
        name="password"
        autoComplete="new-password"
        required
        minLength={MIN_PASSWORD}
        ayuda={`Mínimo ${MIN_PASSWORD} caracteres.`}
        error={errorPassword}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <Boton type="submit" cargando={enviando} tamano="grande" anchoCompleto>
        {enviando ? 'Creando tu cuenta…' : 'Crear cuenta'}
      </Boton>
    </form>
  );
}

export default function Registro() {
  return (
    <main className="mensura-mayor flex flex-1 items-center justify-center px-5 py-12">
      <div className="motion-safe:desplegar w-full max-w-md">
        <Link
          href="/"
          className="mb-5 inline-flex items-center gap-2 text-[0.875rem] text-tinta-700 underline decoration-tinta-200 hover:decoration-tinta-600"
        >
          <Icono nombre="flecha-izquierda" className="size-4" />
          Volver al inicio
        </Link>

        <div className="rounded-hoja border border-grafito-200 bg-papel-alto px-6 py-7 shadow-[0_1px_2px_rgba(16,20,24,0.06),0_8px_20px_-6px_rgba(16,20,24,0.14)] sm:px-8 sm:py-9">
          <h1 className="text-2xl font-bold tracking-[-0.02em] text-grafito-900">
            Creá tu cuenta
          </h1>
          <p className="mt-2 text-[0.9375rem] leading-relaxed text-grafito-600">
            Es para que puedas seguir tus reportes y que el municipio sepa a quién
            responder.
          </p>

          <Suspense
            fallback={<div className="mt-6 h-80 rounded-hoja border border-grafito-100 bg-papel" />}
          >
            <FormularioRegistro />
          </Suspense>

          <p className="mt-6 border-t border-grafito-200 pt-5 text-[0.875rem] text-grafito-600">
            ¿Ya tenés cuenta?{' '}
            <Link
              href="/login"
              className="font-medium text-tinta-700 underline decoration-tinta-200 hover:decoration-tinta-600"
            >
              Entrá acá
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
