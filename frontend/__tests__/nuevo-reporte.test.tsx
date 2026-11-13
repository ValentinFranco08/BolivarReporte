import { fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import NuevoReportePage from '@/app/reportes/nuevo/page';

vi.mock('next/navigation', () => ({
  useSearchParams: () => new URLSearchParams('tipo=perdido'),
}));

afterEach(() => vi.unstubAllGlobals());

test.each(['coincidencia', 'revisión', 'vacío'])('publica la foto y muestra el cotejo (%s)', async (resultado) => {
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
        matches: resultado === 'coincidencia'
          ? [{ report: kinoto, visual_similarity: 1, distance_km: 1.15, combined_score: 0.851 }]
          : [],
        review_candidates: resultado === 'revisión'
          ? [{ report: { ...kinoto, contact_phone: '123' }, visual_similarity: 0.714, distance_km: 1.15 }]
          : [],
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
  if (resultado === 'coincidencia') {
    expect(await screen.findByRole('dialog', { name: /posible coincidencia/i })).toBeInTheDocument();
    expect(await screen.findByText('Kinoto')).toBeInTheDocument();
    expect(screen.getByText('100% de similitud visual')).toBeInTheDocument();
    expect(screen.queryByText(/85%/)).not.toBeInTheDocument();
  } else if (resultado === 'revisión') {
    fireEvent.click(await screen.findByRole('button', { name: 'Revisar avisos de similitud baja' }));
    expect(await screen.findByRole('dialog', { name: /similitud baja/i })).toBeInTheDocument();
    expect(screen.getByText('71,4% de similitud visual')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /confirmar recuperación/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /whatsapp/i })).not.toBeInTheDocument();
  } else {
    expect(await screen.findByText('Todavía no encontramos coincidencias visuales.')).toBeInTheDocument();
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  }
});
