// UserPromptSubmit hook: appends every user prompt to history/PROMPTS.md.
// Must stay silent on stdout (stdout of this hook is injected into Claude's context)
// and must never block the prompt, so all errors are swallowed.
const fs = require("fs");
const path = require("path");

let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => (raw += chunk));
process.stdin.on("end", () => {
  try {
    const input = JSON.parse(raw);
    const root = process.env.CLAUDE_PROJECT_DIR || input.cwd || process.cwd();
    const file = path.join(root, "history", "PROMPTS.md");
    const stamp = new Date().toISOString().replace("T", " ").slice(0, 19) + " UTC";
    const session = (input.session_id || "unknown").slice(0, 8);
    const prompt = String(input.prompt || "").trimEnd();
    const entry = `\n## ${stamp} · session \`${session}\`\n\n\`\`\`\`text\n${prompt}\n\`\`\`\`\n`;
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.appendFileSync(file, entry, "utf8");
  } catch (err) {
    process.stderr.write(`log-prompt hook failed: ${err.message}\n`);
  }
  process.exit(0);
});
