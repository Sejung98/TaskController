"""
Task Controller - 투명 배경 심플 컨트롤러 아이콘 생성기
Pillow를 이용해 4x 슈퍼샘플링으로 매끄러운 투명 배경 게임 컨트롤러 아이콘을 생성합니다.
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_controller_icon(size=512):
    # 4배 슈퍼샘플링으로 부드러운 안티앨리어싱
    scale = 4
    canvas_size = size * scale
    im = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    # 중심 좌표 및 기준 크기
    cx, cy = canvas_size / 2, canvas_size / 2
    w = canvas_size * 0.82
    h = canvas_size * 0.52

    # 컨트롤러 바디 좌표
    # 양쪽 그립과 중앙 바디를 부드럽게 연결
    # 상단 범퍼 및 곡선 바디
    body_left = cx - w / 2
    body_top = cy - h / 2 - 20 * scale
    body_right = cx + w / 2
    body_bottom = cy + h / 2 + 10 * scale

    # 컨트롤러 본체 (현대적인 딥 슬레이트 + 인디고 그라데이션 느낌의 둥근 형태)
    # 1. 외부 그림자/글로우 (은은한 바이올렛-블루 글로우)
    glow = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.rounded_rectangle(
        [body_left - 10 * scale, body_top - 5 * scale, body_right + 10 * scale, body_bottom + 15 * scale],
        radius=int(90 * scale),
        fill=(99, 102, 241, 70)
    )
    glow = glow.filter(ImageFilter.GaussianBlur(15 * scale))
    im.paste(glow, (0, 0), glow)

    # 2. 메인 바디 외형
    draw.rounded_rectangle(
        [body_left, body_top, body_right, body_bottom],
        radius=int(85 * scale),
        fill=(26, 32, 53, 255),
        outline=(99, 102, 241, 230),
        width=int(6 * scale)
    )

    # 컨트롤러 상단 범퍼 (L1 / R1 느낌)
    bumper_w = 70 * scale
    bumper_h = 14 * scale
    draw.rounded_rectangle(
        [cx - w * 0.35, body_top - bumper_h * 0.6, cx - w * 0.35 + bumper_w, body_top + 10 * scale],
        radius=int(7 * scale),
        fill=(59, 130, 246, 240)
    )
    draw.rounded_rectangle(
        [cx + w * 0.35 - bumper_w, body_top - bumper_h * 0.6, cx + w * 0.35, body_top + 10 * scale],
        radius=int(7 * scale),
        fill=(59, 130, 246, 240)
    )

    # 3. D-PAD (좌측 십자키)
    dpad_cx = cx - w * 0.26
    dpad_cy = cy - 5 * scale
    dpad_arm_len = 38 * scale
    dpad_arm_w = 26 * scale

    # 수평 암
    draw.rounded_rectangle(
        [dpad_cx - dpad_arm_len, dpad_cy - dpad_arm_w / 2, dpad_cx + dpad_arm_len, dpad_cy + dpad_arm_w / 2],
        radius=int(6 * scale),
        fill=(45, 55, 80, 255),
        outline=(148, 163, 184, 200),
        width=int(2.5 * scale)
    )
    # 수직 암
    draw.rounded_rectangle(
        [dpad_cx - dpad_arm_w / 2, dpad_cy - dpad_arm_len, dpad_cx + dpad_arm_w / 2, dpad_cy + dpad_arm_len],
        radius=int(6 * scale),
        fill=(45, 55, 80, 255),
        outline=(148, 163, 184, 200),
        width=int(2.5 * scale)
    )
    # D-pad 중심 둥근 음각
    draw.ellipse(
        [dpad_cx - 6 * scale, dpad_cy - 6 * scale, dpad_cx + 6 * scale, dpad_cy + 6 * scale],
        fill=(30, 38, 58, 255)
    )

    # 4. Action Buttons (우측 4버튼 - 모던 컬러)
    btn_cx = cx + w * 0.26
    btn_cy = cy - 5 * scale
    btn_dist = 28 * scale
    btn_radius = 12 * scale

    buttons = [
        (btn_cx, btn_cy - btn_dist, (244, 63, 94, 255)),   # 상 (Rose/Red)
        (btn_cx + btn_dist, btn_cy, (59, 130, 246, 255)),   # 우 (Blue)
        (btn_cx, btn_cy + btn_dist, (16, 185, 129, 255)),  # 하 (Emerald/Green)
        (btn_cx - btn_dist, btn_cy, (245, 158, 11, 255)),  # 좌 (Amber/Yellow)
    ]

    for bx, by, color in buttons:
        # 버튼 베이스 그림자
        draw.ellipse([bx - btn_radius - 1, by - btn_radius - 1, bx + btn_radius + 1, by + btn_radius + 1], fill=(15, 23, 42, 255))
        draw.ellipse([bx - btn_radius, by - btn_radius, bx + btn_radius, by + btn_radius], fill=color)
        # 하이라이트
        draw.ellipse([bx - btn_radius * 0.5, by - btn_radius * 0.6, bx + btn_radius * 0.2, by], fill=(255, 255, 255, 160))

    # 5. 아날로그 스틱 2개 (하단 중심 좌/우)
    stick_radius = 24 * scale
    stick_y = cy + h * 0.2
    stick_lx = cx - w * 0.12
    stick_rx = cx + w * 0.12

    for sx in [stick_lx, stick_rx]:
        # 베이스 링
        draw.ellipse([sx - stick_radius * 1.2, stick_y - stick_radius * 1.2, sx + stick_radius * 1.2, stick_y + stick_radius * 1.2],
                     fill=(15, 23, 42, 255), outline=(99, 102, 241, 150), width=int(2 * scale))
        # 스틱 캡
        draw.ellipse([sx - stick_radius, stick_y - stick_radius, sx + stick_radius, stick_y + stick_radius],
                     fill=(38, 48, 72, 255), outline=(148, 163, 184, 180), width=int(2 * scale))
        # 스틱 중앙 하이라이트/링
        draw.ellipse([sx - 8 * scale, stick_y - 8 * scale, sx + 8 * scale, stick_y + 8 * scale],
                     fill=(59, 130, 246, 200))

    # 6. 중앙 기능 버튼 (Select / Start & LED 인디케이터)
    # Select / Start 슬롯
    draw.rounded_rectangle([cx - 30 * scale, cy - 18 * scale, cx - 12 * scale, cy - 10 * scale], radius=int(4 * scale), fill=(100, 116, 139, 255))
    draw.rounded_rectangle([cx + 12 * scale, cy - 18 * scale, cx + 30 * scale, cy - 10 * scale], radius=int(4 * scale), fill=(100, 116, 139, 255))

    # 중앙 브랜드 심볼/원형 홈
    draw.ellipse([cx - 16 * scale, cy - 3 * scale, cx + 16 * scale, cy + 29 * scale],
                 fill=(15, 23, 42, 255), outline=(99, 102, 241, 220), width=int(2 * scale))
    # 중앙 홈 내부 작은 전원/동작 번개 또는 전원 표시
    draw.ellipse([cx - 9 * scale, cy + 4 * scale, cx + 9 * scale, cy + 22 * scale],
                 fill=(6, 182, 212, 255))

    # 리사이즈 (LANCZOS로 고품질 다운샘플링)
    final_img = im.resize((size, size), Image.Resampling.LANCZOS)
    return final_img


def create_tray_simple_icon(size=64):
    """트레이 알림 영역용 (작은 크기에서도 매우 또렷하게 보이는 고대비 심플 컨트롤러)"""
    scale = 4
    canvas_size = size * scale
    im = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    cx, cy = canvas_size / 2, canvas_size / 2
    w = canvas_size * 0.88
    h = canvas_size * 0.58

    # 본체 외형
    draw.rounded_rectangle(
        [cx - w/2, cy - h/2, cx + w/2, cy + h/2],
        radius=int(28 * scale),
        fill=(255, 255, 255, 245),
        outline=(99, 102, 241, 255),
        width=int(3 * scale)
    )

    # 십자키
    d_cx = cx - w * 0.25
    d_cy = cy
    d_len = 16 * scale
    d_w = 10 * scale
    draw.rectangle([d_cx - d_len, d_cy - d_w/2, d_cx + d_len, d_cy + d_w/2], fill=(30, 41, 59, 255))
    draw.rectangle([d_cx - d_w/2, d_cy - d_len, d_cx + d_w/2, d_cy + d_len], fill=(30, 41, 59, 255))

    # 4버튼
    b_cx = cx + w * 0.25
    b_cy = cy
    b_r = 5 * scale
    b_dist = 11 * scale
    draw.ellipse([b_cx - b_r, b_cy - b_dist - b_r, b_cx + b_r, b_cy - b_dist + b_r], fill=(239, 68, 68, 255))
    draw.ellipse([b_cx + b_dist - b_r, b_cy - b_r, b_cx + b_dist + b_r, b_cy + b_r], fill=(59, 130, 246, 255))
    draw.ellipse([b_cx - b_r, b_cy + b_dist - b_r, b_cx + b_r, b_cy + b_dist + b_r], fill=(16, 185, 129, 255))
    draw.ellipse([b_cx - b_dist - b_r, b_cy - b_r, b_cx - b_dist + b_r, b_cy + b_r], fill=(245, 158, 11, 255))

    # 중앙 점 2개
    draw.ellipse([cx - 7 * scale, cy - 3 * scale, cx - 2 * scale, cy + 2 * scale], fill=(100, 116, 139, 255))
    draw.ellipse([cx + 2 * scale, cy - 3 * scale, cx + 7 * scale, cy + 2 * scale], fill=(100, 116, 139, 255))

    return im.resize((size, size), Image.Resampling.LANCZOS)


def main():
    target_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(target_dir)
    web_dir = os.path.join(base_dir, "web")

    print("컨트롤러 투명 배경 아이콘 생성 중...")

    # 1. 512x512 고해상도 메인 아이콘
    icon_512 = create_controller_icon(512)
    icon_png_path = os.path.join(target_dir, "icon.png")
    icon_512.save(icon_png_path, format="PNG")
    print(f"저장 완료: {icon_png_path}")

    # web favicon 저장
    favicon_path = os.path.join(web_dir, "favicon.png")
    icon_512.save(favicon_path, format="PNG")
    print(f"저장 완료: {favicon_path}")

    # 2. Windows .ico 파일 생성 (16, 32, 48, 64, 128, 256 크기 모두 내장)
    ico_path = os.path.join(target_dir, "icon.ico")
    icon_512.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"저장 완료: {ico_path}")

    # 3. 트레이 전용 심플 아이콘 (투명 배경)
    tray_img = icon_512.resize((64, 64), Image.Resampling.LANCZOS)
    tray_path = os.path.join(target_dir, "tray_icon.png")
    tray_img.save(tray_path, format="PNG")
    print(f"저장 완료: {tray_path}")

    print("모든 컨트롤러 아이콘 생성 완료!")

if __name__ == "__main__":
    main()
