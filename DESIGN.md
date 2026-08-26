---
name: Reporte Bolívar
description: Los reportes de Bolívar como parcelas numeradas de una hoja de mensura — papel vegetal, tinta ferroprusiato y cifras monoespaciadas.
colors:
  papel: "#f4f1e8"
  papel-alto: "#fbfaf5"
  papel-hondo: "#e7e2d3"
  tinta-50: "#eef2fa"
  tinta-100: "#d9e2f4"
  tinta-200: "#b3c5e6"
  tinta-300: "#7f9dd1"
  tinta-500: "#1d4ea0"
  tinta-600: "#0b3c8c"
  tinta-700: "#082f6e"
  tinta-800: "#062350"
  grafito-100: "#dcdcd4"
  grafito-200: "#c3c3b9"
  grafito-400: "#8a8a80"
  grafito-500: "#6d6d64"
  grafito-600: "#55554e"
  grafito-900: "#101418"
  sello-100: "#f7dcd7"
  sello-500: "#c8402c"
  sello-700: "#86281a"
  visto-100: "#d7e8dc"
  visto-600: "#2f6b45"
  visto-700: "#234f34"
  margen-100: "#f6e6c8"
  margen-600: "#8a6316"
typography:
  display:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "2.5rem → 3.75rem (sm) → 4.25rem (lg)"
    fontWeight: 800
    lineHeight: 0.95
    letterSpacing: "-0.03em"
    fontVariation: "wdth 118"
  headline:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.5rem → 1.875rem (sm)"
    fontWeight: 700
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1rem–1.25rem"
    fontWeight: 600
    lineHeight: 1.375
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.8125rem–1.125rem"
    fontWeight: 400
    lineHeight: 1.625
  label:
    fontFamily: "Chivo Mono, ui-monospace, monospace"
    fontSize: "0.625rem–0.6875rem"
    fontWeight: 400
    lineHeight: 1.2
    letterSpacing: "0.1em"
  cifra:
    fontFamily: "Chivo Mono, ui-monospace, monospace"
    fontSize: "0.75rem–1.875rem"
    fontFeature: "tabular-nums"
    letterSpacing: "-0.02em"
rounded:
  hoja: "2px"
  lamina: "1px"
spacing:
  grilla: "28px"
components:
  boton-tinta:
    backgroundColor: "{colors.tinta-600}"
    textColor: "{colors.papel-alto}"
    rounded: "{rounded.hoja}"
    padding: "0 20px"
    height: "48px"
  boton-tinta-hover:
    backgroundColor: "{colors.tinta-700}"
    textColor: "{colors.papel-alto}"
    rounded: "{rounded.hoja}"
    padding: "0 20px"
    height: "48px"
  boton-contorno:
    backgroundColor: "{colors.papel-alto}"
    textColor: "{colors.tinta-700}"
    rounded: "{rounded.hoja}"
    padding: "0 20px"
    height: "48px"
  boton-sello:
    backgroundColor: "{colors.papel-alto}"
    textColor: "{colors.sello-700}"
    rounded: "{rounded.hoja}"
    padding: "0 12px"
    height: "36px"
  boton-callado:
    backgroundColor: "transparent"
    textColor: "{colors.grafito-600}"
    rounded: "{rounded.hoja}"
    padding: "0 20px"
    height: "48px"
  campo-texto:
    backgroundColor: "{colors.papel-alto}"
    textColor: "{colors.grafito-900}"
    rounded: "{rounded.hoja}"
    padding: "12px 14px"
  marca-estado:
    backgroundColor: "{colors.papel-alto}"
    textColor: "{colors.grafito-600}"
    typography: "{typography.label}"
    rounded: "{rounded.hoja}"
    padding: "2px 8px"
  lamina:
    backgroundColor: "{colors.papel-alto}"
    rounded: "{rounded.hoja}"
---

# Design System: Reporte Bolívar

## Overview

**Creative North Star: "La Hoja de Mensura"**

