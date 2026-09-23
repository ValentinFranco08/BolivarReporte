# Plan de implementación — Rediseño “Rastro”

## 1. Propósito

Rediseñar la interfaz de **Bolívar Animal** para que funcione como una herramienta de búsqueda y recuperación comunitaria, no como una red social genérica, un dashboard de IA ni un portal municipal burocrático.

La propuesta visual se llama **Rastro**: cada aviso aporta evidencia para reencontrar un animal —foto, situación, última zona vista, momento y una vía de contacto—. La inteligencia artificial permanece en segundo plano para la persona vecina; solo se presenta como “posibles coincidencias”.

## 2. Problema que resuelve

La interfaz actual mezcla recursos que compiten entre sí: brutalismo de emergencia, bordes y sombras fuertes, uso generalizado de mayúsculas, emojis, estética de cartelera y patrones de dashboard. El resultado llama la atención, pero no sostiene bien la lectura bajo estrés ni diferencia suficiente entre una búsqueda, un hallazgo, una adopción y una alerta sanitaria.

Rastro introduce una jerarquía estable:

1. La foto identifica al animal.
2. La situación indica qué necesita la comunidad.
3. Lugar y hora orientan la acción.
4. El contacto permite cerrar el circuito.

## 3. Decisiones de producto previas

Antes de implementar, actualizar `PRODUCT.md` para declarar como verdad canónica:

- Nombre del producto: **Bolívar Animal**.
- Público principal: vecinos de San Carlos de Bolívar, especialmente desde teléfono y en la calle.
- Casos de uso públicos: mascota perdida, mascota encontrada, tránsito/adopción, alerta sanitaria por cebo y consulta de mapa.
- Casos de uso internos: moderación, priorización, corrección y resolución de avisos.
- La IA no se muestra como arquitectura, confianza o modelo en la experiencia pública.
- La plataforma no debe presentarse como servicio municipal oficial si no existe ese respaldo formal.

También actualizar `DESIGN.md`: Rastro reemplaza la identidad visual anterior; las referencias de mensura quedan limitadas a la mesa operativa si aportan valor funcional.

## 4. Dirección de diseño

### Principio rector

**Una búsqueda no se navega: se reconoce y se actúa.**

### Sistema visual

| Elemento | Decisión |
| --- | --- |
| Material | Papel mineral claro, líneas territoriales muy sutiles, fotos reales sin filtros. |
| Color | Carbón para lectura; terracota para “se busca”; verde bosque para resguardo; rojo profundo solo para alertas sanitarias. |
| Tipografía | Sans legible y expresiva para títulos; monoespaciada únicamente para hora, distancia, barrio, código y datos operativos. |
| Profundidad | Bordes finos y sombras suaves con desplazamiento; sin sombras duras ni volumen decorativo. |
| Iconografía | SVG coherente de trazo único; no emojis como iconos de producto. |
| Estados | Siempre palabra + color + símbolo. No depender solo del color. |
| Movimiento | Un solo momento relevante: transición de un aviso a su detalle/mapa. Respetar `prefers-reduced-motion`. |

### Restricciones visuales

- No usar gradientes decorativos, tarjetas idénticas por toda la página ni pills como navegación principal.
- No usar mayúsculas sostenidas en párrafos, textos de ayuda o acciones largas.
- No repetir cintas de peligro: el rojo y la señalización fuerte solo se usan en la alerta sanitaria.
- No usar imágenes generadas para representar mascotas, rescates o testimonios. Usar las fotografías que ya existen en los reportes.

## 5. Arquitectura de información

### Navegación pública

| Ruta | Propósito | Acción primaria |
| --- | --- | --- |
| `/` | Actividad de búsqueda y avisos activos. | Crear aviso. |
| `/mapa` | Ubicar avisos y zonas de precaución. | Ver aviso seleccionado. |
| `/reportes/nuevo` | Crear un aviso en pocos pasos. | Publicar aviso. |
| `/sos` | Resolver una sospecha de intoxicación. | Llamar/ir a guardia. |
| `/remum` | Identificación y datos sanitarios, si está activo. | Registrar o consultar mascota. |
| `/qr/[id]` | Rescate instantáneo desde chapita QR. | Contactar al responsable. |

