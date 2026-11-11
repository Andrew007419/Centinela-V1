# 02 · Git y GitHub paso a paso

Los nombres de menús de GitHub pueden cambiar un poco con el tiempo. Si algo no aparece donde se indica, busca la misma opción en **Settings** del repositorio.

## Quién hace qué

- **Dueño del repositorio:** recomendado el Integrante 3 (software y datos). Crea el repo y agrega a los demás.
- **Con acceso de escritura (crean ramas y suben código):** Integrantes 1, 2 y 3.
- **Asesor mecatrónica e Integrante 4:** no tocan código. Entregan en Drive y, si quieren ver el repo, se agregan con permiso de **lectura** (o de escritura si quieren subir sus documentos ligeros ellos mismos).

---

## Parte A · Preparación (cada persona, una sola vez)

1. Crea una cuenta en https://github.com y anota tu **nombre de usuario**.
2. Instala Git: https://git-scm.com/downloads
3. Configura tu identidad:
   ```bash
   git config --global user.name "Tu Nombre"
   git config --global user.email "tu_correo@ejemplo.com"
   ```
   Usa el mismo correo de tu cuenta de GitHub.
4. Configura cómo te autenticas (elige una opción):
   - **Opción fácil, GitHub CLI:** instala `gh` desde https://cli.github.com y ejecuta `gh auth login`. Sigue las preguntas (GitHub.com, HTTPS, login por navegador).
   - **GitHub Desktop:** https://desktop.github.com, inicia sesión y listo.
   - **Token personal:** GitHub ya no acepta la contraseña en la terminal. Si usas HTTPS sin `gh`, crea un token en *Settings > Developer settings > Personal access tokens* y úsalo como contraseña.

## Parte B · Crear el repositorio y subir el proyecto (solo el dueño)

1. Descomprime el `.zip` y entra a la carpeta:
   ```bash
   unzip centinela-agave.zip
   cd centinela-agave
   ```
2. Inicializa Git y haz el primer commit:
   ```bash
   git init -b main
   git add .
   git commit -m "chore: estructura inicial del proyecto"
   ```
3. Crea el repositorio vacío en GitHub: https://github.com/new
   - Nombre: `centinela-agave`
   - Visibilidad: público o privado (ver la nota de la Parte D)
   - **No marques** "Add a README", ni `.gitignore`, ni licencia. Debe quedar vacío.
4. Conecta y sube:
   ```bash
   git remote add origin https://github.com/TU_USUARIO/centinela-agave.git
   git push -u origin main
   ```
   *Atajo con GitHub CLI (hace los pasos 3 y 4 juntos):*
   ```bash
   gh repo create centinela-agave --private --source=. --remote=origin --push
   ```
5. Abre la página del repo y confirma que se ven las carpetas.
6. Edita `.github/CODEOWNERS` y cambia los `@USUARIO_...` por los usuarios reales (se hace en una rama, como se explica en la Parte E).

## Parte C · Agregar colaboradores con permiso de escribir y crear ramas

### Si el repo está en tu cuenta personal

1. Entra al repositorio y abre **Settings**.
2. En el menú izquierdo, abre **Collaborators**. GitHub puede pedir tu contraseña o confirmar tu identidad.
3. Pulsa **Add people**.
4. Escribe el usuario, nombre o correo de GitHub de la persona y elígela de la lista.
5. Pulsa **Add** (o *Add to repository*).
6. Repite para cada integrante.
7. **La persona debe aceptar la invitación**, desde el correo que le llega o desde https://github.com/notifications. La invitación caduca a los 7 días.

En repositorios de cuenta personal, un colaborador invitado recibe acceso de **escritura**: puede clonar, crear ramas, subir commits y abrir Pull Requests. No hay un permiso aparte "solo crear ramas". Lo que se evita con la protección de `main` (Parte D) es que suba directo a la rama principal.

### Si prefieres roles más finos: usar una Organización (gratis)

1. En GitHub: foto de perfil, **Your organizations**, **New organization**, plan **Free**.
2. Crea el repo dentro de la organización.
3. En el repo: **Settings > Collaborators and teams > Add people**, elige a la persona y asigna el rol:

| Rol | Qué puede hacer | Para quién |
|---|---|---|
| Read | Ver y clonar | Asesor, Integrante 4 (solo ver) |
| Triage | Gestionar issues y PRs sin escribir código | Opcional |
| **Write** | Crear ramas, subir commits, abrir PRs | Integrantes 1, 2 y 3 |
| Maintain / Admin | Administrar el repo | Solo el dueño |

## Parte D · Proteger `main` (para que nadie suba directo)

