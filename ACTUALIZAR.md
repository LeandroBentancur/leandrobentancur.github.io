# Cómo actualizar el sitio y los CV

Todo —el sitio en dos idiomas y los tres CV en PDF— sale de los archivos de
`data/` y `content/`. **Cada dato se escribe una sola vez.** Si algo aparece
mal en el sitio o en un CV, el error nunca está en el sitio ni en el CV: está
en `data/`.

**Son dos carpetas, hermanas dentro de `Webpage_and_CV/`:**

| Carpeta | Qué es | ¿Va a GitHub? |
|---|---|---|
| `web/` | este repo: los datos, el sitio y lo que lo construye | **Sí**, es público |
| `cv-build/` | los CV: perfiles, plantilla LaTeX, PDF y tus datos personales | **No**, solo Nextcloud |

`cv-build/` lee `../web/data/`, así que un congreso que cargás acá aparece en
el próximo CV sin tocar nada más. Lo que nunca cruza en la otra dirección son
tus datos personales: el renderizador del sitio no tiene forma de leerlos.

Si volvés después de meses y no te acordás de nada, empezá por acá:

```sh
make status
```

Te dice qué hay cargado, qué está marcado para la portada, qué páginas están
hechas y de qué se está quejando el validador.

El sitio tiene tres páginas en cada idioma: portada, investigación, y
publicaciones y charlas. La de enseñanza existió y se retiró; está guardada en
la historia de git por si algún día querés volver a ponerla.

---

## La regla de oro: tres niveles

| Nivel | Qué es | ¿Se edita a mano? |
|---|---|---|
| **1. Verdad** | `data/*.yml`, `content/*.md` | **Sí. Solo esto.** |
| **2. Derivado** | `docs/`, `assets/`, `reports/`, `../cv-build/out/` | Nunca. Se regenera con `make all` |
| **3. Externo** | CVUy en ANII | Solo a mano en la web de ANII |

Borrar la carpeta `docs/` no rompe nada. Editarla sí: el próximo `make site`
pisa el cambio y lo perdés.

---

## Recetas

### 1. Fui a un congreso, di una charla o hice una visita

Abrí `data/events.yml` y agregá una entrada arriba de todo:

```yaml
- id: nombre-corto-2027          # sin espacios ni tildes, único
  name: Nombre oficial del evento
  name_es: Nombre en español      # solo si difiere del anterior
  kind: conference                # conference | school | seminar | workshop | visit
  role: poster                    # oral | poster | attended | visit | organizer
  title: Título de la charla      # solo si role es oral; los pósters no lo necesitan
  place: Ciudad, País
  place_es: Ciudad, País          # solo si difiere
  date: 2027-03                   # AAAA-MM, o AAAA si no te acordás del mes
  visibility: public
  featured: true                  # solo si querés que salga en la portada
```

```sh
make site
```

Esa única entrada alimenta tres cosas a la vez: la sección de charlas del CV
(si `role` es `oral` o `poster`), la lista de congresos asistidos del CV y, solo
si le ponés `featured: true`, la lista «Reciente y próximo» de la portada. Por
eso no hay que cargarlo dos veces.

**Fechas:** mes y año, nunca rangos de días. Es la regla que pediste.

**La portada la elegís vos.** No sale lo más reciente: sale exactamente lo que
tenga `featured: true`. Sacarle esa línea a un evento lo baja de la portada y no
lo borra de ningún lado — sigue en las charlas del sitio y en los CV. Lo que
todavía no pasó va arriba de todo, con la etiqueta «pronto». Si no queda ninguno
marcado, `make check` te avisa de que la sección quedó vacía.

### 2. Un evento futuro que todavía no puedo anunciar

**No lo cargues todavía.** El repositorio es público: cualquiera puede leer
`data/events.yml` en GitHub, aunque la entrada diga `visibility: private`. Ahí
"privado" significa que no se dibuja en la página, no que no se pueda leer. Y
como la historia de git guarda todo, borrarlo después tampoco lo saca.

