# 风险预测：R美化版原格式 / Original R nomogram

## 更新已经部署的网页

解压后，把本文件夹内全部14个文件（包括.streamlit文件夹中的config.toml）更新到原GitHub仓库同一位置。入口仍是app.py。

本次需要新增regplot_view.py；也要覆盖distribution.json，因为里面现在包含R实际生成的原版美化SVG、坐标和计分参数。不要只更新app.py。现成部署包已经生成好，不用重新跑R。

字体与间距修订：英文/数字使用Times New Roman，中文使用宋体；覆盖页面、侧边栏、表格及图表。滑块当前值缩小为13px，并与输入框拉开距离。英文署名为“Rednote: si_xu_sui_feng · 6739802809”。

## 列线图格式

直接使用regplot生成的美化版矢量图：原始变量排序、纯白底、蓝色分布线、浅青色分类方块、黑色刻度和总分分布。网页仅叠加动态红点、引导线、总分、预测概率及95%区间，没有用其他绘图库重新模拟该图。

R模型系数、协方差及编码保持不变，网页采用原regplot计分方式。多中心原始第7条输入显示约457分、概率0.364（36.41%），与R美化图相符。切换中英文仅翻译标签，患者数据不变。

## 后续运行R

侧边栏收起后主内容自动占满可用窗口宽度，展开后自动为输入区让出空间。若已使用“字体与间距修订”版本，本次布局修订只需更新styles.css，无需重新运行R。

R需要rms、regplot、jsonlite、svglite。保留export_streamlit.R、export_regplot.R及完整streamlit_template文件夹。导出的distribution.json只包含汇总分布、原始美化图和绘图坐标，没有患者级数据。云端仍只运行Python，不需要安装R。

## English

Upload all 14 files, including the .streamlit folder, to the same GitHub location. Keep app.py as the entrypoint. Include the new regplot_view.py and replace distribution.json.

The nomogram is the actual R regplot SVG, with a live patient overlay. It uses the same ordering, distributions, boxes, axes and point scale as the R beautified figure. No R process is needed on Streamlit. Coefficients and probability calculations remain unchanged.

For a new R export, install rms, regplot, jsonlite and svglite, and preserve both R exporters and the complete template directory.
