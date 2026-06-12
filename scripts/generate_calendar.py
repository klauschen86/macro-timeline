#!/usr/bin/env python3
"""
宏观数据日历生成器
基于已知发布规律，自动生成未来N个月的宏观数据发布日历
"""

import json
import os
from datetime import date, datetime, timedelta
from calendar import monthrange


# ============================================================
# 数据发布规律定义
# ============================================================

# 辅助函数：获取某月第N个星期X的日期
def nth_weekday(year, month, weekday, n):
    """返回 year/month 的第n个 weekday (0=Mon, 6=Sun)"""
    first_day = date(year, month, 1)
    first_wd = first_day.weekday()
    days_until = (weekday - first_wd) % 7
    result = first_day + timedelta(days=days_until + (n - 1) * 7)
    if result.month != month:
        return None
    return result


def last_weekday(year, month, weekday):
    """返回 year/month 的最后一个 weekday"""
    last_day = date(year, month, monthrange(year, month)[1])
    offset = (last_day.weekday() - weekday) % 7
    return last_day - timedelta(days=offset)


def first_business_day(year, month):
    """返回 year/month 的第一个工作日（周一至周五，跳过假设的节假日）"""
    d = date(year, month, 1)
    while d.weekday() >= 5:  # 周六或周日
        d += timedelta(days=1)
    return d


def around_day(year, month, day, max_adjust=2):
    """返回某月大致第day天，自动调整到工作日"""
    last = monthrange(year, month)[1]
    actual_day = min(day, last)
    d = date(year, month, actual_day)
    # 如果是周末，往后调整
    attempts = 0
    while d.weekday() >= 5 and attempts < max_adjust:
        d += timedelta(days=1)
        attempts += 1
    return d


# ============================================================
# 指标定义
# ============================================================

