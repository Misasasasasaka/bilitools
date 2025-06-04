#!/usr/bin/env python3
"""Fetch bilibili ranking list using bilibili_api."""
import argparse
from bilibili_api import rank, sync


def fetch_rank(rid: int = 0):
    """Return ranking list."""
    ranking_type = rank.RankType.All if rid == 0 else rank.RankType(rid)
    data = sync(rank.get_rank(ranking_type))
    return data['list']


def main():
    parser = argparse.ArgumentParser(description='Get bilibili ranking')
    parser.add_argument('--rid', type=int, default=0, help='category id as RankType value')
    args = parser.parse_args()
    ranking = fetch_rank(args.rid)
    for idx, item in enumerate(ranking, 1):
        print(f"{idx}. {item['title']} (bvid={item['bvid']}, aid={item['aid']})")


if __name__ == '__main__':
    main()


