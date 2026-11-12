import { fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import NuevoReportePage from '@/app/reportes/nuevo/page';

vi.mock('next/navigation', () => ({
  useSearchParams: () => new URLSearchParams('tipo=perdido'),
}));

afterEach(() => vi.unstubAllGlobals());

test('publica la foto y muestra la coincidencia con otro reporte perdido', async () => {
  const milo = { id: 18, pet_name: 'Milo', report_type: 'perdido', image_path: '/uploads/milo.jpg' };
  const kinoto = { id: 9, pet_name: 'Kinoto', report_type: 'perdido', image_path: '/uploads/kinoto.jpg' };
  const pedir = vi.fn(async (url: string, init?: RequestInit) => {
    const ruta = new URL(url).pathname;
    if (ruta === '/api/ai/predict') {
      expect((init?.body as FormData).get('file')).toBeInstanceOf(File);
      return Response.json({ image_path: milo.image_path, predictions: [{ label: 'animal_perdido', score: 0.9 }] });
    }
    if (ruta === '/api/reports') {
      expect(JSON.parse(init?.body as string)).toMatchObject({
        image_path: milo.image_path,
        report_type: 'perdido',
      });
      return Response.json(milo);
    }
    if (ruta === '/api/reports/18/matches') {
      return Response.json({
        matches: [{ report: kinoto, visual_similarity: 1, distance_km: 1.15, combined_score: 0.851 }],
      });
    }
    throw new Error(`Ruta inesperada: ${ruta}`);
  });
  vi.stubGlobal('fetch', pedir);
  vi.stubGlobal('localStorage', { getItem: () => null });
  vi.stubGlobal('URL', class extends URL {
    static createObjectURL = () => 'blob:foto-de-prueba';
    static revokeObjectURL = vi.fn();
  });

  const { container } = render(<NuevoReportePage />);
  const input = container.querySelector('input[type=file]');
  expect(input).toBeInTheDocument();
  fireEvent.change(input!, { target: { files: [new File(['foto'], 'milo.jpg', { type: 'image/jpeg' })] } });
  fireEvent.click(screen.getByRole('button', { name: 'Publicar aviso en Bolívar' }));

  expect(await screen.findByRole('heading', { name: /publicación subida con éxito/i })).toBeInTheDocument();
  expect(await screen.findByRole('dialog', { name: /posible coincidencia/i })).toBeInTheDocument();
  expect(await screen.findByText('Kinoto')).toBeInTheDocument();
});