INDICATORS = {
    # ---- 中国 ----
    "CN_PMI_MFG": {
        "country": "CN", "country_name": "中国",
        "indicator": "官方制造业PMI", "indicator_en": "Manufacturing PMI",
        "frequency": "月度", "importance": 3,
        "release_time": "09:30", "timezone": "BJS",
        "source": "国家统计局", "source_url": "https://www.stats.gov.cn/",
        "unit": "",
        "calc": lambda y, m: last_weekday(y, m, 0) if last_weekday(y, m, 0).day >= 28 else date(y, m+1 if m<12 else 1, 1) if m < 12 else date(y+1, 1, 1)
    },
    "CN_PMI_NONMFG": {
        "country": "CN", "country_name": "中国",
        "indicator": "官方非制造业PMI", "indicator_en": "Non-Manufacturing PMI",
        "frequency": "月度", "importance": 3,
        "release_time": "09:30", "timezone": "BJS",
        "source": "国家统计局",
        "unit": "",
        "calc": lambda y, m: last_weekday(y, m, 0) if last_weekday(y, m, 0).day >= 28 else date(y, m+1 if m<12 else 1, 1) if m < 12 else date(y+1, 1, 1)
    },
    "CN_CAIXIN_PMI": {
        "country": "CN", "country_name": "中国",
        "indicator": "财新制造业PMI", "indicator_en": "Caixin Manufacturing PMI",
        "frequency": "月度", "importance": 2,
        "release_time": "09:45", "timezone": "BJS",
        "source": "财新/Markit",
        "unit": "",
        "calc": lambda y, m: around_day(y, m, 1, 2)
    },
    "CN_CPI": {
        "country": "CN", "country_name": "中国",
        "indicator": "CPI 居民消费价格指数（同比）", "indicator_en": "CPI YoY",
        "frequency": "月度", "importance": 3,
        "release_time": "09:30", "timezone": "BJS",
        "source": "国家统计局",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 9, 2)
    },
    "CN_PPI": {
        "country": "CN", "country_name": "中国",
        "indicator": "PPI 工业生产者出厂价格指数（同比）", "indicator_en": "PPI YoY",
        "frequency": "月度", "importance": 2,
        "release_time": "09:30", "timezone": "BJS",
        "source": "国家统计局",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 9, 2)
    },
    "CN_TRADE": {
        "country": "CN", "country_name": "中国",
        "indicator": "进出口贸易数据", "indicator_en": "Trade Balance",
        "frequency": "月度", "importance": 2,
        "release_time": "11:00", "timezone": "BJS",
        "source": "海关总署",
        "unit": "亿美元",
        "calc": lambda y, m: around_day(y, m, 10, 3)
    },
    "CN_M2": {
        "country": "CN", "country_name": "中国",
        "indicator": "M2 货币供应量（同比）", "indicator_en": "M2 Money Supply YoY",
        "frequency": "月度", "importance": 3,
        "release_time": "16:00", "timezone": "BJS",
        "source": "中国人民银行",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 12, 3)
    },
    "CN_SOCIAL_FINANCING": {
        "country": "CN", "country_name": "中国",
        "indicator": "社会融资规模", "indicator_en": "Aggregate Financing",
        "frequency": "月度", "importance": 3,
        "release_time": "16:00", "timezone": "BJS",
        "source": "中国人民银行",
        "unit": "亿元",
        "calc": lambda y, m: around_day(y, m, 12, 3)
    },
    "CN_NEW_LOANS": {
        "country": "CN", "country_name": "中国",
        "indicator": "新增人民币贷款", "indicator_en": "New Yuan Loans",
        "frequency": "月度", "importance": 2,
        "release_time": "16:00", "timezone": "BJS",
        "source": "中国人民银行",
        "unit": "亿元",
        "calc": lambda y, m: around_day(y, m, 12, 3)
    },
    "CN_GDP": {
        "country": "CN", "country_name": "中国",
        "indicator": "GDP 国内生产总值（同比）", "indicator_en": "GDP YoY",
        "frequency": "季度", "importance": 3,
        "release_time": "10:00", "timezone": "BJS",
        "source": "国家统计局",
        "unit": "%",
        "calc": lambda y, m: around_day(y, {1: 1, 4: 4, 7: 7, 10: 10}[m], 16, 3) if m in (1, 4, 7, 10) else None
    },
    "CN_INDUSTRIAL": {
        "country": "CN", "country_name": "中国",
        "indicator": "规模以上工业增加值（同比）", "indicator_en": "Industrial Production YoY",
        "frequency": "月度", "importance": 2,
        "release_time": "10:00", "timezone": "BJS",
        "source": "国家统计局",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 15, 3)
    },
    "CN_RETAIL": {
        "country": "CN", "country_name": "中国",
        "indicator": "社会消费品零售总额（同比）", "indicator_en": "Retail Sales YoY",
        "frequency": "月度", "importance": 2,
        "release_time": "10:00", "timezone": "BJS",
        "source": "国家统计局",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 15, 3)
    },
    "CN_FAI": {
        "country": "CN", "country_name": "中国",
        "indicator": "固定资产投资（累计同比）", "indicator_en": "Fixed Asset Investment YTD YoY",
        "frequency": "月度", "importance": 2,
        "release_time": "10:00", "timezone": "BJS",
        "source": "国家统计局",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 15, 3)
    },
    "CN_LPR_1Y": {
        "country": "CN", "country_name": "中国",
        "indicator": "贷款市场报价利率 LPR（1年期）", "indicator_en": "Loan Prime Rate 1Y",
        "frequency": "月度", "importance": 3,
        "release_time": "09:15", "timezone": "BJS",
        "source": "中国人民银行",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 20, 2)
    },
    "CN_LPR_5Y": {
        "country": "CN", "country_name": "中国",
        "indicator": "LPR（5年期以上）", "indicator_en": "Loan Prime Rate 5Y",
        "frequency": "月度", "importance": 3,
        "release_time": "09:15", "timezone": "BJS",
        "source": "中国人民银行",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 20, 2)
    },
    "CN_FX_RESERVES": {
        "country": "CN", "country_name": "中国",
        "indicator": "外汇储备", "indicator_en": "FX Reserves",
        "frequency": "月度", "importance": 2,
        "release_time": "16:00", "timezone": "BJS",
        "source": "中国人民银行",
        "unit": "亿美元",
        "calc": lambda y, m: around_day(y, m, 7, 2)
    },
    "CN_UNEMPLOYMENT": {
        "country": "CN", "country_name": "中国",
        "indicator": "城镇调查失业率", "indicator_en": "Surveyed Unemployment Rate",
        "frequency": "月度", "importance": 2,
        "release_time": "10:00", "timezone": "BJS",
        "source": "国家统计局",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 15, 3)
    },

    # ---- 美国 ----
    "US_ISM_MFG": {
        "country": "US", "country_name": "美国",
        "indicator": "ISM 制造业PMI", "indicator_en": "ISM Manufacturing PMI",
        "frequency": "月度", "importance": 3,
        "release_time": "10:00", "timezone": "EST",
        "source": "Institute for Supply Management",
        "unit": "",
        "calc": lambda y, m: first_business_day(y, m)
    },
    "US_ISM_SERVICES": {
        "country": "US", "country_name": "美国",
        "indicator": "ISM 非制造业PMI", "indicator_en": "ISM Services PMI",
        "frequency": "月度", "importance": 3,
        "release_time": "10:00", "timezone": "EST",
        "source": "Institute for Supply Management",
        "unit": "",
        "calc": lambda y, m: around_day(y, m, 3, 2)
    },
    "US_NFP": {
        "country": "US", "country_name": "美国",
        "indicator": "非农就业人数", "indicator_en": "Non-Farm Payrolls",
        "frequency": "月度", "importance": 3,
        "release_time": "08:30", "timezone": "EST",
        "source": "Bureau of Labor Statistics",
        "unit": "万人",
        "calc": lambda y, m: nth_weekday(y, m, 4, 1)
    },
    "US_UNEMPLOYMENT": {
        "country": "US", "country_name": "美国",
        "indicator": "失业率", "indicator_en": "Unemployment Rate",
        "frequency": "月度", "importance": 3,
        "release_time": "08:30", "timezone": "EST",
        "source": "Bureau of Labor Statistics",
        "unit": "%",
        "calc": lambda y, m: nth_weekday(y, m, 4, 1)
    },
    "US_CPI": {
        "country": "US", "country_name": "美国",
        "indicator": "CPI 消费者物价指数（同比）", "indicator_en": "CPI YoY",
        "frequency": "月度", "importance": 3,
        "release_time": "08:30", "timezone": "EST",
        "source": "Bureau of Labor Statistics",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 12, 3)
    },
    "US_CORE_CPI": {
        "country": "US", "country_name": "美国",
        "indicator": "核心CPI（同比）", "indicator_en": "Core CPI YoY",
        "frequency": "月度", "importance": 3,
        "release_time": "08:30", "timezone": "EST",
        "source": "Bureau of Labor Statistics",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 12, 3)
    },
    "US_PPI": {
        "country": "US", "country_name": "美国",
        "indicator": "PPI 生产者物价指数（同比）", "indicator_en": "PPI YoY",
        "frequency": "月度", "importance": 2,
        "release_time": "08:30", "timezone": "EST",
        "source": "Bureau of Labor Statistics",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 14, 3)
    },
    "US_RETAIL": {
        "country": "US", "country_name": "美国",
        "indicator": "零售销售（环比）", "indicator_en": "Retail Sales MoM",
        "frequency": "月度", "importance": 2,
        "release_time": "08:30", "timezone": "EST",
        "source": "Census Bureau",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 16, 3)
    },
    "US_FOMC": {
        "country": "US", "country_name": "美国",
        "indicator": "美联储利率决议", "indicator_en": "FOMC Rate Decision",
        "frequency": "每年8次", "importance": 3,
        "release_time": "14:00", "timezone": "EST",
        "source": "Federal Reserve",
        "unit": "%",
        "calc": lambda y, m: None  # FOMC需要特殊处理
    },
    "US_GDP": {
        "country": "US", "country_name": "美国",
        "indicator": "GDP 环比折年率（初值）", "indicator_en": "GDP QoQ Annualized (Advance)",
        "frequency": "季度", "importance": 3,
        "release_time": "08:30", "timezone": "EST",
        "source": "Bureau of Economic Analysis",
        "unit": "%",
        "calc": lambda y, m: around_day(y, {1: 25, 4: 29, 7: 30, 10: 29}[m], 0) if m in (1, 4, 7, 10) else None
    },
    "US_DURABLE_GOODS": {
        "country": "US", "country_name": "美国",
        "indicator": "耐用品订单（环比）", "indicator_en": "Durable Goods Orders MoM",
        "frequency": "月度", "importance": 2,
        "release_time": "08:30", "timezone": "EST",
        "source": "Census Bureau",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 26, 3)
    },
    "US_CONSUMER_CONF": {
        "country": "US", "country_name": "美国",
        "indicator": "谘商会消费者信心指数", "indicator_en": "Consumer Confidence",
        "frequency": "月度", "importance": 2,
        "release_time": "10:00", "timezone": "EST",
        "source": "Conference Board",
        "unit": "",
        "calc": lambda y, m: last_weekday(y, m, 1)  # Last Tuesday
    },
    "US_NEW_HOME_SALES": {
        "country": "US", "country_name": "美国",
        "indicator": "新屋销售（年化）", "indicator_en": "New Home Sales",
        "frequency": "月度", "importance": 2,
        "release_time": "10:00", "timezone": "EST",
        "source": "Census Bureau",
        "unit": "万套",
        "calc": lambda y, m: around_day(y, m, 25, 3)
    },
    "US_EXISTING_HOME": {
        "country": "US", "country_name": "美国",
        "indicator": "成屋销售（年化）", "indicator_en": "Existing Home Sales",
        "frequency": "月度", "importance": 2,
        "release_time": "10:00", "timezone": "EST",
        "source": "National Association of Realtors",
        "unit": "万套",
        "calc": lambda y, m: around_day(y, m, 21, 3)
    },
    "US_JOBLESS_CLAIMS": {
        "country": "US", "country_name": "美国",
        "indicator": "初请失业金人数", "indicator_en": "Initial Jobless Claims",
        "frequency": "周度", "importance": 2,
        "release_time": "08:30", "timezone": "EST",
        "source": "Department of Labor",
        "unit": "万人",
        "calc": lambda y, m: None  # 每周四，需要特殊处理
    },

    # ---- 欧元区 ----
    "EU_CPI_FLASH": {
        "country": "EU", "country_name": "欧元区",
        "indicator": "CPI 初值（同比）", "indicator_en": "CPI Flash Estimate YoY",
        "frequency": "月度", "importance": 3,
        "release_time": "11:00", "timezone": "CET",
        "source": "Eurostat",
        "unit": "%",
        "calc": lambda y, m: last_weekday(y, m, 0)  # Last working day of month
    },
    "EU_GDP_FLASH": {
        "country": "EU", "country_name": "欧元区",
        "indicator": "GDP 环比初值", "indicator_en": "GDP QoQ Flash",
        "frequency": "季度", "importance": 3,
        "release_time": "11:00", "timezone": "CET",
        "source": "Eurostat",
        "unit": "%",
        "calc": lambda y, m: around_day(y, {1: 30, 4: 30, 7: 31, 10: 31}[m], 0) if m in (1, 4, 7, 10) else None
    },
    "EU_PMI_MFG_FLASH": {
        "country": "EU", "country_name": "欧元区",
        "indicator": "制造业PMI 初值", "indicator_en": "Manufacturing PMI Flash",
        "frequency": "月度", "importance": 2,
        "release_time": "10:00", "timezone": "CET",
        "source": "S&P Global / HCOB",
        "unit": "",
        "calc": lambda y, m: around_day(y, m, 23, 2)
    },
    "EU_ECB": {
        "country": "EU", "country_name": "欧元区",
        "indicator": "欧洲央行利率决议", "indicator_en": "ECB Rate Decision",
        "frequency": "约6周", "importance": 3,
        "release_time": "14:15", "timezone": "CET",
        "source": "European Central Bank",
        "unit": "%",
        "calc": lambda y, m: None  # 需要特殊处理
    },
    "EU_RETAIL": {
        "country": "EU", "country_name": "欧元区",
        "indicator": "零售销售（环比）", "indicator_en": "Retail Sales MoM",
        "frequency": "月度", "importance": 1,
        "release_time": "11:00", "timezone": "CET",
        "source": "Eurostat",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 6, 2)
    },

    # ---- 日本 ----
    "JP_CPI": {
        "country": "JP", "country_name": "日本",
        "indicator": "CPI 全国（同比）", "indicator_en": "National CPI YoY",
        "frequency": "月度", "importance": 2,
        "release_time": "08:30", "timezone": "JST",
        "source": "Statistics Bureau of Japan",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 19, 3)
    },
    "JP_BOJ": {
        "country": "JP", "country_name": "日本",
        "indicator": "日本央行利率决议", "indicator_en": "BOJ Rate Decision",
        "frequency": "约6周", "importance": 3,
        "release_time": "11:00", "timezone": "JST",
        "source": "Bank of Japan",
        "unit": "%",
        "calc": lambda y, m: None
    },
    "JP_GDP": {
        "country": "JP", "country_name": "日本",
        "indicator": "GDP 环比折年率（初值）", "indicator_en": "GDP QoQ Annualized (Prelim)",
        "frequency": "季度", "importance": 2,
        "release_time": "08:50", "timezone": "JST",
        "source": "Cabinet Office",
        "unit": "%",
        "calc": lambda y, m: around_day(y, {2: 16, 5: 17, 8: 15, 11: 15}[m], 0) if m in (2, 5, 8, 11) else None
    },
    "JP_INDUSTRIAL": {
        "country": "JP", "country_name": "日本",
        "indicator": "工业产出（环比初值）", "indicator_en": "Industrial Production MoM Prelim",
        "frequency": "月度", "importance": 2,
        "release_time": "08:50", "timezone": "JST",
        "source": "METI",
        "unit": "%",
        "calc": lambda y, m: last_weekday(y, m, 0)
    },

    # ---- 英国 ----
    "UK_CPI": {
        "country": "UK", "country_name": "英国",
        "indicator": "CPI（同比）", "indicator_en": "CPI YoY",
        "frequency": "月度", "importance": 2,
        "release_time": "07:00", "timezone": "BST",
        "source": "Office for National Statistics",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 17, 3)
    },
    "UK_BOE": {
        "country": "UK", "country_name": "英国",
        "indicator": "英国央行利率决议", "indicator_en": "BOE Rate Decision",
        "frequency": "约6周", "importance": 3,
        "release_time": "12:00", "timezone": "BST",
        "source": "Bank of England",
        "unit": "%",
        "calc": lambda y, m: None
    },
    "UK_GDP": {
        "country": "UK", "country_name": "英国",
        "indicator": "GDP 环比", "indicator_en": "GDP MoM",
        "frequency": "月度", "importance": 2,
        "release_time": "07:00", "timezone": "BST",
        "source": "Office for National Statistics",
        "unit": "%",
        "calc": lambda y, m: around_day(y, m, 13, 3)
    },
}


