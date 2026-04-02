#!/bin/bash
# AIBI Token 管理工具
# 用法:
#   aibi-token.sh save <token>   保存 Token
#   aibi-token.sh check          检查 Token 是否有效
#   aibi-token.sh show           显示当前 Token（脱敏）
#   aibi-token.sh guide          显示获取指引

TOKEN_DIR="$HOME/.aibi"
TOKEN_FILE="$TOKEN_DIR/token"
API_BASE="https://hdbs-service-api.hellobike.cn"

save_token() {
    local token="$1"
    if [ -z "$token" ]; then
        echo "❌ 请提供 Token 值"
        echo "用法: $0 save bearer_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        exit 1
    fi
    if [[ ! "$token" =~ ^bearer_ ]]; then
        echo "⚠️  Token 格式可能不正确，应以 bearer_ 开头"
        echo "仍然保存? (y/N)"
        read -r confirm
        [ "$confirm" != "y" ] && exit 1
    fi
    mkdir -p "$TOKEN_DIR"
    echo "$token" > "$TOKEN_FILE"
    chmod 600 "$TOKEN_FILE"
    echo "✅ Token 已保存到 $TOKEN_FILE"
    check_token
}

check_token() {
    if [ ! -f "$TOKEN_FILE" ]; then
        echo "❌ TOKEN_MISSING — 未找到 $TOKEN_FILE"
        echo "运行 '$0 guide' 查看获取方式"
        return 1
    fi
    local token
    token=$(cat "$TOKEN_FILE" | tr -d '[:space:]')
    if [ -z "$token" ]; then
        echo "❌ TOKEN_EMPTY — 文件存在但内容为空"
        return 1
    fi
    echo "⏳ 正在验证 Token 有效性..."
    local response
    response=$(curl -s --max-time 10 \
        "${API_BASE}/api/v1/db/logicDatabases?env=PRO&logicDbName=sparklab_starcard" \
        -H "Token: $token" 2>/dev/null)
    local code
    code=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('code','error'))" 2>/dev/null)
    if [ "$code" = "200" ]; then
        echo "✅ TOKEN_VALID — Token 有效"
        return 0
    elif [ "$code" = "401" ]; then
        echo "❌ TOKEN_EXPIRED — Token 已过期，请重新获取"
        echo "运行 '$0 guide' 查看获取方式"
        return 1
    else
        echo "⚠️  TOKEN_UNKNOWN — 无法判断 (网络问题或 API 异常)"
        echo "响应: $response"
        return 2
    fi
}

show_token() {
    if [ ! -f "$TOKEN_FILE" ]; then
        echo "❌ 未找到 Token 文件"
        return 1
    fi
    local token
    token=$(cat "$TOKEN_FILE" | tr -d '[:space:]')
    local len=${#token}
    if [ "$len" -le 16 ]; then
        echo "Token: ${token:0:4}****"
    else
        echo "Token: ${token:0:10}...${token: -6} (共${len}字符)"
    fi
    echo "文件: $TOKEN_FILE"
    echo "更新: $(stat -f '%Sm' -t '%Y-%m-%d %H:%M:%S' "$TOKEN_FILE" 2>/dev/null || stat -c '%y' "$TOKEN_FILE" 2>/dev/null | cut -d. -f1)"
}

print_guide() {
    cat << 'GUIDE'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DBOPS SSO Token 获取指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【前置】先申请数据库只读权限（已有权限跳过）

  打开以下链接 → 点「申请权限」→ 选「只读」：

  星卡:     https://dbops.hellobike.cn/?#/workspace/resource/MySQL/sparklab_starcard/1198/info
  绘本:     https://dbops.hellobike.cn/?#/workspace/resource/MySQL/sparklab_picbook/1199/info
  泡泡玩具: https://dbops.hellobike.cn/?#/workspace/resource/MySQL/sg_sparklab_poptoy/1200/info

  等权限审批通过后再继续。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【获取 Token】

步骤 1: 浏览器打开 https://dbops.hellobike.cn 并登录（SSO）

步骤 2: 按 F12 打开开发者工具

步骤 3: 切到「Network（网络）」标签页

步骤 4: 在 DBOPS 页面随意点击一个数据库

步骤 5: 在 Network 列表中找任意一个请求：
         域名为 hdbs-service-api.hellobike.cn

步骤 6: 点击该请求 → 查看「Request Headers」
         找到 Token 字段，值类似:
         bearer_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

步骤 7: 复制完整 Token（含 bearer_ 前缀）

步骤 8: 运行保存:
         ./aibi-token.sh save "你的Token"

⏰ Token 有效期约 8 小时，过期需重新获取
⚠️  如查询返回「无权限」，请先完成上面的权限申请

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GUIDE
}

case "${1:-}" in
    save)  save_token "$2" ;;
    check) check_token ;;
    show)  show_token ;;
    guide) print_guide ;;
    *)
        echo "AIBI Token 管理工具"
        echo ""
        echo "用法:"
        echo "  $0 save <token>   保存 Token"
        echo "  $0 check          检查 Token 有效性"
        echo "  $0 show           查看当前 Token（脱敏）"
        echo "  $0 guide          显示获取指引"
        ;;
esac