1. En el repo: **Settings > Rules > Rulesets > New ruleset > New branch ruleset**.
   (En algunas cuentas aparece como **Settings > Branches > Add branch protection rule**.)
2. Nombre: `proteger-main`. En *Enforcement status* elige **Active**.
3. En *Target branches*, agrega la rama por defecto (`main`).
4. Activa:
   - **Require a pull request before merging**, con **1 aprobación** requerida.
   - **Block force pushes**.
   - **Restrict deletions**.
5. Guarda con **Create**.

> **Nota:** en cuentas gratuitas, las reglas de protección funcionan en repositorios **públicos**. En un repositorio **privado** con plan gratuito puede que no se apliquen. Si es tu caso, hagan un acuerdo de equipo: *nadie sube a `main` sin Pull Request y sin revisión*.

## Parte E · Flujo de trabajo diario

### 1. Clonar el repo (una sola vez)
```bash
git clone https://github.com/TU_USUARIO/centinela-agave.git
cd centinela-agave
```

### 2. Antes de empezar cada tarea: actualizar `main` y crear tu rama
```bash
git switch main
git pull
git switch -c vision/dataset-anotacion
```
**Nombres de rama:** `rol/tarea-corta`. Ejemplos:
`vision/entrenamiento-yolov8`, `ipo/cohortes`, `ipo/endpoint`, `software/panel-seccion-1`, `software/etl-denue`, `mecatronica/bom`, `entregables/pitch`.

### 3. Trabajar y guardar cambios
```bash
git status                      # ver qué cambió
git add vision/src/entrenar.py  # agregar archivos concretos
git commit -m "feat(vision): script de entrenamiento YOLOv8"
```
**Formato de mensajes:** `tipo(area): descripción corta`
- `feat` nueva función, `fix` corrección, `docs` documentación, `data` datos, `chore` orden o configuración.

Haz commits pequeños y seguidos. Es mejor 5 commits claros que uno gigante.

### 4. Subir tu rama
La primera vez:
```bash
git push -u origin vision/dataset-anotacion
```
Las siguientes: `git push`

### 5. Abrir un Pull Request
1. En GitHub aparece un botón **Compare & pull request**. Púlsalo (o ve a la pestaña *Pull requests > New pull request*).
2. Base: `main`. Compare: tu rama.
3. Llena la plantilla (qué cambia, cómo probarlo, checklist).
4. En **Reviewers** elige a otra persona.
5. Pulsa **Create pull request**.

### 6. Revisar y fusionar
- Quien revisa abre **Files changed**, comenta y pulsa **Approve** o **Request changes**.
- Con la aprobación, el autor pulsa **Squash and merge** y luego **Delete branch**.

### 7. Mantener tu rama al día
Si `main` avanzó mientras trabajabas:
```bash
git switch main
git pull
git switch vision/dataset-anotacion
git merge main
```

### 8. Si hay conflictos
Git marca los archivos en conflicto con `<<<<<<<`, `=======` y `>>>>>>>`. Abre el archivo, deja la versión correcta, borra las marcas y:
```bash
git add archivo_resuelto
git commit
```
Si no sabes cuál versión es la correcta, **pregunta a la persona que editó ese archivo**. Las carpetas separadas por rol reducen mucho los conflictos.

## Comandos de rescate

| Situación | Comando |
|---|---|
| Ver en qué rama estoy | `git branch` |
| Ver historial corto | `git log --oneline -10` |
| Descartar cambios de un archivo no guardado | `git restore ruta/archivo` |
| Quitar un archivo del `git add` | `git restore --staged ruta/archivo` |
| Guardar cambios a medias sin commit | `git stash` y luego `git stash pop` |
| Corregir el último mensaje de commit (antes de subir) | `git commit --amend` |
| Cambiar de rama | `git switch nombre-de-rama` |

## Archivos pesados

GitHub rechaza archivos de más de 100 MB. Por eso:
- Datasets de imágenes, `.blend`, CAD, videos y pesos grandes del modelo van en **Drive** (con enlace en `docs/ENLACES.md`).
- En Git solo: código, `.md`, tablas CSV pequeñas, imágenes ligeras (menos de 5 MB) y los pesos `best.pt` si pesan pocos MB.
- Si algo grande se subió por accidente, avisa al dueño antes de seguir: no basta con borrarlo en el siguiente commit.

## Lista rápida de verificación antes de abrir un PR

- [ ] Mi rama parte de un `main` actualizado
- [ ] Lo mío corre desde cero siguiendo el README de mi carpeta
- [ ] No hay archivos pesados ni contraseñas ni claves
- [ ] Mis supuestos nuevos están escritos
- [ ] Pedí revisión a alguien
