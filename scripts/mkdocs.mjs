import path from 'node:path';
import { existsSync } from 'node:fs';

export const mkdocsArgs = ['-m', 'mkdocs', 'serve', '-f', 'mkdocs.yml', '--dev-addr', '127.0.0.1:8001'];

export function getMkDocsConfigPath(rootDir = process.cwd()) {
	return path.join(rootDir, 'mkdocs.yml');
}

export function resolvePythonCommand(rootDir = process.cwd()) {
	const venvPythonPath = path.join(rootDir, 'venv', 'Scripts', 'python.exe');

	if (existsSync(venvPythonPath)) {
		return {
			command: venvPythonPath,
			label: 'the virtualenv Python',
		};
	}

	return {
		command: 'python',
		label: 'the system Python',
	};
}
