import requests
import os

# 源播放列表 URL
PLAYLIST_URL = "https://raw.githubusercontent.com/sggc/SDU-IPTV-NEW/refs/heads/main/playlist.m3u"

# 输出文件名
OUTPUT_FILES = {
    'catchup': 'unicast-catchup.m3u',
    'rtp': 'unicast-rtp.m3u'
}

def write_if_changed(filename, content_lines):
    """仅当内容变化时才写入文件"""
    new_content = ''.join(content_lines)
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            old_content = f.read()
        if old_content == new_content:
            print(f"ℹ️ {filename} unchanged, skipping write.")
            return False
    with open(filename, 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(content_lines)
    print(f"✅ Updated {filename}")
    return True

def main():
    try:
        response = requests.get(PLAYLIST_URL, timeout=10)
        response.raise_for_status()
        lines = response.text.splitlines(keepends=True)
    except Exception as e:
        print(f"❌ Failed to fetch playlist: {e}")
        return

    catchup_lines = []
    rtp_lines = []

    for line in lines:
        if line.startswith('#'):
            catchup_lines.append(line)
            rtp_lines.append(line)
        elif line.strip().startswith('http'):
            # 单播流：保留原 URL（支持 catchup）
            catchup_lines.append(line)
        elif line.strip().startswith('rtp://'):
            # RTP 流：转为 unicast RTP
            rtp_lines.append(line)

    # 只在内容变化时写入
    write_if_changed(OUTPUT_FILES['catchup'], catchup_lines)
    write_if_changed(OUTPUT_FILES['rtp'], rtp_lines)

if __name__ == "__main__":
    main()
