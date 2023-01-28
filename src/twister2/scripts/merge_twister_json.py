import argparse
import glob
import json
import os
import zipfile

from collections import OrderedDict
from pathlib import Path


def merge_json_v1(reports=None, path_to=None):
    merged_json_v1 = None
    for file in reports:
        with open(file, 'r') as f:
            loaded_json = json.load(f, object_pairs_hook=OrderedDict)
            if not merged_json_v1:
                merged_json_v1 = loaded_json
            else:
                merged_json_v1["testsuites"].extend(loaded_json["testsuites"])

    with open(path_to / 'results_merged.json', 'w') as output_file:
        json.dump(merged_json_v1, output_file, indent=4)

    return 0


def merge_json_v2(reports=None, path_to=None):
    merged_json_v2 = None
    for file in reports:
        with open(file, 'r') as f:
            loaded_json = json.load(f, object_pairs_hook=OrderedDict)
            if not merged_json_v2:
                merged_json_v2 = loaded_json
            else:
                merged_json_v2["environment"]["duration"] += loaded_json["environment"]["duration"]
                for key in merged_json_v2["summary"].keys():
                    merged_json_v2["summary"][key] += loaded_json["summary"][key]

                merged_json_v2["tests"].extend(loaded_json["tests"])

    with open(path_to / 'results_merged.json', 'w') as output_file:
        json.dump(merged_json_v2, output_file, indent=4)

    return 0


def unzip_reports(path_from, path_to):
    with zipfile.ZipFile(path_from, 'r') as zip_ref:
        zip_ref.extractall(path_to)


def get_reports_paths(path_to):
    pattern = path_to / 'results*.json'
    res = glob.glob(str(pattern))
    if not res:
        print("No reports given")
        os.exit(1)
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--path-to',
        action='store',
        help='Path to where unzip reports',
    )
    # TODO: Add mutualy exclusive v1 and v2 workflows
    parser.add_argument(
        '--v1-reports',
        metavar='path',
        action='store',
        help='Path to ziped v1 json reports',
    )
    parser.add_argument(
        '--v2-reports',
        metavar='path',
        action='store',
        help='Path to ziped v2 json reports',
    )
    args = parser.parse_args()

    if not args.path_to:
        print("Missing 'path_to' arg")
        return 1
    path_to = Path(args.path_to)

    if args.v1_reports and args.v2_reports:
        print("Only single type at once supported")
    elif args.v1_reports:
        reports_ziped = args.v1_reports
    elif args.v2_reports:
        reports_ziped = args.v2_reports
    else:
        print("No reports chosen")
        os.exit(1)

    unzip_reports(reports_ziped, path_to)
    reports_to_merge = get_reports_paths(path_to)
    if args.v1_reports:
        merge_json_v1(reports_to_merge, path_to)
    if args.v2_reports:
        merge_json_v2(reports_to_merge, path_to)

    print(f"Successfuly merged {len(reports_to_merge)} reports")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