### Navegación móvil

Barra inferior con cuatro destinos:

- Buscar
- Mapa
- Crear aviso (botón central con cámara)
- Mis avisos / perfil

La alerta sanitaria no ocupa una pestaña fija: aparece como aviso prioritario cuando existe y conserva un acceso visible en mapa y portada.

### Mesa operativa

`/dashboard` es una superficie separada para gestión. Debe priorizar tabla, filtros, fotos de evidencia, estado, prioridad, acciones rápidas e historial. No debe imitar la experiencia pública.

## 6. Diseño por pantalla

### Fase A — Base del sistema

Archivos principales:

- `frontend/app/globals.css`
- `frontend/app/layout.tsx`
- `frontend/components/layout/Navbar.tsx`
- `frontend/components/layout/MobileBottomNav.tsx`
- `frontend/components/ui/Icono.tsx`

Tareas:

1. Crear tokens de color, espaciado, tipografía, bordes, elevación y foco accesible.
2. Definir componentes base: botón primario, botón secundario, sello de estado, rótulo de dato, ficha, aviso crítico y bandeja móvil.
3. Sustituir emojis por iconos existentes o SVG propios consistentes.
4. Aplicar foco visible, selección, cursor, scrollbar y reducción de movimiento.
5. Definir breakpoints y tamaños mínimos táctiles de 48 × 48 px.

Criterio de aceptación:

- Ninguna ruta pública depende de estilos específicos improvisados.
- Contraste AA en texto, controles y estados.
- La navegación funciona a 360 px, 768 px y 1440 px.

### Fase B — Portada y avisos

Archivos principales:

- `frontend/app/page.tsx`
- `frontend/components/pets/PetCard.tsx`
- `frontend/components/pets/VisualMatchModal.tsx`

Estructura propuesta:

1. Aviso de búsqueda prioritaria: foto grande, nombre/situación, lugar y hora.
2. Resumen territorial con acceso directo al mapa.
3. Bloque de hallazgos recientes.
4. Alerta sanitaria condicional y aislada visualmente.
5. Listado de avisos con filtros por situación, zona y fecha.

Cambios de copy:

- “Nuevo reporte” → “Crear aviso”.
- “Cotejar con IA” → “Ver posibles coincidencias”.
- “Match” → “Similitud” o “Posible coincidencia”.
- “Ficha” se reserva para contexto interno; la interfaz pública usa “aviso” o “publicación”.

Criterio de aceptación:

- Una persona entiende qué hacer en los primeros cinco segundos.
- La foto, estado y zona se ven sin abrir cada aviso.
- La alerta sanitaria domina solo cuando hay una activa.

### Fase C — Crear aviso

Archivo principal: `frontend/app/reportes/nuevo/page.tsx`.

Convertir el formulario largo en tres pasos progresivos:

1. **Situación**: busco, encontré, necesita hogar/tránsito, alerta sanitaria.
2. **Evidencia**: foto y último lugar visto; GPS sugerido y dirección editable.
3. **Contacto**: nombre, WhatsApp y detalles opcionales.

Reglas:

- No pedir categoría ni datos técnicos del modelo.
- Mantener la foto como requisito explícito cuando corresponde.
- Mostrar una revisión final compacta antes de publicar.
- Conservar el flujo de login actual, pero explicar con claridad por qué se solicita acceso.
- Reemplazar `alert()` por un aviso accesible dentro de la interfaz.

Criterio de aceptación:

- El recorrido es realizable con una mano en móvil.
- Se puede crear un aviso completo en menos de un minuto.
- Los errores indican qué falta y cómo resolverlo.

### Fase D — Mapa de rastreo

Archivos principales:

- `frontend/app/mapa/page.tsx`
- `frontend/components/ui/Map.tsx`

Tareas:

