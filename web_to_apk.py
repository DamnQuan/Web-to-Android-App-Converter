# -*- coding: utf-8 -*-
# 网页转APK工具
# 本脚本用于将指定网址转换为Android APK应用，使用Capacitor框架实现。
# 应用将在WebView中加载指定的网址内容。

import os
import sys
import json
import subprocess
import tempfile
import shutil
import argparse
from urllib.parse import urlparse

def validate_url(url):
    # 验证URL格式是否正确
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def find_icon_file(directory):
    # 在指定目录查找图标文件（优先PNG，然后是SVG）
    # 先查找PNG
    for file in os.listdir(directory):
        if file.lower().endswith('.png') and 'icon' in file.lower():
            return os.path.join(directory, file)
    # 如果没有找到PNG，查找SVG
    for file in os.listdir(directory):
        if file.lower().endswith('.svg') and 'icon' in file.lower():
            return os.path.join(directory, file)
    return None

def update_capacitor_config(app_id, app_name, web_dir="."):
    # 更新Capacitor配置文件
    config_path = os.path.join(os.getcwd(), 'capacitor.config.json')
    
    # 检查必要的配置键
    required_keys = ['bundledWebRuntime', 'npmClient', 'android', 'ios']
    
    # 如果配置文件存在，读取它
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print("警告: Capacitor配置文件格式错误，将创建新的配置文件")
            config = {}
    else:
        config = {}
    
    # 更新基本配置
    config['appId'] = app_id
    config['appName'] = app_name
    config['webDir'] = web_dir
    
    # 确保高级配置存在
    if 'bundledWebRuntime' not in config:
        config['bundledWebRuntime'] = False
    if 'npmClient' not in config:
        config['npmClient'] = 'npm'
    if 'android' not in config:
        config['android'] = {
            'allowMixedContent': True,
            'webContentsDebuggingEnabled': True
        }
    if 'ios' not in config:
        config['ios'] = {
            'minVersion': '13.0'
        }
    
    # 写入配置文件
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        print(f"已更新Capacitor配置: appId={app_id}, appName={app_name}")
    except Exception as e:
        print(f"警告: 无法写入Capacitor配置文件: {e}")

def create_index_html(url):
    # 创建index.html文件，用于加载指定的网页
    # 确保public目录存在
    public_dir = os.path.join(os.getcwd(), 'public')
    os.makedirs(public_dir, exist_ok=True)
    
    html_content = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>网页应用</title>
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: #f0f0f0;
        }}
        #webview {{
            width: 100%;
            height: 100%;
            border: none;
            position: absolute;
            top: 0;
            left: 0;
        }}
        .loading-spinner {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            z-index: 1000;
        }}
        @keyframes spin {{
            0% {{ transform: translate(-50%, -50%) rotate(0deg); }}
            100% {{ transform: translate(-50%, -50%) rotate(360deg); }}
        }}
        .error-message {{
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            z-index: 1000;
        }}
    </style>
</head>
<body>
    <div class="loading-spinner"></div>
    <div class="error-message" id="errorMessage">
        <h3>加载失败</h3>
        <p>无法加载网页，请检查网络连接后重试</p>
        <button onclick="reloadPage()">重试</button>
    </div>
    <iframe id="webview" src="{url}" sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe>
    <script>
        function reloadPage() {{
            document.getElementById('errorMessage').style.display = 'none';
            document.querySelector('.loading-spinner').style.display = 'block';
            document.getElementById('webview').src = document.getElementById('webview').src;
        }}
        
        // 监听iframe加载完成
        document.getElementById('webview').onload = function() {{
            console.log('网页加载完成');
            document.querySelector('.loading-spinner').style.display = 'none';
        }};
        
        // 监听加载错误
        document.getElementById('webview').onerror = function() {{
            console.log('网页加载失败');
            document.querySelector('.loading-spinner').style.display = 'none';
            document.getElementById('errorMessage').style.display = 'block';
        }};
        
        // 处理返回按钮
        window.addEventListener('popstate', function(event) {{
            const webview = document.getElementById('webview');
            if (webview.contentWindow.history.length > 1) {{
                webview.contentWindow.history.back();
            }}
        }});
        
        // 处理Android返回按钮（通过Capacitor提供的API）
        window.addEventListener('DOMContentLoaded', function() {{
            // 尝试初始化Capacitor
            try {{
                if (window.Capacitor) {{
                    console.log('Capacitor已加载');
                }}
            }} catch (e) {{
                console.log('Capacitor未加载:', e);
            }}
        }});
    </script>