Reporte Bolívar se ve como una hoja de mensura catastral. Bolívar ya está dibujada como una grilla de parcelas numeradas; cada reporte es una parcela con número propio sobre esa hoja. La interfaz toma prestado el idioma de las planchas del IGN: papel vegetal con grilla visible, tinta ferroprusiato para el trazo, grafito para la anotación a lápiz, cajetines de datos en lugar de heroes, cifras de parcela en monoespaciada, fotos como láminas pegadas sobre el papel. Es un idioma técnico y descriptivo a propósito: la hoja describe una situación, nunca imputa una infracción — el descargo legal ("La IA clasifica la situación…") es texto obligatorio de la hoja, no un adorno.

Hay una sola escena de luz: papel claro, siempre. El uso real es a la intemperie, a pleno sol, con un pulgar: por eso el texto secundario tiene piso de contraste 4.5:1 (grafito-500 sobre papel), los controles miden y el estado nunca vive sólo en el color — siempre hay palabra, y la prioridad es una escala de trazos que se cuenta (1 a 4). El sistema rechaza explícitamente el portal municipal celeste con hero y tres tarjetas, el dashboard oscuro de IA, el glass, los gradientes decorativos y los kickers sobre el h1: los rótulos son etiquetas de campo dentro de cajetines, no ojos encima de títulos.

La inteligencia artificial es invisible para el vecino: ni confianza, ni top-3, ni nombres de arquitectura en las superficies públicas. Toda la maquinaria (confianza, feedback de reentrenamiento, revisión humana) vive exclusivamente en `/dashboard`. El movimiento tiene dos momentos autorizados — la hoja que se despliega y la constancia que se sella — con curva exponencial de salida y `prefers-reduced-motion` respetado de forma global. La voz tipográfica es Archivo (Omnibus-Type, Buenos Aires) con su eje de ancho estirado para el display de la hoja, y Chivo Mono reservada a la medición: números de parcela, coordenadas, rótulos de campo.

