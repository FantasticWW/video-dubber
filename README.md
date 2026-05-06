# 视频配音工具

一个基于 Python + Kivy 的 Android 应用，支持本地上传多个视频并边播放边配音。

## 功能特性

- 从本地添加多个视频到列表
- 视频列表管理（选择、删除、清空）
- 视频播放预览
- 实时配音录制
- 配音音频保存

## 开发环境设置

### 桌面端测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py
```

### Android APK 打包

#### 方法一：使用 Buildozer（推荐，在 Linux 环境）

1. 安装 Buildozer：
```bash
pip install buildozer
```

2. 初始化（如果需要）：
```bash
buildozer init
```

3. 编译 APK：
```bash
# 调试版本
buildozer android debug

# 发布版本
buildozer android release
```

4. 编译后的 APK 位于 `bin/` 目录

#### 方法二：使用 GitHub Actions 自动编译

创建 `.github/workflows/build.yml`:

```yaml
name: Build Android APK

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Build with Buildozer
      uses: ArtemSBulgakov/buildozer-action@v1
      id: buildozer
      with:
        workdir: .
        buildozer_version: stable

    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: app-debug
        path: ${{ steps.buildozer.outputs.filename }}
```

#### 方法三：使用 Docker

```bash
# 拉取镜像
docker pull kivy/buildozer

# 运行编译
docker run --rm -v "$PWD":/home/user/hostcwd kivy/buildozer android debug
```

## 项目结构

```
video/
├── main.py            # 主应用代码
├── buildozer.spec     # Buildozer 配置文件
├── requirements.txt   # Python 依赖
└── README.md          # 说明文档
```

## 权限说明

APK 需要以下 Android 权限：

- `READ_EXTERNAL_STORAGE` - 读取视频文件
- `WRITE_EXTERNAL_STORAGE` - 保存配音文件
- `RECORD_AUDIO` - 录制配音
- `CAMERA` - 相机权限（预留）
- `INTERNET` - 网络权限（预留）

## 使用说明

1. 点击「添加视频」选择本地视频文件
2. 在视频列表中点击选择要配音的视频
3. 视频开始播放后，点击「开始配音」
4. 配音完成后点击「停止配音」
5. 点击「播放配音」预览录制效果
6. 点击「保存配音」导出配音文件

## 注意事项

1. **桌面端限制**：桌面端测试时文件选择和录音功能可能受限，完整功能需要在 Android 设备上测试

2. **视频格式**：支持 MP4, AVI, MOV, MKV, 3GP, WebM 等常见格式

3. **视频音频合并**：完整合并视频和音频需要 FFmpeg 支持，建议在应用外使用专业工具完成

4. **存储权限**：Android 11+ 需要额外申请存储权限

## 常见问题

### Q: 编译 APK 时报错？
A: 确保 buildozer.spec 中的配置正确，特别是 `android.api` 和 `android.minapi` 值

### Q: 视频无法播放？
A: 检查视频格式是否支持，确保已授予存储权限

### Q: 录音无声音？
A: 确保已授予录音权限，检查设备麦克风是否正常

## License

MIT License