1. Usar leyenda sobria y sellos de situación.
2. Al seleccionar un pin, abrir una bandeja inferior en móvil y panel lateral en escritorio.
3. Mostrar foto, tipo de aviso, zona, hora y acción contextual.
4. Delimitar visualmente la zona de precaución para alertas sanitarias, si los datos y reglas del producto lo permiten.
5. Agregar enlace directo a crear aviso desde el mapa.

Criterio de aceptación:

- Los pines se distinguen sin depender solo del color.
- El contenido seleccionado es legible sobre el mapa.
- El mapa no bloquea la navegación ni los controles táctiles.

### Fase E — Protocolo SOS

Archivo principal: `frontend/app/sos/page.tsx`.

Tareas:

1. Separar la emergencia inmediata de la denuncia posterior.
2. Ordenar por acciones: llamar, trasladar, no hacer, conservar evidencia si es seguro.
3. Presentar teléfonos solo si fueron verificados por el responsable del proyecto.
4. Mantener rojo profundo exclusivo para este contexto.
5. El generador de denuncia se muestra luego del protocolo y no compite con las acciones urgentes.

Criterio de aceptación:

- Una persona reconoce qué hacer primero sin leer toda la pantalla.
- Las acciones de llamada son accesibles en un toque.
- No se realizan afirmaciones médicas o institucionales no verificadas.

### Fase F — REMUM y rescate por QR

Archivos principales:

- `frontend/app/remum/page.tsx`
- `frontend/app/remum/[id]/page.tsx`
- `frontend/app/remum/nuevo/page.tsx`
- `frontend/app/qr/[id]/page.tsx`

Tareas:

1. Diseñar la credencial como identificación simple, no como tarjeta ornamental.
2. En la ruta QR, priorizar foto, nombre, contacto y “enviar mi ubicación”.
3. Reducir la ruta QR a una sola pantalla de carga rápida, sin navegación secundaria.
4. Mostrar datos de salud o identificación solo cuando sean reales y estén autorizados.

Criterio de aceptación:

- Quien escanea un QR entiende en segundos cómo ayudar.
- La acción de contacto no requiere registro.
- La pantalla funciona correctamente con conectividad limitada.

### Fase G — Login, registro y seguimiento

Archivos principales:

- `frontend/app/login/page.tsx`
- `frontend/app/registro/page.tsx`
- `frontend/app/reportes/page.tsx`

Tareas:

1. Simplificar acceso y registro como “seguir mis avisos”.
2. Explicar el beneficio del acceso sin prometer funciones no implementadas.
3. Diseñar estados vacíos, carga y error dentro del sistema Rastro.
4. Crear una vista de “mis avisos” con estado, última actualización y acción de editar/cerrar si existe API para ello.

### Fase H — Mesa operativa municipal

Archivo principal: `frontend/app/dashboard/page.tsx`.

Tareas:

1. Mantener una tabla de alta densidad para escritorio.
2. Priorizar avisos críticos y pendientes con un orden visible.
3. Convertir el detalle de un aviso en una superficie de decisión: evidencia, ubicación, estado, prioridad, acciones e historial.
4. Mantener confianza, clasificación alternativa y feedback del modelo solo dentro de esta ruta.
5. Verificar permisos de rol en backend antes de representar acciones como exclusivas del municipio.

## 7. Componentes a construir o consolidar

| Componente | Uso |
| --- | --- |
| `AvisoCard` | Vista pública de mascota perdida, encontrada, tránsito o adopción. |
| `EstadoSello` | Situación textual con color semántico y símbolo. |
| `DatoRastro` | Zona, hora, distancia y código con icono y lectura accesible. |
| `AlertaSanitaria` | Bloque crítico reutilizable. |
| `FiltroBandeja` | Filtros de móvil en bottom sheet. |
| `MapaDetalle` | Detalle contextual de un pin. |
| `ComparadorCoincidencias` | Dos fotos, zona, distancia y acción de contacto. |
| `PasoAviso` | Contenedor del flujo de creación de aviso. |
| `TablaOperativa` | Tabla de gestión con filtros y acciones. |

