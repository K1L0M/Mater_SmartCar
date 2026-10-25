# Mater_SmartCar

基于**逐飞 TC264 开源库**（SeekFree TC264 Library）的 TC264D 智能车工程，克隆后可直接用 **AURIX Development Studio** 导入并编译。

## 1. 目录结构

```
Mater_SmartCar
├── .cproject / .project / .settings     ADS(Eclipse) 工程配置，工程名 Mater_SmartCar
├── Lcf_Tasking_Tricore_Tc.lsl           TASKING 链接脚本
├── code/                                用户代码目录（建议把新增 .c/.h 放这里）
├── user/                                主函数、中断（cpu0_main / cpu1_main / isr）
├── libraries/
│   ├── infineon_libraries/              Infineon iLLD 底层库
│   ├── zf_common/                       逐飞公共层
│   ├── zf_driver/                       逐飞外设驱动层
│   ├── zf_device/                       逐飞器件驱动层（含预编译库 zf_device_config.a）
│   └── doc/                             版本与许可证说明
├── 推荐IO分配.txt / 尽量不要使用的引脚.txt
├── 删除临时文件.bat                     清理 Debug、.ads、*.launch 等生成物
└── AURIX修改工程名称.bat                重命名工程用（一般无需执行）
```

## 2. 编译步骤

1. 安装 **AURIX Development Studio**（工程使用 v1.10.2 验证，需已安装 TASKING 编译器）。
2. `File → Import → General → Existing Projects into Workspace`，`Select root directory` 选择本仓库根目录。
3. 导入后工程名应为 **Mater_SmartCar**（与 `.project` 一致；若目录名不同，导入向导会以 `.project` 中的名字为准）。
4. 选择 `Debug` 配置 → `Project → Build Project`，生成 `Debug/Mater_SmartCar.elf`。
5. 下载运行：`Run → Debug Configurations`，新建 `DAS Debugger` 配置，选择对应调试器与 elf 后烧录。

> 工程内所有头文件路径均为 `${workspace_loc:/${ProjName}/...}` 形式的相对路径，不含任何本机绝对路径，因此换电脑克隆后可直接编译。

## 2.1 VS Code 头文件与 IntelliSense

- 用 VS Code 打开仓库根目录，选择 `AURIX TC264 (TASKING)` 配置。`.vscode/c_cpp_properties.json` 已包含 `code/**`、`user/**`、`libraries/**` 和 TASKING 标准库路径，`math.h`、`stdio.h` 等来自实际工具链。
- `env.TASKING_CTC` 默认指向本机 `D:/Infineon/AURIX-Studio-1.10.10/tools/Compilers/Tasking_1.1r8/ctc`。换电脑或升级 ADS 后，只需把这一项改成自己的 `ctc` 目录（其下应存在 `include/math.h`）。
- `compilerPath` 显式留空，避免扩展自动选择 Windows 桌面编译器；TASKING 的头文件路径和必要宏手动指定，语言标准与当前 Debug 构建的 C99 / C++14 一致。32 位 Clang IntelliSense 模式仅供编辑辅助，不是 TriCore 编译器；TASKING 专用语法仍以 ADS 的编译结果为准。
- 新增 `.c/.h` 可直接放入 `code/`；ADS 的 Debug 配置已加入该目录的头文件搜索路径。添加文件后在 ADS 刷新工程（F5）再构建，让生成的 Makefile 收录新源文件。若使用子目录，头文件建议按 `#include "模块/文件.h"`（相对于 `code/`）引用，或在 ADS 中显式添加相应目录；VS Code 的 `**` 递归搜索不会自动改变 ADS 编译选项。
- 如果仍显示旧的 1696 提示，执行 `C/C++: Reset IntelliSense Database`，然后执行 `Developer: Reload Window`。实际构建继续使用 ADS。

## 3. 版本管理说明

