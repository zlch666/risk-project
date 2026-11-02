# MySQL 8.0.28 免安装版部署到 D 盘：解压 → 初始化 → 注册服务 → 建库建号
$ErrorActionPreference = 'Continue'
$ROOT = 'D:\mysql8'
$ZIP  = 'D:\risk_project\_install\mysql-8.0.28-winx64.zip'
$DATA = Join-Path $ROOT 'data'
$SVC  = 'MySQL80'

Write-Output "=== 1) 解压 ==="
if (Test-Path (Join-Path $ROOT 'bin\mysqld.exe')) { Write-Output "已解压过，跳过" }
else {
    New-Item -ItemType Directory -Force -Path $ROOT | Out-Null
    & "$env:SystemRoot\System32\tar.exe" -xf $ZIP -C $ROOT
    # 解压后通常多一层目录，拍平
    $inner = Get-ChildItem $ROOT -Directory | Where-Object { $_.Name -like 'mysql-8.0*' } | Select-Object -First 1
    if ($inner) {
        Get-ChildItem $inner.FullName -Force | Move-Item -Destination $ROOT -Force
        Remove-Item $inner.FullName -Recurse -Force
    }
    Write-Output "解压完成：$ROOT"
}
$MYSQLD = Join-Path $ROOT 'bin\mysqld.exe'
$MYSQL  = Join-Path $ROOT 'bin\mysql.exe'
if (-not (Test-Path $MYSQLD)) { throw "找不到 mysqld.exe，解压结构异常" }

Write-Output "=== 2) 写 my.ini ==="
$ini = @"
[mysqld]
basedir=$($ROOT -replace '\\','/')
datadir=$($DATA -replace '\\','/')
port=3306
character-set-server=utf8mb4
collation-server=utf8mb4_general_ci
default-authentication-plugin=mysql_native_password
max_connections=200
skip-name-resolve
[client]
port=3306
default-character-set=utf8mb4
"@
[System.IO.File]::WriteAllText((Join-Path $ROOT 'my.ini'), $ini, (New-Object System.Text.UTF8Encoding($false)))
Write-Output "my.ini 已写入"

Write-Output "=== 3) 初始化数据目录 ==="
if (Test-Path (Join-Path $DATA 'mysql')) {
    Write-Output "数据目录已初始化，跳过"
} else {
    & $MYSQLD --initialize-insecure --basedir="$ROOT" --datadir="$DATA" --console 2>&1 |
        Select-Object -Last 6
    Write-Output "初始化完成"
}

Write-Output "=== 4) 注册并启动服务 ==="
$installed = & sc.exe query $SVC 2>$null
if ($LASTEXITCODE -ne 0) {
    & $MYSQLD --install $SVC --defaults-file="$(Join-Path $ROOT 'my.ini')" 2>&1 | Select-Object -Last 3
} else { Write-Output "服务已存在" }
& net.exe start $SVC 2>&1 | Select-Object -Last 2

Write-Output "=== 5) 等待 3306 ==="
$ok = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 2
    if (Get-NetTCPConnection -LocalPort 3306 -State Listen -ErrorAction SilentlyContinue) { $ok = $true; break }
}
Write-Output ("3306 监听: " + $(if ($ok) { '是' } else { '否' }))

if (-not $ok) {
    Write-Output "=== 5b) 服务方式失败，改用后台进程 ==="
    Start-Process $MYSQLD -ArgumentList "--defaults-file=`"$(Join-Path $ROOT 'my.ini')`"" -WindowStyle Hidden
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 2
        if (Get-NetTCPConnection -LocalPort 3306 -State Listen -ErrorAction SilentlyContinue) { $ok = $true; break }
    }
    Write-Output ("后台进程方式 3306 监听: " + $(if ($ok) { '是' } else { '否' }))
}

if (-not $ok) { throw "MySQL 未能启动，请检查 data 目录权限" }

Write-Output "=== 6) 建库建号 ==="
$sql = @"
ALTER USER 'root'@'localhost' IDENTIFIED BY 'root123456';
CREATE DATABASE IF NOT EXISTS risk_assessment DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER IF NOT EXISTS 'risk_user'@'localhost' IDENTIFIED BY 'risk123456';
ALTER USER 'risk_user'@'localhost' IDENTIFIED BY 'risk123456';
GRANT ALL PRIVILEGES ON risk_assessment.* TO 'risk_user'@'localhost';
FLUSH PRIVILEGES;
SELECT VERSION() AS mysql_version;
SHOW DATABASES;
SHOW GRANTS FOR 'risk_user'@'localhost';
"@
$sqlFile = Join-Path $env:TEMP 'init_mysql.sql'
[System.IO.File]::WriteAllText($sqlFile, $sql, (New-Object System.Text.UTF8Encoding($false)))
& $MYSQL -u root --skip-password --default-character-set=utf8mb4 -e "source $($sqlFile -replace '\\','/')" 2>&1 |
    Select-Object -Last 20

Write-Output "=== 7) 用 risk_user 验证连接 ==="
& $MYSQL -u risk_user -prisk123456 -e "SELECT DATABASE() AS cur_db, VERSION() AS ver; SHOW DATABASES;" 2>&1 |
    Select-Object -Last 12

Write-Output "=== 完成 ==="
