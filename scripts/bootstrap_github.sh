#!/usr/bin/env bash
# ==============================================================================
# Bootstrap: 建公开 GitHub repo + 配 Secrets + 首次 push
# 在你本机终端跑(sandbox 里没 gh token,必须本地执行)
# ==============================================================================
# 用法:
#   bash scripts/bootstrap_github.sh
#
# 前置:
#   1. 已安装 gh CLI:  brew install gh (macOS)
#   2. 已登录:         gh auth login
#   3. .env 文件存在,且填了 ANTHROPIC_API_KEY / OPENAI_API_KEY
# ==============================================================================

set -euo pipefail

REPO_OWNER="${REPO_OWNER:-LovRanRan}"
REPO_NAME="${REPO_NAME:-ai-jobs-trends}"
VISIBILITY="${VISIBILITY:-public}"  # public | private

echo "📦 Bootstrap GitHub repo: ${REPO_OWNER}/${REPO_NAME} (${VISIBILITY})"
echo

# --- 检查 ---
command -v gh >/dev/null || { echo "❌ gh CLI not found. Install: brew install gh"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "❌ gh not logged in. Run: gh auth login"; exit 1; }
[[ -f .env ]] || { echo "⚠️  .env not found. Copy .env.example to .env and fill keys first."; exit 1; }

# 读 .env
set -a; source .env; set +a
[[ -n "${ANTHROPIC_API_KEY:-}" ]] || { echo "❌ ANTHROPIC_API_KEY not set in .env"; exit 1; }
[[ -n "${OPENAI_API_KEY:-}" ]]    || { echo "❌ OPENAI_API_KEY not set in .env"; exit 1; }

# --- 1. 建 repo(如果已存在会跳过)---
if gh repo view "${REPO_OWNER}/${REPO_NAME}" >/dev/null 2>&1; then
  echo "ℹ️  Repo already exists, skipping create"
else
  echo "→ Creating ${VISIBILITY} repo..."
  gh repo create "${REPO_OWNER}/${REPO_NAME}" \
    --"${VISIBILITY}" \
    --description "Daily-updated AI job market trends tracker." \
    --homepage "https://github.com/${REPO_OWNER}/${REPO_NAME}"
fi

# --- 2. 绑 remote(幂等)---
# 默认 HTTPS(gh 已登录即可,无需 SSH key)
# 若你 gh 是 SSH 登录,可 export REMOTE_PROTOCOL=ssh
REMOTE_PROTOCOL="${REMOTE_PROTOCOL:-https}"
if [[ "${REMOTE_PROTOCOL}" == "ssh" ]]; then
  REMOTE_URL="git@github.com:${REPO_OWNER}/${REPO_NAME}.git"
else
  REMOTE_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}.git"
fi

if git remote get-url origin >/dev/null 2>&1; then
  CURRENT_URL="$(git remote get-url origin)"
  if [[ "${CURRENT_URL}" != "${REMOTE_URL}" ]]; then
    echo "→ Fixing remote URL: ${CURRENT_URL} → ${REMOTE_URL}"
    git remote set-url origin "${REMOTE_URL}"
  else
    echo "ℹ️  Remote 'origin' already set correctly"
  fi
else
  echo "→ Adding remote origin (${REMOTE_PROTOCOL})..."
  git remote add origin "${REMOTE_URL}"
fi

# 确保 gh 作为 HTTPS git credential helper(只在 HTTPS 模式下设置)
if [[ "${REMOTE_PROTOCOL}" == "https" ]]; then
  gh auth setup-git >/dev/null 2>&1 || true
fi

# --- 3. Push 初始 commit ---
echo "→ Pushing main..."
git branch -M main
git push -u origin main

# --- 4. 配 Secrets ---
echo "→ Setting GitHub Secrets..."
echo "${ANTHROPIC_API_KEY}" | gh secret set ANTHROPIC_API_KEY --repo "${REPO_OWNER}/${REPO_NAME}"
echo "${OPENAI_API_KEY}"    | gh secret set OPENAI_API_KEY    --repo "${REPO_OWNER}/${REPO_NAME}"

# --- 5. 触发一次 CI 验证 ---
echo "→ Triggering CI (workflow_dispatch)..."
gh workflow run daily-run.yml --repo "${REPO_OWNER}/${REPO_NAME}" || echo "ℹ️  Workflow dispatch may need 30s after first push"

echo
echo "✅ Done!"
echo "   View:     https://github.com/${REPO_OWNER}/${REPO_NAME}"
echo "   Actions:  https://github.com/${REPO_OWNER}/${REPO_NAME}/actions"
echo "   Secrets:  https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/secrets/actions"
