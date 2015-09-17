from readfile import load_data2002
#import writefile as wf
#import balancedAllocation as bAlloc
from subgroupIdentify import subgroup_identification as subid
from numpy.random import permutation as pm
from numpy import arange
from networkx import DiGraph as DG
#from lifelines.statistics import logrank_test
from plotting import plot_kmf

#def sides():

#    LAPTOP
#    all-2002
#    fname1 = 'D:\\Users\\AL\\Copy\\CoursePaper3\\DATA\\all-2002-rg1-6-60.txt'
#    fname2 = 'D:\\Users\\AL\\Copy\\CoursePaper3\\DATA\\all-2002-rg2-6-60.txt'
#    all-2008
#    fname3 = 'D:\\Users\\AL\\Copy\\CoursePaper3\\DATA\\all-2008-rg1-100-200.txt'
#    fname4 = 'D:\\Users\\AL\\Copy\\CoursePaper3\\DATA\\all-2008-rg1-100-300.txt'
#    fname5 = 'D:\\Users\\AL\\Copy\\CoursePaper3\\DATA\\all-2008-rg1-200-300.txt'
#    fname6 = 'D:\\Users\\AL\\Copy\\CoursePaper3\\DATA\\all-2008-rg2-400-500.txt'

#    PC
#    all-2002
#    fname1 = 'D:\\Copy\\CoursePaper3\\DATA\\all-2002-rg1-6-60.txt'
#    fname2 = 'D:\\Copy\\CoursePaper3\\DATA\\all-2002-rg2-6-60.txt'
#    all-2008
#    fname3 = 'D:\\Copy\\CoursePaper3\\DATA\\all-2008-rg1-100-200.txt'
#    fname4 = 'D:\\Copy\\CoursePaper3\\DATA\\all-2008-rg1-100-300.txt'
#    fname5 = 'D:\\Copy\\CoursePaper3\\DATA\\all-2008-rg1-200-300.txt'
#    fname6 = 'D:\\Copy\\CoursePaper3\\DATA\\all-2008-rg2-400-500.txt'
#    alpha_logrank = 0.05
#    cov_at_level = 3
#    sample, ncov, nobs = load_data2002(fname1)
#    groups = subid(sample, alpha_logrank, cov_at_level)
#    return groups, sample, ncov, nobs

fname1 = 'D:\\Copy\\CoursePaper3\\DATA\\all-2002-rg1-6-60.txt'
fname2 = 'D:\\Copy\\CoursePaper3\\DATA\\all-2002-rg2-6-60.txt'

def permute_sample(sample):
    nobs = len(sample['Rand'])
    inds = pm(nobs)
    s = {key: range(nobs) for key in sample.keys()}
    s['Rand'] = list(sample['Rand'])
    s['Tod'] = list(sample['Tod'])
    s['Time'] = list(sample['Time'])
    for i in xrange(len(inds)):
        for cov in s.keys():
            if cov == 'Rand' or cov == 'Tod' or cov == 'Time':
                continue
            s[cov][i] = sample[cov][inds[i]]
    return s


def select_candidates(groups):
    candidates = {}
    for nn in groups.nodes():
        if not len(DG.successors(groups, nn)):
            candidates[nn] = None
    return candidates


def resampling(sample, upper, lower, step, alpha0, cov_at_level, n=100):
    cutoffs = arange(upper, lower, step)
    max_cutoff = 1

    out_dir = 'D:\\Copy\\CoursePaper3\\out-files-1\\2002-rg1\\groups2.txt'

    for cut in cutoffs:

        print 'Cutoff = %f' % cut

        count = 0

        print 'Run: ',

        for i in xrange(n):

            print '%d' % i,

            groups = subid(permute_sample(sample), cut, cov_at_level)
            candidates = select_candidates(groups)

            f = open(out_dir, 'a')

            for cs in candidates:

                f.write(cs + '\n')
                f.write('Left: %d\tRight: %d\n' % (len(groups.node[cs]['content'].kmf1.durations),
                                                   len(groups.node[cs]['content'].kmf2.durations)))
                f.write('Power: ' + str(groups.node[cs]['content'].pwr) + '\n')
                f.write(str(groups.node[cs]['content'].res_logrank) + '\n')

                if groups.node[cs]['content'].res_logrank.is_significant:
                    count += 1
                    break

            f.write('\n')
            f.close()

            if count > n * alpha0:
                break

        print ''

        if count <= n * alpha0:
            max_cutoff = cut
            break
    return max_cutoff


def get_group(groups, nnode):
    return groups.node[nnode]['content']


def get_description(groups, nnode):
    s = ''
    while nnode != '0':
        parent = groups.predecessors(nnode)[0]
        if parent == '0':
            s += groups.get_edge_data(parent, nnode)['level']
        else:
            s += ''.join([groups.get_edge_data(parent, nnode)['level'], '\n'])
        nnode = parent
    return s