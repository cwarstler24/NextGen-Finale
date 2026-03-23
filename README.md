# Setup

## Database Credentials

The backend can now read database credentials from either `credentials.json` or environment variables.

### Option 1: Local file

1. Copy `credentials_template.json` and rename it to `credentials.json`
2. Fill in the values where there are `[brackets]`:
   - Replace `[database]` with your database name
   - Replace `[username]` with your database username
   - Replace `[password]` with your database password
3. The hostname, port, protocol, and authentication fields are pre-configured

**Note:** `credentials.json` is gitignored and should never be committed to version control.

### Option 2: Environment variables

Set these variables instead of using `credentials.json`:

- `DB_DATABASE`
- `DB_HOSTNAME`
- `DB_PORT`
- `DB_PROTOCOL`
- `DB_AUTHENTICATION`
- `DB_UID`
- `DB_PWD`
- `DB_ENVIRONMENT` (`PRODUCTION` or `TEST`)
- `DB_SCHEMA` (optional override)

## Running the Frontend

The frontend uses Vite and is managed from the repository root with the npm scripts in `package.json`.

1. Install dependencies if you have not already:
   ```bash
   npm install
   ```
2. Start the frontend development server:
   ```bash
   npm run dev
   ```
3. Open the local URL shown in the terminal, which is typically `http://localhost:5173`.

If `mkdocs.yml` is present at the repository root, `npm run dev` also starts the MkDocs development server on `http://127.0.0.1:8001`. It uses `venv\Scripts\python.exe` when that virtual environment exists, so you do not need to activate the venv manually first. You can still run the docs server by itself with:

```bash
npm run docs:dev
```

The frontend source code lives in `main/frontend`, and the Vite dev server will automatically reload as you make changes.

## Running the Backend

Start the API from the repository root with:

```bash
uvicorn main.backend.server:app --reload
```

The backend listens on `http://localhost:8000` by default.

## Docker Demo Stack

A repeatable local demo stack is available with Docker Compose.

### What it starts

- Frontend on `http://localhost:5173`
- Backend API on `http://localhost:18137`
- MkDocs site on `http://localhost:18139`

### Important limitation

The repository now containerizes the application stack, but it does **not** provision the IBM DB2 database itself. The backend container still needs reachable DB2 credentials, either for your shared DB2 server or a DB2 instance you manage separately.

### First-time setup

1. Copy `docker/demo.env.example` to `.env`
2. Fill in the DB2 values in `.env`
3. (Optional) change `BACKEND_HOST_PORT`, `DOCS_HOST_PORT`, and `FRONTEND_PORT` in `.env`
4. Start the stack:
   ```bash
   docker compose up --build
   ```

### Useful commands

Start in the background:

```bash
docker compose up --build -d
```

Stop the stack:

```bash
docker compose down
```

Rebuild only the frontend after env URL changes:

```bash
docker compose build frontend
```

The compose file is in `compose.yaml`, and the container build files live in `docker/`.
