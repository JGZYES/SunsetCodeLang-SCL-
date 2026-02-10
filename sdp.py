import os
import urllib.request
import urllib.parse
import sys
import json

class SCLPluginDownloader:
    def __init__(self):
        self.base_url = "https://scl.ecuil.com/forum/api/download.php"
        self.api_url = "https://scl.ecuil.com/forum/api/packages.php"
        self.plugins_dir = "./plugins"
    
    def log(self, message):
        print(message)
    
    def download_plugin(self, plugin_name):
        self.log(f"正在下载插件: {plugin_name}")
        
        try:
            url = f"{self.base_url}?name={plugin_name}"
            self.log(f"下载地址: {url}")
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'SCL-Plugin-Downloader/1.0')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
                
                content_type = response.headers.get('Content-Type', '')
                
                if 'application/json' in content_type:
                    data = json.loads(content.decode('utf-8'))
                    self.log(f"下载失败: {data.get('error', '未知错误')}")
                    return False
                
                self.log(f"下载成功，大小: {len(content)} 字节")
                
                os.makedirs(self.plugins_dir, exist_ok=True)
                dest_path = os.path.join(self.plugins_dir, f"{plugin_name}.py")
                
                with open(dest_path, 'wb') as f:
                    f.write(content)
                
                self.log(f"插件已保存到: {dest_path}")
                return True
                
        except urllib.error.HTTPError as e:
            self.log(f"HTTP错误: {e.code} - {e.reason}")
            return False
        except urllib.error.URLError as e:
            self.log(f"网络错误: {e}")
            return False
        except Exception as e:
            self.log(f"下载失败: {e}")
            return False
    
    def search_plugin(self, keyword):
        self.log(f"搜索插件: {keyword}")
        
        try:
            req = urllib.request.Request(self.api_url + "?action=list&search=" + urllib.parse.quote(keyword))
            req.add_header('User-Agent', 'SCL-Plugin-Downloader/1.0')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status != 200:
                    self.log(f"搜索失败: HTTP {response.status}")
                    return []
                
                data = json.loads(response.read().decode('utf-8'))
                
                if data.get('success'):
                    packages = data.get('packages', [])
                    self.log(f"找到 {len(packages)} 个匹配的插件")
                    return packages
                else:
                    self.log(f"搜索失败: {data.get('error', '未知错误')}")
                    return []
                    
        except Exception as e:
            self.log(f"搜索失败: {e}")
            return []
    
    def list_plugins(self):
        self.log("本地插件列表:")
        
        if not os.path.exists(self.plugins_dir):
            self.log("插件目录不存在")
            return
        
        plugins = []
        for file in os.listdir(self.plugins_dir):
            if file.endswith('.py') and file != '__init__.py':
                plugin_name = file[:-3]
                plugins.append(plugin_name)
                self.log(f"  - {plugin_name}")
        
        return plugins

def main():
    if len(sys.argv) < 2:
        print("SCL Plugin Downloader (SDP)")
        print("用法:")
        print("  sdp <插件名>          - 下载插件")
        print("  sdp search <关键词>    - 搜索插件")
        print("  sdp list              - 列出本地插件")
        print("  sdp help              - 显示帮助信息")
        return
    
    command = sys.argv[1].lower()
    downloader = SCLPluginDownloader()
    
    if command == 'help':
        print("SCL Plugin Downloader (SDP)")
        print("用法:")
        print("  sdp <插件名>          - 下载插件")
        print("  sdp search <关键词>    - 搜索插件")
        print("  sdp list              - 列出本地插件")
        print("  sdp help              - 显示帮助信息")
    
    elif command == 'list':
        downloader.list_plugins()
    
    elif command == 'search':
        if len(sys.argv) < 3:
            downloader.log("请提供搜索关键词")
            return
        keyword = sys.argv[2]
        results = downloader.search_plugin(keyword)
        
        if results:
            print("\n搜索结果:")
            for pkg in results:
                print(f"\n名称: {pkg['name']}")
                print(f"描述: {pkg['description']}")
                print(f"分类: {pkg['category']}")
                print(f"版本: {pkg['version']}")
                print(f"作者: {pkg['author_name']}")
                print(f"下载: {pkg['downloads']}")
                print(f"评分: {pkg['rating_count'] > 0 and round(pkg['rating'] / pkg['rating_count'], 1) or '暂无评分'}")
        else:
            print("未找到匹配的插件")
    
    else:
        plugin_name = command
        if downloader.download_plugin(plugin_name):
            print(f"\n插件 {plugin_name} 下载成功！")
            print(f"使用方法: simp{{{plugin_name}}}")
        else:
            print(f"\n插件 {plugin_name} 下载失败！")

if __name__ == "__main__":
    main()
