#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT
cc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined "$ROOT_DIR/tests/player_animation_test.c" -o "$TEST_DIR/player_animation_test"
"$TEST_DIR/player_animation_test"
python3 "$ROOT_DIR/tests/test_routes.py"
python3 "$ROOT_DIR/tests/test_inventory_snapshot.py"
bash -n "$ROOT_DIR/tools/build_deploy_v101.sh"
