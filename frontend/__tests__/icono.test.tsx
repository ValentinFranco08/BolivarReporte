import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Icono } from '../components/ui/Icono'

describe('Icono Component', () => {
  it('renders without a title by default (aria-hidden)', () => {
    const { container } = render(<Icono nombre="camara" />)
    const svg = container.querySelector('svg')
    expect(svg).toBeInTheDocument()
    expect(svg).toHaveAttribute('aria-hidden', 'true')
  })

  it('renders a title when provided and removes aria-hidden', () => {
    render(<Icono nombre="camara" titulo="Icono de cámara" />)
    const svg = screen.getByRole('img', { name: /icono de cámara/i })
    expect(svg).toBeInTheDocument()
    expect(svg).not.toHaveAttribute('aria-hidden')
    expect(screen.getByText('Icono de cámara')).toBeInTheDocument()
  })
})
