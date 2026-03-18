# Setup

## Database Credentials

Before running the application, you must configure database credentials:

1. Copy `credentials_template.json` and rename it to `credentials.json`
2. Fill in the values where there are `[brackets]`:
   - Replace `[database]` with your database name
   - Replace `[username]` with your database username
   - Replace `[password]` with your database password
3. The hostname, port, protocol, and authentication fields are pre-configured

**Note:** `credentials.json` is gitignored and should never be committed to version control.

# Running the Frontend

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

The frontend source code lives in `main/frontend`, and the Vite dev server will automatically reload as you make changes.
