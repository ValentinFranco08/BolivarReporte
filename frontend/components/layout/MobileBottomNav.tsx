'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Icono } from '@/components/ui/Icono';

export function MobileBottomNav() {
  const pathname = usePathname();
  const items = [{ href: '/', label: 'Buscar', icono: 'pata' as const }, { href: '/mapa', label: 'Mapa', icono: 'plano' as const }, { href: '/reportes/nuevo', label: 'Crear', icono: 'camara' as const }, { href: '/remum', label: 'Mis datos', icono: 'credencial' as const }];
  return <nav aria-label="Navegación móvil" className="fixed inset-x-0 bottom-0 z-50 border-t border-borde-fuerte bg-lino-alto md:hidden"><div className="mx-auto grid h-16 max-w-md grid-cols-4">{items.map((item) => { const active = pathname === item.href; return <Link key={item.href} href={item.href} className={`flex flex-col items-center justify-center gap-1 text-[11px] font-semibold ${active ? 'text-terracota' : 'text-corteza-suave'}`}><span className={`grid size-8 place-items-center rounded-md ${item.href === '/reportes/nuevo' ? 'bg-terracota text-white' : active ? 'bg-terracota-50' : ''}`}><Icono nombre={item.icono} className="size-5" /></span>{item.label}</Link>; })}</div></nav>;
}
