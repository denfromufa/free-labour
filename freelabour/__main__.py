import datetime
import pathlib
import sys

from . import conf


def percentage_str(stat):
    try:
        percent = stat.me / stat.everyone * 100
    except ZeroDivisionError:
        percent = 0.0
    return '{:.2f}%'.format(percent)


def stats(project):
    print(project.name)
    if project.claimed_commits:
        print('  Manually claimed all commits')
    else:
        names = sorted(map(repr, project.found_names))
        print('  Author/committer as', ', '.join(names))
    print('  Lifetime')
    if project.claimed_commits:
        print('    {:,} commits'.format(project.analysis.all.commit_count.me))
    else:
        commit_stats = '{:,} out of {:,} ({})'.format(
                project.analysis.all.commit_count.me,
                project.analysis.all.commit_count.everyone,
                percentage_str(project.analysis.all.commit_count))
        print('    Commits:', commit_stats)
        if len(names) == 1:
            print('    Ranking:', project.analysis.all.ranking.me)

    print('  Last 12 months')
    if project.analysis.past_year is None:
        print('    No commits made')
    elif project.claimed_commits:
        print('    {:,} commits'.format(project.analysis.past_year.commit_count.me))
    else:
        commit_stats = '{:,} out of {:,} ({})'.format(
                project.analysis.past_year.commit_count.me,
                project.analysis.past_year.commit_count.everyone,
                percentage_str(project.analysis.past_year.commit_count))
        print('    Commits:', commit_stats)
        if len(names) == 1:
            print('    Ranking:', project.analysis.past_year.ranking.me)

    if project.analysis.all.date_range is not None:
        first_commit = project.analysis.all.date_range.first.isoformat()
        print('  First commit:', first_commit)
        last_commit = project.analysis.all.date_range.last.isoformat()
        print('  Latest commit:', last_commit)
    print()


def main(conf_path):
    data = conf.read(conf_path)
    projects = conf.process(data, pathlib.Path(conf_path).parent / 'repos')
    print()
    total_commits = sum(map(lambda p: p.analysis.all.commit_count.me, projects))
    first_commit = datetime.date.today()
    last_commit = datetime.date(1978, 10, 1)
    for project in projects:
        first = project.analysis.all.date_range.first.date()
        last = project.analysis.all.date_range.last.date()
        if first < first_commit:
            first_commit = first
        if last > last_commit:
            last_commit = last
    print('Made {:,} commits across {:,} projects between {} and {}'.format(
            total_commits, len(projects), first_commit.isoformat(),
            last_commit.isoformat()))
    print()
    for project in sorted(projects, key=lambda project: project.name.lower()):
        stats(project)


if __name__ == '__main__':
    main(sys.argv[1])
