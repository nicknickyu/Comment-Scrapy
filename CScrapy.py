# -*- coding:utf-8 -*-
import sys
import ui_mwindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QGuiApplication
import pandas as pd
import time as tm
import ScrapyCode
#from win32ctypes import pywin32, core
#from win32ctypes.core import ctypes
#from win32ctypes.core.ctypes import _common,_dll,_resource,_util,_time,_authentication,_system_information,_nl_support


ui_mainWindow = ui_mwindow.Ui_MainWindow  # 实例化窗口类


class CoperQt(QtWidgets.QMainWindow, ui_mainWindow):  # 创建一个Qt对象
    # 这里的第一个变量是你该窗口的类型，第二个是该窗口对象。
    # 这里是主窗口类型。所以设置成当QtWidgets.QMainWindow。
    # 你的窗口是一个会话框时你需要设置成:QtWidgets.QDialog
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)  # 创建主界面对象
        ui_mainWindow.__init__(self)  # 主界面对象初始化
        self.setupUi(self)  # 配置主界面对象
        self.pushButton_start.clicked.connect(self.Scrapy)


    # ***************************************************************
    # 函数功能：读取输入的appid和页数，并根据选择的Tap和B站，跳转到到对应爬取逻辑
    # ***************************************************************
    def Scrapy(self):
        self.textBrowser.clear()
        if self.lineEdit_appid.text().isdigit():
            app_id = int(self.lineEdit_appid.text())
        else:
            QMessageBox.warning(self,
                                "错误",
                                "请输入正确的AppID",
                                QMessageBox.Close)
            return
        if self.lineEdit_page_total.text().isdigit():
            page_total = int(self.lineEdit_page_total.text())
        else:
            QMessageBox.warning(self,
                                "错误",
                                "请输入正确的爬取页数",
                                QMessageBox.Close)
            return
        if self.radioButton_Bili.isChecked():
            self.BiliScrapy(app_id, page_total)
        elif self.radioButton_Tap.isChecked():
            self.TapScrapy(app_id, page_total)
        else:
            return

    # ***************************************************************
    # 函数功能：B站评论爬取函数，根据appid和页数，循环爬取每个页面的评论数据
    # ***************************************************************
    def BiliScrapy(self, app_id, page_total):
        all_content = []
        all_grade = []
        all_publish_time = []
        all_up_count = []
        all_down_count = []
        all_user_name = []
        all_user_level = []

        self.textBrowser.append('正在从【B站】获取游戏:{0}的评论数据...\n'.format(app_id))
        QGuiApplication.processEvents()
        # step 2  爬取数据，循环爬取，每页获取10条评论数据
        for pagenum in range(1, page_total + 1):
            t1 = tm.time()  # 用于调试代码效率
            url = "https://line1-h5-pc-api.biligame.com/game/comment/page?game_base_id={0}&rank_type=2&page_num={1}&page_size=10".format(
                app_id, pagenum)
            comment_page = ScrapyCode.fetchURL(url)  # 加载url
            parsered_comment = ScrapyCode.parserBiliHtml(comment_page)  # 解析一页

            # 从解析后的json对象中获取所需要的信息
            all_content.extend(parsered_comment[0])
            all_grade.extend(parsered_comment[1])
            all_publish_time.extend(parsered_comment[2])
            all_up_count.extend(parsered_comment[3])
            all_down_count.extend(parsered_comment[4])
            all_user_name.extend(parsered_comment[5])
            all_user_level.extend(parsered_comment[6])
            t2 = tm.time()  # 用于调试代码效率
            timing = t2 - t1
            self.textBrowser.append('已爬取第 %d 页, 耗时 %5.2f 秒' % (pagenum, timing))  # 输出爬取进度
            if pagenum % 10 == 0:
                self.textBrowser.append('歇会儿，避免被反爬虫...')
                tm.sleep(5)
            QGuiApplication.processEvents()
        # step 3  爬取完成，整理并导出数据
        result = {"content": all_content,
                  "grade": all_grade,
                  "publish_time": all_publish_time,
                  "up_count": all_up_count,
                  "down_count": all_down_count,
                  "user_name": all_user_name,
                  "user_level": all_user_level,
                  }
        resultpd = pd.DataFrame(result)
        resultpd.to_excel('bilibili_comment_AppID{}.xlsx'.format(app_id))
        self.textBrowser.append('\n评论爬取完成！共获取到 %d 条B站评论' % (len(resultpd['content'])))
        self.textBrowser.append('结果已保存到文件：bilibili_comment_AppID{}.xlsx'.format(app_id))

    # ***************************************************************
    # 函数功能：Tap评论爬取函数，根据appid和页数，循环爬取每个页面的评论数据
    # ***************************************************************
    def TapScrapy(self, app_id, page_total):

        # 准备输出容器
        content_out = []
        score_out = []
        datetime_out = []

        self.textBrowser.append('正在从【TapTap】获取游戏:{0}的评论数据...\n'.format(app_id))
        QGuiApplication.processEvents()
        # step2 由于需要爬去多页数据，建立循环爬取机制
        for j in range(1, page_total + 1):
            t1 = tm.time()
            url = "https://www.taptap.com/app/{0}/review?order=update&page={1}#review-list".format(app_id,
                                                                                                   j)  # 拼接每一页的url
            # step3 抓取单页数据
            comment_page = ScrapyCode.fetchURL(url)
            content_tmp, score_tmp, datetime_tmp = ScrapyCode.parserTapHtml(comment_page)
            if (j==1 and len(content_tmp)==0):
                QMessageBox.warning(self,
                                    "错误",
                                    "该游戏无评论内容",
                                    QMessageBox.Close)
                self.textBrowser.clear()
                return


            content_out.extend(content_tmp)  # 装入输出容器
            score_out.extend(score_tmp)
            datetime_out.extend(datetime_tmp)

            t2 = tm.time()
            timing = t2 - t1  # 计时，用于调试
            self.textBrowser.append('已爬取第 %d 页, 耗时 %5.2f 秒' % (j, timing))  # 输出爬取进度
            QGuiApplication.processEvents()
        # step4 整理成数据框格式，导出数据
        result = {"content": content_out,
                  "score": score_out,
                  "comment_date": datetime_out}  # 先把列表转为字典

        resultpd = pd.DataFrame(result)  # 再把字典转为pandas数据框
        resultpd['content'] = resultpd['content'].str.replace("\n<p>", "").replace("</p><p>", " ")
        resultpd.to_excel('tap_comment_AppID{}.xlsx'.format(app_id))

        self.textBrowser.append('\n评论爬取完成！共获取到 %d 条Tap评论' % (len(resultpd['content'])))
        self.textBrowser.append('结果已保存到文件：tap_comment_AppID{}.xlsx'.format(app_id))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # 实例化窗口控制流对象
    file = QtCore.QFile('Aqua.qss')  # 加载QSS样式表文件
    file.open(QtCore.QFile.ReadOnly)
    styleSheet = file.readAll()
    styleSheet = str(styleSheet, encoding='utf8')
    app.setStyleSheet(styleSheet)  # 设置样式表
    window = CoperQt()  # 创建QT对象
    window.show()  # QT对象显示
    sys.exit(app.exec_())