# ============================================================
# FOMC 2026 会议日期（官方公布）
# ============================================================
FOMC_2026 = [
    ("2026-01-28", "2026-01-29"),
    ("2026-03-18", "2026-03-19"),
    ("2026-05-06", "2026-05-07"),
    ("2026-06-17", "2026-06-18"),
    ("2026-07-29", "2026-07-30"),
    ("2026-09-16", "2026-09-17"),
    ("2026-11-04", "2026-11-05"),
    ("2026-12-16", "2026-12-17"),
]


def generate_fomc_events():
    """生成FOMC事件"""
    events = []
    for start_str, end_str in FOMC_2026:
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        events.append({
            "id": f"US_FOMC_{end_str}",
            "country": "US", "country_name": "美国",
            "indicator": "美联储利率决议（FOMC）", "indicator_en": "FOMC Rate Decision",
            "frequency": "每年8次", "importance": 3,
            "release_date": end_str,
            "release_time": "14:00", "timezone": "EST",
            "period": start_str[:7],
            "source": "Federal Reserve",
            "source_url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
            "unit": "%",
        })
    return events


def generate_weekly_jobless_claims(start_date, end_date):
    """生成每周初请失业金数据"""
    events = []
    current = start_date
    while current <= end_date:
        # 每个周四
        if current.weekday() == 3:
            events.append({
                "id": f"US_JOBLESS_CLAIMS_{current.strftime('%Y%m%d')}",
                "country": "US", "country_name": "美国",
                "indicator": "初请失业金人数", "indicator_en": "Initial Jobless Claims",
                "frequency": "周度", "importance": 2,
                "release_date": current.strftime("%Y-%m-%d"),
                "release_time": "08:30", "timezone": "EST",
                "period": (current - timedelta(days=7)).strftime("%Y-%m-%d"),
                "source": "Department of Labor",
                "source_url": "https://www.dol.gov/",
                "unit": "万人",
            })
        current += timedelta(days=1)
    return events


