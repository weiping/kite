// tools/orchestrator/run-role.mjs
// 参考实现：接口按你自己的编排框架调整，形状比签名重要。
import { query } from '@anthropic-ai/claude-agent-sdk';
import { readFileSync } from 'node:fs';
import { loadAgentConfig } from './agents.mjs';
import { budget } from './budget.mjs';

export async function runRole(role, prompt, { cwd = process.cwd() } = {}) {
  const cfg = loadAgentConfig(role);          // 从 .claude/agents.json 读
  budget.assertNotExhausted();                // 预算耗尽直接抛，不进模型

  const result = await query({
    prompt,
    options: {
      systemPrompt: readFileSync(`.claude/skills/${role}/SKILL.md`, 'utf8'),
      model: cfg.model,
      maxTurns: cfg.maxTurns,
      allowedTools: cfg.allowedTools,          // 权限来自配置，不来自提示词
      cwd,
      env: cfg.env,                            // 白名单注入，不透传宿主环境
    },
  });

  budget.add(result.modelUsage);               // 直读用量，不靠自报
  return { data: parseJson(result), usage: result.modelUsage };
}
