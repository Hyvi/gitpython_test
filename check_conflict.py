# -*- coding: utf-8 -*-     
from git import Repo
repo_path = '/Users/hyvi/Documents/gliese-vtiger-magento-all/hyvi.github.com/.git'
repo = Repo(repo_path)
def merge_base_between_branchs():
    #  print repo.refs.master.commit
    #  print repo.remotes.origin.refs.master.commit
    repo.remotes.origin.fetch()
    merge_base = repo.merge_base(repo.remotes.origin.refs.master, repo.refs.master)
    return merge_base


def get_origin_diff_base():
    diffs = dict()
    for diff in repo.remotes.origin.refs.master.commit.diff(merge_base_between_branchs()):
        # 如果是rename的情况，a与b的path是不一样，其他情况('A','M','D')下是一样的
        #  print '%s VS %s' % (diff.a_path, diff.b_path)
        # a_path 在新增情况下为None
        if diff.a_path:
            diffs[diff.a_path] = diff
        if diff.b_path:
            diffs[diff.b_path] = diff

    return diffs

# 获取origin/master分支的所有的diff,并检查提交的diff文件是否存在远程主干分支上diff
# 如果不存冲突，则返回所有False, 否则返回冲突list
def check_branch_commit_vs_master_diff(branch_diffs):
    result = False 
    conflict_diffs = dict()
    origin_master_diffs = get_origin_diff_base() 
    for k in branch_diffs:
        if k in origin_master_diffs:
            result = True
            conflict_diffs[k] = origin_master_diffs[k]

    if result == True:
        return conflict_diffs
    else:
        return result

# 检查当前分支提交的diff是否存在待审核的的文件中 , 连表查询
def check_branch_commit_vs_auditing_commit(branch_diffs):
    # 查数据库中待审核的文件列表，返回list
    session = create_session()
    auditing_paths = query_sir_by_psr_state(session, 1)

    result = False 
    conflict_diffs = dict()
    for k in branch_diffs:
        if k in auditing_paths:
            result = True
            conflict_diffs[k] = auditing_paths[k]

    session.close()
    if result == True:
        return conflict_diffs
    else:
        return result


# 根据psr中state=1待审核的查询所有的sir记录，
def query_sir_by_psr_state(session, state):
    
    all_auditing_paths = dict()
    auditing_psrs = session.query(ProtocolSubmitRecord).filter_by(state=state).all()
    sub_ids = []
    [sub_ids.append(apsr.id) for apsr in auditing_psrs]

    sirs = session.query(SubmitItemRecord).filter_by(SubmitItemRecord.sub_id.in_(sub_ids)).all()

    for sir in sirs:
        for path in sir.paths.split('++'):
            all_auditing_paths[path] = sir



if __name__ == "__main__":
    print merge_base_between_branchs()
    diffs = get_origin_diff_base()
    # 当前分支的最新一个提交
    bdiffs = dict()
    for bdiff in repo.refs.master.commit.diff('HEAD~1'):
        # 如果是rename的情况，a与b的path是不一样，其他情况('A','M','D')下是一样的
        # a_path 在新增情况下为None
        if bdiff.a_path:
            bdiffs[bdiff.a_path] = bdiff
        if bdiff.b_path:
            bdiffs[bdiff.b_path] = bdiff

    print check_branch_commit_vs_master_diff(bdiffs)

    