## 8. Compatibilidad con backend

El rediseño no requiere cambiar la API para su primera versión. Reutilizar:

- `GET /api/reports` para cartelera y mapa.
- `POST /api/reports` para crear aviso.
- `POST /api/ai/predict` y la búsqueda de coincidencias solo después de crear o abrir un aviso.
- `PATCH /api/reports/{id}` para cambios operativos existentes.
- Rutas REMUM y QR ya existentes cuando devuelvan información validada.

Mejoras de backend recomendadas, pero no bloqueantes para la capa visual:

1. Centralizar la URL del backend en una variable de entorno.
2. Aplicar control de rol real a las acciones de administración.
3. Implementar logout y pruebas de frontend.
4. Persistir prioridad y estado sugeridos cuando el modelo los produzca, si se aprueba esa regla de negocio.
5. Definir paginación para la cartelera antes de que el volumen de avisos crezca.

## 9. Accesibilidad y rendimiento

- Texto normal con contraste mínimo 4.5:1.
- Controles táctiles de al menos 48 px.
- Labels asociados a todos los campos.
- Diálogos con foco atrapado, cierre por Escape y devolución de foco al disparador.
- Navegación por teclado completa en dashboard.
- `alt` descriptivo en fotos; no repetir información visual en exceso.
- Carga diferida de imágenes fuera del primer viewport; usar `next/image` cuando sea compatible con el host de uploads.
- Mapas cargados dinámicamente y con fallback de estado.
- Sin animaciones esenciales; respetar `prefers-reduced-motion`.

## 10. Pruebas y verificación

Por cada fase:

1. Ejecutar `npm run build`.
2. Ejecutar `npm run lint` y resolver errores nuevos.
3. Ejecutar pruebas de frontend existentes; ampliar Vitest para estados críticos.
4. Capturar escritorio a 1440 px y móvil a 390 px.
5. Revisar: carga, vacío, error, contenido real, foco, teclado y desbordes.
6. Probar creación de aviso con GPS permitido, GPS rechazado, sin foto y sin sesión.
7. Ejecutar el detector de Impeccable sobre los archivos UI modificados.

Casos mínimos de prueba:

- Aviso perdido con contacto.
- Aviso encontrado sin contacto.
- Alerta sanitaria activa.
- Sin avisos.
- Sin conexión/API caída.
- Coincidencia visual disponible y sin coincidencias.
- QR válido e inválido.
- Dashboard sin permisos, vacío y con prioridades mixtas.

## 11. Orden de ejecución

| Orden | Fase | Dependencia | Resultado |
| --- | --- | --- | --- |
| 1 | Base del sistema | Ninguna | Tokens y componentes coherentes. |
| 2 | Portada y avisos | Base | Nueva jerarquía pública. |
| 3 | Crear aviso | Base | Flujo móvil de alta conversión. |
| 4 | Mapa | Avisos y componentes de estado | Lectura territorial. |
| 5 | SOS | Base | Protocolo crítico seguro. |
| 6 | Coincidencias | Avisos | Comparación útil sin tecnicismos. |
| 7 | REMUM y QR | Base | Identificación y rescate rápido. |
| 8 | Login y seguimiento | Base | Continuidad para cada vecino. |
| 9 | Dashboard | Base + backend de roles | Gestión operativa. |
| 10 | QA y documentación | Todas | Diseño consolidado y verificable. |

## 12. Definición de terminado

El rediseño se considera terminado cuando:

- Todas las rutas públicas y operativas comparten la identidad Rastro.
- Una persona puede crear, localizar y contactar sobre un aviso desde móvil sin explicaciones externas.
- Alertas sanitarias son distinguibles, claras y no contaminan el resto de la experiencia.
- La IA no aparece como jerga ni promesa excesiva para vecinos.
- Escritorio y móvil fueron inspeccionados visualmente.
- Build, lint y pruebas pasan.
- `PRODUCT.md` y `DESIGN.md` describen la experiencia que realmente se entrega.