def generate_calendar(num_months=3, lookback_months=6):
    """生成未来N个月 + 回顾lookback_months个月的宏观数据日历"""
    today = date.today()
    events = []

    # 计算需要覆盖的月份范围：从 lookback_months 个月前开始
    start_month = today.replace(day=1)
    for _ in range(lookback_months):
        start_month = (start_month.replace(day=1) - timedelta(days=1)).replace(day=1)
    end_month = (today.replace(day=28) + timedelta(days=4 * 31)).replace(day=1)
    end_month = (end_month.replace(day=28) + timedelta(days=(num_months - 3) * 31)).replace(day=1)

    months = []
    current = start_month
    while current <= end_month:
        months.append((current.year, current.month))
        current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)

    # 生成各指标事件
    for key, info in INDICATORS.items():
        calc_func = info.get("calc")
        if calc_func is None:
            continue
        for year, month in months:
            try:
                release_date = calc_func(year, month)
            except Exception:
                continue
            if release_date is None:
                continue
            # 只保留从今天起的事件（以及过去30天内的历史事件）
            cutoff = today - timedelta(days=180)
            if release_date < cutoff:
                continue
            if release_date > today + timedelta(days=num_months * 31):
                continue

            # 计算数据期间
            if info["frequency"] == "月度":
                data_month = month - 1 if month > 1 else 12
                data_year = year if month > 1 else year - 1
                period = f"{data_year}-{data_month:02d}"
            elif info["frequency"] == "季度":
                quarter = (month - 1) // 3
                prev_quarter = quarter - 1 if quarter > 0 else 3
                prev_year = year if quarter > 0 else year - 1
                period = f"{prev_year}-Q{prev_quarter + 1}"
            else:
                period = f"{year}-{month:02d}"

            event = {
                "id": f"{key}_{release_date.strftime('%Y%m%d')}",
                "country": info["country"],
                "country_name": info["country_name"],
                "indicator": info["indicator"],
                "indicator_en": info["indicator_en"],
                "frequency": info["frequency"],
                "importance": info["importance"],
                "release_date": release_date.strftime("%Y-%m-%d"),
                "release_time": info["release_time"],
                "timezone": info["timezone"],
                "period": period,
                "source": info["source"],
                "source_url": info.get("source_url", ""),
                "unit": info.get("unit", ""),
            }
            events.append(event)

    # 生成 FOMC
    events.extend(generate_fomc_events())

    # 生成每周初请
    events.extend(generate_weekly_jobless_claims(today, today + timedelta(days=num_months * 31)))

    # 按发布日期排序
    events.sort(key=lambda e: e["release_date"])

    return events


