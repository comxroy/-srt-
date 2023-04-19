#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   网易见外翻译.py
@Time    :   2023/04/18 17:18:23
@Author  :   R
'''

# here put the import lib
from playwright.sync_api import Playwright, sync_playwright, expect, FileChooser, Page
from pathlib import Path
'''
对于递归遍历文件夹获取.srt文件路径的函数get_srt_path，应该使用生成器（yield）而不是列表（append）返回结果，这样可以节省内存并且支持惰性计算。
对于等待时间的操作，应该使用page.wait_for_timeout替代time.sleep，因为前者可以使页面异步加载，而后者会阻塞线程。
在循环中反复调用page.locator方法，可以将查找到的元素保存在变量中以便重复使用，可提高代码效率。
'''


# 登录账号
def login_set(page: Page):
    username = input("请输入账号：")
    password = input("请输入密码：")
    frame = page.frame_locator("//iframe").nth(0)
    frame.locator("input[name=\"email\"]").fill(username)
    frame.locator("input[name=\"password\"]").fill(password)
    with page.expect_navigation():
        frame.locator("text=登 录").click()


# 获取文件夹下所有srt文件，并返回文件路径列表
def get_srt_path(dir_path):
    """
    此函数递归地生成给定目录路径中所有“.srt”文件的路径。
    
    :param dir_path: 输入参数 `dir_path` 是表示目录路径的字符串。此函数旨在搜索目录及其子目录中的所有 .srt 文件，并将它们的路径作为生成器对象返回。
    """
    srt_path = Path(dir_path)
    for item in srt_path.iterdir():
        if item.is_file() and item.suffix == ".srt":
            # `yield str(item)` 是一个生成器表达式，它生成当前文件路径 `item` 的字符串表示形式作为生成器对象中的下一个值。这允许函数 get_srt_path
            # 返回一个生成器对象，该对象可以被迭代以延迟生成给定目录及其子目录中所有 .srt
            # 文件的文件路径，而不是一次生成所有文件路径的列表并且归还它。这可以节省内存并提高性能，尤其是对于包含许多文件的大目录。
            yield str(item)
        elif item.is_dir():
            yield from get_srt_path(item)


# 下载导出文件
def download(page: Page, srt_path):
    card = page.locator("li.card").nth(0)
    with page.expect_navigation():
        card.click()
    page.wait_for_timeout(2000)
    file_name = page.locator("div.title >> nth=0").inner_text()
    print(file_name)
    export_btn = page.locator("text=导出")
    export_btn.click()
    confirm_btn = page.locator("#boxBody >> text=确定")
    with page.expect_download() as download_info:
        with page.expect_popup() as popup_info:
            confirm_btn.click()
        page1 = popup_info.value
    download = download_info.value
    # 保存为原文件名，如果不想覆盖原文件请修改代码
    download.save_as(srt_path)
    # Close page
    page1.close()
    page.locator("span.icon.icon-back").click()


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    try:
        context = browser.new_context(storage_state="youdao.json")
        cookie_load = True
    except Exception:
        print("未发现登录cookie，请先登录")
        context = browser.new_context()
        cookie_load = False
    # Open new page
    page = context.new_page()
    # Go to https://jianwai.youdao.com/
    page.goto("https://jianwai.youdao.com/")
    if not cookie_load:
        login_set(page)

    for srt_path in get_srt_path(dir_path):
        # Click text=新建项目
        new_project_btn = page.locator("text=新建项目")
        new_project_btn.click()
        # Click text=字幕翻译
        trans_btn = page.locator("text=字幕翻译")
        trans_btn.click()
        with page.expect_file_chooser() as fc_info:
            add_btn = page.locator("text=添加字幕")
            add_btn.click()
        file_chooser = fc_info.value
        file_chooser.set_files(srt_path)
        page.wait_for_timeout(2000)
        submit_btn = page.locator("text=提交").nth(1)
        submit_btn.click()
        download(page, srt_path)
        # delete item
        time_span = page.locator("span.time")
        time_span.click()
        remove_icon = page.locator("span.icon.icon-remove")
        remove_icon.click()
        page.wait_for_timeout(2000)
        confirm_btn = page.locator("text=确定")
        confirm_btn.click()
        page.wait_for_timeout(1000)
        print("delete item complete")

    # Close page
    page.close()

    context.storage_state(path="youdao.json")
    context.close()
    browser.close()


with sync_playwright() as playwright:
    pathlist = []
    dir_path = input("请输入文件夹路径：")
    run(playwright)
