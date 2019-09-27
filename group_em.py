# group_em.py
from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist, InvalidAccessToken, Unauthorized
from requests.exceptions import ConnectionError, MissingSchema
from collections import defaultdict
import os, sys
import argparse
import csv
import re

def csvToTeams(file_name):
    with open(file_name) as f:
        tuples=[tuple(line) for line in csv.reader(f)]
    pattern = re.compile("\d+")
    if pattern.match(tuples[0][1]) == None:
        tuples = tuples[1:]
    if pattern.match(tuples[0][1]) == None:
        sys.exit(1)

    plannedTeams = defaultdict(list)
    for k, v in tuples:
        plannedTeams[k].append(v)
    return plannedTeams

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--canvas_key",
        default=None,
        help="your canvas account token. see: https://canvas.instructure.com/doc/api/file.oauth.html#manual-token-generation")

    parser.add_argument(
        "--canvas_url",
        default=None,
        help="the URL of your canvas instance, e.g. https://canvas.jmu.edu/")
    

    parser.add_argument("assignments", help="csv file with 2 columns: teamname,canvasstudentid")
    parser.add_argument("course", help="canvas course id")
    
    parser.add_argument(
        "--wet_run",
        action="store_true",
        help="really create the memberships (script defaults to a dry-run)")
    
    args = parser.parse_args()

    DRY = not args.wet_run

    canvas_key = args.canvas_key
    canvas_url = args.canvas_url
    if canvas_key is None:
        canvas_key = os.environ["CANVAS_KEY"]
    if canvas_url is None:
        canvas_url = os.environ["CANVAS_URL"]
    if canvas_key is None or canvas_url is None:
        print("must provide canvas api key and url via either the optional flags or the environment variables: CANVAS_KEY and CANVAS_URL")
        sys.exit(1)
    
    canvas = Canvas(canvas_url, canvas_key)
    try:
        the_course = canvas.get_course(args.course)
    except ResourceDoesNotExist:
        print("couldn't find course with canvas id:", args.course)
        sys.exit(1)
    except InvalidAccessToken:
        print("the access key your provided does not seem to be correct:", canvas_key)
        sys.exit(1)
    except Unauthorized:
        print("the access key your provided does not seem to have access to course:", args.course)
        sys.exit(1)
    except (ConnectionError, MissingSchema) as canvas_url_issue:
        print("--canvas_url may have been incorrect:", args.canvas_url, canvas_url_issue)
        sys.exit(1)
    course_groups = the_course.get_groups()

    plannedTeams = csvToTeams(args.assignments)
    group_count = 0
    if DRY:
        print("run with --wet_run to actually add to the following groups the followingfollowing members")
    group_membership_count = 0
    for group in course_groups:
        if group.name in plannedTeams:
            group_count += 1
            # member_count = 0
            if DRY:
                print("group:", group.name)
            for member in plannedTeams[group.name]:
                # member_count += 1
                group_membership_count += 1
                if DRY:
                    print("\tmember:", member)
                else:
                    group.create_membership(member)
    if DRY:
        plural_suffix = "s" if group_membership_count != 1 else ""
        print("run with --wet_run to create the", group_membership_count, " group membership"+ plural_suffix)

if __name__ == "__main__":
    main()
