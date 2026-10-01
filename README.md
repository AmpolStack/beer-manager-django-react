# 🍺 Beer Manager — Django + React + MariaDB con Docker

Sistema CRUD mínimo para registrar **marcas** de cerveza y sus **cervezas** asociadas.

Este README está escrito para alguien que viene de **Java/Spring Boot + Angular** y quiere
entender **Django** y **React** en menos de una hora. Cada sección explica la teoría base
y la conecta con algo que ya conoces.

---

## 📑 Índice (léelo en este orden, toma ~50 min)

| # | Sección | Tiempo | Qué aprendes |
|---|---------|--------|--------------|
| 1 | [Levantar el proyecto](#1-levantar-el-proyecto-5-min) | 5 min | Docker Compose, ver la app |
| 2 | [Mapa mental de la arquitectura](#2-mapa-mental-de-la-arquitectura-8-min) | 8 min | Cómo encajan las 3 piezas |
| 3 | [Django: los conceptos base](#3-django-los-conceptos-base-15-min) | 15 min | MTV, ORM, apps, migraciones, DRF |
| 4 | [React: los conceptos base](#4-react-los-conceptos-base-15-min) | 15 min | JSX, componentes, estado, hooks |
| 5 | [Docker: los conceptos base](#5-docker-los-conceptos-base-7-min) | 7 min | Dockerfile, compose, volumes, redes |
| 6 | [El flujo completo de una petición](#6-el-flujo-completo-de-una-petición-5-min) | 5 min | Clic en "Guardar" → fila en MariaDB |
| 7 | [Referencia de la API](#7-referencia-de-la-api) | ref | Endpoints y ejemplos curl |
| 8 | [Comandos útiles](#8-comandos-útiles) | ref | Tu cheat sheet diario |
| 9 | [Cómo hacer cambios](#9-cómo-hacer-cambios-tipo-tarea-común) | ref | Práctica guiada |
| 10 | [Troubleshooting](#10-troubleshooting) | ref | Errores típicos |
| 11 | [Del prototipo a producción](#11-del-prototipo-a-producción) | ref | Buenas prácticas reales |

---

## 1. Levantar el proyecto (5 min)

### Requisitos

Solo necesitas **Docker Desktop** instalado y corriendo. Nada más.
(No necesitas Python ni Node local — viven dentro de los contenedores.)

```bash
cd beer-project
docker compose up --build
```

Espera a ver en la terminal del frontend:

```
Compiled successfully!
You can now view beer-frontend in the browser.
```

### Direcciones

| Servicio | URL | ¿Qué es? |
|----------|-----|----------|
| **Frontend** (React) | http://localhost:3000 | La UI que ves |
| **Backend** (Django) | http://localhost:8000 | La API REST |
| **Admin de Django** | http://localhost:8000/admin/ | Panel de administración gratis |
| **API raíz** | http://localhost:8000/api/ | Navegador de la API estilo Swagger |
| **MariaDB** | `localhost:3306` | La base de datos (no se navega) |

### Cargar datos de ejemplo

```bash
docker compose exec backend python manage.py seed_beers
docker compose exec backend python manage.py createsuperuser
```

El primer comando mete 5 marcas y 12 cervezas. El segundo crea tu usuario para el admin.
Si quieres resetear los datos: `python manage.py seed_beers --empty`

### ⚠️ Sobre el proxy de CORS (léelo, es confuso)

En `frontend/package.json` hay `"proxy": "http://backend:8000"`. Esto significa que cuando
React pide `/api/brands/`, el servidor de desarrollo de React **reenvía** la petición al
backend. El navegador nunca ve a Django directamente, **no hay CORS**.

Si en cambio configuras `REACT_APP_API_URL=http://localhost:8000/api`, React llama directo
al backend, y entonces **sí** hay CORS, y por eso `settings.py` tiene
`CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]`.

Ambas formas funcionan. La primera (proxy) es la que usa este proyecto por defecto.

### Detener / limpiar

```bash
docker compose stop          # para los contenedores, conserva datos
docker compose down          # quita contenedores, conserva datos
docker compose down -v       # ¡BORRA la base de datos también!
```

---

## 2. Mapa mental de la arquitectura (8 min)

```
┌──────────────────────────────────────────────────────────────┐
│  NAVEGADOR  (tu máquina)                                     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐      │
│  │  React  :3000                                     │      │
│  │  App.js → BeerList.js / BrandList.js              │      │
│  │  Componentes = funciones que devuelven JSX        │      │
│  │  Estado local con useState / useEffect            │      │
│  └──────────────────────┬─────────────────────────────┘      │
│                         │  HTTP/JSON  (fetch/axios)          │
│                         │  GET/POST/PUT/DELETE /api/...      │
└─────────────────────────┼────────────────────────────────────┘
                          │
        ┌─────────────────┴──────────────────┐
        │  RED DE DOCKER (bridge: beer-      │
        │  project_default)                  │
        │  Los contenedores se ven por      │
        │  NOMBRE: "backend", "db"           │
        └─────────────────┬──────────────────┘
                          │
        ┌─────────────────┴──────────────────┐
        ▼                                     ▼
┌────────────────────────┐        ┌─────────────────────────────┐
│  Django  :8000         │        │  MariaDB  :3306            │
│  beer_project/         │───────▶│  beer_db                   │
│   └ settings.py        │ SQL    │   ├ brands                 │
│   └ urls.py            │        │   └ beers (FK → brands.id) │
│  beers/                │        └─────────────────────────────┘
│   ├ models.py   (ORM)  │
│   ├ serializers.py     │
│   ├ views.py    (API)  │
│   └ urls.py            │
└────────────────────────┘
```

### Cómo se comparan con tu stack

| responsibility | Java / Spring Boot | Angular | Este proyecto |
|----------------|-------------------|---------|---------------|
| Entidad JPA | `@Entity class Beer` | `beer.model.ts` | `beers/models.py` |
| Tabla SQL | `@Table` + Flyway/Liquibase | — | **Migrations de Django** (archivos Python autogenerados) |
| Repositorio | `BeerRepository extends JpaRepository` | `BeerService` | **El ORM de Django hace de repositorio** (no escribes repo) |
| Controlador REST | `@RestController @GetMapping` | — | `views.py` → `BeerViewSet` |
| DTO / validación | `@Valid` + records | interfaces + `Validators` | `serializers.py` |
| Inyección de dependencias | `constructor(private repo: BeerRepository)` | Angular DI (providers) | **Autowiring por importing** (no hay container) |
| Configuración | `application.yml` | `environment.ts` | `settings.py` + `docker-compose.yml` env vars |
| Componente UI | — | `@Component({...})` | `function BeerList() {...}` |
| Router | `@RequestMapping` | `app.routes.ts` + RouterModule | `beer_project/urls.py` + `beers/urls.py` |

**La diferencia mental más importante:** Django y React tienen mucho menos "código de
andamiaje" (boilerplate) que Spring Boot y Angular. No hay `pom.xml`, no hay `@Service`,
no hay `@Autowired`, no hay `NgModule`. Escribes menos y obtienes más por defecto.

---

## 3. Django: los conceptos base (15 min)

### 3.1 El patrón MTV y por qué importa

Django sigue **MTV** (*Model-Template-View*):

```
   Petición HTTP
        │
        ▼
   ┌─────────┐   lee/escribe   ┌──────────┐
   │  MODEL  │ ◄──────────────► │ MariaDB  │
   │(models) │   (ORM)         └──────────┘
   └─────────┘
        │
        │ objetos Python
        ▼
   ┌──────────┐   serializa a   ┌──────────┐
   │  VIEW    │ ──────────────► │   JSON   │ ──► respuesta HTTP
   │(views.py)│                └──────────┘
   └──────────┘
```

- **Model** = tu entidad de dominio + la definición de la tabla (aquí vive el SQL).
- **View** = la lógica que produce una respuesta. En una API, produce JSON.
- **Template** = el HTML. **En este proyecto NO lo usamos**, porque el frontend es React.

> En Spring, View+Template ≈ tu `@RestController`. Django separa más las piezas.

### 3.2 El ORM: no escribes SQL

`backend/beers/models.py`:

```python
class Beer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,      # ← si borro la marca, borro sus cervezas
        related_name='beers',
        verbose_name="Marca",
    )
    alcohol_content = models.DecimalField(max_digits=4, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)   # se llena solo al crear
    updated_at = models.DateTimeField(auto_now=True)       # se actualiza solo al editar
```

Eso genera una tabla MariaDB con esas columnas, la FK, los índices, y los timestamps
automáticos. En Java sería:

```java
@Entity
@Table(name = "beers_beer")
class Beer {
    @Id @GeneratedValue Long id;
    String name;
    @ManyToOne Brand brand;              // y el cascade lo Defines en el otro lado
    BigDecimal alcoholContent;
}
```

**QuerySets** — la parte que más se parece a JPA pero es perezosa (*lazy*):

```python
Beer.objects.all()                                    # SELECT * FROM beers_beer
Beer.objects.filter(beer_type='ipa')                  # SELECT ... WHERE beer_type='ipa'
Beer.objects.filter(is_active=True).order_by('-ibu')  # ORDER BY ibu DESC
Brand.objects.annotate(beers_count=Count('beers'))    # LEFT JOIN + GROUP BY
```

Nada se ejecuta hasta que realmente lo necesitas. Equivalente conceptual a
`Stream` de Java, pero la diferencia clave: los QuerySets son **reutilizables e
inmutables** (cada `filter()` devuelve uno nuevo, no muta el anterior).

`select_related('brand')` en `views.py` es una **optimización clave**: hace un solo JOIN
en vez de 1 + N consultas. Equivalente a `JOIN FETCH` en JPA para evitar el problema
N+1.

### 3.3 Apps: la unidad de organización

Un proyecto Django tiene **apps** (módulos con propósito). Este tiene dos:

```
beer-project/
├── beer_project/          ← la "configuración" del proyecto (NO tu código de negocio)
│   ├── settings.py          toda la config en un archivo
│   ├── urls.py              rutas raíz
│   └── wsgi.py              punto de entrada para servidores de producción
└── beers/                 ← TU app: todo el dominio de cervezas
    ├── models.py            entidades
    ├── serializers.py       DTOs + validación
    ├── views.py             la API
    ├── urls.py              rutas de la app
    ├── admin.py             panel gratis (te ahorra escribir 300 líneas)
    ├── apps.py              configuración de la app
    └── management/
        └── commands/
            └── seed_beers.py   comando de consola
```

Regla práctica: **si es configuración, va en `beer_project/`. Si es negocio, va en `beers/`.**
Equivalente a separar `config/` de tu código en Spring, pero con la diferencia de que en
Spring tú eliges la estructura; en Django la estructura ya existe.

### 3.4 Migrations: el control de versiones del esquema

Cuando cambias `models.py`, Django genera un archivo en `beers/migrations/` que describe
el cambio al esquema.

```bash
docker compose exec backend python manage.py makemigrations   # genera el archivo
docker compose exec backend python manage.py migrate          # aplica a la BD
```

- `makemigrations` = "el modelo cambió, ¿qué SQL necesito?" → escribe Python.
- `migrate` = "aplica los cambios pendientes" → ejecuta SQL.

> **Equivalente:** `makemigrations` ≈ `git diff` (snapshot del esquema),
> `migrate` ≈ `git apply`. Los archivos de migration se commitean a Git, siempre.
> Es **el** reemplazo de Flyway/Liquibase, y ya viene incluido.

Un archivo de migration se ve así (no lo escribas a mano, pero lelo para entenderlo):

```python
class Migration(migrations.Migration):
    dependencies = [('beers', '0001_initial')]      # orden entre migraciones
    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[...],
        ),
    ]
```

### 3.5 Django REST Framework: las piezas que usamos

Aquí es donde DRF (la librería que añade la API) entra.

**`serializers.py`** — el contrato de la API. Define qué campos entran y salen, y valida:

```python
class BeerSerializer(serializers.ModelSerializer):   # ← "genera esto solo desde el Model"
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = Beer
        fields = ['id', 'name', 'brand', 'brand_name', 'alcohol_content', ...]

    def validate_alcohol_content(self, value):     # ← validación por campo
        if value < 0 or value > 100:
            raise serializers.ValidationError("...")
        return value
```

`source='brand.name'` es como un **getter anidado**: lee `obj.brand.name` y lo expone
plano como `brand_name` en el JSON. Evita que el frontend haga el join.

`read_only=True` = el campo se lee pero no se puede escribir en un POST/PUT.

> En Angular tú escribirías un `Beer` interface + validaciones manuales.
> Acá el serializer es la interface **y** el validador **y** el que decide el JSON.

**`views.py`** — los `ViewSet`s. Esta es la parte más "mágica" frente a Spring:

```python
class BeerViewSet(viewsets.ModelViewSet):
    queryset = Beer.objects.select_related('brand').all()
    serializer_class = BeerSerializer
    filterset_fields = ['brand', 'beer_type', 'is_active']
    search_fields = ['name', 'brand__name', 'description']
    ordering_fields = ['name', 'alcohol_content', 'ibu']
```

`ModelViewSet` genera **7 endpoints automáticamente**:

| Método | URL | Acción |
|--------|-----|--------|
| GET | `/api/beers/` | listar (paginado) |
| POST | `/api/beers/` | crear |
| GET | `/api/beers/{id}/` | obtener uno |
| PUT | `/api/beers/{id}/` | actualizar completo |
| PATCH | `/api/beers/{id}/` | actualizar parcial |
| DELETE | `/api/beers/{id}/` | eliminar |
| GET | `/api/beers/{id}/` + acciones extra | ver abajo |

> Compara: en Spring escribes 6 métodos en un `@RestController`. Acá una clase.
> El "truco" es que `queryset` + `serializer_class` son toda la configuración;
> DRF se encarga del CRUD, la paginación, los filtros y la negociación de contenido.

**Filtros y búsqueda** son casi gratis declarando attributes:

```python
filterset_fields = ['beer_type']                      # ?beer_type=ipa  (django-filter)
search_fields = ['name', 'brand__name']              # ?search=guin  (icontains, OR)
ordering_fields = ['name', 'ibu']                    # ?ordering=-ibu
```

Los tres se combinan: `/api/beers/?search=ipa&beer_type=lager&ordering=-ibu`

**Acciones personalizadas** con `@action`, que agregan endpoints a medida:

```python
@action(detail=False, methods=['get'])
def types(self, request):
    """GET /api/beers/types/  → devuelve los tipos para llenar el <select>"""
    return Response([{'value': 'ipa', 'label': 'IPA'}, ...])
```

`detail=False` = acción de colección (no necesita `/{id}/`).
`detail=True` = acción de un objeto (necesita `/{id}/`).

Ejemplo en `BrandViewSet`: `GET /api/brands/{id}/beers/` → las cervezas de esa marca.

**El Router** (`beers/urls.py`) conecta las clases a URLs automáticamente:

```python
router = DefaultRouter()
router.register(r'brands', BrandViewSet, basename='brand')   # → /api/brands/
router.register(r'beers', BeerViewSet, basename='beer')      # → /api/beers/
```

> En Spring tú declaras cada `@GetMapping` a mano. En Django registras la clase y
> obtienes las 7 rutas. Es el mismo concepto que los routers de Flask/FastAPI, pero
> Django te lo da de fábrica.

### 3.6 `settings.py`: todo en un archivo

No hay `application.yml` ni inyección: es un módulo de Python, así que puedes usar
lógica real.

```python
# Las variables de entorno de docker-compose llegan como 'DEBUG', 'DB_HOST', etc.
DEBUG = config('DEBUG', default=True, cast=bool)
DB_HOST = config('DB_HOST', default='localhost')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='beer_db'),
        ...
    }
}
```

`python-decouple` lee variables de entorno con un default si no existen. Por eso el
mismo código sirve para tu laptop y para Docker sin cambios.

### 3.7 El panel admin: gratis y subestimado

`beers/admin.py` con 6 líneas te da un panel CRUD completo con buscador, filtros,
paginación y edición inline:

```python
@admin.register(Beer)
class BeerAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'beer_type', 'alcohol_content', 'ibu', 'is_active']
    list_filter = ['brand', 'beer_type', 'is_active']
    search_fields = ['name', 'brand__name', 'description']
```

**Úsalo para validar datos mientras aprendes.** Entras a http://localhost:8000/admin/
y experimentas. Luego lo usas como tool interno para revisar datos sin tocar la UI.

---

## 4. React: los conceptos base (15 min)

### 4.1 La idea central: un componente es una función

```jsx
function BeerList() {
  return <div>Hola</div>;
}
```

- Es una **función de JavaScript** que devuelve **JSX**.
- JSX es HTML con `{}` para inyectar JavaScript. Se compila a llamadas `React.createElement`.
- React **solo vuelve a renderizar** el componente cuando cambia el estado.

> En Angular escribes una clase con decorador `@Component` y un `template:` separado.
> Acá: una función, el markup pegado arriba del return, y cero decoradores.
> Hay debate sobre si esto es mejor o peor; lo importante es que es menos ceremony.

### 4.2 JSX en 30 segundos

```jsx
<div className="card">          {/* class, no class: HTML no aplica a JSX */}
  <h2>{beers.length} cervezas</h2>   {/* {} = expresión interpolada */}
  {loading ? <Spinner /> : <Table />} {/* ternario para condicionar */}
  {beers.map(b => <Row key={b.id} beer={b} />)}  {/* .map para listas */}
</div>
```

Cuatro cosas que te van a sorprender vs Angular templates:
1. `className` en vez de `class`.
2. `onClick={...}` en vez de `(click)="..."`.
3. `{...}` interpola valores (no hay `{{ }}`).
4. **`key` es obligatorio** en cada elemento de una lista. Sin ella React se confunde
   al reordenar y renderiza mal. Es el problema clásico de listas en React.

### 4.3 Estado: `useState` y `useEffect`

**`useState`** — el equivalente a propiedades con cambio de detección automática:

```jsx
const [beers, setBeers] = useState([]);       // beers = valor, setBeers = setter
const [loading, setLoading] = useState(true);

setBeers(data.results);    // dispara un re-render automático
```

Dos reglas que no puedes romper:
1. **Nunca** llames `setBeers(...)` directo en el render (provoca loop infinito).
2. Los `useState` se declaran en el **mismo orden** siempre. Por eso los Hooks empiezan
   con "use".

**`useEffect`** — el equivalente a `ngOnInit` + Observer:

```jsx
useEffect(() => {
  beerApi.getTypes().then(({ data }) => setTypes(data));
}, []);   // ← el [] significa "solo al montar"
```

El segundo argumento es el **array de dependencias**:
- `[]` → ejecuta una vez al montar (como `ngOnInit`).
- `[search, brand]` → re-ejecuta cuando cambia cualquiera de esos valores.
- sin array → re-ejecuta en cada render (casi siempre es un bug).

**El cleanup function** para cancelar peticiones:

```jsx
useEffect(() => {
  const t = setTimeout(loadBeers, 300);
  return () => clearTimeout(t);      // se ejecuta antes de la próxima corrida
}, [loadBeers]);
```

Ese es el **debounce** del buscador: espera 300 ms a que dejes de escribir.

### 4.4 `useCallback`: la memoización

```jsx
const loadBeers = useCallback(async () => {
  const { data } = await beerApi.list(params);
  setBeers(data.results || data);
}, [search, brandFilter, typeFilter]);   // se recrea solo si cambian estas deps
```

Si `loadBeers` fuera una función normal, sería una referencia **nueva** en cada render,
y eso re-dispararía el `useEffect` que la usa → loop infinito de peticiones. `useCallback`
estabiliza la referencia. **Es la trampa #1 de React para quien viene de otro stack.**

`useMemo` hace lo mismo pero para **valores**, no funciones (ej. filtrar una lista cara).

### 4.5 Flujo de datos unidireccional

```
        state (datos)
            │
            ▼
     render (JSX)
            │
            ▼
        DOM (lo que ve el usuario)
            │
            ▼
      evento (click, input)
            │
            ▼
     setState() ← actualiza el state
            └──► vuelve a render
```

El flujo es **siempre en una sola dirección** y **siempre a través del estado**. Nunca
mutas el DOM directamente. Esto es lo que hace React predecible.

> En Angular tienes `[(ngModel)]` (two-way binding) y `EventEmitter` para propagar.
> En React el two-way se hace **a mano**:
> ```jsx
> <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
> ```
> No es `[(ngModel)]`; es `value` + `onChange` actualizando el state. Más verboso pero
> siempre explícito.

### 4.6 Props: pasar datos hacia abajo

```jsx
function BeerForm({ beer, brands, onClose, onSaved }) { ... }

<BeerForm beer={editing} brands={brands} onClose={fn} onSaved={fn} />
```

Props = **parámetros de función**, de padre a hijo. No hay `@Input()`: destructuras el
objeto. Y las funciones que le pasas al hijo funcionan como `@Output()`/callbacks.

### 4.7 Cómo estructurar el frontend

```
src/
├── index.js          ← punto de entrada: monta React en el DOM
├── App.js            ← componente raíz, maneja qué pestaña se muestra
├── api.js            ← ÚNICA capa que habla HTTP con Django
├── index.css         ← estilos globales
└── components/
    ├── BrandList.js  ← lista + modal de marca (dos componentes en un archivo)
    └── BeerList.js   ← lista + modal de cerveza
```

`api.js` centraliza todo el acceso a datos. **Ningún componente hace `fetch` directo.**
Si mañana cambias de REST a GraphQL, tocas un archivo.

```js
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';
const api = axios.create({ baseURL: API_BASE_URL, headers: {...} });

export const beerApi = {
  list: (params) => api.get('/beers/', { params }),
  create: (data) => api.post('/beers/', data),
  delete: (id) => api.delete(`/beers/${id}/`),
};
```

`process.env.REACT_APP_*` es la forma de inyectar variables de entorno en Create React
App. El prefijo `REACT_APP_` es obligatorio.

> En Angular tendrías un `BeerService` con `HttpClient` e `providedIn: 'root'`.
> La idea es la misma, con una sintaxis más corta.

### 4.8 Nota importante sobre CRA

Este proyecto usa **Create React App** (`react-scripts`) porque es lo más simple para
aprender. Está **oficialmente obsoleto** (la comunidad ya migró a Vite). Para un proyecto
real nuevo en 2026 usa **Vite**:

```bash
npm create vite@latest beer-frontend -- --template react
```

La diferencia son 3 líneas de `vite.config.js` en vez del `Dockerfile` de CRA. Los
conceptos de React (componentes, hooks, estado) son **idénticos**; solo cambia el
tooling.

---

## 5. Docker: los conceptos base (7 min)

### 5.1 Dockerfile — la receta de una imagen

```dockerfile
FROM python:3.12-slim          # 1. imagen base (como una VM mínima)

WORKDIR /app                   # 2. dónde vivo

COPY requirements.txt .        # 3. copio deps primero (capa cacheable)
RUN pip install -r requirements.txt

COPY . .                       # 4. copio el resto del código

EXPOSE 8000                    # 5. documento el puerto
```

**El orden importa (best practice).** Copiar los requisitos *antes* del código hace que
Docker reutilice la capa de `pip install` si solo cambió un `.py`. Si copias todo primero,
reinstalas todo en cada build. Es **cache layering** y es la optimization #1.

**El frontend usa `CMD ["npm", "start"]`** (forma exec) en vez de `CMD npm start`
(forma shell). La forma exec es preferible: cuando el contenedor recibe `SIGTERM`, el
proceso node lo recibe directamente y puede cerrar limpiamente. La forma shell corre un
`/bin/sh` intermedio que **no pasa las señales**, y por eso Docker tiene que matar -9.

### 5.2 docker-compose.yml — orquestar varios servicios

```yaml
services:
  db:
    image: mariadb:11              # ← imagen oficial, no construyes nada
    environment:                   # ← credenciales por variable de entorno
      MYSQL_DATABASE: beer_db
    healthcheck:                   # ← ¿ya está lista para aceptar conexiones?
      test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
      retries: 5
      start_period: 30s            # ← margen para el primer arranque

  backend:
    build: ./backend
    environment:                   # ← estas variables las lee settings.py
      DB_HOST: db                  # ← "db" es el NOMBRE del servicio
      ALLOWED_HOSTS: "localhost,127.0.0.1,0.0.0.0,backend"  # ← ¡importante!
    depends_on:
      db:
        condition: service_healthy  # ← espera al healthcheck, no solo al arranque
    volumes:
      - ./backend:/app              # ← monta mi código local dentro del contenedor
    command: >                      # ← sobreescribe el CMD del Dockerfile
      sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"

volumes:
  db_data:                          # ← volumen nombrado: persiste datos de MariaDB
```

Cinco ideas que debes retener:

1. **Los contenedores se hablan por nombre de servicio.** `DB_HOST: db` funciona porque
   Docker crea una red donde `db` resuelve a la IP del contenedor de MariaDB. No
   necesitas ni IPs ni `localhost` (dentro del contenedor, `localhost` eres tú mismo).

2. **`depends_on` solo espera el arranque, no que esté listo.** Por eso usamos
   `condition: service_healthy`. Sin esto, Django intenta conectar a MariaDB antes de que
   termine de inicializar y falla. Es una de las causas #1 de "mi Docker no arranca".

3. **Los volumes con `:`** montan tu carpeta local dentro del contenedor. Cambias un
   `.py` y Django recarga solo, sin rebuild. Es el equivalente a hot-reload de Spring
   DevTools. `/app/node_modules` se monta como volumen **anónimo vacío** para tapar la
   carpeta del host: si no, tu `node_modules` de Windows (con binaries nativos) rompe el
   Linux del contenedor.

4. **`volumes: db_data`** persiste los datos **fuera** del ciclo de vida del contenedor.
   Sin esto, `docker compose down && up` = base de datos vacía.

5. **`0.0.0.0:8000`** en vez de `localhost:8000` al arrancar un servidor en un
   contenedor. `localhost` solo acepta conexiones de dentro del contenedor; para que
   llegue desde fuera tiene que escuchar en todas las interfaces.

6. **`ALLOWED_HOSTS` debe incluir el nombre del servicio backend.** Cuando el dev server
   de React proxea `/api/...`, la petición llega a Django con `Host: backend:8000`. Si
   `backend` no está en `ALLOWED_HOSTS`, Django responde **400 DisallowedHost** (y lo
   ves como un 400 en el navegador). Por eso `docker-compose.yml` define
   `ALLOWED_HOSTS: "...,backend"`.

7. **El healthcheck oficial de MariaDB es `healthcheck.sh`**, no `mysqladmin ping`. La
   imagen `mariadb:11` ya **no incluye** `mysqladmin` (el binario se llama
   `mariadb-admin`), y además un `ping` anónimo da `Access denied`. El script
   `healthcheck.sh --connect --innodb_initialized` es el método soportado y comprueba
   que InnoDB terminó de inicializar de verdad.

---

## 6. El flujo completo de una petición (5 min)

Seguir el rastro completo ayuda más que leer los archivos por separado.
**Escenario: el usuario llena el form de una cerveza y presiona "Guardar".**

```
[1] Usuario escribe "Corona Extra" y presiona Guardar
     └─ src/components/BeerList.js  → <BeerForm>
        El <form onSubmit={handleSubmit}> dispara preventDefault() y llama handleSubmit

[2] handleSubmit arma el payload (beers/BeerList.js)
     └─ Convierte strings a números: alcohol_content: "4.6" → 4.6
        Sin esto, el backend recibe texto y el DecimalField explota.

[3] Petición HTTP (frontend/src/api.js)
     └─ axios.post('/beers/', payload)
        → POST /api/beers/
        → El dev server de React lo proxea a backend:8000

[4] Ruteo (beer_project/urls.py → beers/urls.py)
     └─ path('api/', include('beers.urls'))
        → el DefaultRouter matchea POST /beers/ → BeerViewSet.create()

[5] Validación (beers/serializers.py)
     └─ BeerSerializer(data=payload) valida:
        - ¿los campos requeridos están? (name, brand, alcohol_content)
        - ¿alcohol_content entre 0 y 100? (validate_alcohol_content)
        - ¿brand existe en la BD?
        Si falla → 400 con {"alcohol_content": ["..."]}  ← el front lo muestra en el modal

[6] Persistencia (beers/models.py — el ORM)
     └─ serializer.save() hace internamente:
        Beer.objects.create(name=..., brand_id=..., ...)
        → INSERT INTO beers_beer (...) VALUES (...)
        (el ORM traduce los tipos Python a tipos MariaDB)

[7] Respuesta
     └─ 201 Created con el objeto serializado como JSON
        {"id": 13, "name": "Corona Extra", "brand_name": "Corona", ...}

[8] Update del estado (frontend/src/components/BeerList.js)
     └─ onSaved() → setShowForm(false) cierra el modal
                  → loadBeers() re-pide la lista
                  → setBeers(nuevos datos) dispara el re-render
                  → la tabla se actualiza

[9] Fin del ciclo. El usuario ve su cerveza en la tabla.
```

Puntos clave:

- El **frontend nunca toca la base de datos** y el **backend nunca toca el DOM**.
- El **serializer** es la frontera: valida y traduce en las dos direcciones.
- El frontend tiene **dos fuentes de verdad** de la lista: no muta el array, lo
  reemplaza con `setBeers(respuestaDelServidor)`. Es más "correcto" que la mutación
  local optimista, a costa de un round-trip.

---

## 7. Referencia de la API

Todas las respuestas GET vienen **paginadas** (20 por página):

```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [ { "id": 1, "name": "...", ... } ]
}
```

Por eso en el frontend ves `data.results || data` — así funciona tanto con paginación
como sin ella.

### Marcas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/brands/` | Listar (params: `search`, `ordering`, `page`) |
| POST | `/api/brands/` | Crear |
| GET | `/api/brands/{id}/` | Obtener una |
| PUT | `/api/brands/{id}/` | Actualizar completo |
| PATCH | `/api/brands/{id}/` | Actualizar parcial |
| DELETE | `/api/brands/{id}/` | Eliminar (cascade a cervezas) |
| GET | `/api/brands/{id}/beers/` | Cervezas de esa marca |

### Cervezas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/beers/` | Listar (params: `brand`, `beer_type`, `is_active`, `search`, `ordering`) |
| POST | `/api/beers/` | Crear |
| GET | `/api/beers/{id}/` | Obtener una |
| PUT / PATCH | `/api/beers/{id}/` | Actualizar |
| DELETE | `/api/beers/{id}/` | Eliminar |
| GET | `/api/beers/types/` | Lista de tipos válidos (para el `<select>`) |

### Ejemplos con curl

```bash
# Ver brands
curl http://localhost:8000/api/brands/

# Crear marca
curl -X POST http://localhost:8000/api/brands/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Asahi","country":"Japón","founded_year":1889}'

# Crear cerveza
curl -X POST http://localhost:8000/api/beers/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Asahi Super Dry",
    "brand": 1,
    "beer_type": "lager",
    "alcohol_content": "5.00",
    "ibu": 15,
    "description": "Lager japonesa muy ligera y refrescante."
  }'

# Filtrar por tipo y ordenar por IBU descendente
curl "http://localhost:8000/api/beers/?beer_type=ipa&ordering=-ibu"

# Buscar
curl "http://localhost:8000/api/brands/?search=corr"

# Eliminar
curl -X DELETE http://localhost:8000/api/beers/13/
```

### Modelo de datos

```
brands                          beers
┌──────────────────────┐        ┌──────────────────────────┐
│ id            PK     │        │ id                 PK    │
│ name          UNIQUE│◄───────┤ brand_id          FK    │
│ country              │  1:N   │ name                     │
│ founded_year         │        │ beer_type                │
│ description          │        │ alcohol_content DECIMAL  │
│ created_at           │        │ ibu                      │
│ updated_at           │        │ description              │
└──────────────────────┘        │ image_url                │
                                │ is_active    BOOLEAN     │
                                │ created_at               │
                                │ updated_at               │
                                └──────────────────────────┘
```

`on_delete=models.CASCADE` significa: borro la marca → se borran sus cervezas.
Las alternativas son `PROTECT` (impide borrar si tiene hijas) y `SET_NULL`.

---

## 8. Comandos útiles

```bash
# --- Ciclo completo ---
docker compose up --build              # arrancar todo
docker compose stop                    # parar (conserva)
docker compose down                    # borrar contenedores
docker compose down -v                 # borrar contenedores + DATOS
docker compose up -d                   # arrancar en background
docker compose logs -f backend         # ver logs en vivo
docker compose logs --tail=50 frontend

# --- Django (dentro del contenedor) ---
docker compose exec backend python manage.py migrate           # aplicar migraciones
docker compose exec backend python manage.py makemigrations    # generar migración
docker compose exec backend python manage.py seed_beers       # datos de ejemplo
docker compose exec backend python manage.py seed_beers --empty  # resetear
docker compose exec backend python manage.py createsuperuser   # crear admin
docker compose exec backend python manage.py shell             # REPL interactivo
docker compose exec backend python manage.py check             # validar config
docker compose exec backend python manage.py showmigrations    # ver estado

# --- Django: experimentar sin API ---
docker compose exec backend python manage.py shell
>>> from beers.models import Beer, Brand
>>> Beer.objects.all()
>>> Brand.objects.create(name="Test")
>>> Beer.objects.filter(beer_type="ipa").count()
>>> b = Beer.objects.first(); b.name; b.brand.name

# --- Frontend ---
docker compose exec frontend npm start
docker compose exec frontend npm run build      # build de producción
```

Atajos: `docker compose exec` abre una shell en el contenedor. Para no escribir `backend`
cada vez: `alias dj="docker compose exec backend python manage.py"`.

---

## 9. Cómo hacer cambios (tipo tarea común)

### Cambiar un campo del modelo (ej. agregar `rating` a Beer)

```bash
# 1. Edita backend/beers/models.py: agrega el campo al modelo Beer
#    rating = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Rating")

docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate

# 2. Agrégalo al serializer (si no, no aparecerá en el JSON)
#    -> en BeerSerializer.Meta.fields

# 3. Agrégalo al form (frontend/src/components/BeerList.js)
#    -> EMPTY_FORM, y un <input> en el <form>

# 4. Agrégalo a la tabla
#    -> un <th> y un <td> en el JSX
```

**Ese orden es el flujo mental de Django**: Model → Migration → Serializer → (View) →
Frontend. Si te saltas el serializer, el campo existe en la BD pero no viaja por la API.
Es el error #1 de quien viene de Spring, donde el Model *es* el contrato.

### Agregar un campo en el serializer que no está en el modelo

```python
class BeerSerializer(serializers.ModelSerializer):
    beers_count = serializers.IntegerField(read_only=True)   # <- campo calculado
```

Y en el viewset, la query que lo produce:

```python
queryset = Brand.objects.annotate(beers_count=Count('beers'))
```

Esto es un campo "virtual" que se calcula en SQL, no existe en la tabla. Equivalente a
una proyección en JPQL (`select b, count(b.beers) ... group by b`).

### Agregar un endpoint custom

```python
# views.py, dentro de BeerViewSet
@action(detail=True, methods=['get'])
def similares(self, request, pk=None):
    beer = self.get_object()
    beers = Beer.objects.filter(beer_type=beer.beer_type).exclude(id=beer.id)[:5]
    return Response(BeerSerializer(beers, many=True).data)
```

Queda disponible en `GET /api/beers/{id}/similares/`. **Sin tocar `urls.py`.**

---

## 10. Troubleshooting

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| `Can't connect to MySQL server` | MariaDB no está listo o el host está mal | `docker compose logs db`. Verifica `DB_HOST: db` (no `localhost`) |
| `Access denied for user` | Credenciales desincronizadas | Debe coincidir con las de `db.environment` en compose |
| `CORS error` en la consola | El frontend llama directo al backend sin proxy | Usa `/api` (proxy) **o** agrega el origen a `CORS_ALLOWED_ORIGINS` |
| Cambié un `.py` y no se refleja | El volumen no está montado | Revisa `volumes: - ./backend:/app` |
| `Unknown field` en serializer | El campo no existe en el modelo | Regresaste a `models.py` y te falta migrar |
| Cambié un `.py` y no se refleja (2) | Falta `INSTALLED_APPS` para una app nueva | Agrega `'mi_app',` a `INSTALLED_APPS` |
| `node_modules` con errores raros | `node_modules` de Windows montado en Linux | Asegúrate de tener el volumen anónimo `/app/node_modules` |
| Pantalla vacía en React | Error en la consola del navegador | Mira la pestaña Console; revisa que el backend responda en `:8000/api/` |
| Cambié CORS y no funciona | `ALLOWED_HOSTS` también importa | Ambos deben incluir `localhost` |
| La página recarga infinitamente | Falta un `useCallback` o un array de deps mal puesto | Revisa los deps del `useEffect` |
| Petición se duplica | Falta cleanup en el `useEffect` | Devuelve el `return () => clearTimeout(...)` |
| `no such table: auth_user` | No corriste las migraciones | `docker compose exec backend python manage.py migrate` |
| **400** al llamar `/api/` desde el navegador | Django rechaza el `Host: backend:8000` del proxy | Agrega `backend` a `ALLOWED_HOSTS` (ver §5.2, punto 6) |
| **500** en `/api/beers/` con `no such table: beers_beer` | La app `beers` no tiene migraciones | `docker compose exec backend python manage.py makemigrations beers && ... migrate` |
| DB queda `unhealthy` y el backend no arranca | Healthcheck con `mysqladmin` (no existe en MariaDB 11) | Usa `["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]` |
| `Proxy error ... EAI_AGAIN` al iniciar | El frontend arrancó antes que el backend | Es inocuo (HMR); `depends_on: backend` lo reduce. Recarga la página |
| `Cannot GET /api/...` en un cliente sin `Accept: application/json` | El dev server de CRA no proxea peticiones "de navegación" (HTML) | Normal: axios (el navegador) sí las proxea. Prueba con `curl -H "Accept: application/json"` |

---

## 11. Del prototipo a producción

Lo que hay aquí es **un prototipo educativo**. Para producción, esto es lo que cambia:

### Lo que hay que cambiar sí o sí

| Tema | Ahora | Producción |
|------|-------|------------|
| **DEBUG** | `True` | `False` (y `ALLOWED_HOSTS` con tu dominio real) |
| **SECRET_KEY** | hardcodeado | Variable de entorno desde un secret manager |
| **CORS** | `localhost:3000` | Solo tu dominio real, nunca `*` |
| **Servidor** | `runserver` (dev only, sin concurrency) | **Gunicorn** (`pip install gunicorn` ya está) |
| **Static files** | dev server | Nginx o whitenoise |
| **Frontend** | `npm start` (dev) | `npm run build` → Nginx sirviendo estáticos |
| **Migraciones** | En cada `up` | Solo en el pipeline de deploy |

```bash
# Cómo sería el backend en producción
gunicorn beer_project.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

`runserver` es **solo para desarrollo**: recarga código y usa un servidor de un solo
hilo. Gunicorn maneja múltiples workers y es lo que usarías detrás de Nginx.

### Autenticación (lo que NO está aquí)

Esto está abierto a propósito, para que veas el CRUD limpio. En un sistema real
necesitarás:

- **JWT o sesión con cookies** para login.
- `django-rest-auth` o `djangorestframework-simplejwt`.
- `permissions = [IsAuthenticated]` en los ViewSets.
- Paginación, throttle, y rate limiting.

### Cosas que un dev con tu stack notaría

1. **No hay DTOs de entrada separados.** El `ModelSerializer` usa el Model como
   contrato de entrada y salida. Es rápido de escribir, pero en un sistema complejo
   expones campos que no deberías. La práctica: separar `BeerWriteSerializer` de
   `BeerReadSerializer`.

2. **No hay capa de repositorio.** El ORM es la capa. Para lógica de negocio
   reutilizable, extrae funciones o servicios en `beers/services.py` (ese archivo es el
   equivalente directo a tus `@Service` de Spring).

3. **Los tests no están incluidos.** La estructura sería `beers/tests.py` con
   `pytest` o el `TestCase` nativo de Django. Vale la pena conocerlo; el test de
   permisos de DRF es de los más usados de ver.

4. **CORS + proxy es un patrón de desarrollo.** En producción, lo normal es que
   un reverse proxy de Nginx `/api/` al backend, y todo queda en el mismo origen, sin
   CORS.

---

## 📚 Recursos para seguir (en orden)

| Recurso | Para qué | Tiempo |
|---------|----------|--------|
| [docs.djangoproject.com](https://docs.djangoproject.com/es/5.0/) — "Tutorial" oficial | La mejor guía de Django que existe, en español | 3 h |
| [docs.djangoproject.com](https://docs.djangoproject.com/es/5.0/topics/db/models/) — "The Models" | Entender el ORM a fondo | 1 h |
| [www.django-rest-framework.org](https://www.django-rest-framework.org/) — "Quickstart" | DRF más allá de lo que vimos | 1 h |
| [react.dev/learn](https://react.dev/learn) — la nueva doc oficial de React | **La mejor** para aprender React moderno | 2 h |
| [react.dev/learn/thinking-in-react](https://react.dev/learn/thinking-in-react) | Cómo estructurar un componente | 20 min |
| [vite.dev/guide](https://vite.dev/guide/) | Migrar el frontend a Vite | 30 min |
| [docs.docker.com/compose](https://docs.docker.com/compose/) | Docker Compose a fondo | 1 h |

### Ruta de aprendizaje sugerida (1 semana, ~2 h/día)

1. **Día 1** — Corre este proyecto, rompe cosas a propósito, mira los logs.
2. **Día 2** — Sigue el [tutorial oficial de Django](https://docs.djangoproject.com/es/5.0/tutorial/01-tutorial/) completo (son ~2 h). Aunque uses otro tema, hazlo una vez.
3. **Día 3** — Migra el frontend a **Vite** y compara. Entenderás CRA vs bundler moderno.
4. **Día 4** — Agrega autenticación JWT. Es el ejercicio que más enseña Django.
5. **Día 5** — Escribe tests con `pytest-django`. Aprende a testear ViewSets.
6. **Día 6** — Agrega un filtro advanced con `django-filter` (rango de IBU, alcohol mínimo).
7. **Día 7** — Deploya: Gunicorn + Nginx + Postgres/MariaDB real.

---

## 📌 Resumen ejecutivo en 5 puntos

Si solo te quedas con cinco ideas de todo este documento:

1. **Django = ORM + migraciones + admin gratis.** El ORM y las migraciones te ahorran
   el 60% del código que escribirías con JPA manual.

2. **Los `ModelViewSet` son el superpoder.** Una clase = 7 endpoints CRUD. Aprende a
   leer `queryset` + `serializer_class` + `filterset_fields` y ya entiendes el 90% de
   cualquier API de Django que encuentres.

3. **El `ModelSerializer` es tu contrato.** Si el campo no está en `Meta.fields`, no
   existe para el frontend. Cambiar la API = cambiar el serializer, no el Model.

4. **En React el estado manda.** `useState` guarda, `useEffect` reacciona,
   `useCallback` estabiliza referencias, `key` identifica listas. Dominar esos cuatro
   resuelve el 80% de los bugs.

5. **El flujo de datos es unidireccional y el HTTP no miente.** UI → estado → request →
   respuesta → estado → UI. Si te pierdes, sigue el rastro de una sola petición por el
   código con tu debugger favorito. Ese ejercicio enseña más que cualquier tutorial.