Anotalo donde anotás el resto de tus cosas —fuera de estas dos carpetas— y
cargalo el día que salga el anuncio. Un renglón menos hoy es más barato que
una filtración.

Si un evento futuro queda cargado, el validador te avisa con **"upcoming AND
public"** para que confirmes que ya está anunciado.

### 3. Sale un preprint, o me aceptan un paper

`data/publications.yml`. Cuando un preprint se publica, no agregues una entrada
nueva: cambiale el `status` a la que ya está y completá los datos de la revista.

```yaml
- id: mollified-cd
  status: published          # era: preprint
  year: 2027
  title: ...
  authors: [...]
  journal: Nombre de la revista
  volume: "12"
  pages: "345"
  doi: 10.xxxx/yyyy
```

```sh
make site
cd ../cv-build && make
```

El validador no te deja marcar algo como `published` sin revista, volumen y
páginas.

### 4. Empieza un semestre nuevo

`data/teaching.yml`. **No crees un curso nuevo si ya existe**: buscá su `id` y
agregale una línea a `offerings`.

```yaml
- id: computacion-matematica
  name: {es: Computación Matemática, en: Mathematical Computing}
  offerings:
    - {year: 2027, institution: cmat, role: assistant}   # ← la línea nueva
    - {year: 2026, institution: cmat, role: assistant}
```

Los cursos ya no salen en el sitio —la página de enseñanza se sacó hasta que
tengas materiales propios para compartir—, así que esto solo toca los CV:

```sh
cd ../cv-build && make
```

Un curso existe una sola vez, con un nombre por idioma. Si además se anuncia
con un título más descriptivo, eso va en `public_title`, no en una entrada
aparte. Esta regla es la que evita que un mismo curso vuelva a tener cuatro
nombres distintos.

### 5. Cambio de cargo o de grado

`data/positions.yml`. La posición vigente lleva `end: null`. Al cerrarla, poné
la fecha y agregá la nueva arriba. Los cursos se asignan solos a cada cargo por
año e institución, así que no hay que tocarlos. Un cargo solo sale en los CV,
no en el sitio:

```sh
cd ../cv-build && make
```

### 6. Quiero reescribir mi bio o una línea de investigación

- Bio de la portada: `content/bio.es.md` y `content/bio.en.md`
- Líneas de investigación: `content/research/<id>.es.md` y `.en.md`

Es Markdown simple: párrafos separados por una línea en blanco, `*cursiva*`,
`**negrita**`, `[texto](url)`. El mismo texto alimenta la portada y el CV.

```sh
make site
cd ../cv-build && make
```

### 7. Foto nueva

Los originales viven en `../Pics/`, fuera del repo, y no se tocan. El recorte
es una receta, no un archivo: está en `build/make_images.py`.

```python
"photo.jpg": {
    "src": "Personal_Photo_1.jpg",
    "crop": "1080x900+0+450",   # ancho x alto + desde_x + desde_y
    "width": 760,
    "quality": 82,
},
```

```sh
make images site
```

Así el recorte siempre se puede reproducir y nadie tiene que acordarse de cuál
era "la foto buena".

`assets/` **sí se commitea**, aunque sea generado: los originales están en
`../Pics/`, fuera del repo, así que GitHub no puede rehacer el recorte. Después
de tocar una receta, corré `make images` y commiteá lo que salga.

Los `.woff2` de `site/static/fonts/` son la tipografía del sitio, servida desde
tu propio dominio en vez de pedírsela a Google en cada visita. No se tocan y no
hay que regenerarlas.

### 8. Un CV a medida para una postulación

No copies un `.tex`. Creá un perfil nuevo en `../cv-build/profiles/`, que son
unas quince líneas:

```yaml
id: postulacion-beca
lang: en
title: Curriculum Vitae
sections: [personal, education, research, publications, teaching, talks]
include_private: false
limits: {talks: 8, events: 0}
```

```sh
cd ../cv-build && make
```

