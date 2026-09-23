---
name: Bolívar Animal
description: Red comunitaria y municipal de búsqueda, recuperación y protección animal ante extravíos y cebos tóxicos en San Carlos de Bolívar.
colors:
  lino: "#faf8f5"
  lino-alto: "#ffffff"
  lino-suave: "#f3efea"
  lino-medio: "#eae5de"
  terracota-50: "#fff6ee"
  terracota-100: "#ffe8d7"
  terracota-200: "#ffd0b0"
  terracota-500: "#d97736"
  terracota-600: "#c25e26"
  terracota-700: "#994703"
  salvia-50: "#f2f8f4"
  salvia-100: "#e3f0e8"
  salvia-200: "#c7e1d2"
  salvia-500: "#3d7a58"
  salvia-600: "#2c6a49"
  coral-50: "#fff1f2"
  coral-100: "#ffe4e6"
  coral-500: "#e11d48"
  coral-600: "#be123c"
  ambar-50: "#fffbeb"
  ambar-100: "#fef3c7"
  ambar-500: "#d97706"
  corteza: "#3a2a20"
  corteza-suave: "#554339"
  corteza-clara: "#78655b"
  borde-calido: "#e8e0d5"
  borde-suave: "#f0ebe4"
typography:
  display:
    fontFamily: "Epilogue, Georgia, serif"
    fontSize: "2.25rem → 3.5rem"
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Epilogue, Georgia, serif"
    fontSize: "1.5rem → 2rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.015em"
  title:
    fontFamily: "Epilogue, Georgia, serif"
    fontSize: "1.125rem → 1.25rem"
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: "Plus Jakarta Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.875rem → 1rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Plus Jakarta Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.6875rem → 0.75rem"
    fontWeight: 600
    letterSpacing: "0.02em"
  cifra:
    fontFamily: "Space Mono, ui-monospace, monospace"
    fontSize: "0.75rem → 1.25rem"
    fontFeature: "tabular-nums"
rounded:
  tarjeta: "1.5rem"
  control: "0.75rem"
  pill: "9999px"
components:
  boton-principal:
    backgroundColor: "{colors.terracota-500}"
    textColor: "{colors.lino-alto}"
    rounded: "{rounded.control}"
    minHeight: "48px"
  boton-whatsapp:
    backgroundColor: "#25d366"
    textColor: "{colors.lino-alto}"
    rounded: "{rounded.control}"
    minHeight: "48px"
  boton-alerta:
    backgroundColor: "{colors.coral-500}"
    textColor: "{colors.lino-alto}"
    rounded: "{rounded.control}"
    minHeight: "48px"
  tarjeta-busqueda:
    backgroundColor: "{colors.lino-alto}"
    borderColor: "{colors.borde-calido}"
    rounded: "{rounded.tarjeta}"
---

# Sistema de Diseño: Bolívar Animal

## Overview

**Creative North Star: "Red de Búsqueda y Recuperación Animal"**

Bolívar Animal es un instrumento de respuesta comunitaria y municipal rápida ante la pérdida de perros y gatos y el riesgo crítico de envenenamiento por cebos tóxicos en la vía pública de San Carlos de Bolívar (problemática formalizada en el proyecto de ordenanza municipal **REMUM**).

El diseño está concebido para actuar bajo estrés y a la intemperie:
- **La foto es la protagonista absoluta:** en la calle, reconocer a una mascota perdida depende de su rostro, manchas y tamaño; no de párrafos explicativos.
- **Acción inmediata al alcance del pulgar:** cada publicación permite contactar directamente al tutor o a quien retuvo al animal en un toque vía WhatsApp o llamada telefónica.
- **Sin burocracia ni palabras extrañas:** el vecino no habla de *"fichas"*, *"expedientes"* ni *"reencuentros"*. El vocabulario del sistema es directo: **Búsqueda Activa** (*"Se busca a..."*), **Animal Encontrado** (*"En resguardo temporal"*) y **Alerta de Cebos**.
- **La Inteligencia Artificial es silenciosa:** la tecnología de cotejo visual (ViT-B/16 y distancia geodésica) trabaja en segundo plano. Al vecino no se le muestran matrices de vectores ni tecnicismos; se le muestra un porcentaje de similitud fotográfica claro y la distancia en kilómetros dentro de Bolívar.
- **Identificación Oficial REMUM:** cada mascota registrada cuenta con su **Chapita de Collar con QR dinámico** y su **Libreta Sanitaria Digital** (vacuna antirrábica municipal y castración al día), permitiendo que quien la encuentre en la calle la devuelva a su familia en cuestión de minutos.

---

## Vocabulario y Tono de la Plataforma (UX Copy)

