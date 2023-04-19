# -srt-
网易见外批量翻译字幕文件
# TIPS：
利用playwright-python自动化批量将目标文件夹及子文件夹中的srt字幕文件上传至网易见外工作台中，并将生成的双语字幕下载后覆盖保存为源文件。

## 安装依赖
pip install playwright

playwright install

## 注意事项
1、下载文件会覆盖源文件，使用前先备份，或修改代码中保存文件名称

2、如果目录下存在auth.json的cookie文件，则会读取cookie，若cookie已失效，请删除该文件后重新登录。
