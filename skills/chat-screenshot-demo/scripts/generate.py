#!/usr/bin/env python3
"""Create a phone-shaped illustrative chat screenshot from editable JSON."""
import argparse
from decimal import Decimal, InvalidOperation
import glob
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:
    bundled = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
    if bundled.exists() and os.path.realpath(sys.executable) != os.path.realpath(bundled):
        os.execv(str(bundled), [str(bundled), str(Path(__file__).resolve()), *sys.argv[1:]])
    sys.exit('Pillow 不可用，请安装与当前 Python 匹配的 Pillow：python3 -m pip install Pillow')

HERE = Path(__file__).resolve().parent.parent
W, BASE_H, HEADER, FOOTER = 1260, 2736, 294, 270
AVATAR_SIZE = 100
AVATAR_LEFT_X = 36
AVATAR_RIGHT_X = W - 38 - AVATAR_SIZE
BUBBLE_LEFT_X = AVATAR_LEFT_X + AVATAR_SIZE + 36
BUBBLE_RIGHT_X = AVATAR_RIGHT_X - 35
DEFAULT_AVATAR_PIXEL_BLOCKS = 5
BG, INCOMING, OUTGOING = '#ededed', '#ffffff', '#95ec69'
FONT_PATH = next((p for p in ['/System/Library/Fonts/PingFang.ttc'] + glob.glob('/System/Library/AssetsV2/com_apple_MobileAsset_Font8/*.asset/AssetData/PingFang.ttc') + ['/System/Library/Fonts/STHeiti Light.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'] if os.path.exists(p)), None)
if not FONT_PATH:
    sys.exit('未找到支持中文的字体。')
def font(size, index=None):
    if index is None: index=3 if 'PingFang' in FONT_PATH else 0
    try: return ImageFont.truetype(FONT_PATH, size, index=index)
    except OSError: return ImageFont.truetype(FONT_PATH, size)
F_BODY = font(50)
F_TITLE = font(48, 7 if 'PingFang' in FONT_PATH else 1)
F_TIME = font(38)
F_NAME = font(34)
F_QUOTE = font(41)
F_AVATAR = font(40)
F_TRANSFER_AMOUNT = font(49, 7 if 'PingFang' in FONT_PATH else 1)
F_TRANSFER_STATUS = font(39)
F_TRANSFER_LABEL = font(35)
_meas = ImageDraw.Draw(Image.new('RGB',(1,1)))
def width(text, f=F_BODY):
    return _meas.textlength(text, font=f)
def wrap(text, maxwidth, f=F_BODY):
    lines=[]
    for para in str(text).split('\n'):
        line=''
        for ch in para:
            if line and width(line+ch, f)>maxwidth:
                # Avoid leaving Chinese punctuation alone at the start of a line.
                if ch in '，。！？：；、）》」』】…,.!?;:)]}' and len(line)>1:
                    lines.append(line[:-1]); line=line[-1]+ch
                else:
                    lines.append(line); line=ch
            else: line += ch
        lines.append(line)
    return lines or ['']
def ellipsis(text, limit, f):
    text=str(text)
    if width(text,f)<=limit: return text
    while text and width(text+'…',f)>limit: text=text[:-1]
    return text+'…'
def resolve(path, root):
    p=Path(path).expanduser()
    return p if p.is_absolute() else root/p
def open_image(path, root):
    p=resolve(path,root)
    try:
        with Image.open(p) as im: return ImageOps.exif_transpose(im).convert('RGB')
    except (OSError,ValueError) as e: raise ValueError(f'无法读取图片 {p}: {e}') from e
def paste_round(canvas, image, xy, size, radius=12, fit=True):
    image=ImageOps.fit(image,size,method=Image.Resampling.LANCZOS) if fit else image.resize(size,Image.Resampling.LANCZOS)
    mask=Image.new('L',size,0); ImageDraw.Draw(mask).rounded_rectangle((0,0,size[0]-1,size[1]-1), radius=radius,fill=255)
    canvas.paste(image,xy,mask)
def template_index(value):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 10:
        raise ValueError('avatar_template 须为 1 到 10 的整数')
    return value

