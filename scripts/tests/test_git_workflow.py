"""Offline integration checks: real Git repositories and PowerShell, no network."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'git-workflow.ps1'
POWERSHELL = shutil.which('powershell') or shutil.which('pwsh')


@unittest.skipUnless(POWERSHELL and shutil.which('git'), 'Git and PowerShell are required')
class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mater-git-workflow-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'work'
        self.repo.mkdir()
        self.env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GIT_CONFIG_NOSYSTEM='1',
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_MERGE_AUTOEDIT='no')
        self.git('init', '--bare', str(self.root / 'origin.git'))
        self.git('init', '--bare', str(self.root / 'github.git'))
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Workflow Test')
        self.git('config', 'user.email', 'workflow@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.git('config', 'commit.gpgsign', 'false')
        (self.repo / 'scripts').mkdir()
        shutil.copy2(SCRIPT, self.repo / 'scripts' / SCRIPT.name)
        (self.repo / 'shared.txt').write_text('base\n', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-m', 'base')
        for remote in ('origin', 'github'):
            self.git('remote', 'add', remote, str(self.root / (remote + '.git')))
            self.git('push', remote, 'main')
        self.git('switch', '-c', 'develop')
        self.git('push', '-u', 'origin', 'develop')
        self.git('switch', '-c', 'feature/test')
        self.git('push', '-u', 'origin', 'feature/test')

    def git(self, *args, ok=True):
        result = subprocess.run(['git', *args], cwd=self.repo, env=self.env,
                                text=True, encoding='utf-8', errors='replace', capture_output=True)
        if ok and result.returncode:
            self.fail(f'git {args}:\n{result.stdout}\n{result.stderr}')
        return result.stdout.strip()

    def run_action(self, action, success=True):
        result = subprocess.run([POWERSHELL, '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                 '-File', str(self.repo / 'scripts' / SCRIPT.name), '-Action', action],
                                cwd=self.repo, env=self.env, text=True, encoding='utf-8',
                                errors='replace', capture_output=True, timeout=40)
        self.assertEqual(result.returncode, 0 if success else 1,
                         f'{action}:\n{result.stdout}\n{result.stderr}')
        self.assertEqual(self.git('branch', '--show-current'), 'feature/test')
        return result.stdout + result.stderr

    def commit(self, name, text):
        (self.repo / name).write_text(text, encoding='utf-8')
        self.git('add', '--', name)
        self.git('commit', '-m', name)
        return self.git('rev-parse', 'HEAD')

    def advance_develop(self, name='team.txt', text='team\n'):
        self.git('switch', 'develop')
        tip = self.commit(name, text)
        self.git('push', 'origin', 'develop')
        self.git('switch', 'feature/test')
        return tip

    def remote_tip(self, remote, branch):
        return self.git('ls-remote', '--heads', remote, f'refs/heads/{branch}').split()[0]

    def test_sync_fast_forwards_without_pushing_personal(self):
        old = self.remote_tip('origin', 'feature/test')
        target = self.advance_develop()
        self.run_action('Sync')
        self.assertEqual(self.git('rev-parse', 'HEAD'), target)
        self.assertEqual(self.git('rev-parse', 'develop'), target)
        self.assertEqual(self.remote_tip('origin', 'feature/test'), old)
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_push_merges_remote_personal_and_develop_without_rewriting(self):
        self.git('switch', '-c', 'remote-personal')
        other = self.commit('other.txt', 'other\n')
        self.git('push', 'origin', 'HEAD:refs/heads/feature/test')
        self.git('switch', 'feature/test')
        local = self.commit('mine.txt', 'mine\n')
        team = self.advance_develop()
        self.run_action('Push')
        for ancestor in (other, local, team):
            self.git('merge-base', '--is-ancestor', ancestor, 'HEAD')
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.remote_tip('origin', 'feature/test'))
        self.assertNotEqual(self.git('rev-parse', 'HEAD'), team)
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_after_merge_aligns_all_four_refs_and_is_repeatable(self):
        self.commit('mine.txt', 'mine\n')
        self.git('push', 'origin', 'feature/test')
        self.git('switch', 'develop')
        self.git('merge', '--no-ff', 'feature/test', '-m', 'simulated PR')
        target = self.git('rev-parse', 'HEAD')
        self.git('push', 'origin', 'develop')
        self.git('switch', 'feature/test')
        self.run_action('AfterMerge')
        self.run_action('AfterMerge')
        for ref in ('HEAD', 'develop', 'origin/develop', 'origin/feature/test'):
            self.assertEqual(self.git('rev-parse', ref), target)
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_after_merge_refuses_unmerged_local_commit(self):
        local = self.commit('mine.txt', 'mine\n')
        remote = self.remote_tip('origin', 'feature/test')
        self.run_action('AfterMerge', success=False)
        self.assertEqual(self.git('rev-parse', 'HEAD'), local)
        self.assertEqual(self.remote_tip('origin', 'feature/test'), remote)

    def test_after_merge_refuses_unmerged_remote_personal_commit(self):
        self.git('switch', '-c', 'remote-personal')
        tip = self.commit('other.txt', 'other\n')
        self.git('push', 'origin', 'HEAD:refs/heads/feature/test')
        self.git('switch', 'feature/test')
        self.run_action('AfterMerge', success=False)
        self.assertEqual(self.remote_tip('origin', 'feature/test'), tip)

    def test_local_develop_ahead_is_not_overwritten(self):
        self.git('switch', 'develop')
        tip = self.commit('local-only.txt', 'keep\n')
        self.git('switch', 'feature/test')
        self.run_action('Sync', success=False)
        self.assertEqual(self.git('rev-parse', 'develop'), tip)

    def test_dirty_and_in_progress_work_are_preserved(self):
        (self.repo / 'untracked.txt').write_text('keep\n', encoding='utf-8')
        self.run_action('Sync', success=False)
        self.assertTrue((self.repo / 'untracked.txt').is_file())
        (self.repo / 'untracked.txt').unlink()
        (self.repo / '.git' / 'rebase-merge').mkdir()
        self.run_action('Sync', success=False)
        self.assertTrue((self.repo / '.git' / 'rebase-merge').is_dir())

    def test_sync_conflict_aborts_only_its_own_merge(self):
        tip = self.commit('shared.txt', 'personal\n')
        self.advance_develop('shared.txt', 'team\n')
        self.run_action('Sync', success=False)
        self.assertEqual(self.git('rev-parse', 'HEAD'), tip)
        self.assertEqual(self.git('status', '--porcelain'), '')
        self.assertFalse((self.repo / '.git' / 'MERGE_HEAD').exists())

    def test_publish_returns_personal_and_is_repeatable(self):
        self.advance_develop()
        personal = self.git('rev-parse', 'HEAD')
        self.run_action('Publish')
        self.run_action('Publish')
        self.assertEqual(self.git('rev-parse', 'HEAD'), personal)
        self.assertEqual(self.remote_tip('origin', 'main'), self.remote_tip('github', 'main'))
        self.git('merge-base', '--is-ancestor', 'origin/develop', 'main')
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_partial_publish_reports_failure_returns_and_can_retry(self):
        self.advance_develop()
        old = self.remote_tip('github', 'main')
        hook = self.root / 'github.git' / 'hooks' / 'pre-receive'
        hook.write_text('#!/bin/sh\nexit 1\n', encoding='utf-8', newline='\n')
        hook.chmod(0o755)
        self.run_action('Publish', success=False)
        self.assertNotEqual(self.remote_tip('origin', 'main'), old)
        self.assertEqual(self.remote_tip('github', 'main'), old)
        hook.unlink()
        self.run_action('Publish')
        self.assertEqual(self.remote_tip('origin', 'main'), self.remote_tip('github', 'main'))

    def test_publish_conflict_aborts_and_restores_branch(self):
        self.git('switch', 'main')
        self.commit('shared.txt', 'main\n')
        self.git('push', 'origin', 'main')
        self.git('push', 'github', 'main')
        self.git('switch', 'feature/test')
        self.advance_develop('shared.txt', 'team\n')
        self.run_action('Publish', success=False)
        self.assertEqual(self.git('status', '--porcelain'), '')
        self.assertFalse((self.repo / '.git' / 'MERGE_HEAD').exists())


    def test_after_squash_merge_refuses_equal_tree_with_different_history(self):
        self.commit('mine.txt', 'mine\n')
        self.git('push', 'origin', 'feature/test')
        self.git('switch', 'develop')
        self.git('merge', '--squash', 'feature/test')
        self.git('commit', '-m', 'squashed PR')
        self.git('push', 'origin', 'develop')
        self.git('switch', 'feature/test')
        self.assertEqual(self.git('diff', 'HEAD', 'develop'), '')
        self.run_action('AfterMerge', success=False)

    def test_sync_creates_missing_local_develop(self):
        self.git('branch', '-d', 'develop')
        self.run_action('Sync')
        self.assertEqual(self.git('rev-parse', 'develop'), self.git('rev-parse', 'origin/develop'))

    def test_publish_rejects_unpublished_direct_main_commit(self):
        old = self.remote_tip('origin', 'main')
        self.git('switch', 'main')
        tip = self.commit('accidental-main.txt', 'preserve\n')
        self.git('switch', 'feature/test')
        self.run_action('Publish', success=False)
        self.assertEqual(self.git('rev-parse', 'main'), tip)
        self.assertEqual(self.remote_tip('origin', 'main'), old)
        self.assertEqual(self.remote_tip('github', 'main'), old)

    def test_github_independent_commits_block_before_either_push(self):
        old = self.remote_tip('origin', 'main')
        self.git('switch', '-c', 'github-only', 'main')
        tip = self.commit('github-only.txt', 'preserve\n')
        self.git('push', 'github', 'HEAD:refs/heads/main')
        self.git('switch', 'feature/test')
        self.advance_develop()
        self.run_action('Publish', success=False)
        self.assertEqual(self.remote_tip('origin', 'main'), old)
        self.assertEqual(self.remote_tip('github', 'main'), tip)

    def test_first_publish_rejection_keeps_release_merge_retryable(self):
        self.advance_develop()
        old = self.remote_tip('origin', 'main')
        hook = self.root / 'origin.git' / 'hooks' / 'pre-receive'
        hook.write_text('#!/bin/sh\nexit 1\n', encoding='utf-8', newline='\n')
        hook.chmod(0o755)
        self.run_action('Publish', success=False)
        self.assertEqual(self.remote_tip('origin', 'main'), old)
        self.assertNotEqual(self.git('rev-parse', 'main'), old)
        hook.unlink()
        self.run_action('Publish')
        self.assertEqual(self.remote_tip('origin', 'main'), self.remote_tip('github', 'main'))

if __name__ == '__main__':
    unittest.main(verbosity=2)