def load_existing_calendar(filepath):
    """加载已有日历"""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("events", [])
    return []


def load_existing_results(filepath):
    """加载已有结果数据"""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def merge_calendars(existing_events, new_events):
    """合并日历：保留已有事件的所有数据，永不覆盖 actual/forecast/previous"""
    existing_map = {e["id"]: e for e in existing_events}
    merged_ids = set()
    merged = []

    # 第一步：处理新事件（基于规则生成的），保留已有数据
    for new_event in new_events:
        eid = new_event["id"]
        merged_ids.add(eid)
        if eid in existing_map:
            old = existing_map[eid]
            # 核心铁律：如果 old 有 actual/forecast/previous，绝不能覆盖
            for field in ("actual", "forecast", "previous"):
                old_val = old.get(field)
                if old_val is not None and old_val != "":
                    new_event[field] = old_val
            # 状态：保留旧状态（released > pending > upcoming）
            old_status = old.get("status", "")
            if old_status in ("released", "pending"):
                new_event["status"] = old_status
            elif new_event.get("actual") is not None:
                new_event["status"] = "released"
            else:
                new_event["status"] = old_status if old_status else "upcoming"
            # 保留备注
            new_event["notes"] = old.get("notes", "")
        else:
            # 新事件，设为 upcoming
            new_event["status"] = "upcoming"
        merged.append(new_event)

    # 第二步：保留旧日历中不在新日历的事件（它们是已经收集的历史数据）
    for eid, old_event in existing_map.items():
        if eid not in merged_ids:
            merged.append(old_event)

    # 按日期排序
    merged.sort(key=lambda e: e.get("release_date", ""))

    return merged