El producto adopta un tono empático, cívico, directo y austero, eliminando la jerga técnica y los eufemismos:

| Evitar terminología técnica / burocrática | Utilizar en la interfaz pública | Propósito en Bolívar |
| :--- | :--- | :--- |
| *"Ficha de la mascota / Ficha N°..."* | **Aviso** o **Publicación** | Refleja cómo la comunidad ya comparte información en veterinarias y grupos vecinales. |
| *"Cédula de extravío"* | **Búsqueda Activa** (*"Se busca a Milo"*) | Genera empatía y movilización barrial inmediata. |
| *"Reporte de avistamiento"* | **Animal Encontrado** (*"En resguardo seguro"*) | Avisa que el animal ya no deambula y está protegido en una casa o comercio. |
| *"Alerta de toxicidad general"* | **Alerta de Cebos Tóxicos** | Advertencia sanitaria directa para no pasear mascotas por la zona afectada. |
| *"Identificador QR / Token"* | **Chapita del Collar** | El objeto cotidiano que cualquier vecino reconoce a simple vista. |
| *"Crear ficha / Iniciar trámite"* | **+ Publicar Mascota** | Llamado a la acción rápido de dos palabras. |
| *"Ficha comunitaria"* | **Animal Comunitario** (*"Perro del barrio"*) | Conforme a la ordenanza REMUM para animales cuidados colectivamente con padrinazgo. |

---

## Colores

La paleta se apoya en superficies de lino natural, acentos terracota de afecto vecinal, verde salvia de salud/tránsito y el coral de alerta sanitaria estricta:

```
Lino Natural:    #FAF8F5  (Lienzo de lectura clara a pleno sol)
Terracota:       #D97736  (Búsqueda activa, identidad primaria, botones de acción)
Verde Salvia:    #3D7A58  (Animales encontrados, a salvo, adopciones y libreta sanitaria)
Verde WhatsApp:  #25D366  (Acción de rescate en un toque con el tutor o vecino)
Coral Alerta:    #E11D48  (Cebos tóxicos y animales extraviados en peligro)
Ámbar Cálido:    #D97706  (Precaución, animales en tránsito, avisos de zona)
Corteza:         #3A2A20  (Tipografía principal cálida de máximo contraste)
Borde Cálido:    #E8E0D5  (Líneas divisorias suaves sin estridencias)
```

### Reglas Clave de Color:
1. **La Regla del Rojo Estricto:** El color Coral (`#E11D48`) se reserva **exclusivamente** para peligro de cebos tóxicos y el botón de pánico de mascota perdida. Nunca se usa como color decorativo ni para botones comunes.
2. **La Regla del Lino contra el Sol:** Las pantallas nunca usan fondos oscuros (no hay Dark Mode). El uso primordial de Bolívar Animal es en la calle, en la plaza o en la puerta de una casa bajo sol directo; el fondo `#FAF8F5` con texto `#3A2A20` garantiza contraste superior a 7:1 sin encandilar.
3. **La Regla del Verde Salvia:** Comunica tranquilidad y resguardo. Cuando un animal fue rescatado o su libreta sanitaria está al día, el verde salvia confirma que la situación está contenida.

---

## Tipografía

El sistema tipográfico combina la fuerza de un afiche de búsqueda con la legibilidad móvil inmediata:

* **Títulos y Cabeceras: Epilogue**  
  Tipografía con carácter de afiche de imprenta local y cartelera de pueblo. Transmite urgencia y calidez sin caer en lo infantil ni en lo burocrático.
* **Cuerpo, Etiquetas e Interfaz: Plus Jakarta Sans**  
  Limpia, geométrica y con curvas amables. Otorga máxima legibilidad en pantallas móviles para direcciones de Bolívar, teléfonos y recomendaciones médicas.
* **Metadatos y Registro: Space Mono / Tabular Numbers**  
  Exclusiva para números de microchip, códigos de chapita municipal `REMUM · BOL-0042` y distancias en kilómetros.

---

## Arquitectura de la Plataforma (4 Pestañas Clave)

Para evitar la saturación de pantallas y garantizar que cualquier vecino pueda publicar o rescatar en segundos:

1. **Cartelera (`/`)**:
   - Tablero principal con dos solapas prioritarias: **Perdidos** y **Encontrados**.
   - Banner superior emergente ante denuncias activas de cebos tóxicos.
   - Tarjetas *photo-first* con último lugar visto (barrio), tiempo transcurrido y botón verde WhatsApp directo.
2. **Mapa Vecinal (`/mapa`)**:
   - Mapa de San Carlos de Bolívar con pines según situación (`Perdido`, `Encontrado`, `Cebo sospechoso`).
   - Radio de precaución sombreado de 250 metros alrededor de puntos de envenenamiento reportados.
