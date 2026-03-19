import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { getMkDocsConfigPath, mkdocsArgs, resolvePythonCommand } from './mkdocs.mjs';

const rootDir = process.cwd();
const mkdocsConfigPath = getMkDocsConfigPath(rootDir);
const viteBinPath = path.join(rootDir, 'node_modules', 'vite', 'bin', 'vite.js');
const childProcesses = [];

let shuttingDown = false;

function stopChildren() {
    for (const child of childProcesses) {
        if (child.killed) {
            continue;
        }

        child.kill('SIGINT');
    }
}

function shutdown(exitCode = 0) {
    if (shuttingDown) {
        return;
    }

    shuttingDown = true;
    stopChildren();
    setTimeout(() => process.exit(exitCode), 250);
}

function startProcess(command, args) {
    const child = spawn(command, args, {
        cwd: rootDir,
        stdio: 'inherit',
    });

    child.on('error', (error) => {
        console.error(`[dev] Failed to start ${command}:`, error);
        shutdown(1);
    });

    child.on('exit', (code) => {
        if (!shuttingDown) {
            shutdown(code ?? 0);
        }
    });

    childProcesses.push(child);
}

if (!existsSync(viteBinPath)) {
    console.error('[dev] Could not find the local Vite executable. Run `npm install` first.');
    process.exit(1);
}

process.on('SIGINT', () => shutdown(0));
process.on('SIGTERM', () => shutdown(0));

startProcess(process.execPath, [viteBinPath]);

if (existsSync(mkdocsConfigPath)) {
    const python = resolvePythonCommand(rootDir);
    console.log(`[dev] Starting MkDocs with ${python.label} on http://127.0.0.1:8001`);
    startProcess(python.command, mkdocsArgs);
} else {
    console.log('[dev] mkdocs.yml not found; starting the frontend only.');
}
