"""
Simple script for post-processing output tables from multiple runs
"""
import argparse
import os

from run import post_process_outputs


def main():
    parser = argparse.ArgumentParser(description="Post-process and combine simulation outputs")
    parser.add_argument(
        "street_segment",
        nargs="+",
        help="The street segment(s) whose outputs you would like to post-process"
    )
    args = parser.parse_args()

    segments = args.street_segment

    for segment in segments:
        if not os.path.exists(os.path.join(f"outputs/{segment}")):
            raise FileNotFoundError(f"Outputs for street segment '{segment}' do not exist!")

    post_process_outputs(True, segments)


if __name__ == "__main__":
    main()
