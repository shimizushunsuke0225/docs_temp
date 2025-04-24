#!/usr/bin/env python
"""
AWS ALB Target Group の RequestCountPerTarget を 5 分分合算して
「ターゲットグループへフォワードされたリクエスト総数」を表示
"""

import boto3
from datetime import datetime, timedelta, timezone


def get_total_requests_per_tg(
    lb_arn: str,
    tg_arn: str,
    region: str = "ap-northeast-1",
    window_minutes: int = 5,
) -> int:
    """
    RequestCountPerTarget の Sum を minute 粒度で取得し window_minutes 分合算
    """
    cw = boto3.client("cloudwatch", region_name=region)

    # CloudWatch に渡すディメンション値は ARN 末尾 (app/.., targetgroup/..)
    lb_dim = "/".join(lb_arn.split("/", 1)[1:])
    tg_dim = "/".join(tg_arn.split("/", 1)[1:])

    end   = datetime.now(timezone.utc)
    start = end - timedelta(minutes=window_minutes)

    resp = cw.get_metric_statistics(
        Namespace="AWS/ApplicationELB",
        MetricName="RequestCountPerTarget",
        Dimensions=[
            {"Name": "LoadBalancer", "Value": lb_dim},
            {"Name": "TargetGroup", "Value": tg_dim},
        ],
        StartTime=start,
        EndTime=end,
        Period=60,           # 1-minute 粒度
        Statistics=["Sum"],  # 1 分ごとの「Sum」を取得
        Unit="Count",
    )

    total = sum(int(dp["Sum"]) for dp in resp.get("Datapoints", []))
    return total


if __name__ == "__main__":
    # ===== サンプル値を自分の ARN に置き換えてください =====
    ALB_ARN = (
        "arn:aws:elasticloadbalancing:ap-northeast-1:123456789012:"
        "loadbalancer/app/my-alb/50dc6c495c0c9188"
    )
    TG_ARN = (
        "arn:aws:elasticloadbalancing:ap-northeast-1:123456789012:"
        "targetgroup/my-tg/73e2d6bc24d8a067"
    )
    # =====================================================

    total_requests = get_total_requests_per_tg(ALB_ARN, TG_ARN)
    print(f"ターゲットグループへフォワードされたリクエスト総数: {total_requests}")
