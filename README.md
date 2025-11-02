# 网页转APK工具

这是一个Python脚本，用于将指定的网址转换为Android APK应用。该工具使用Capacitor框架，将网页嵌入到WebView中，创建一个原生Android应用。

## 功能特性

- 将任何网址转换为Android APK应用
- 自动使用根目录下的PNG文件作为应用图标
- 自定义应用ID和应用名称
- 自动处理Android图标尺寸适配

## 环境要求

- Python 3.6+
- Node.js 和 npm
- Android SDK
- Java JDK 11或更高版本

## 环境变量配置
在构建APK前，需要设置以下环境变量：

### macOS/Linux
```bash
export ANDROID_HOME=/path/to/android/sdk
export JAVA_HOME=/path/to/java
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

### Windows (PowerShell)
```powershell
$env:ANDROID_HOME="C:\path\to\android\sdk"
$env:JAVA_HOME="C:\path\to\java"
$env:PATH+=";$env:ANDROID_HOME\tools;$env:ANDROID_HOME\platform-tools"
```

## 安装依赖

### Python依赖

脚本会自动安装Pillow库用于图像处理，也可以手动安装：

```bash
pip install Pillow
```

### Node.js依赖

脚本会自动安装Capacitor相关依赖，但需要先确保Node.js已安装：

```bash
# 安装Node.js后，脚本会自动运行以下命令
npm install --save @capacitor/core @capacitor/cli
```

## 使用方法

### 基本用法
```bash
python web_to_apk.py <网址>
```

### 自定义参数

- `--app-id`：指定应用ID（默认：com.example.webapp）
- `--app-name`：指定应用名称（默认：从URL自动生成）
- `--icon`：指定图标文件路径（默认：查找根目录中的PNG文件）
- `--skip-build`：仅设置项目，跳过构建过程
- `--debug`：启用调试模式，输出详细信息

示例：

```bash
python web_to_apk.py https://example.com --app-id com.mycompany.myapp --app-name "我的网页应用" --icon my_custom_icon.png
```

### 高级选项
```bash
# 仅设置项目，不构建APK
python web_to_apk.py https://example.com --skip-build

# 启用调试模式
python web_to_apk.py https://example.com --debug
```

## 功能说明
1. 脚本会自动设置Capacitor项目
2. 处理应用图标（支持PNG格式）
3. 通过命令行构建APK
4. 构建完成后，APK文件将位于 `android/app/build/outputs/apk/debug/app-debug.apk`

## 工作原理

1. 验证输入的URL格式
2. 更新Capacitor配置文件
3. 创建index.html文件，使用iframe加载指定网页
4. 初始化Capacitor项目并添加Android平台
5. 处理并更新Android应用图标
6. 打开Android Studio进行最终构建

## 注意事项

1. 确保目标网址支持在WebView中加载（没有X-Frame-Options限制）
2. 首次构建会下载大量依赖，需要耐心等待
3. 确保已正确设置ANDROID_HOME和JAVA_HOME环境变量
4. 确保Android SDK已安装并包含所需的构建工具
5. 图标文件会自动查找（优先使用根目录中的PNG文件）
6. 如果遇到构建问题，请使用 `--debug` 参数获取详细错误信息

## 故障排除

- 如果遇到npm或Capacitor相关错误，请确保Node.js版本兼容
- 如果图标未正确显示，请检查PNG文件是否有效
- 如果网页加载失败，可能是网站限制了iframe嵌入

## 构建说明

脚本将自动执行命令行构建，生成Debug版本的APK文件。构建过程中需要：

1. 确保ANDROID_HOME环境变量已正确设置，指向Android SDK目录
2. 确保JAVA_HOME环境变量已正确设置，指向JDK目录
3. 首次构建会下载大量依赖，需要耐心等待

构建完成后，APK文件将位于：
`android/app/build/outputs/apk/debug/app-debug.apk`

### 构建Release版本

如需构建Release版本，您需要：
1. 在Android项目中配置签名信息
2. 然后手动运行：
```bash
cd android
./gradlew assembleRelease
```

## 许可证

MIT License