def apply_avatar_template(info, index):
    """Resolve the bundled image only if an explicit image was not provided."""
    if info.get('avatar'):
        return
    number=template_index(info.get('avatar_template', index))
    path=HERE/'assets'/'avatars'/f'avatar-{number:02d}.png'
    if not path.is_file():
        raise ValueError(f'头像模板不存在：{path}，请恢复随技能提供的头像资源')
    info['avatar']=str(path)
    # A crop applies to a supplied source image, not a bundled template.
    info.pop('avatar_crop',None)

def avatar(canvas, x, y, info, root, default, pixel_blocks):
    if info.get('avatar'):
        # Anonymize the entire avatar, including its background, text and hair.
        # Raw images never go into an output image or an intermediate file.
        raw = open_image(info['avatar'], root)
        crop = info.get('avatar_crop')
        if crop is not None:
            if (not isinstance(crop, (list,tuple)) or len(crop)!=4 or
                any(isinstance(v,bool) or not isinstance(v,int) for v in crop)):
                raise ValueError('avatar_crop 必须是原图上的四个整数像素坐标 [左, 上, 右, 下]')
            x0,y0,x1,y1=crop
            if not (0 <= x0 < x1 <= raw.width and 0 <= y0 < y1 <= raw.height):
                raise ValueError(f'avatar_crop 超出图片范围：{raw.width} × {raw.height}')
            raw=raw.crop((x0,y0,x1,y1))
        square = ImageOps.fit(raw, (AVATAR_SIZE, AVATAR_SIZE), method=Image.Resampling.LANCZOS)
        mosaic = square.resize((pixel_blocks, pixel_blocks), Image.Resampling.LANCZOS)
        mosaic = mosaic.resize((AVATAR_SIZE, AVATAR_SIZE), Image.Resampling.NEAREST)
        paste_round(canvas, mosaic, (x,y), (AVATAR_SIZE,AVATAR_SIZE), 9, fit=False)
    else:
        d=ImageDraw.Draw(canvas)
        d.rounded_rectangle((x,y,x+AVATAR_SIZE-1,y+AVATAR_SIZE-1),radius=9,fill=info.get('color',default))
        name=str(info.get('name','友')).strip() or '友'
        d.text((x+AVATAR_SIZE//2,y+AVATAR_SIZE//2),name[-1],font=F_AVATAR,fill='white',anchor='mm')
def validate(data):
    if not isinstance(data,dict): raise ValueError('输入必须是 JSON 对象')
    pixel_blocks=data.get('avatar_pixel_blocks',DEFAULT_AVATAR_PIXEL_BLOCKS)
    if isinstance(pixel_blocks,bool) or not isinstance(pixel_blocks,int) or not 3<=pixel_blocks<=10:
        raise ValueError('avatar_pixel_blocks 须为 3 到 10 的整数，且不能关闭头像全图打码')
    msgs=data.get('messages')
    if not isinstance(msgs,list) or not msgs: raise ValueError('messages 必须是非空数组')
    if len(msgs)>100: raise ValueError('单张图片最多支持 100 条消息，请拆分案例')
    parts=data.get('participants',{})
    if not isinstance(parts,dict) or any(not isinstance(parts.get(k,{}),dict) for k in ('left','right')): raise ValueError('participants.left 和 participants.right 必须是对象')
    for i,m in enumerate(msgs,1):
        if not isinstance(m,dict) or m.get('side') not in ('left','right','system'): raise ValueError(f'第 {i} 条消息的 side 必须是 left、right 或 system')
        typ=m.get('type','text')
        if typ not in ('text','image','video','card','transfer'): raise ValueError(f'第 {i} 条消息类型不支持：{typ}')
        if m['side']=='system' or typ in ('text','card'):
            if not isinstance(m.get('text'),str) or not m['text'].strip(): raise ValueError(f'第 {i} 条文字消息必须包含非空 text')
        if typ in ('image','video') and not isinstance(m.get('image'),str): raise ValueError(f'第 {i} 条图片或视频消息必须提供本地 image 路径')
        if typ=='transfer':
            try:
                amount=Decimal(str(m['amount']))
            except (KeyError, InvalidOperation, ValueError):
                raise ValueError(f'第 {i} 条转账必须提供有效的 amount')
            if not amount.is_finite() or amount < 0 or amount > Decimal('999999999') or amount.as_tuple().exponent < -2:
                raise ValueError(f'第 {i} 条转账金额需为非负数、最多两位小数，且不超过 999999999')
            if m.get('status','已被接收') not in ('已被接收','已收款'):
                raise ValueError(f'第 {i} 条转账状态只支持 已被接收 或 已收款')
            if m['side']=='system': raise ValueError(f'第 {i} 条转账的 side 必须是 left 或 right')
        if len(str(m.get('text','')))>3000: raise ValueError(f'第 {i} 条消息超过 3000 字符')
        if 'sender' in m and not isinstance(m['sender'],dict): raise ValueError(f'第 {i} 条 sender 必须是对象')

def layout(m,root,group):
    typ=m.get('type','text')
    name_h=42 if group and m['side']=='left' else 0
    if m['side']=='system':
        lines=wrap(m['text'],850,F_TIME)
        return {'kind':'system','lines':lines,'height':max(60,len(lines)*50),'name_h':0}
    if typ=='transfer':
        return {'kind':'transfer','w':784,'h':258,'height':max(AVATAR_SIZE,name_h+258),'name_h':name_h}
    if typ in ('image','video'):
        im=open_image(m['image'],root)
        iw,ih=im.size
        scale=min(472/iw,630/ih,1)
        if iw*scale<190 and ih*scale<190: scale=min(190/iw,190/ih,2)
        w,h=max(1,round(iw*scale)),max(1,round(ih*scale))
        return {'kind':typ,'w':w,'h':h,'height':max(AVATAR_SIZE,name_h+h),'name_h':name_h}
    if typ=='card':
        lines=wrap(m['text'],700,F_BODY)
        detail=wrap(m.get('detail',''),700,F_QUOTE) if m.get('detail') else []
        h=65*len(lines)+48*len(detail)+95
        return {'kind':'card','w':786,'h':h,'lines':lines,'detail':detail,'height':max(AVATAR_SIZE,name_h+h),'name_h':name_h}
    lines=wrap(m['text'],780)
    w=max(120,math.ceil(max(width(s) for s in lines))+72)
    h=123+(len(lines)-1)*64
    quote_lines=wrap(str(m['quote']),768,F_QUOTE) if m.get('quote') else []
    # A quoted reply is attached immediately below the bubble, as in the sample.
    qh=93+(min(2,len(quote_lines))-1)*51 if quote_lines else 0
    return {'kind':'text','lines':lines,'w':w,'h':h,'quote_lines':quote_lines,'quote_h':qh,'height':max(AVATAR_SIZE,name_h+h+(12+qh if qh else 0)),'name_h':name_h}

def header(canvas,data):
    reference=HERE/'assets'/'reference-header.png'
    if reference.exists(): canvas.paste(Image.open(reference).convert('RGB'),(0,0))
    else: ImageDraw.Draw(canvas).rectangle((0,0,W,HEADER),fill=BG)
    # Reconstruct the subtle background gradient from pixels on both sides of
    # the original title, so it does not leave a flat rectangle behind.
    def erase_region(x0,y0,x1,y1):
        strip=Image.new('RGB',(2,y1-y0))
        strip.paste(canvas.crop((x0-1,y0,x0,y1)),(0,0))
        strip.paste(canvas.crop((x1,y0,x1+1,y1)),(1,0))
        canvas.paste(strip.resize((x1-x0,y1-y0),Image.Resampling.BILINEAR),(x0,y0))
    erase_region(290,215,970,286)
    d=ImageDraw.Draw(canvas)
    title=ellipsis(data.get('title') or data.get('participants',{}).get('left',{}).get('name') or '林女士',620,F_TITLE)
    d.text((W//2,228),title,font=F_TITLE,fill='#161616',anchor='mt')
    if 'status_time' in data and data['status_time']!='20:38':
        erase_region(118,78,282,150)
        d=ImageDraw.Draw(canvas)
        d.text((122,90),str(data['status_time']),font=font(56,7 if 'PingFang' in FONT_PATH else 1),fill='#080808',anchor='lt')
    d.line((0,293,W,293),fill='#d8d8d8',width=1)
def footer(canvas,y):
    reference=HERE/'assets'/'reference-footer.png'
    if reference.exists(): canvas.paste(Image.open(reference).convert('RGB'),(0,y))
    else: ImageDraw.Draw(canvas).rectangle((0,y,W,y+FOOTER),fill='#f6f6f6')
def render(data,root):
    validate(data)
    pixel_blocks=data.get('avatar_pixel_blocks',DEFAULT_AVATAR_PIXEL_BLOCKS)
    group=bool(data.get('group',False))
    parts=data.get('participants',{})
    # Derive a stable per-case base; animation repeatedly renders this same JSON.
    # The optional key allows a caller to keep an avatar when the script changes.
    case_key=data.get('avatar_case_key')
    if case_key is None:
        case_key=json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    else:
        case_key=str(case_key)
    base=int.from_bytes(hashlib.sha256(case_key.encode('utf-8')).digest()[:8],'big')%10
    # Keep each of the first ten named group members visually distinct, while
    # repeated messages by the same member always retain the same avatar.
    sender_names=sorted({str(m.get('sender',{}).get('name') or parts.get('left',{}).get('name') or '')
                         for m in data['messages'] if m.get('side')=='left'}) if group else []
    sender_offsets={name:i for i,name in enumerate(sender_names)}
    layouts=[layout(m,root,group) for m in data['messages']]
    notice=bool(group and data.get('announcement'))
    notice_h=184 if notice else 0
    content_h=sum(l['height']+51+(90 if m.get('time') else 0) for m,l in zip(data['messages'],layouts))
    content_h=max(0,content_h-51)
    start_y=HEADER+notice_h+(8 if data['messages'][0].get('time') else 55)
    # Use a full-height phone viewport for short chats; extend a long image only
    # when messages exceed that viewport.  Keep the first message at the top,
    # like the conversation view of a phone with a short chat history.
    H=max(BASE_H,start_y+content_h+40+FOOTER)
    if H>60000: raise ValueError('图片过长，请减少消息或拆分案例')
    canvas=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(canvas)
    header(canvas,data)
    if notice:
        d.rounded_rectangle((24,318,1236,454),radius=25,fill='white')
        d.text((67,356),'●',font=font(40),fill='#ffb400',anchor='lt')
        d.text((170,358),ellipsis(data['announcement'],1020,F_NAME),font=F_NAME,fill='#202020',anchor='lt')
    # Start near the navigation bar. Bottom-aligning a short conversation
    # creates a large artificial gap before the first timestamp.
    y=start_y
    for m,l in zip(data['messages'],layouts):
        if m.get('time'):
            d.text((W//2,y+8),str(m['time']),font=F_TIME,fill='#a4a4a4',anchor='mt'); y+=90
        if m['side']=='system':
            for line in l['lines']:
                d.text((W//2,y+3),line,font=F_TIME,fill='#a3a3a3',anchor='mt'); y+=50
            y+=max(0,l['height']-len(l['lines'])*50)+51
            continue
        left=m['side']=='left'; info=dict(parts.get(m['side'],{})); sender=m.get('sender',{})
        # A new sender image must not accidentally inherit another image's crop.
        if 'avatar' in sender or 'avatar_template' in sender:
            for key in ('avatar','avatar_template','avatar_crop'): info.pop(key,None)
        info.update(sender)
        if left:
            sender_name=str(sender.get('name') or parts.get('left',{}).get('name') or '')
            number=(base+sender_offsets.get(sender_name,0))%10+1
            apply_avatar_template(info,number)
        elif 'avatar_template' in info and not info.get('avatar'):
            apply_avatar_template(info,1)
        avatar(canvas,AVATAR_LEFT_X if left else AVATAR_RIGHT_X,y,info,root,'#88a9a3' if left else '#9d8cae',pixel_blocks)
        if l['name_h']:
            d.text((BUBBLE_LEFT_X,y-3),ellipsis(info.get('name','朋友'),700,F_NAME),font=F_NAME,fill='#909090',anchor='lt')
        by=y+l['name_h']; x=BUBBLE_LEFT_X if left else BUBBLE_RIGHT_X-l['w']
        if l['kind']=='transfer':
            color='#fdce9d'
            d.rounded_rectangle((x,by,x+l['w'],by+l['h']),radius=11,fill=color)
            if left: d.polygon(((x+1,by+46),(x-15,by+62),(x+1,by+79)),fill=color)
            else: d.polygon(((x+l['w']-1,by+46),(x+l['w']+15,by+62),(x+l['w']-1,by+79)),fill=color)
            cx,cy=x+96,by+96
            d.ellipse((cx-64,cy-64,cx+64,cy+64),outline='white',width=7)
            d.line(((cx-27,cy),(cx-9,cy+19),(cx+34,cy-24)),fill='white',width=7,joint='curve')
            amount=f"¥{Decimal(str(m['amount'])):.2f}"
            d.text((x+187,by+39),amount,font=F_TRANSFER_AMOUNT,fill='white',anchor='lt')
            d.text((x+187,by+101),m.get('status','已被接收'),font=F_TRANSFER_STATUS,fill='white',anchor='lt')
            d.text((x+31,by+190),'转账',font=F_TRANSFER_LABEL,fill='#fff0df',anchor='lt')
        elif l['kind'] in ('image','video'):
            paste_round(canvas,open_image(m['image'],root),(x,by),(l['w'],l['h']),10)
            if l['kind']=='video':
                cx=x+l['w']//2; cy=by+l['h']//2; r=59
                d.ellipse((cx-r,cy-r,cx+r,cy+r),outline='white',width=3)
                d.polygon(((cx-14,cy-23),(cx-14,cy+23),(cx+27,cy)),fill='white')
        else:
            color='white' if left else OUTGOING
            d.rounded_rectangle((x,by,x+l['w'],by+l['h']),radius=10,fill=color)
            if left: d.polygon(((x+1,by+40),(x-14,by+53),(x+1,by+65)),fill=color)
            else: d.polygon(((x+l['w']-1,by+40),(x+l['w']+14,by+53),(x+l['w']-1,by+65)),fill=color)
            for j,line in enumerate(l['lines']): d.text((x+36,by+32+j*64),line,font=F_BODY,fill='#1b1b1b',anchor='lt')
            if l['kind']=='card':
                for j,line in enumerate(l['detail']): d.text((x+36,by+40+len(l['lines'])*65+j*48),line,font=F_QUOTE,fill='#898989',anchor='lt')
                d.text((x+36,by+l['h']-52),'聊天记录',font=F_NAME,fill='#999999',anchor='lt')
            if l.get('quote_h'):
                qlines=l['quote_lines'][:2]
                if len(l['quote_lines'])>2: qlines[-1]=ellipsis(qlines[-1]+'…',768,F_QUOTE)
                qw=max(l['w']+15,math.ceil(max(width(line,F_QUOTE) for line in qlines))+78); qw=min(qw,850)
                qx=x if left else BUBBLE_RIGHT_X-qw; qy=by+l['h']+12
                d.rounded_rectangle((qx,qy,qx+qw,qy+l['quote_h']),radius=9,fill='#e1e1e1')
                # Center the actual glyph ink, not the font's larger bounding box.
                boxes=[d.textbbox((0,0),line,font=F_QUOTE,anchor='lt') for line in qlines]
                ink_top=min(box[1]+j*51 for j,box in enumerate(boxes))
                ink_bottom=max(box[3]+j*51 for j,box in enumerate(boxes))
                text_y=qy+(l['quote_h']-(ink_bottom-ink_top))//2-ink_top
                for j,line in enumerate(qlines): d.text((qx+39,text_y+j*51),line,font=F_QUOTE,fill='#656565',anchor='lt')
        y+=l['height']+51
    footer(canvas,H-FOOTER)
    return canvas

def main():
    parser=argparse.ArgumentParser(description='根据对话 JSON 生成竖版手机聊天截图')
    parser.add_argument('--input','-i',required=True,help='对话 JSON 文件')
    parser.add_argument('--output','-o',required=True,help='输出 PNG 文件')
    args=parser.parse_args()
    try:
        src=Path(args.input).expanduser().resolve(); dst=Path(args.output).expanduser().resolve()
        if dst.suffix.lower()!='.png': raise ValueError('输出文件必须以 .png 结尾')
        with src.open(encoding='utf-8-sig') as f: data=json.load(f)
        canvas=render(data,src.parent)
        dst.parent.mkdir(parents=True,exist_ok=True); canvas.save(dst,'PNG',optimize=True)
        print(f'已生成：{dst}（{canvas.width} × {canvas.height}）')
    except (ValueError,OSError,json.JSONDecodeError) as exc:
        print(f'生成失败：{exc}',file=sys.stderr); return 1
    return 0
if __name__=='__main__': sys.exit(main())
