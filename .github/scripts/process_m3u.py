# .github/scripts/process_m3u.py
import re
import requests
from datetime import datetime, timezone, timedelta

SOURCE_URL = "https://raw.githubusercontent.com/sggc/SDU-IPTV-NEW/refs/heads/main/playlist.m3u"

def fetch_source():
    try:
        resp = requests.get(SOURCE_URL, timeout=10)
        resp.raise_for_status()
        return resp.text.splitlines(keepends=True)
    except Exception as e:
        print(f"❌ 获取源文件失败: {e}")
        exit(1)

def process():
    lines = fetch_source()
    catchup_lines = []
    rtp_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        # 判断是否为频道信息行
        if line.startswith('#EXTINF') and 'tvg-name=' in line and i + 1 < len(lines):
            url_line = lines[i + 1]

            # 修改 catchup-source 参数（仅替换时间格式部分）
            new_line = re.sub(
                r'\?tvdr=\{utc:YmdHMS\}GMT-\{utcend:YmdHMS\}GMT',
                r'?tvdr=${(b)yyyyMMddHHmmss}GMT-${(e)yyyyMMddHHmmss}GMT&r2h-seek-offset=-28800',
                line
            )

            # 构建 RTP 版本：主 URL 和 catchup-source 都转 HTTP 代理
            rtp_url = re.sub(
                r'^rtsp://',
                r'http://192.168.100.1:5140/rtsp/',
                url_line.strip()
            ) + '\n'

            rtp_catchup = re.sub(
                r'(catchup-source="rtsp://)',
                r'catchup-source="http://192.168.100.1:5140/rtsp/',
                new_line
            )

            catchup_lines.append(new_line)
            catchup_lines.append(url_line)

            rtp_lines.append(rtp_catchup)
            rtp_lines.append(rtp_url)

            i += 2
        else:
            # 其他所有行（包括 #EXTM3U、注释、空行等）原样保留
            catchup_lines.append(line)
            rtp_lines.append(line)
            i += 1

    # 写出文件（保持原始换行风格）
    with open('unicast-catchup.m3u', 'w', encoding='utf-8', newline='') as f:
        f.writelines(catchup_lines)

    with open('unicast-rtp.m3u', 'w', encoding='utf-8', newline='') as f:
        f.writelines(rtp_lines)

    print("✅ 文件生成完成：unicast-catchup.m3u 和 unicast-rtp.m3u")

if __name__ == '__main__':
    process()
