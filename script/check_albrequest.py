#!/usr/bin/env python
"""
Application Load Balancer の RequestCount を取得して合計を表示
  ・ウィンドウ長は引数 window_minutes で指定（既定: 5 分）
  ・24 時間を取りたい場合は window_minutes=1440
"""

import boto3
from datetime import datetime, timedelta, timezone
from typing import List


REGION = "ap-northeast-1"

# ======== 自分の ALB ARN に書き換えてください ========
ALB_ARN = (
    "arn:aws:elasticloadbalancing:ap-northeast-1:123456789012:"
    "loadbalancer/app/my-alb/50dc6c495c0c9188"
)
# ====================================================


def _lb_dimension(arn: str) -> str:
    """CloudWatch に渡す LoadBalancer ディメンション値 (app/…) に変換"""
    return "/".join(arn.split("/", 1)[1:])


def fetch_requestcount_datapoints(
    lb_dimension: str,
    start: datetime,
    end: datetime,
    period: int,
) -> List[dict]:
    """RequestCount の Datapoints をそのまま返す"""
    cw = boto3.client("cloudwatch", region_name=REGION)

    resp = cw.get_metric_statistics(
        Namespace="AWS/ApplicationELB",
        MetricName="RequestCount",
        Dimensions=[{"Name": "LoadBalancer", "Value": lb_dimension}],
        StartTime=start,
        EndTime=end,
        Period=period,
        Statistics=["Sum"],
        Unit="Count",
    )
    return resp["Datapoints"]


def total_requestcount_last_n_minutes(
    lb_arn: str,
    window_minutes: int = 5,
) -> int:
    """
    直近 window_minutes 分の RequestCount 合計を返す
    """
    lb_dim = _lb_dimension(lb_arn)

    # CloudWatch への反映遅延 (約 1 分) を避けるため EndTime を 1 分前に設定
    end   = datetime.now(timezone.utc).replace(second=0, microsecond=0) - timedelta(minutes=1)
    start = end - timedelta(minutes=window_minutes - 1)  # 例: 5 分なら 4 分前〜

    datapoints = fetch_requestcount_datapoints(lb_dim, start, end, period=60)
    return int(sum(dp["Sum"] for dp in datapoints))


if __name__ == "__main__":
    # --- 直近 5 分のリクエスト総数 ---
    total_5m = total_requestcount_last_n_minutes(ALB_ARN, window_minutes=5)
    print(f"直近 5 分間のリクエスト総数: {total_5m}")

    # --- 直近 24 時間 (1 日) のリクエスト総数 ---
    total_1d = total_requestcount_last_n_minutes(ALB_ARN, window_minutes=24 * 60)
    print(f"直近 1 日 (24h) のリクエスト総数: {total_1d}")
