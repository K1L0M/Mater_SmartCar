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

## 4. 参考

- 逐飞 TC264 开源库：<https://gitee.com/seekfree/TC264_Library>
- 逐飞科技：<https://seekfree.taobao.com/>
