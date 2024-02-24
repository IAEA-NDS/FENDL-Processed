import re


def get_moder_comment_line_idx(lines):
    idx = -1
    while idx+2 < len(lines):
        idx += 1
        if lines[idx][:len('moder')] != 'moder':
            continue
        if lines[idx+1].rstrip('/').split() != ['1', '-21']:
            continue
        if not lines[idx+2].startswith("'"):
            continue
        return idx+2
    raise IndexError('moder comment line not found')


def get_moder_comment(lines):
    idx = get_moder_comment_line_idx(lines)
    m = re.match("^[^']*'([^']*)'", lines[idx])
    if not m:
        raise IndexError('comment not found')
    return m.group(1)


def set_moder_comment(lines, comment):
    idx = get_moder_comment_line_idx(lines)
    lines[idx] = f"'{comment}'/"


def _get_reconr_comment_line_idx(lines, tapeids):
    idx = -1
    while idx+6 < len(lines):
        idx += 1
        if lines[idx][:len('reconr')] != 'reconr':
            continue
        if lines[idx+1].rstrip('/').split() != tapeids:
            continue
        if not lines[idx+2].startswith("'"):
            continue
        if not lines[idx+5].startswith("'"):
            continue
        if not lines[idx+6].startswith("'"):
            continue
        return idx+2
    raise IndexError('reconr comment line not found')


def _get_reconr_comments(lines, tapeids):
    idx = _get_reconr_comment_line_idx(lines, tapeids)
    comments = []
    for i in (0, 3, 4):
        m = re.search("'([^']*)'", lines[idx+i])
        if not m:
            raise IndexError('not able to extract comment')
        comments.append(m.group(1))
    return comments


def _set_reconr_comments(lines, tapeids, comments):
    if len(comments) != 3:
        raise IndexError('expecting three comment lines')
    idx = _get_reconr_comment_line_idx(lines, tapeids)
    lines[idx] = f"'{comments[0]}'/"
    lines[idx+3] = f"'{comments[1]}'/"
    lines[idx+4] = f"'{comments[2]}'/"


def get_reconr_comments1(lines):
    return _get_reconr_comments(lines, ['-21', '-22'])


def set_reconr_comments1(lines, comments):
    return _set_reconr_comments(lines, ['-21', '-22'], comments)


def get_reconr_comments2(lines):
    return _get_reconr_comments(lines, ['-41', '-42'])


def set_reconr_comments2(lines, comments):
    return _set_reconr_comments(lines, ['-41', '-42'], comments)


def get_ace_comment_line_idx(lines):
    idx = -1
    while idx+4 < len(lines):
        idx += 1
        if lines[idx][:len('acer')] != 'acer':
            continue
        if lines[idx+1].rstrip('/').split()[3] != '27':
            continue
        if lines[idx+3][0] != '\'' or lines[idx+3][-2:] != '\'/':
            continue
        return idx+3
    raise IndexError('acer comment line not found')


def get_ace_comment(lines):
    idx = get_ace_comment_line_idx(lines)
    m = re.match("^ *'([^']*)'", lines[idx])
    if not m:
        raise IndexError('comment not found')
    return m.group(1)


def set_ace_comment(lines, comment):
    idx = get_ace_comment_line_idx(lines)
    lines[idx] = '\'' + comment + '\'/'


def get_g_comment_line_idx(lines):
    idx = -1
    while idx+4 < len(lines):
        idx += 1
        if lines[idx][:len('groupr')] != 'groupr':
            continue
        if lines[idx+1].rstrip('/').split()[3] != '31':
            continue
        if lines[idx+3][0] != "'" or lines[idx+3][-2:] != "'/":
            continue
        return idx+3
    raise IndexError('groupr comment line not found')


def get_g_comment(lines):
    idx = get_g_comment_line_idx(lines)
    m = re.match("^ *'([^']*)'", lines[idx])
    if not m:
        raise IndexError('comment not found')
    return m.group(1)


def set_g_comment(lines, comment):
    idx = get_g_comment_line_idx(lines)
    lines[idx] = f"'{comment}'/"


def get_gam_comment_line_idx(lines):
    idx = -1
    while idx+4 < len(lines):
        idx += 1
        if lines[idx][:len('gaminr')] != 'gaminr':
            continue
        if lines[idx+1].rstrip('/').split()[3] != '43':
            continue
        if lines[idx+3][0] != "'" or lines[idx+3][-2:] != "'/":
            continue
        return idx+3
    raise IndexError('gaminr comment line not found')


def get_gam_comment(lines):
    idx = get_gam_comment_line_idx(lines)
    m = re.match("^ *'([^']*)'", lines[idx])
    if not m:
        raise IndexError('comment not found')
    return m.group(1)


def set_gam_comment(lines, comment):
    idx = get_gam_comment_line_idx(lines)
    lines[idx] = f"'{comment}'/"


def get_m_comment_line_idx(lines):
    idx = -1
    while idx+4 < len(lines):
        idx += 1
        if lines[idx][:len('matxsr')] != 'matxsr':
            continue
        if lines[idx+1].rstrip('/').split()[2] != '44':
            continue
        if lines[idx+2][:3] != "1 '" or lines[idx+2][-2:] != "'/":
            continue
        return idx+2
    raise IndexError('matxsr comment line not found')


def get_m_comment(lines):
    idx = get_m_comment_line_idx(lines)
    m = re.match("^[^']*'([^']*)'", lines[idx])
    if not m:
        raise IndexError('comment not found')
    return m.group(1)


def set_m_comment(lines, comment):
    idx = get_m_comment_line_idx(lines)
    lines[idx] = f"1 '{comment}'/"


def get_m_long_comment_line_idx(lines):
    idx = -1
    while idx+4 < len(lines):
        idx += 1
        if lines[idx][:len('matxsr')] != 'matxsr':
            continue
        if lines[idx+1].rstrip('/').split()[2] != '44':
            continue
        if not lines[idx+4].startswith("'"):
            continue
        if not lines[idx+5].startswith("'Photo-atomic"):
            continue
        if not lines[idx+6].startswith("'"):
            continue
        return idx+4
    raise IndexError('matxsr comment line not found')


def get_m_long_comments(lines):
    idx = get_m_long_comment_line_idx(lines)
    comments = []
    for i in range(3):
        m = re.search("'([^']*)'", lines[idx+i])
        if not m:
            raise IndexError('not able to extract comment')
        comments.append(m.group(1))
    return comments


def set_m_long_comments(lines, comments):
    if len(comments) != 3:
        raise IndexError('expecting three comment lines')
    if 'Photo-atomic' not in comments[1]:
        raise ValueError('expecting "Photo-atomic" in second comment line')
    idx = get_m_long_comment_line_idx(lines)
    lines[idx] = f"'{comments[0]}'/"
    lines[idx+1] = f"'{comments[1]}'/"
    lines[idx+2] = f"'{comments[2]}'/"