Sale en `cv-build/out/postulacion-beca.pdf`, con los mismos datos que todo lo
demás.
Un perfil nunca se desactualiza; un `.tex` copiado sí. Por eso los cuatro CV
sueltos que tenías se convirtieron en tres perfiles.

### 9. El CV en español para trámites (con C.I. y fecha de nacimiento)

Esos datos no están en el repo y no se suben a ningún lado: viven en
`cv-build/`, que no es un repositorio de git. Copiá el ejemplo y completalo una
vez:

```sh
cd ../cv-build && cp private.example.yml private.yml
```

Lo lee solamente `render_cv.py`, y solo para el perfil `full-es`, que tiene
`include_private: true`. El renderizador del sitio no lo abre nunca — no tiene
ninguna línea de código que llegue a ese archivo.

### 10. Antes de un llamado o una renovación: poner CVUy al día

CVUy es tu registro más completo, pero es de **una sola vía**: exporta, no
importa, y los datos entran solo tipeando en el formulario de ANII.

1. Entrá a ANII y exportá tu CV en `.txt`.
2. Guardalo en `../CV/CVUY/`.
3. Corré:

```sh
make reconcile
```

Ni el espejo (`data/_cvuy_snapshot.yml`) ni el reporte suben al repo: son tu
registro oficial con anotaciones sobre sus errores, y solo hacen falta en tu
máquina. Se regeneran con `make import-cvuy`.

Te deja en `reports/cvuy-drift.md` una lista en dos direcciones: lo que está
acá y falta en ANII (para tipear a mano), y lo que está en ANII y falta acá
(para agregar). También marca los defectos del propio registro de ANII, como la
URL con doble esquema y el título viejo de tesis.

---

## Los comandos

```sh
make status      # dónde quedaste
make check       # valida los datos, no genera nada
make site        # data/ + content/ -> docs/
make images      # ../Pics/ -> assets/
make serve       # mirar el sitio en localhost:8000 (el español en /es/)
make reconcile   # comparar contra CVUy
make all         # todo lo anterior, en orden
```

Los CV se arman desde la otra carpeta, que no es un repo:

```sh
cd ../cv-build
make             # ../web/data + perfiles -> out/*.pdf
make one P=full-es
```

---

## Publicar

```sh
git add -A
git commit -m "lo que cambiaste"
git push
```

GitHub Actions valida, construye y publica. Si la validación falla, no publica
nada: es a propósito.

---

## Si algo falla

**"i18n mapping has stray keys"** — escribiste algo como
`{es: 19 créditos, promedio 9,74/10}`. YAML corta en cada coma y se come medio
valor. Poné comillas: `{es: "19 créditos, promedio 9,74/10"}`, o usá varias
líneas.

**"date must be YYYY or YYYY-MM"** — la fecha tiene día, o le falta el cero:
va `2027-03`, no `2027-3` ni `2027-03-14`.

**"published entry needs journal, volume and pages"** — marcaste un paper como
publicado sin los datos de la revista.

**"upcoming AND public"** — hay un evento futuro visible. Confirmá que ya está
anunciado públicamente.

**pdflatex falla** — el error sale con las últimas líneas del log. Casi siempre
es un carácter raro en un título; el `.tex` generado queda en
`../cv-build/out/` para mirarlo.

**El sitio no cambió** — abriste `docs/` a mano en vez de correr `make site`, o
estás mirando la caché del navegador.

---

## Lo que no hay que hacer nunca

- Editar `docs/`, `assets/` o `../cv-build/out/`: se regeneran y perdés el cambio.
- Copiar un `.tex` para hacer un CV distinto: usá un perfil.
- Agregar un curso que ya existe con otro nombre: buscá el `id`.
- Renderizar desde el export de CVUy: atrasa y tiene errores propios.
- Publicar un evento futuro sin anuncio público.
- Poner un dato personal, un PDF de CV o un export de ANII adentro de `web/`:
  esa carpeta es pública. Van en `cv-build/` o en `CV/`.
- Convertir `cv-build/` en un repositorio de git.
