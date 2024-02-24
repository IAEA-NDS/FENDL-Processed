import re
import hashlib
import subprocess
import tempfile
import os


def insert_pdf_trailer_ids(data, id1, id2):
    assert isinstance(id1, str)
    assert isinstance(id2, str)
    id1 = str.encode(id1.upper())
    id2 = str.encode(id2.upper())
    if len(id1) != 32 or len(id2) != 32:
        raise TypeError('ids must be 32 chars each')
    try:
        int(id1, 16)
        int(id2, 16)
    except:
        raise TypeError('ids must be hexadecimal strings')
    new_idstr = b'/ID [<' + id1 + b'><' + id2 + b'>]'
    myiter = re.finditer(b'/ID \[(<[0-9a-z]{32}>){2}\]', data)
    last_end = 0
    new_data = b''
    for m in myiter:
        cur_start = m.start()
        cur_end = m.end()
        new_data += data[last_end:cur_start]
        new_data += new_idstr
        last_end = cur_end
    new_data += data[last_end:]
    return new_data


def zero_pdf_trailer_ids(data):
    zerostr = '0' * 32
    return insert_pdf_trailer_ids(data, zerostr, zerostr)


def compute_sha256(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()


def normalize_pdf_trailer_ids(data):
    new_data = zero_pdf_trailer_ids(data)
    checksum = compute_sha256(new_data)
    id1 = checksum[:32]
    id2 = checksum[32:]
    new_data = insert_pdf_trailer_ids(new_data, id1, id2)
    return new_data


def remove_pdf_documentid(data):
    with tempfile.TemporaryDirectory() as tmpdir:
        fpath = os.path.join(tmpdir, 'tempfile')
        with open(fpath, 'wb') as f:
            f.write(data)
        p = subprocess.run(['exiftool', '-DocumentID=', '-overwrite_original', fpath])
        with open(fpath, 'rb') as f:
            new_data = f.read()
    if p.returncode != 0:
        raise OSError('unable to apply exiftool to file')
    return new_data


def _set_pdf_dates(data, datestr):
    with tempfile.TemporaryDirectory() as tmpdir:
        fpath = os.path.join(tmpdir, 'tempfile')
        with open(fpath, 'wb') as f:
            f.write(data)
        p1 = subprocess.run(['exiftool', f'-ModifyDate={datestr}', '-overwrite_original', fpath])
        p2 = subprocess.run(['exiftool', f'-CreateDate={datestr}', '-overwrite_original', fpath])
        with open(fpath, 'rb') as f:
            new_data = f.read()
    if p1.returncode != 0 or p2.returncode != 0:
        raise OSError('unable to apply exiftool to file')
    return new_data


def set_pdf_dates(data, datetime_obj):
    datestr = datetime_obj.strftime('%Y:%m:%d %H:%M:%S')
    return _set_pdf_dates(data, datestr)


def remove_pdf_dates(data):
    return _set_pdf_dates(data, '')


def linearize_pdf(data):
    with tempfile.TemporaryDirectory() as tmpdir:
        fin_path = os.path.join(tmpdir, 'input')
        fout_path = os.path.join(tmpdir, 'output')
        with open(fin_path, 'wb') as fin:
            fin.write(data)
        p = subprocess.run(['qpdf', '--linearize', fin_path, fout_path]) 
        if p.returncode != 0:
            raise OSError('unable to run/apply qpdf command-line tool')
        with open(fout_path, 'rb') as fout:
            new_data = fout.read()
    return new_data


def remove_volatile_pdf_metadata(data, datetime_obj=None):
    new_data = remove_pdf_documentid(data)
    if datetime_obj is None:
        new_data = remove_pdf_dates(new_data)
    else:
        new_data = set_pdf_dates(new_data, datetime_obj)
    new_data = linearize_pdf(new_data)
    new_data = normalize_pdf_trailer_ids(new_data)
    return new_data


def remove_metadata_from_pdf(filename, datetime_obj=None):
    with open(filename, 'rb') as f:
        data = f.read()
    new_data = remove_volatile_pdf_metadata(data, datetime_obj)
    with open(filename, 'wb') as f:
        f.write(new_data)
