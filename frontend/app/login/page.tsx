'use client';

import React, { Suspense, useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { Aviso, Boton, CampoTexto } from '@/components/ui/primitivas';
import { Icono } from '@/components/ui/Icono';
import { ErrorAPI, guardarToken, login } from '@/lib/api';

function FormularioLogin() {
  const router = useRouter();
  const params = useSearchParams();
  const volver = params.get('volver') ?? '/reportes/nuevo';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const entrar = async (e: React.FormEvent) => {
    e.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      guardarToken(await login(email, password));
      router.push(volver);
    } catch (err) {
      setError(
        err instanceof ErrorAPI && err.status === 401
          ? 'Ese email y contraseña no coinciden. Revisalos e intentá de nuevo.'
          : err instanceof ErrorAPI
            ? err.message
            : 'No pudimos iniciar tu sesión.',
      );
    } finally {
      setEnviando(false);
    }
  };

  return (
    <form onSubmit={entrar} className="mt-6 space-y-4">
      {error ? <Aviso tono="error">{error}</Aviso> : null}

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
        autoComplete="current-password"
        required
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <Boton type="submit" cargando={enviando} tamano="grande" anchoCompleto>
        {enviando ? 'Entrando…' : 'Entrar'}
      </Boton>
    </form>
  );
}

export default function Login() {
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
            Entrá a tu cuenta
          </h1>
          <p className="mt-2 text-[0.9375rem] leading-relaxed text-grafito-600">
            Necesitás una cuenta para que tu reporte quede con seguimiento.
          </p>

          <Suspense
            fallback={<div className="mt-6 h-64 rounded-hoja border border-grafito-100 bg-papel" />}
          >
            <FormularioLogin />
          </Suspense>

          <p className="mt-6 border-t border-grafito-200 pt-5 text-[0.875rem] text-grafito-600">
            ¿Todavía no tenés cuenta?{' '}
            <Link
              href="/registro"
              className="font-medium text-tinta-700 underline decoration-tinta-200 hover:decoration-tinta-600"
            >
              Creá una acá
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
