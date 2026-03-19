import { existsSync } from 'node:fs';
import { getMkDocsConfigPath, mkdocsArgs, resolvePythonCommand } from './mkdocs.mjs';
import { spawn } from 'node:child_process';

const rootDir = process.cwd();
const mkdocsConfigPath = getMkDocsConfigPath(rootDir);

if (!existsSync(mkdocsConfigPath)) {
	console.error('[docs:dev] Could not find mkdocs.yml at the repository root.');
	process.exit(1);
}

const python = resolvePythonCommand(rootDir);
console.log(`[docs:dev] Starting MkDocs with ${python.label} on http://127.0.0.1:8001`);

const child = spawn(python.command, mkdocsArgs, {
	cwd: rootDir,
	stdio: 'inherit',
});

child.on('error', (error) => {
	console.error(`[docs:dev] Failed to start MkDocs with ${python.command}:`, error);
	process.exit(1);
});

child.on('exit', (code) => {
	process.exit(code ?? 0);
});
