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
├── 设置双远端推送.bat                   配置 GitHub + Gitee 双远端推送（队友首次使用执行一次）
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

## 4. 多人协作与推送同步

### 4.1 仓库有两个远端，内容必须一致

| 远端 | 地址 | 说明 |
|---|---|---|
| GitHub（主） | `https://github.com/K1L0M/Mater_SmartCar.git` | 主仓库、Issue/PR |
| Gitee（镜像） | `git@gitee.com:wisdel/Mater_SmartCar.git` | 国内访问快，内容与 GitHub 保持一致 |

维护者的本机 `origin` 配了**两个推送地址**，所以 `git push` 会依次推 GitHub 和 Gitee，`git pull` 只从 GitHub 拉。

> ⚠️ 这个双推配置只保存在各自电脑的 `.git/config` 里，**不会随仓库同步**。队友克隆后必须执行一次 `设置双远端推送.bat`，否则只会推到其中一个仓库，两边就会不一致。

### 4.2 队友第一次使用（4 步）

**① 先拿到推送权限**（没有权限会报 `403` 或 `You do not have permission to push`）

- GitHub：仓库 `Settings → Collaborators → Add people`，邀请你的 GitHub 账号，去邮箱接受邀请
- Gitee：仓库 `管理 → 仓库成员 → 邀请用户`，角色选「开发者」

**② 克隆**（两个地址任选，国内网络建议用 Gitee）

```bash
git clone https://github.com/K1L0M/Mater_SmartCar.git
# 或
git clone git@gitee.com:wisdel/Mater_SmartCar.git
```

**③ 配置双远端推送**（只需一次）

在仓库根目录双击运行 `设置双远端推送.bat`，看到 `git remote -v` 里有两条 `(push)` 即成功。

**④ 配置自己的身份与认证**

```bash
git config user.name  "你的名字"
git config user.email "你的邮箱"
```

| 平台 | 认证方式 |
|---|---|
| Gitee（脚本默认 SSH） | `ssh-keygen -t ed25519 -C "你的邮箱"` 生成密钥，把 `~/.ssh/id_ed25519.pub` 内容贴到 Gitee → 设置 → **SSH 公钥** |
| Gitee（改用 HTTPS） | 把脚本里的 `GITEE_URL` 换成 `https://gitee.com/wisdel/Mater_SmartCar.git`，首次推送输入 Gitee 用户名 + **私人令牌**（设置 → 私人令牌，不是登录密码） |
| GitHub | HTTPS 用 Personal Access Token，或同样配置 SSH key |

> ⚠️ 每个人用自己的账号和密钥，**不要共用别人的私钥**；`user.name/user.email` 也要改成自己的，否则提交记录全挂在同一个人名下。

### 4.3 日常推送流程

```bash
git pull --rebase          # 先拉取队友的提交（有本地改动时先 commit 或 stash）
git add -A
git commit -m "改了什么"
git push                   # 一条命令同时推 GitHub + Gitee
```

推送后核对两边是否一致（两个哈希应完全相同）：

```bash
git ls-remote origin master
git ls-remote git@gitee.com:wisdel/Mater_SmartCar.git master
```

### 4.4 必须知道的 4 件事

1. **双推不是原子操作**：GitHub 成功、Gitee 失败（断网/没权限）时，两边就会不一致。`git push` 报错后先按 4.3 的两条 `ls-remote` 核对，缺哪边就补推：
   ```bash
   git push git@gitee.com:wisdel/Mater_SmartCar.git master
   ```
2. **不要只推一边**：除非是在补推失败的那一侧，平时一律用不带参数的 `git push`。
3. **两人同时推送**：后推的人会收到 `! [rejected] non-fast-forward`，执行 `git pull --rebase` 后再 `git push` 即可；**不要用 `git push -f`**，会覆盖队友的提交。
4. **生成物不入库**：`Debug/`、`.ads/`、`*.launch` 已被 `.gitignore` 忽略，不要用 `git add -f` 强行加入；`zf_device_config.a` 是二进制静态库，别用文本编辑器打开保存，否则链接会失败。

## 5. 参考

- 逐飞 TC264 开源库：<https://gitee.com/seekfree/TC264_Library>
- 逐飞科技：<https://seekfree.taobao.com/>