3. **SOS Cebos & Guardia (`/sos`)**:
   - Guía de primeros auxilios ante sospecha de envenenamiento (qué hacer y qué NO hacer).
   - Teléfonos de emergencia con marcado directo (Guardia Veterinaria 24hs `2314-421111`, Bomberos 100, Policía 101, SAPAAB).
   - Generador de denuncia penal bajo la Ley Nacional 14.346.
4. **Credencial REMUM (`/remum`)**:
   - Registro cívico municipal: pasaporte digital de la mascota con matrícula `REMUM · BOL-0042-M`.
   - Generador e impresión de **Chapita con QR** para el collar.
   - Libreta Sanitaria Digital con semáforo Zoonosis (antirrábica, castración y desparasitación).
   - Botón de pánico vecinal: *"¡Se me perdió! Activar alerta vecinal e IA"*.
   - Módulo de Animales Comunitarios y Padrinazgo (*Barbincho* en Plaza Alsina).

*(Ruta Pública de Rescate)*: **`/qr/[id]`**
- Vista ultra-rápida y ligera que se abre cuando un vecino escanea una chapita en la calle: foto grande, datos del perro, botón 1-tap WhatsApp para avisar al dueño, botón para enviar ubicación GPS actual y teléfono de guardia de Bolívar.

---

## Componentes Esenciales

### 1. Tarjeta de Búsqueda / Hallazgo (`PetCard`)
- Esquinas redondeadas (`1.5rem / 24px`), borde cálido `#E8E0D5` y sombra suave `shadow-warm-card`.
- Foto en proporción 4:3 con chip flotante de barrio (`📍 B° Las Flores`).
- Badge de situación:
  - `⚠️ Se busca a su familia` (ámbar/terracota con pulso).
  - `🛡️ En resguardo seguro` (salvia).
  - `🚨 Peligro: Cebo Tóxico` (coral).
- Botones de acción directa al pie: **Contactar por WhatsApp** y **Comparar con IA**.

### 2. Comparador de Huella Visual con IA (`VisualMatchModal`)
- Diseñado para responder a la pregunta del vecino: *"¿Será este el perro que estoy buscando?"*.
- Presenta las dos fotos lado a lado (la de la publicación vs. el candidato encontrado).
- Barra de porcentaje de coincidencia biométrica (ViT-B/16).
- Datos objetivos de ayuda: distancia geográfica estimada en Bolívar y marcas de pelaje identificadas.

### 3. Chapita y Credencial Municipal REMUM
- Inspirada físicamente en una placa de collar y un pasaporte sanitario cívico.
- Código QR vectorial nítido con alto contraste.
- Certificación del Quirófano Móvil Municipal y número de acta de Zoonosis.

---

## Mesa Operativa Municipal (Dashboard `/dashboard`)

Tal como establece la ordenanza, el municipio necesita una mesa técnica de trabajo. Esta sección vive en `/dashboard` y está destinada al personal veterinario, zoonosis e inspectores municipales:
- Triage de reportes entrantes y verificación de autenticidad.
- Cola de moderación de alertas de cebos tóxicos antes de emitir notificación masiva.
- Revisión de nuevas categorías no catalogadas propuestas por IA.
- Control de expedientes y estado de resoluciones (`Reportado` → `En proceso` → `Resuelto`).

---

## Do's and Don'ts

### Do:
- **Do** priorizar la foto y el botón de contacto directo por sobre cualquier descripción extensa.
- **Do** redactar los avisos en lenguaje vecinal directo: *"Se busca a Milo"*, *"Encontrado en Brown y Balcarce"*.
- **Do** poner a disposición el botón de WhatsApp con texto predefinido para que avisar no tome más de 2 segundos.
- **Do** mantener el diseño utilizable con un solo pulgar en la calle.
- **Do** verificar que las alertas de cebos informen con precisión la calle o plaza para proteger a otros animales.

### Don't:
- **Don't** utilizar el término *"ficha"*, *"expediente"* ni *"reencuentro"* en las pantallas del vecino.
- **Don't** mostrar nombres de modelos de IA, confianza decimal (`0.892`) o datos matemáticos en la experiencia vecinal.
- **Don't** usar fondos oscuros (Dark Mode), degradados de arcoíris ni efectos de vidrio borroso (glassmorphism).
- **Don't** utilizar emojis como íconos de la interfaz; la iconografía es un set de trazo limpio consistente en SVG.
- **Don't** permitir que una alerta sanitaria de cebo pase desapercibida: debe tener presencia inmediata en la portada y en el mapa.