- `Debug/`、`Release/`、`.ads/`、`*.launch`、`.metadata/` 属于编译/调试生成物，已在 `.gitignore` 中忽略（与《删除临时文件.bat》清理的内容一致），**克隆后首次编译会自动重新生成**。
- `libraries/zf_device/zf_device_config.a` 是逐飞提供的预编译静态库，已在 `.gitattributes` 中标记为二进制，必须随仓库提交，否则链接失败。
- 新增用户代码建议直接放在 `code/` 目录，再在工程中引用；使用子目录时按第 2.1 节配置包含路径。

## 4. 两端分工与分支模型

### 4.1 两个远端的职责

| 远端 | 地址 | 放什么 | 用途 |
|---|---|---|---|
| **origin**（Gitee） | `git@gitee.com:wisdel/Mater_SmartCar.git` | **所有分支**：main、develop、feature/* | 日常拉取 + 推送（国内速度快） |
| **github**（GitHub） | `https://github.com/K1L0M/Mater_SmartCar.git` | **只放 `main`** | 比赛版归档 / 对外展示 |

- `origin` 是 **Gitee**。下面的命令显式指定远端和分支，不依赖各人机器上的默认推送设置。
- GitHub 约定只推送 `main`。远端地址和 `remote.github.push` 是本机配置，不会随克隆复制；维护者按 5.3 配置，且始终显式推送 `main`。

### 4.2 分支结构

```
main            可比赛 / 可烧录的稳定代码，只从 develop 合并
 └─ develop     日常集成分支，三个人的改动汇总到这里
     ├─ feature/<姓名>   每个人自己的开发分支
     ├─ feature/<姓名>
     └─ feature/<姓名>
```

| 分支 | 从哪分出 | 用途 | 推送到 |
|---|---|---|---|
| `main` | — | 比赛版、烧录版，**不直接在 main 上改代码** | Gitee + GitHub |
| `develop` | main | 日常集成，合并三个人的功能 | Gitee |
| `feature/<姓名>` | develop | 各自的开发分支，随便提交 | Gitee |

已有分支：`main`、`develop`、`feature/K1L0M`（维护者）。**另外两条由队友自己按 `feature/姓名` 创建**。

## 5. 三步走：个人分支 → develop → main

> ① 个人分支开发并推送 → ② Gitee 合并 PR，再同步回个人分支 → ③ 维护者发布 main，结束后自动返回个人分支。
> 日常 develop 通过 PR 集成；共享过的个人分支使用 merge 同步，不重写历史、不强推。维护者经明确授权的直接推送属于例外，仍须先 fetch 并使用普通快进推送。

**以下命令在仓库根目录的 PowerShell 中执行。** 手动命令逐条执行，任何失败都先处理，不能跳过错误继续粘贴后续步骤。`scripts/git-workflow.ps1` 会检查每条 Git 命令的退出码，失败即停止。

脚本必须从自己的 `feature/<姓名>` 分支启动。运行前先提交需要保留的修改，或自行 `git stash push -u`（之后需要自己 `git stash pop` 并处理可能的冲突）；脚本不自动暂存、提交或 stash。存在未跟踪文件、未完成的合并/rebase 等操作时会拒绝运行。

### 5.0 第一次使用：克隆并建立个人分支

```powershell
git clone git@gitee.com:wisdel/Mater_SmartCar.git
cd Mater_SmartCar
git config user.name "你的名字"
git config user.email "你的邮箱"
git fetch --prune origin

# 仅用于第一次创建新分支；把“你的名字”替换为自己的名字
git switch -c feature/你的名字 origin/develop
git push -u origin HEAD:refs/heads/feature/你的名字
```

如果自己的远端分支已经存在，**不要重新创建同名分支或覆盖它**：本地没有该分支时执行 `git switch --track -c feature/你的名字 origin/feature/你的名字`；本地已有时执行 `git switch feature/你的名字`。已有分支完成切换后执行 5.1 的 `Sync`。

此时停留在个人分支。每个人只使用自己的 `feature/*`，不要使用队友的分支。

### 5.1 第一步：同步、开发、推送个人分支

```powershell
# 1) 开工前同步；结束后仍在当前个人分支
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\git-workflow.ps1 -Action Sync

# 2) 修改代码，在 ADS 中编译通过，再检查实际改动
git status
git diff

# 3) 只暂存本次要提交的文件；下面路径按实际修改替换
git add -- code/你的文件.c code/你的文件.h
git diff --cached
git commit -m "完成了什么功能"

# 4) 重新获取远端、合入远端个人分支及 develop，再推送当前个人分支
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\git-workflow.ps1 -Action Push
```

- `Sync` / `Push` 将本地 `develop` 安全快进到本次获取的 `origin/develop`，并把远端个人分支和 develop 的变化合入当前个人分支；**不会切到 develop 开发**。`Sync` 不推送，`Push` 只推送当前个人分支。
- 同步发生代码变化后要重新编译/测试，PR 合并前必须确认集成后的代码通过；Git 合并成功不代表固件编译或功能测试通过。
- `git push` 只上传提交，**不会等待 PR、不会自动拉取别人后续的改动，也不会让带有未合并提交的个人分支与 develop 完全相同**。此时保留个人提交才是正确行为。
- 脚本遇到合并冲突会中止它刚发起的合并，并报告失败；按 5.4 手动解决后重试。不会留下一个未提示的冲突状态让后续命令接着运行。

### 5.2 第二步：个人分支 → develop，合并后同步收尾

1. 在 Gitee 的本仓库「Pull Requests」页面新建 PR，源分支为自己的 `feature/姓名`，目标为 `develop`。
2. 审查修改并完成编译/测试；有冲突时按 5.4 处理并重新推送。
3. 选择**保留源提交历史的普通合并（Merge）或快进合并**，不要选择 Squash/Rebase 合并；长期使用的个人分支不要勾选合并后删除源分支。
4. **等网页显示 PR 已合并后**，回到本地执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\git-workflow.ps1 -Action AfterMerge
```

`AfterMerge` 会获取 Gitee 最新状态，确认本地和远端个人分支的所有提交都已经进入 develop，然后快进本地 `develop` 和当前个人分支、普通推送个人分支，最后核对提交哈希。成功后满足：

```text
当前分支 = feature/自己的名字
本地个人分支 = Gitee 个人分支 = 本地 develop = 本次核验的 Gitee develop
工作区干净，可以直接开始下一轮开发
```

**不需要再手动签回个人分支。** 如果在 PR 合并后又写了新提交、PR 尚未合并、采用了 Squash/Rebase，或者远端在核验期间继续变化，脚本会明确报错，不会用 `reset --hard` / 强推丢弃提交。先处理提示；有新功能时先保留提交、另开 PR，全部合入后再执行 `AfterMerge`。相同文件内容不一定代表相同提交历史。

### 5.3 第三步：develop → main（维护者，比赛前）

维护者首次在本机配置 GitHub（`git remote -v` 中没有 `github` 时才执行 `remote add`；地址错误用 `git remote set-url` 修正）：

```powershell
git remote -v
git remote add github https://github.com/K1L0M/Mater_SmartCar.git
git config remote.github.push refs/heads/main:refs/heads/main
```

确认准备发布的 develop 已编译、测试通过，且自己停留在干净的个人分支上，再执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\git-workflow.ps1 -Action Publish -ReleaseMessage "合并 develop 到 main：比赛版"
```

脚本获取 origin 和 GitHub main，更新本地 develop、快进本地 main，然后以 `--no-ff` 合并本次获取的 develop，普通推送 main 到两个远端，核对两处 main 哈希，并在成功或失败时尝试**返回启动时的个人分支**。如果返回失败，会明确报错并要求检查 `git status`；不要在 main 上继续开发。

- 两个远端不能作为一个 Git 原子事务推送：若 Gitee 成功、GitHub 失败，会报告失败并保留已成功的推送。修复权限/网络后重跑 `Publish`，不要 reset 或强推；若远端有独有提交，先人工核对。
- `Already up to date`、`Everything up-to-date` **都可能是正常成功**，例如重复发布。成功依据是退出码、目标提交的包含关系及远端哈希核验，不是输出必须出现新合并或哈希范围。
- `Publish` 不会把 main 的发布合并提交反向合入 develop/个人分支，也不会把 develop/个人分支推到 GitHub；若需要对齐个人分支与 develop，按 5.2 执行 `AfterMerge`。

### 5.4 故障处理与自检

```powershell
git status
git branch --show-current
git fetch --prune origin
git branch -vv
git rev-list --left-right --count develop...origin/develop
```

最后两个数字分别为本地 develop 独有提交数、远端 develop 独有提交数：

| 结果 | 含义 | 处理 |
|---|---|---|
| `0 0` | 本地 develop 与本次 fetch 的远端一致 | 可以继续 |
| `0 N` | 本地 develop 落后 | 在个人分支运行 `Sync` / `AfterMerge` 安全快进 |
| `N 0` 或 `N M` | 本地 develop 有远端没有的提交 | 停止，先 `git branch backup/develop-before-repair develop` 备份（名称已存在则换新名称），核对提交并通过个人分支/PR 集成；不要直接硬重置 |

`git pull --ff-only` 成功**不能证明本地与远端完全相同**：本地仅领先时也可能成功并保持领先；失败还可能是网络、认证或跟踪配置问题，不能都解释成分叉。精确一致以哈希或 `rev-list` 的 `0 0` 为准。

个人分支发生冲突时，在自己的分支手动处理（每次只合并一个目标，解决完成后再进行下一个）：

```powershell
git branch --show-current        # 确认是自己的 feature/*
git fetch --prune origin
git merge --no-edit --no-autostash origin/feature/你的名字
# 若有冲突：编辑冲突文件，git add -- 实际解决的文件，再 git commit --no-edit
# 不继续本次合并则执行 git merge --abort；不能带着冲突运行下一条 merge
git merge --no-edit --no-autostash origin/develop
# 若有冲突，同样解决并提交；随后在 ADS 重新编译/测试
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\git-workflow.ps1 -Action Push
```

若推送被拒绝（远端在操作期间新增提交），重新执行 `Push` 合并更新后正常推送；遇到受保护分支/权限错误按平台权限处理，不能强推绕过。已有 rebase/cherry-pick 等未完成操作时，先按 `git status` 提示完成或中止该操作。

### 5.5 流程脚本的离线验证

安装 Python 3、Git 和 PowerShell 后，可在仓库根目录运行：

```powershell
python scripts/tests/test_git_workflow.py
```

测试在临时目录创建本地裸仓库模拟两个远端，覆盖同步、合并后四处分支一致、冲突中止、未合并提交保护、发布失败重试和自动返回个人分支；不会连接或修改真实 Gitee/GitHub。

## 6. 注意事项

1. **日常 develop 走 PR**，不直接在 develop 上开发；维护者经明确授权的直接推送也不能覆盖别人的历史。
2. **main 只接受 develop 合并**；发布流程结束要确认回到个人分支。
3. **先保存修改再同步**；脚本不会隐式 stash、自动 add 全部文件或生成业务提交。
4. **已推送个人分支使用 merge**；不依赖 rebase 后强推，不执行 `git push -f` 或未经检查的 `reset --hard`。
5. **合并后运行 `AfterMerge` 才完成本地同步闭环**；以后远端有新提交仍须再次同步，不存在永久自动一致。
6. **生成物不入库**：`Debug/`、`.ads/`、`*.launch` 已被忽略；`zf_device_config.a` 是二进制静态库，不能用文本编辑器修改。
7. **每人用自己的账号和密钥**；Git 身份、SSH 公钥、远端/推送配置均需在自己的机器配置。

## 7. 参考

- 逐飞 TC264 开源库：<https://gitee.com/seekfree/TC264_Library>
- 逐飞科技：<https://seekfree.taobao.com/>
