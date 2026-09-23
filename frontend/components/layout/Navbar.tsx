'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Icono } from '@/components/ui/Icono';

export function Navbar() {
  const pathname = usePathname();
  const links = [{ href: '/', label: 'Buscar', icono: 'pata' as const }, { href: '/mapa', label: 'Mapa', icono: 'plano' as const }, { href: '/remum', label: 'Identificación', icono: 'credencial' as const }, { href: '/sos', label: 'SOS', icono: 'atencion' as const }];
  return <header className="sticky top-0 z-40 border-b border-borde-fuerte bg-lino-alto"><div className="mx-auto flex min-h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
    <Link href="/" className="flex items-center gap-3"><span className="grid size-9 place-items-center rounded-md bg-corteza text-lino-alto"><Icono nombre="pata" className="size-5" /></span><span><strong className="block text-lg font-extrabold leading-none tracking-[-.04em]">BOLÍVAR ANIMAL</strong><span className="rotulo mt-1 block">red de búsqueda vecinal</span></span></Link>
    <nav className="hidden items-center gap-1 md:flex" aria-label="Navegación principal">{links.map((link) => <Link key={link.href} href={link.href} className={`inline-flex h-10 items-center gap-2 rounded-md px-3 text-sm font-semibold ${pathname === link.href ? 'bg-corteza text-lino-alto' : link.href === '/sos' ? 'text-coral hover:bg-coral-50' : 'text-corteza hover:bg-lino-suave'}`}><Icono nombre={link.icono} className="size-4" />{link.label}</Link>)}</nav>
    <div className="flex items-center gap-2"><Link href="/dashboard" className="hidden size-10 place-items-center rounded-md border border-borde-fuerte text-corteza hover:bg-lino sm:grid" title="Mesa operativa"><Icono nombre="regla" className="size-4" /></Link><Link href="/reportes/nuevo" className="boton-principal inline-flex h-11 items-center gap-2 px-4 text-sm"><Icono nombre="camara" className="size-4" /><span className="hidden sm:inline">Crear aviso</span><span className="sm:hidden">Crear</span></Link></div>
  </div></header>;
}
