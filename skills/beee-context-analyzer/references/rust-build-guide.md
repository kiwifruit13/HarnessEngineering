# Rust 核心编译指南

## 目录
1. [前置要求](#前置要求)
2. [编译步骤](#编译步骤)
3. [集成到 Python](#集成到-python)
4. [故障排查](#故障排查)

## 前置要求

### 安装 Rust 工具链

如果没有安装 Rust，请先安装：

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

验证安装：

```bash
rustc --version
cargo --version
```

### Python 依赖

确保已安装 Python 开发工具：

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev

# macOS
brew install python3

# Windows
# Python 安装包中已包含
```

## 编译步骤

### 1. 进入 Rust 核心目录

```bash
cd beee-context-analyzer/scripts/rust_core
```

### 2. 编译 Release 版本

```bash
cargo build --release
```

### 3. 验证编译结果

编译成功后，会在以下位置生成库文件：

- **Linux**: `target/release/libbeee_core.so`
- **macOS**: `target/release/libbeee_core.dylib`
- **Windows**: `target/release/beee_core.dll`

检查文件是否生成：

```bash
ls -lh target/release/libbeee_core.so  # Linux/macOS
ls -lh target/release/beee_core.dll   # Windows
```

### 4. 复制到指定位置（可选）

Python 代码会自动在以下位置搜索库文件：

```
beee-context-analyzer/scripts/rust_core/libbeee_core.so
beee-context-analyzer/scripts/rust_core/target/release/libbeee_core.so
```

如果需要，可以复制到指定位置：

```bash
cp target/release/libbeee_core.so ./
```

## 集成到 Python

### 自动检测

Python 代码会自动检测并加载 Rust 核心：

```python
from scripts.weight_calculator import WeightCalculator

calc = WeightCalculator()
# 自动检测并加载 Rust 核心（如果可用）
```

### 手动验证

运行测试脚本验证 Rust 核心是否正常工作：

```python
from scripts.weight_calculator import WeightCalculator
import numpy as np

calc = WeightCalculator()

if calc.rust_lib:
    print("✅ Rust 核心已加载")
else:
    print("⚠️ 使用 Python 实现")

# 测试计算
query = np.random.randn(128).astype(np.float32)
candidates = [np.random.randn(128).astype(np.float32) for _ in range(10)]
scores = calc.compute_similarity(query, candidates)
print(f"相似度分数: {scores}")
```

### 预期输出

```
✅ Rust 核心已加载: /path/to/libbeee_core.so
相似度分数: [0.123, 0.456, ...]
```

或

```
ℹ️ 未找到 Rust 核心，使用 Python 实现
相似度分数: [0.123, 0.456, ...]
```

## 故障排查

### 问题1: 编译失败 - 找不到 Python 开发文件

**错误信息**：
```
error: failed to run custom build command for `pyo3 v0.20.0`
```

**解决方案**：

Ubuntu/Debian:
```bash
sudo apt-get install python3-dev
```

macOS:
```bash
brew install python3
```

### 问题2: 编译失败 - 找不到 numpy 开发文件

**错误信息**：
```
error: failed to run custom build command for `numpy v0.20.0`
```

**解决方案**：

确保已安装 numpy：
```bash
pip install numpy
```

### 问题3: Python 无法加载 .so 文件

**错误信息**：
```
ImportError: dynamic module does not define init function
```

**解决方案**：

检查 Python 版本是否匹配：
```bash
python --version
```

Rust 编译时使用的 Python 版本必须与运行时版本一致。

如果版本不匹配，重新指定 Python 版本编译：

```bash
# 设置 Python 版本
export PYTHON_SYS_EXECUTABLE=$(which python3)

# 重新编译
cargo clean
cargo build --release
```

### 问题4: 加载失败 - 缺少依赖库

**错误信息**：
```
ImportError: libpython3.x.so: cannot open shared object file
```

**解决方案**：

安装 Python 动态库：

Ubuntu/Debian:
```bash
sudo apt-get install libpython3.x
```

### 问题5: 性能没有提升

**可能原因**：
1. Rust 核心未正确加载
2. 数据量太小，优化效果不明显
3. Python 版本实现已经足够快

**验证步骤**：

```python
import time
from scripts.weight_calculator import WeightCalculator
import numpy as np

calc = WeightCalculator()
query = np.random.randn(128).astype(np.float32)
candidates = [np.random.randn(128).astype(np.float32) for _ in range(1000)]

# 测试性能
start = time.time()
scores = calc.compute_similarity(query, candidates)
elapsed = time.time() - start

print(f"计算耗时: {elapsed*1000:.2f}ms")
print(f"使用的核心: {'Rust' if calc.rust_lib else 'Python'}")
```

如果耗时 > 200ms，可能 Rust 核心未正确加载。

## 性能优化建议

### 1. 启用 LTO（链接时优化）

在 `Cargo.toml` 中已配置：

```toml
[profile.release]
lto = true
opt-level = 3
```

### 2. 使用目标特定的优化

```bash
cargo build --release --target=x86_64-unknown-linux-gnu
```

### 3. 启用并行编译

```bash
cargo build --release -j$(nproc)
```

## 跨平台编译

### Linux → Windows

需要交叉编译工具链：

```bash
rustup target add x86_64-pc-windows-gnu
cargo build --release --target=x86_64-pc-windows-gnu
```

### Linux → macOS

需要 macOS SDK 和交叉编译工具链（较复杂，建议在 macOS 上编译）。

## 调试

### 启用调试信息

```bash
cargo build
# 不带 --release，生成未优化的版本，便于调试
```

### 使用 GDB 调试

```bash
gdb python
(gdb) break PyInit_beee_core
(gdb) run your_script.py
```

## 清理

清理编译产物：

```bash
cargo clean
```

清理后重新编译：

```bash
cargo build --release
```

## 常见问题

### Q: Rust 核心是必须的吗？

A: 不是。Rust 核心是可选的性能优化。如果没有编译 Rust 核心，系统会自动使用 Python 纯实现（功能相同，性能略低）。

### Q: 可以在不重新编译 Python 代码的情况下替换 Rust 核心吗？

A: 可以。只需要重新编译 Rust 核心，替换 `.so` 文件即可。Python 代码会在运行时自动加载新的库文件。

### Q: 支持哪些平台？

A: 支持 Linux、macOS、Windows。需要分别在每个平台上编译。

### Q: 如何贡献 Rust 代码？

A: 修改 `src/lib.rs` 后，重新编译并测试：

```bash
cargo build --release
python test_rust_core.py
```

## 附录

### 完整的编译脚本

创建 `build.sh`：

```bash
#!/bin/bash
set -e

echo "开始编译 Rust 核心..."
cargo build --release

echo "复制库文件..."
cp target/release/libbeee_core.so ./

echo "验证编译..."
python -c "
from ctypes import CDLL
lib = CDLL('./libbeee_core.so')
print('✅ Rust 核心编译成功')
"

echo "完成！"
```

运行：

```bash
chmod +x build.sh
./build.sh
```

### 技术支持

如果遇到问题：

1. 检查 Rust 版本：`rustc --version`
2. 检查 Python 版本：`python --version`
3. 查看完整错误信息
4. 参考 Rust 官方文档：https://doc.rust-lang.org/
