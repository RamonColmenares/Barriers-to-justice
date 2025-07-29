# Static Assets Guide

Este directorio contiene todos los recursos estáticos del sitio web. 

## Imágenes Requeridas

### Página Principal
- `hero-background.jpg` - Imagen de fondo para la sección hero (aspecto 16:9, min 1920x1080px)

### Equipo de Investigación (/team/)
- `ammar-osman.jpg` - Foto de Ammar Osman (cuadrada, min 300x300px)
- `amro-mohamed.jpg` - Foto de Amro Mohamed (cuadrada, min 300x300px)
- `azza.jpg` - Foto de Azza (cuadrada, min 300x300px)
- `banu-ozyilmaz.jpg` - Foto de Banu Özyılmaz (cuadrada, min 300x300px)
- `gennadii-ershov.jpg` - Foto de Gennadii Ershov (cuadrada, min 300x300px)
- `muhammad-shahroz.jpg` - Foto de Muhammad Shahroz (cuadrada, min 300x300px)
- `muhammet-isik.jpg` - Foto de Muhammet Isik (cuadrada, min 300x300px)
- `niloufar-ahadi.jpg` - Foto de Niloufar Ahadi (cuadrada, min 300x300px)
- `ramon-colmenares.jpg` - Foto de Ramon Colmenares (cuadrada, min 300x300px)

### Página de Investigación (/research/)
- `research-hero.jpg` - Imagen principal de investigación (aspecto 3:2, min 900x600px)
- `systems-thinking.jpg` - Imagen para enfoque de sistemas (aspecto 3:2, min 600x400px)
- `methodology.jpg` - Imagen para metodología (aspecto 3:2, min 600x400px)

## Notas

- Todas las imágenes deben estar optimizadas para web (formato JPG recomendado)
- Si una imagen no está disponible, se mostrará un gradiente de respaldo con iconos
- Las imágenes del equipo se muestran en círculos, por lo que deben estar centradas
- Recomendamos usar imágenes profesionales para mantener la credibilidad

## Estructura de Directorios

```
static/
├── favicon.png           # Icono del sitio (existente)
├── hero-background.jpg   # Fondo principal
├── team/                 # Fotos del equipo
│   ├── ammar-osman.jpg
│   ├── amro-mohamed.jpg
│   └── ...
└── research/             # Imágenes de investigación
    ├── research-hero.jpg
    ├── systems-thinking.jpg
    └── methodology.jpg
```