def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    calendar_file = os.path.join(data_dir, "calendar.json")

    # 生成新日历
    new_events = generate_calendar(num_months=2)

    # 合并已有数据
    existing_events = load_existing_calendar(calendar_file)
    merged_events = merge_calendars(existing_events, new_events)

    # 统计
    today = date.today()
    upcoming = [e for e in merged_events if e["release_date"] >= today.strftime("%Y-%m-%d")]
    past = [e for e in merged_events if e["release_date"] < today.strftime("%Y-%m-%d")]
    by_country = {}
    for e in merged_events:
        cn = e["country_name"]
        by_country[cn] = by_country.get(cn, 0) + 1

    output = {
        "meta": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "generated_by": "generate_calendar.py",
            "timezone": "BJS (UTC+8)",
            "total_events": len(merged_events),
            "upcoming_events": len(upcoming),
            "past_30d_events": len(past),
            "by_country": by_country,
        },
        "events": merged_events,
    }

    with open(calendar_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"日历已生成: {calendar_file}")
    print(f"总计: {len(merged_events)} 条事件")
    print(f"即将发布: {len(upcoming)} 条")
    print(f"过去30天: {len(past)} 条")
    print(f"按国家分布: {by_country}")

    # 打印未来30天重要事件
    print("\n=== Next 30 Days Key Events ===")
    next_30 = [e for e in upcoming if e["release_date"] <= (today + timedelta(days=30)).strftime("%Y-%m-%d")]
    # Write summary to file to avoid encoding issues
    summary_lines = []
    for e in next_30[:30]:
        importance_star = "*" * e.get("importance", 1)
        line = f"  {e['release_date']} {importance_star} [{e['country_name']}] {e['indicator']}"
        summary_lines.append(line)
        print(line.encode('ascii', errors='replace').decode('ascii'))

    summary_file = os.path.join(data_dir, "summary.txt")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))
    print(f"\nSummary written to {summary_file}")


if __name__ == "__main__":
    main()
