@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ==========================================================
echo   Mater_SmartCar - 配置 GitHub + Gitee 双远端推送
echo   每个队友克隆后执行一次即可
echo ==========================================================
echo.

git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo [错误] 当前目录不是 Git 仓库，请把本脚本放在仓库根目录再运行。
    echo.
    pause
    exit /b 1
)

set "GITHUB_URL=https://github.com/K1L0M/Mater_SmartCar.git"
set "GITEE_URL=git@gitee.com:wisdel/Mater_SmartCar.git"

echo 当前仓库：%CD%
echo.

echo [1/3] 清除旧的推送地址 ...
git config --unset-all remote.origin.pushurl >nul 2>&1

echo [2/3] 添加 GitHub 推送地址 ...
git remote set-url --add --push origin "%GITHUB_URL%"

echo [3/3] 添加 Gitee 推送地址 ...
git remote set-url --add --push origin "%GITEE_URL%"

echo.
echo ---------- 当前远端配置 ----------
git remote -v
echo ----------------------------------
echo.
echo 完成。之后 git push 会依次推送到 GitHub 和 Gitee。
echo.
echo 提示：
echo   * 只想用 HTTPS 方式访问 Gitee（不想配 SSH 密钥）时，请把本脚本里的
echo     GITEE_URL 改成：https://gitee.com/wisdel/Mater_SmartCar.git
echo     首次推送输入 Gitee 用户名 + 私人令牌（不是登录密码）。
echo   * 推送失败或想确认两边是否一致，可执行：
echo       git ls-remote origin master
echo       git ls-remote git@gitee.com:wisdel/Mater_SmartCar.git master
echo     两个哈希相同即为同步。
echo.
pause