**Key Characteristics:**
- Papel vegetal como único soporte; una escena de luz, sin dark mode (`color-scheme: light`, themeColor papel).
- Grilla de mensura visible como instrumento real: paso de 28px, trazo mayor cada 5 pasos.
- Cajetín de datos (rótulo + cifra) como apertura de superficie; nunca hero con kicker.
- Estado, prioridad y área siempre con palabra; prioridad como escala contable de 1 a 4 trazos.
- Sello rojizo (#c8402c) sólo para marcar (corregir, crítica, cerrar, error de campo); nunca alarma.
- Chivo Mono mide (cifras, coordenadas, rótulos, marcas); Archivo escribe todo lo demás.
- Radios de 2px, esquinas a escuadra, marcas de registro; sin glass, sin gradientes, sin sombras duras.
- Superficies del navegador tematizadas: selection, caret, focus, scrollbar y tabular-nums en la tinta de la hoja.

## Colors

La paleta es la de una plancha técnica: tres papeles que sostienen, una tinta que trabaja, un grafito que anota, y tres colores de expediente que sólo marcan.

### Primary
- **Tinta ferroprusiato** (#0b3c8c, `tinta-600`): el trazo de la mensura. Único relleno sólido de interacción — botón primario, filtro activo, foco, selección de texto, chinchetas. Su rampa va de `tinta-50` (#eef2fa, hover y realces) a `tinta-800` (#062350, presión del botón); `tinta-700` (#082f6e) es el tono de texto azulado y el borde del botón sólido; `tinta-500` (#1d4ea0) marca prioridad media y la barra de confianza; `tinta-200`/`tinta-300` (#b3c5e6/#7f9dd1) son bordes de botón contorno y de marcas.
- **Grafito de texto** (`grafito-900` #101418, `grafito-600` #55554e, `grafito-500` #6d6d64): la anotación a lápiz. Grafito-900 es el cuerpo titular; grafito-600 el cuerpo secundario; grafito-500 es el piso de texto secundario (4.6:1 sobre papel; grafito-600 sobre papel-hondo da 5.8:1). Grafito-200/100 (#c3c3b9/#dcdcd4) son divisiones y bordes hairline; grafito-400 (#8a8a80) bordes de estado neutro.

### Secondary
- **Sello** (#c8402c, `sello-500`): sólo marca — botón "No, corregir", prioridad crítica, estado `requiere_informacion`, error de campo (borde sello-500, texto sello-700 #86281a), hover de "Salir". Con fondo `sello-100` (#f7dcd7). Nunca es alarma de denuncia.
- **Visto de expediente** (`visto-600` #2f6b45, `visto-700` #234f34, `visto-100` #d7e8dc): lo cerrado y confirmado — estado resuelto, constancia "Registrado", avisos de éxito, área Higiene Urbana.
- **Ámbar de margen** (`margen-600` #8a6316, `margen-100` #f6e6c8): anotación al margen — prioridad alta, estado pendiente, aviso de atención, confianza baja, "Requiere revisión humana".

### Neutral
- **Papel vegetal** (#f4f1e8, `papel`): el fondo del cuerpo y de la hoja.
- **Papel alto** (#fbfaf5, `papel-alto`): toda superficie de contenido — láminas, cajetines, campos, marcas.
- **Papel hondo** (#e7e2d3, `papel-hondo`): lo hundido — fondos de foto sin imagen, contenedor del mapa, hover callado.

### Named Rules
**La Regla de la Escena Única.** Una sola escena de luz: papel claro, `color-scheme: light`, themeColor #f4f1e8. No existe variante oscura ni a medio mantener; el caso difícil es la calle a pleno sol.
**La Regla del Sello.** El sello (#c8402c) sólo marca: corregir, crítica, requerir información, error de campo. Nunca encabeza una superficie ni hace de rojo de denuncia — el producto describe situaciones, no acusa vecinos.
**La Regla de la Tinta de Trabajo.** La tinta es el único relleno sólido generoso de la interfaz; todo lo demás es papel. La parquedad de la tinta es lo que hace que el obturador azul se encuentre de un vistazo al sol.

## Typography

**Display Font:** Archivo (con ui-sans-serif, system-ui, sans-serif) — variable, eje `wdth` cargado
**Body Font:** Archivo (mismo stack)
**Label/Mono Font:** Chivo Mono (con ui-monospace, monospace)

**Character:** Archivo es la voz rioplatense de la hoja: humanista, directa, sin infantilizar; estirada a 118% de ancho se vuelve la voz display de las planchas. Chivo Mono es el instrumento de medición: sólo cifras, coordenadas y rótulos de campo, nunca prosa. Ambas de Omnibus-Type, Buenos Aires.

### Hierarchy
- **Display** (800, 2.5rem→3.75rem(sm)→4.25rem(lg), leading 0.95, tracking −0.03em, `wdth 118%` vía `titulo-hoja`): el título de la portada — una voz por producto, la razón de ser del eje ancho.
- **Headline** (700, 1.5rem→1.875rem(sm), tracking −0.02em; variante 1.75rem en la ficha de clasificación): el h1 de cada superficie interior.
- **Title** (600, 1rem–1.25rem, leading 1.375, tracking −0.01em): títulos de sección, de tarjeta, de diálogo.
- **Body** (400, 0.8125rem–1.125rem, leading 1.625): prosa de la hoja; el párrafo introductorio llega a 1.125rem y al legible max-w-[42ch]–[68ch]; el texto legal baja a 0.75rem en grafito-500.
- **Label — rótulo** (Chivo Mono 400, 0.625–0.6875rem, leading 1.2, letter-spacing 0.1em, uppercase, grafito-500): etiqueta de campo de cajetín (`rotulo`), encabezados de tabla, marcas.
- **Cifra** (Chivo Mono, 0.75rem–1.875rem, `tabular-nums`, tracking −0.02em): número de parcela con ceros a la izquierda atenuados, fechas, conteos, coordenadas, porcentajes de confianza.

### Named Rules
**La Regla de la Monoespaciada que Mide.** Chivo Mono sólo aparece donde hay medición: cifras de parcela, fechas, coordenadas, rótulos de campo, marcas de estado/prioridad, encabezados de tabla, referencias del plano. Si el texto se lee como una frase, va en Archivo.
**La Regla del Eje Ancho.** El eje `wdth` de Archivo existe para el display de la hoja (`font-stretch: 118%`). El cuerpo de texto viaja a ancho normal; estirar tipografía corriente diluye la voz de portada.

## Layout

La hoja es una superficie continua de papel; el contenido se organiza en cajetines y renglones dibujados, no en tarjetas flotantes sueltas. Contenedores: `max-w-[86rem]` en superficies públicas, `max-w-[92rem]` en la cola municipal, `max-w-[68rem]` en el flujo del vecino, `max-w-md`–`max-w-2xl` en diálogos y tarjetas de sesión; margen lateral `px-5` (móvil) → `sm:px-8`. Móvil: una sola columna, un gesto por paso. `lg`: dos columnas — cajetín a la izquierda (~46%), grilla de parcelas a la derecha. La portada es hoja a sangre: cajetín de hoja arriba a la izquierda, grilla de las 4 áreas a la derecha, obturador anclado al pie con `mt-auto`, descargo legal en el borde inferior.

La grilla de mensura (`mensura`, paso 28px; `mensura-mayor`, trazo reforzado cada 5 pasos = 140px) es el armazón visible de las superficies: portada, listado, alta, dashboard, sesión abren sobre ella. Las grillas de contenido se dibujan con el truco de plancha: contenedor `border` + `gap-px` + `bg-grafito-200` con celdas `bg-papel-alto`, de modo que la separación es un trazo de 1px, no un vacío. Los cajetines de datos son `dl` con `rotulo`/`cifra` y divisores `border-b`; las filas de constancia usan `divide-y`. La tabla municipal hace scroll interno (`relative` + `overflow-x-auto`, `min-w-[54rem]`) con columnas que se ocultan progresivamente (`hidden sm:table-cell`, `lg`, `xl`). Leaflet vive dentro del mundo: teselas claras, controles re-estilados (radio 2px, borde grafito-100, mono 0.6875rem), chinchetas SVG propias por prioridad; el cajetín del plano flota en papel opaco, nunca translúcido.

Objetivos táctiles, tal como están construidos: 56px (`min-h-14`) para el obturador y CTAs principales; 48px (`min-h-12`) el estándar de la mayoría de los controles; 40px (`min-h-10`) en filtros de área y acciones secundarias compactas; 36px (`min-h-9`, tamaño `chico`) confinado al panel municipal de escritorio. Los iconos de navegación de vuelta son objetivos cuadrados `size-11` (44px) con `size-10` (40px) en el cajetín flotante del mapa.

### Named Rules
**La Regla del Cajetín.** Toda superficie abre con datos en cajetín (rótulo + cifra reales) o con un renglón de encabezado con botón de vuelta. Nunca un hero con kicker sobre el h1: los rótulos son etiquetas de campo dentro de cajetines.
**La Regla del Papel de Medir.** La grilla de mensura es un instrumento, no una textura: parcelas, renglones y tablas se apoyan en trazos dibujados de 1px (gap-px sobre grafito-200). Si un bloque no se apoya en la grilla, es una tarjeta suelta y no pertenece a esta hoja.

## Elevation & Depth

La hoja es plana; la profundidad es física, no atmosférica. Sólo se lleva sombra lo que está literalmente pegado o flotando sobre el papel: la lámina de foto, el diálogo, el cajetín flotante del plano. Las sombras son suaves, con offset corto más blur difuso, en grafito casi negro — nunca offset duro estilo neobrutalista. Cada elemento lleva una sola elevación: borde hairline (grafito-100/200) o sombra de lámina; la lámina combina un borde de 1px con la sombra suave, que es el máximo permitido. El diálogo agrega un velo `grafito-900/55` sobre la hoja. Leaflet se re-estiliza con las mismas dos sombras.

### Shadow Vocabulary
- **Lámina** (`box-shadow: 0 1px 2px rgba(16,20,24,0.06), 0 8px 20px -6px rgba(16,20,24,0.14)`): reposo — fotos, tarjetas de sesión, cajetín flotante del mapa.
- **Lámina alta** (`box-shadow: 0 2px 4px rgba(16,20,24,0.08), 0 22px 44px -12px rgba(16,20,24,0.22)`): lo elevado sobre la hoja — diálogo de gestión, popups de Leaflet.
- **Velo de diálogo** (`background: grafito-900 al 55%`): el único oscurecimiento del sistema, siempre detrás de un diálogo.

### Named Rules
**La Regla de la Hoja Plana.** El papel no proyecta sombra. La sombra es la prueba de que algo está pegado (lámina) o flotando (diálogo, cajetín del plano) — y aparece junto a un borde hairline como máximo acompañante, nunca junto a otra sombra.

## Shapes

Las esquinas se dibujan, no se redondean. Radio de hoja: 2px (`rounded-hoja`) en botones, campos, láminas, marcas, diálogos, popups; 1px (`rounded-[1px]`) reservado a lo que va enmarcado dentro de una lámina: fotos dentro del marco, miniaturas, barras de medición (prioridad, confianza). El borde es el idioma estructural: hairlines grafito-100/200 para dividir, trazos de tinta para lo interactivo (borde `tinta-200`→`tinta-300` en hover de contorno; `tinta-700` en el botón sólido). Dos dispositivos de escuadra recurren: las marcas de registro en las cuatro esquinas de la portada (spans absolutos `border-tinta-600/25`) y las escuadras de encuadre del uploader de fotos. La iconografía es dibujada: 17 iconos SVG de trazo 1.5, terminales cuadrados (`strokeLinecap: square`, `miter`), viewBox 24; la chincheta del mapa es un SVG propio con borde de papel. El uploader vacío es el único borde punteado (`border-dashed`) del sistema.

### Named Rules
**La Regla de la Escuadra.** Nada se redondea más de 2px y los trazos terminan a escuadra. Radio grande, terminal redondeado y blob son de otro mundo; la hoja se construye con regla y compás.

## Components

### Buttons
- **Shape:** esquinas de hoja (2px), borde de 1px siempre presente (tinta-700 en el sólido; tinta-200 en contorno).
- **Primary — tono tinta:** fondo tinta-600, texto papel-alto, borde tinta-700; `px-5`, min-h 48px (56px en tamaño `grande`). Hover tinta-700, activo tinta-800. Es el único relleno sólido de la superficie; uno por vista como acción principal (el obturador de la portada, "Confirmar y enviar").
- **Hover / Focus:** transición de color de 150ms, sin movimiento ni sombra; foco visible global (outline 2px tinta-600, offset 2px). En carga, el botón se deshabilita (`aria-busy`) y muestra el Compás girando en lugar de un spinner genérico.
- **Contorno:** papel-alto con texto tinta-700 y borde tinta-200 → hover tinta-50/tinta-300. **Callado:** transparente, grafito-600, hover papel-hondo. **Sello:** papel-alto con texto sello-700 y borde sello-500/40, hover sello-100 — reservado a "corregir/cerrar".
- **Tamaños:** `grande` min-h-14 (56px), `normal` min-h-12 (48px), `chico` min-h-9 (36px, sólo panel de escritorio).

### Chips
- **Marcas de estado/área:** píldora 2px, mono 0.6875rem uppercase tracking 0.08em, borde+fonso del color del expediente (papel-alto para reportado; tinta-50/300 para clasificado; margen para pendiente; visto para resuelto; sello para requiere_informacion). El área lleva su letra de plancha (I/H/A/T) en mono bold.
- **Filtro de área:** botón `aria-pressed`, min-h-10, px-3; activo se invierte a tinta-600 sólido; inactivo papel-alto con borde grafito-200. La cuenta viaja en el texto ("Todas (32)"), no en un badge.

### Cards / Containers
- **Lámina:** papel-alto, borde grafito-200 (o grafito-100 en la foto), radio 2px, sombra de lámina en reposo; padding interno variable (p-5/p-6 típico; px-6 py-7 en sesión). Las grillas de láminas se dibujan con `gap-px` sobre grafito-200 — renglones de hoja, no tarjetas sueltas.
- **Cajetín:** bloque de datos sin sombra — `dl` de rótulo+cifra con `border-b`, o fila de constancia con `divide-y`. El plano lleva cajetín flotante opaco con sombra de lámina y referencias de prioridad (punto de color + palabra).

### Inputs / Fields
- **Style:** papel-alto, borde grafito-200 (2px de radio, `px-3.5 py-3`, texto 0.9375rem), hover grafito-400, foco tinta-600. Placeholder en grafito-500. Select con chevron SVG propio y `appearance-none`.
- **Label:** rótulo mono uppercase (`rotulo`) siempre asociado por `htmlFor`/`useId`; ayuda y error conectadas con `aria-describedby`; error declara `aria-invalid` y pinta borde sello-500 con texto sello-700 + icono de atención.
- **Búsqueda de la cola:** input `search` con lupa incrustada (pl-9), mismo campo base.

### Navigation
- Navegación mínima textual: enlaces subrayados (grosor 1px, offset 0.2em) en tinta-700 con `decoration-tinta-200` → hover `tinta-600`. Botón de vuelta: cuadrado 44px con borde, icono de flecha, `titulo` accesible para lectores de pantalla. Pie de portada con nav textual y descargo legal + proveniencia académica (obligatorios, nunca decorativos). El dashboard agrega "Salir" con hover de sello.

### Marcas del cajetín (firma del sistema)
- **MarcaEstado:** la palabra del estado (8 estados, etiquetas legibles), nunca sólo color.
- **MarcaPrioridad:** escala de mensura contable — 4 barras de 3px (alturas 8/11/14/17px), llenas según prioridad (baja 1 → crítica 4), color por nivel (grafito-400, tinta-500, margen-600, sello-500) + palabra o `sr-only`. Se cuenta, no se interpreta.
- **NumeroParcela:** id real del reporte en cifra mono tabular, ceros a la izquierda atenuados en grafito-500, `sr-only` "Parcela". Hasta text-3xl en la constancia.
- **Dialogo:** `role="dialog"` + `aria-modal`, foco atrapado con Tab/Shift+Tab, cierre con Escape y clic en el velo, devolución del foco al elemento que lo abrió; entra con `desplegar`, sombra de lámina alta, cabecera papel-alto con cierre de 40px.
- **Aviso:** bloque con icono, `role="alert"` (error) o `role="status"`; tonos atención (margen), error (sello), visto.
- **ImageUploader:** lámina en blanco con escuadras de encuadre, `capture="environment"` (cámara trasera del vecino), validación de tipo y peso con mensajes que nombran el problema ("La foto pesa más de 12 MB…"), CTA sólido de 56px.
- **Iconografía:** 17 iconos dibujados (trazo 1.5, escuadra) reemplazan emojis; `aria-hidden` por defecto, `role="img"` + `<title>` cuando informan. El Compás girando (motion-safe) es el único spinner del sistema y la tercera y última pieza de movimiento.

## Do's and Don'ts

### Do:
- **Do** abrir cada superficie con cajetín o renglón de encabezado; los rótulos son etiquetas de campo dentro de cajetines, con cifras reales.
- **Do** escribir estado, prioridad y área siempre con palabra; prioridad como escala contable de 1 a 4 trazos.
- **Do** usar Chivo Mono sólo para medir (cifras, coordenadas, rótulos, marcas, encabezados de tabla) con `tabular-nums`.
- **Do** mantener un solo botón de tinta sólida por superficie como acción principal, de 56px en CTAs de la calle.
- **Do** tematizar las superficies del navegador en la tinta: selection, caret, focus-visible (outline 2px tinta-600 offset 2px), scrollbar thin grafito-200/papel, tap-highlight.
- **Do** limitar el movimiento a los dos momentos (desplegar 620ms, sellar 420ms, `cubic-bezier(0.16,1,0.3,1)`) más el compás de trabajo; siempre `motion-safe:` y el corte global de `prefers-reduced-motion`.
- **Do** incluir el descargo legal textual en toda superficie de reporte, y mensajes de error que nombran el problema concreto.
- **Do** mantener la maquinaria de IA (confianza, feedback, revisión) únicamente en `/dashboard`; al vecino se le muestra la deducción, nunca el modelo.
- **Do** operar por teclado de punta a punta: diálogo con foco atrapado, filas con botón real ("Gestionar" + sr-only), campos con label asociada.

### Don't:
- **Don't** crear una variante oscura: una sola escena de luz, el papel claro es el sistema.
- **Don't** usar glass, blur de fondo, gradientes de color o gradient text; los únicos `linear-gradient` del sistema son los trazos de 1px de la grilla de mensura.
- **Don't** poner kickers/eyebrows sobre el h1, ni heroes con tres tarjetas.
- **Don't** usar el sello (#c8402c) como alarma o denuncia; sólo marca acciones y estados puntuales.
- **Don't** usar emojis como iconografía: siempre iconos dibujados del set propio.
- **Don't** componer cuerpo de texto en monoespaciada, ni estirar Archivo fuera del display de hoja.
- **Don't** apilar sombras ni usar offset duro; una elevación por elemento, y la hoja plana por defecto.
- **Don't** codificar información sólo en color, ni bajar del piso de contraste de grafito-500 para texto pequeño.
- **Don't** mostrar confianza, top-k o arquitectura del modelo en superficies públicas.
