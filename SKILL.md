---
name: hjh-jipiaojiudian-price
description: 查询指定日期的机票或酒店公开实时参考报价，比较航班、房型和价格；适用于 Codex 和 Muse 中使用 PriceWin MCP 的旅行查询与定期复查。
---

# 旅行价格查询

使用免登录的 PriceWin MCP `https://mcp.price.win/mcp` 查询当次公开报价。优先调用客户端已连接的 MCP 工具；若客户端未提供直接的 MCP 调用，但允许运行 Python 3 和访问网络，可用 `scripts/pricewin_mcp.py` 调用同一服务。不要把 Skill 当成定时器；每日复查由 Codex 的 Scheduled 或 Muse 的 cron/任务功能触发。

## 机票

- 明确年份、出发地及其机场、目的地、去返日期、人数和舱位。上海同时查 `PVG` 与 `SHA`，冲绳那霸为 `OKA`。用户指定航司时按航司筛选，不把其他航司说成符合要求。
- 对每个出发机场调用 `search_flights_live`，再用返回的 `sessionId` 调用 `poll_flight_results`，直到完成或超时。往返结果是两个方向的**单程报价**，相加只表示两张单程票的参考合计，不能称为已核实的往返套票。
- 检查每条记录的出发和到达机场、日期、转机次数、跨日抵达、航司、价格币种及售票来源。丢弃机场与查询不符的记录。PriceWin 曾把同一航班同时标为浦东和虹桥，不能仅按最低数值排序后直接报告。
- 给出最低可解释的组合及直飞选项（如有），注明两段价格和链接。链接可能只打开搜索页，购票前须复核具体航班、行李、税费与最终应付金额。无法核实时明确说“参考报价”。

## 酒店

- 对指定酒店优先调用 `get_ota_hotel_detail`，传英文或官网常用名称、城市、入住/退房日期、成人和房间数；城市列表搜索可能漏掉目标酒店。例：`Le Meridien Suzhou, Suzhou Bay`、`Suzhou`。
- 只比较相同入住日期、晚数、人数和房间数的报价。报告房型、餐食、退改、币种、来源和页面链接。未确认税费或汇率时，不把展示价说成人民币实付价；Trip.com、Booking.com、Agoda 与携程中国站价格可能不同。

## 定期复查与通知

- 每次任务重新查询，记录查询时间、目标日期、平台、币种和可核实的价格。阈值比较应采用同币种的最终应付总额；没有可靠税费或汇率时先核实，不凭估算触发“低于阈值”通知。
- 用户要求每日检查时，由所用客户端的任务功能安排执行。只有真正创建并启用了任务后，才说“已设置每日提醒”。价格源查询失败时报告失败，不推断“没有低价”。

## 备用调用方法

在此 Skill 目录运行：

```bash
python3 scripts/pricewin_mcp.py call search_flights_live '{"origin":"PVG","destination":"OKA","departureDate":"2026-11-28","returnDate":"2026-12-05","adults":1,"cabin":"economy","language":"zh"}'
python3 scripts/pricewin_mcp.py call poll_flight_results '{"sessionId":"<上一步返回的 sessionId>","limit":100}'
python3 scripts/pricewin_mcp.py call get_ota_hotel_detail '{"hotelName":"Le Meridien Suzhou, Suzhou Bay","city":"Suzhou","checkIn":"2026-11-28","checkOut":"2026-11-29","adults":2,"rooms":1,"language":"zh"}'
```

这些是调用示例，不代表当前价格。Muse 若尚未安装此 Skill，可从 `https://github.com/1989roben-lab/hjh-jipiaojiudian-price` 读取完整目录，或接收同目录 ZIP，在自己的工作区安装；Muse 云端不能读取 Codex 本机目录。
