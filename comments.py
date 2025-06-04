#!/usr/bin/env python3
"""Fetch video comments and replies from bilibili."""
import argparse
import re
import requests

HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.bilibili.com'}


def bvid_to_aid(bvid: str) -> int:
    """Convert BV id to aid."""
    url = 'https://api.bilibili.com/x/web-interface/view'
    resp = requests.get(url, params={'bvid': bvid}, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    if data.get('code') != 0:
        raise RuntimeError(data.get('message'))
    return int(data['data']['aid'])


def parse_oid(oid: str) -> int:
    if oid.lower().startswith('bv'):
        return bvid_to_aid(oid)
    if oid.lower().startswith('av'):
        oid = oid[2:]
    return int(oid)


def get_comments(oid: int, page: int = 1, sort: int = 2):
    url = 'https://api.bilibili.com/x/v2/reply'
    params = {'oid': oid, 'type': 1, 'pn': page, 'sort': sort}
    resp = requests.get(url, params=params, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()['data']
    comments = []
    for r in data.get('replies', []) or []:
        item = {
            'rpid': r['rpid'],
            'user': r['member']['uname'],
            'message': r['content']['message'],
            'replies': get_sub_comments(oid, r['rpid']) if r.get('rcount') else []
        }
        comments.append(item)
    return comments


def get_sub_comments(oid: int, root: int, page: int = 1):
    url = 'https://api.bilibili.com/x/v2/reply/reply'
    params = {'oid': oid, 'type': 1, 'root': root, 'pn': page}
    resp = requests.get(url, params=params, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()['data']
    subs = []
    for r in data.get('replies', []) or []:
        subs.append({'rpid': r['rpid'], 'user': r['member']['uname'], 'message': r['content']['message']})
    return subs


def main():
    parser = argparse.ArgumentParser(description='Get bilibili video comments')
    parser.add_argument('oid', help='BV id or AV id or aid')
    parser.add_argument('--page', type=int, default=1, help='comment page index')
    parser.add_argument('--sort', type=int, default=2, help='0=time, 2=hot')
    args = parser.parse_args()
    oid = parse_oid(args.oid)
    for c in get_comments(oid, page=args.page, sort=args.sort):
        print(f"{c['user']}: {c['message']}")
        for sub in c['replies']:
            print(f"  ↳ {sub['user']}: {sub['message']}")


if __name__ == '__main__':
    main()
