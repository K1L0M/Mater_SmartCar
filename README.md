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

## 3. 版本管理说明

- `Debug/`、`Release/`、`.ads/`、`*.launch`、`.metadata/` 属于编译/调试生成物，已在 `.gitignore` 中忽略（与《删除临时文件.bat》清理的内容一致），**克隆后首次编译会自动重新生成**。
- `libraries/zf_device/zf_device_config.a` 是逐飞提供的预编译静态库，已在 `.gitattributes` 中标记为二进制，必须随仓库提交，否则链接失败。
- 新增用户代码建议直接放在 `code/` 目录（不要建子目录），再在工程中引用。

## 4. 两端分工与分支模型

### 4.1 两个远端的职责

| 远端 | 地址 | 放什么 | 用途 |
|---|---|---|---|
| **origin**（Gitee） | `git@gitee.com:wisdel/Mater_SmartCar.git` | **所有分支**：main、develop、feature/* | 日常拉取 + 推送（国内速度快） |
| **github**（GitHub） | `https://github.com/K1L0M/Mater_SmartCar.git` | **只放 `main`** | 比赛版归档 / 对外展示 |

- 本机 `origin` 就是 **Gitee**，所以 `git pull`、`git push` 默认都走 Gitee。
- GitHub 只接收 `main` 的推送，`github` 远端的推送范围已固定为 `main`，不会把 develop、个人分支带上去。

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

## 5. 日常操作（维护者与队友完全一致）

### 5.1 第一次使用：克隆 + 建自己的分支

三个人做法相同，只有分支名不同：

```bash
git clone git@gitee.com:wisdel/Mater_SmartCar.git
cd Mater_SmartCar
git config user.name  "你的名字"
git config user.email "你的邮箱"

git checkout develop
git checkout -b feature/你的名字        # 例如 feature/张三
git push -u origin feature/你的名字     # 第一次推送，建立跟踪关系
```

> 只克隆 Gitee 即可，`origin` 自动指向 Gitee，`git pull`/`git push` 都走 Gitee，不需要再配置任何远端。
> 队友**不要**使用别人已有的 `feature/xxx` 分支。

### 5.2 每次改代码（三个人一样）

```bash
git pull --rebase        # 从 Gitee 拉取 develop 的最新改动（origin = Gitee）
git add -A
git commit -m "改了什么"
git push                 # 推到 Gitee 上自己的 feature 分支
```

> 第一次推送后，之后直接 `git push` 即可，不用再写分支名。

### 5.3 把功能合并回 develop

在 Gitee 网页上，从 `feature/你的名字` 向 `develop` 发 **Pull Request**（推荐，能看见改动），或者本地合并：

```bash
git checkout develop
git pull --rebase
git merge --no-ff feature/你的名字
git push origin develop
```

**合并前必须保证 ADS 里能编译通过**，`Debug/`、`.ads/` 之类的生成物不会被提交。

### 5.4 发版到 main（维护者）

比赛前把 develop 合成比赛版：

```bash
git checkout main
git pull --rebase origin main
git merge --no-ff develop
git push origin main     # 推到 Gitee
git push github main     # 推到 GitHub（只有 main）
```

> GitHub 上只有 `main`，队友不需要也无法往 GitHub 推送；`github` 远端已配置为只推 `main`。

## 6. 注意事项

1. **不要往 GitHub 推 develop/个人分支**：GitHub 只保留比赛版 `main`，日常改动一律在 Gitee。
2. **不要直接在 main 上提交**：main 只接受来自 develop 的合并，否则比赛版会混进半成品。
3. **两人同时推同一个分支**：后推的人会收到 `rejected (non-fast-forward)`，执行 `git pull --rebase` 再 `git push`；**不要用 `git push -f`**。
4. **生成物不入库**：`Debug/`、`.ads/`、`*.launch` 已被 `.gitignore` 忽略，不要用 `git add -f` 强行加入；`zf_device_config.a` 是二进制静态库，别用文本编辑器打开保存。
5. **每人用自己的账号和密钥**：`user.name`/`user.email`、Gitee SSH 公钥都要各自配置，不要共用。

## 7. 参考

- 逐飞 TC264 开源库：<https://gitee.com/seekfree/TC264_Library>
- 逐飞科技：<https://seekfree.taobao.com/>
