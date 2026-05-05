#!/bin/bash
# カランメソッド ドリル関数
# Usage: calan_drill "Question?" "Answer." [wait_seconds]

calan_drill() {
  local question="$1"
  local answer="$2"
  local wait_sec="${3:-1}"

  # 質問を2回読み上げ
  say -v Samantha -r 220 "$question"
  sleep 0.3
  say -v Samantha -r 220 "$question"

  # ユーザーが答える時間を待つ
  sleep "$wait_sec"

  # 答えを読み上げ（2回）
  say -v Samantha -r 220 "$answer"
  sleep 0.3
  say -v Samantha -r 220 "$answer"
}

# 直接実行された場合のデモ
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  calan_drill "${1:-Is this a book?}" "${2:-Yes, it is a book.}" "${3:-5}"
fi