</body>
</html>
'''
    
    # 写入public目录下
    index_path = os.path.join(public_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content.strip())
    
    print(f"已创建index.html，将加载网页: {url}")
    print(f"文件位置: {index_path}")

def setup_capacitor_project():
    # 设置Capacitor项目
    # 检查是否已安装npm依赖
    if not os.path.exists('package.json'):
        print("创建package.json文件...")
        try:
            subprocess.run(['npm', 'init', '-y'], check=False)
        except Exception as e:
            print(f"警告: 创建package.json失败: {e}")
    
    # 安装Capacitor CLI和核心包
    print("安装Capacitor依赖...")
    try:
        subprocess.run(['npm', 'install', '--save', '@capacitor/core', '@capacitor/cli', '@capacitor/android'], check=False)
        print("Capacitor依赖安装完成")
    except Exception as e:
        print(f"警告: 安装Capacitor依赖失败: {e}")
    
    # 初始化Capacitor（如果尚未初始化）
    if not os.path.exists('capacitor.config.json'):
        print("初始化Capacitor项目...")
        try:
            # 使用指定参数进行非交互式初始化
            app_id = "com.example.webapp"
            app_name = "web-to-apk"
            subprocess.run(['npx', 'cap', 'init', app_id, app_name, '--web-dir', 'public'], check=False)
            print("Capacitor项目初始化完成")
        except Exception as e:
            print(f"警告: Capacitor初始化失败: {e}")
    
    # 创建public目录作为webDir
    public_dir = os.path.join(os.getcwd(), 'public')
    if not os.path.exists(public_dir):
        print("创建public目录...")
        os.makedirs(public_dir, exist_ok=True)
    
    # 更新capacitor.config.json中的webDir为'public'
    update_web_dir_config()
    
    # 添加Android平台
    if not os.path.exists('android'):
        print("添加Android平台...")
        try:
            # 先确保@capacitor/android已安装
            print("确保@capacitor/android已安装...")
            subprocess.run(['npm', 'install', '--save', '@capacitor/android'], check=False)
            # 然后添加Android平台
            subprocess.run(['npx', 'cap', 'add', 'android'], check=False)
            print("Android平台添加完成")
        except Exception as e:
            print(f"错误: 添加Android平台失败: {e}")
            raise
    else:
        print("Android平台已存在，跳过添加步骤")

def update_web_dir_config():
    # 更新webDir配置为'public'
    config_path = os.path.join(os.getcwd(), 'capacitor.config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 更新webDir
            config['webDir'] = 'public'
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            print("已更新webDir配置为'public'")
        except Exception as e:
            print(f"警告: 无法更新webDir配置: {e}")

def update_android_icon(icon_path):
    # 更新Android应用图标
    if not icon_path or not os.path.exists(icon_path):
        print("警告: 未找到有效的图标文件，将使用默认图标")
        return
    
    # Android图标目录
    android_res_dir = os.path.join('android', 'app', 'src', 'main', 'res')
    
    if not os.path.exists(android_res_dir):
        print("警告: Android项目目录结构不存在，请先运行 npx cap add android")
        return
    
    # 图标尺寸列表
    icon_sizes = [
        ('mipmap-mdpi', 48),
        ('mipmap-hdpi', 72),
        ('mipmap-xhdpi', 96),
        ('mipmap-xxhdpi', 144),
        ('mipmap-xxxhdpi', 192)
    ]
    
    print(f"更新Android应用图标: {icon_path}")
    
    # 检查图标文件类型
    is_svg = icon_path.lower().endswith('.svg')
    
    # 处理SVG图标
    if is_svg:
        try:
            # 尝试导入必要的库
            try:
                import cairosvg
            except ImportError:
                print("安装cairosvg库用于SVG到PNG的转换...")
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', 'cairosvg'], check=False)
                    import cairosvg
                except Exception:
                    print("警告: 无法安装cairosvg，尝试使用PIL作为备选")
                    cairosvg = None
            
            # 处理并复制图标到各个尺寸目录
            for mipmap_dir, size in icon_sizes:
                dest_dir = os.path.join(android_res_dir, mipmap_dir)
                os.makedirs(dest_dir, exist_ok=True)
                
                launcher_path = os.path.join(dest_dir, 'ic_launcher.png')
                round_path = os.path.join(dest_dir, 'ic_launcher_round.png')
                
                try:
                    if cairosvg:
                        # 使用cairosvg转换
                        cairosvg.svg2png(url=icon_path, write_to=launcher_path, width=size, height=size)
                        cairosvg.svg2png(url=icon_path, write_to=round_path, width=size, height=size)
                    else:
                        # 备选方案：如果没有cairosvg，使用PIL（虽然PIL处理SVG可能有问题）
                        from PIL import Image
                        img = Image.open(icon_path)
                        img_resized = img.resize((size, size), Image.Resampling.LANCZOS)
                        img_resized.save(launcher_path, 'PNG')
                        img_resized.save(round_path, 'PNG')
                    
                    print(f"已生成图标: {launcher_path}")
                    print(f"已生成图标: {round_path}")
                except Exception as e:
                    print(f"警告: 生成{size}x{size}图标失败: {e}")
            
            print("Android图标更新完成")
        except Exception as e:
            print(f"错误: 更新SVG图标时发生错误: {e}")
    # 处理PNG图标
    else:
        # 检查是否安装了Pillow库用于图像处理
        try:
            from PIL import Image
        except ImportError:
            print("安装Pillow库用于图像处理...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow'], check=False)
                from PIL import Image
            except Exception as e:
                print(f"错误: 安装Pillow失败: {e}")
                return
        
        # 处理并复制图标到各个尺寸目录
        try:
            for mipmap_dir, size in icon_sizes:
                dest_dir = os.path.join(android_res_dir, mipmap_dir)
                os.makedirs(dest_dir, exist_ok=True)
                
                # 调整图标尺寸
                try:
                    img = Image.open(icon_path)
                    img_resized = img.resize((size, size), Image.Resampling.LANCZOS)
                    
                    # 保存图标文件
                    launcher_path = os.path.join(dest_dir, 'ic_launcher.png')
                    img_resized.save(launcher_path, 'PNG')
                    print(f"已生成图标: {launcher_path}")
                    
                    # 也保存圆形图标
                    round_path = os.path.join(dest_dir, 'ic_launcher_round.png')
                    img_resized.save(round_path, 'PNG')
                    print(f"已生成图标: {round_path}")
                except Exception as e:
                    print(f"警告: 生成{size}x{size}图标失败: {e}")
            
            print("Android图标更新完成")
        except Exception as e:
            print(f"错误: 更新图标时发生错误: {e}")

def build_android_app():
    # 构建Android APK (命令行方式，不依赖Android Studio)
    # 先同步Capacitor项目
    print("同步Capacitor项目...")
    try:
        subprocess.run(['npx', 'cap', 'sync'], check=False)
    except Exception as e:
        print(f"警告: Capacitor同步失败: {e}")
    
    # 执行命令行构建
    print("开始命令行构建APK...")
    print("此过程将使用Gradle进行构建，可能需要一些时间...")
    
    # 进入android目录执行构建命令
    android_dir = os.path.join(os.getcwd(), 'android')
    if not os.path.exists(android_dir):
        print("错误: Android目录不存在，请先确保Capacitor项目设置正确")
        return False
    
    try:
        # 在Mac/Linux上使用./gradlew，Windows上使用gradlew.bat
        gradle_cmd = './gradlew' if os.path.exists(os.path.join(android_dir, 'gradlew')) else 'gradlew.bat'
        
        # 设置执行权限（针对Mac/Linux）
        if gradle_cmd == './gradlew' and os.name != 'nt':
            subprocess.run(['chmod', '+x', gradle_cmd], cwd=android_dir, check=False)
        
        # 使用gradlew构建debug版本APK
        print("正在构建Debug版本APK...")
        process = subprocess.Popen([gradle_cmd, 'assembleDebug'], 
                                 cwd=android_dir,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # 实时输出构建日志
        for line in process.stdout:
            print(line.strip())
        
        # 等待构建完成
        stdout, stderr = process.communicate()
        if stderr:
            print(f"构建警告/错误: {stderr}")
        
        if process.returncode == 0:
            apk_path = os.path.join(android_dir, 'app', 'build', 'outputs', 'apk', 'debug', 'app-debug.apk')
            if os.path.exists(apk_path):
                print("\nDebug版本APK构建完成!")
                print(f"APK文件位置: {apk_path}")
                
                # 提示用户可以选择构建release版本
                print("\n注意: 这是Debug版本APK，仅用于测试")
                print("如果需要Release版本，请确保已配置签名信息")
                print(f"然后可以运行: {gradle_cmd} assembleRelease")
                
                return True
            else:
                print("\n构建似乎成功，但未找到APK文件")
                print("请检查构建输出或手动查找APK文件")
                return False
        else:
            print(f"\n构建失败，退出码: {process.returncode}")
            print("请检查Android SDK是否正确安装")
            print("以及JAVA_HOME环境变量是否设置正确")
            return False
    except Exception as e:
        print(f"构建过程中发生错误: {e}")
        return False

def main():
    # 主函数
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='网页转APK工具')
    parser.add_argument('url', help='要嵌入的网页URL')
    parser.add_argument('--app-id', default='com.example.webapp', help='应用ID (默认: com.example.webapp)')
    parser.add_argument('--app-name', help='应用名称 (如果不提供，将从URL自动生成)')
    parser.add_argument('--icon', help='应用图标路径 (默认: 查找根目录中的图标文件)')
    parser.add_argument('--skip-build', action='store_true', help='跳过构建步骤，只设置项目')
    parser.add_argument('--debug', action='store_true', help='启用调试输出')
    args = parser.parse_args()
    
    # 验证URL
    if not validate_url(args.url):
        print("错误: 无效的URL格式，请确保包含http://或https://")
        sys.exit(1)
    
    # 如果没有提供应用名称，从URL生成
    if not args.app_name:
        parsed_url = urlparse(args.url)
        domain = parsed_url.netloc.replace('www.', '')
        args.app_name = domain.replace('.', '-')
    
    # 查找图标文件
    icon_path = args.icon
    if not icon_path:
        icon_path = find_icon_file(os.getcwd())
    
    print(f"=== 网页转APK工具 ===")
    print(f"目标URL: {args.url}")
    print(f"应用ID: {args.app_id}")
    print(f"应用名称: {args.app_name}")
    print(f"图标文件: {icon_path if icon_path else '未找到，将使用默认图标'}")
    print("====================")
    
    # 检查环境
    check_environment()
    
    # 更新Capacitor配置
    update_capacitor_config(args.app_id, args.app_name)
    
    # 创建index.html
    create_index_html(args.url)
    
    # 设置Capacitor项目
    try:
        setup_capacitor_project()
        
        # 同步项目
        print("\n同步Capacitor项目...")
        try:
            subprocess.run(['npx', 'cap', 'sync'], check=False)
        except Exception as e:
            print(f"警告: Capacitor同步失败: {e}")
        
        # 更新Android图标
        update_android_icon(icon_path)
        
        # 如果不需要构建，直接退出
        if args.skip_build:
            print("\n项目设置完成，已跳过构建步骤")
            print("您可以稍后手动运行构建命令")
            print("建议在运行构建前设置以下环境变量:")
            print("  export ANDROID_HOME=/path/to/android/sdk")
            print("  export JAVA_HOME=/path/to/java")
            return
        
        # 提示用户下一步操作
        print("\n=== 项目准备完成 ===")
        print("即将开始命令行构建APK")
        print("注意: 首次构建可能需要下载依赖，耗时较长")
        print("如果遇到构建问题，请确保ANDROID_HOME和JAVA_HOME环境变量已正确设置")
        input("按Enter键继续...")
        
        # 构建Android应用
        success = build_android_app()
        
        if success:
            print("\n操作完成！APK已成功构建")
            print("您可以在Android设备或模拟器上安装并测试此APK")
        else:
            print("\n构建过程中出现错误，请查看上面的错误信息")
            print("常见问题解决方法:")
            print("1. 确保已正确设置ANDROID_HOME环境变量")
            print("2. 确保已正确设置JAVA_HOME环境变量")
            print("3. 确保Android SDK已安装并包含所需的构建工具")
            print("4. 检查网络连接，确保Gradle能够下载依赖")
        
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"错误: 发生未知错误: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        else:
            print("使用 --debug 参数可以查看详细错误信息")
        sys.exit(1)

def check_environment():
    # 检查构建环境
    print("\n检查构建环境...")
    
    # 检查Android SDK环境变量
    android_home = os.environ.get('ANDROID_HOME')
    if not android_home:
        print("警告: 未设置ANDROID_HOME环境变量")
        print("构建过程中可能会遇到问题")
    else:
        print(f"ANDROID_HOME: {android_home}")
    
    # 检查Java环境
    java_home = os.environ.get('JAVA_HOME')
    if not java_home:
        print("警告: 未设置JAVA_HOME环境变量")
        print("构建过程中可能会遇到问题")
    else:
        print(f"JAVA_HOME: {java_home}")
    
    # 尝试检查Java版本
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        if result.stderr:
            java_version = result.stderr.split('"')[1]
            print(f"Java版本: {java_version}")
    except Exception:
        print("警告: 无法检查Java版本")

if __name__ == "__main__":
    main()