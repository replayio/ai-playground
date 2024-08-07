import * as path from 'path';
import { getArtifactsDir } from '../constants';

export function resolveFilePath(relativePath: string): string {
  return path.join(getArtifactsDir(), relativePath);
}

export function resolveModulePath(module: string): string {
  return resolveFilePath(`${module.replace('.', path.sep)}.ts`);
}

export function getModuleName(filePath: string): string {
  return path.basename(filePath, '.ts').replace(path.sep, '.');
}
