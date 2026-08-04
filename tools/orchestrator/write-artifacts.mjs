// tools/orchestrator/write-artifacts.mjs
// 参考实现：落盘永远由编排代码执行，带白名单校验。
import { resolve, extname, dirname } from 'node:path';
import { writeFileSync, mkdirSync } from 'node:fs';

export function writeArtifacts(root, files, { allowDir, allowExt }) {
  const base = resolve(root, allowDir);
  for (const f of files) {
    const dest = resolve(root, f.path);
    // 注意 base + '/' 不能省：只判前缀会把 tests-evil/ 当成 tests/ 的子路径放行。
    if (!dest.startsWith(base + '/')) throw new Error(`路径越界: ${f.path}`);
    if (!allowExt.includes(extname(dest))) throw new Error(`扩展名不允许: ${f.path}`);
    mkdirSync(dirname(dest), { recursive: true });
    writeFileSync(dest, f.content, 'utf8');
  }
  return files.map(f => f.path);
}
