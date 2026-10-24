@echo off
chcp 65001 >nul
setlocal

echo ============================================
echo  单词智能记忆系统 - Windows exe 打包脚本
echo ============================================

echo [1/3] 安装依赖...
python -m pip install -r requirements.txt
if errorlevel 1 goto error

echo [2/3] 清理旧产物...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/3] 使用 PyInstaller 打包...
python -m PyInstaller app.spec --noconfirm
if errorlevel 1 goto error

echo.
echo 打包完成！输出文件：dist\WordMemorySystem.exe
goto end

:error
echo.
echo 打包失败，请检查上方错误信息。
exit /b 1

:end
endlocal