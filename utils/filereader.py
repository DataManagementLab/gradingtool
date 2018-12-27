import sys

from chardet.universaldetector import UniversalDetector

# for on the file charset detection
detector = UniversalDetector()


def robust_filereader(filename, as_lines=True, try_naive=True, fix_nls=False):
    """
    Return the contents of a file while beeing robust to different charsets.
    The charset is determined using chardet if the naive way fails.

    :param filename: filename
    :param as_lines: return file contents as list of lines or a single string
    :param try_naive: wether to try the normal file-reading first and then fallback
    :param fix_nls: replace known line-endings with a single backslash-n newline character
    :param one_pass: read as binary
    :return: points, comment
    """

    if try_native:
        try:
            with open(filename, 'r') as f:
                if as_lines:
                    return [line for line in f]
                else:
                    return f.read()
        except UnicodeDecodeError:
            print(f"[ERROR]: \"{filename}\" could not be read using the naive filereader", file=sys.stderr)


    detector.reset()
    lines = []

    with open(filename, 'rb') as f:
        for line in f:
            detector.feed(line)
            lines.append(line)
            #if detector.done: break
    detector.close()

    encoding = detector.result['encoding']
    confidence = detector.result['confidence']
    print(f"[INFO]: \"{filename}\" was read as {encoding} with confidence={confidence}", file=sys.stderr)

    lines = [line.decode(encoding) for line in lines]

    if fix_nls:
        lines = [line.replace('\r\n', '\n').replace('\r', '\n') for line in lines]

    # print(''.join(lines))

    if as_lines:
        return lines
    else:
        return ''.join(lines)
