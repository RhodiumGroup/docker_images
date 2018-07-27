import yaml
import argparse
import sys


if __name__ == '__main__':
    stream = open('rhg-hub/Chart.yaml', 'r')
    d = yaml.load(stream)
    if sys.argv[1:]:
        d['tag'] = sys.argv[1]
    if sys.argv[2]:
        d['version'] = sys.argv[2]

