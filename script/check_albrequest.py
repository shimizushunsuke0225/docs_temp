#!/usr/bin/env python
"""
ALB の RequestCount を 1 日（24 時間）分取得して合計を表示
"""

import boto3
from datetime import datetime, timedelta, timezone


def get_daily_request_count(lb_arn: str,
                            region: str = "ap-northeast-1") -> int:
    """
    直近 24 時間の RequestCount (Sum) を返す
    """
    cw = boto3.client("cloudwatch", region_name=region)

    # CloudWatch のディメンション値は ARN の 'app/...' 部分だけ
    lb_dim = "/".join(lb_arn.split("/", 1)[1:])   # app/my-alb/...

    # 集計ウィンドウ：現在時刻を含めない “確定済み” の 24 時間
    end   = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=1)

    resp = cw.get_metric_statistics(
        Namespace="AWS/ApplicationELB",
        MetricName="RequestCount",
        Dimensions=[{"Name": "LoadBalancer", "Value": lb_dim}],
        StartTime=start,
        EndTime=end,
        Period=24 * 60 * 60,     # 86400 秒＝1 日
        Statistics=["Sum"],      # 合計リクエスト数
        Unit="Count",
    )

    # データポイントは 1 つだけ（86400 秒粒度 × 1 日）
    datapoints = resp.get("Datapoints", [])
    return int(datapoints[0]["Sum"]) if datapoints else 0


if __name__ == "__main__":
    # ======= ここを自分の ALB ARN に置き換えてください =======
    ALB_ARN = (
        "arn:aws:elasticloadbalancing:ap-northeast-1:123456789012:"
        "loadbalancer/app/my-alb/50dc6c495c0c9188"
    )
    # ======================================================

    total = get_daily_request_count(ALB_ARN)
    print(f"1 日あたりのリクエスト総数: {total}")
